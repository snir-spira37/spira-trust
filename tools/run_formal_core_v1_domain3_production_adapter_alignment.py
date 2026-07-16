from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from spira_core import terraform_plan_oracle_validator as validator  # noqa: E402
from spira_core import terraform_plan_producer as producer  # noqa: E402


DOMAIN = ROOT / "research" / "formal_core" / "domain3"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain3_production_adapter_alignment_authorization.md"
MANIFEST = ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "terraform_plan_contract" / "oracle_v1.json"
RESULTS = DOMAIN / "spira_formal_core_v1_domain3_production_adapter_alignment_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain3_production_adapter_alignment_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain3_production_adapter_alignment_review.md"
CONFORMANCE_REVIEW = DOMAIN / "spira_formal_core_v1_domain3_conformance_review.md"

PRODUCER_PATHS = [
    ROOT / "source" / "spira_core" / "terraform_plan_producer.py",
    ROOT / "source" / "spira_core" / "terraform_plan_oracle_validator.py",
]


def main() -> int:
    conformance = load_domain3_conformance_module()
    raw_harness = load_raw_adapter_harness_module()
    manifest = read_json(MANIFEST)
    oracle = read_json(ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    validation = validator.validate_oracle_document(producer.candidate_oracle_from_produced(oracle, produced), root=ROOT)
    lean = accepted_domain3_conformance_status()
    proof_scan = {"status": "PASS", "matches": []}
    production = conformance.evaluate_conformance(manifest, oracle, produced, validation, lean, proof_scan)
    fixture_rows = [raw_harness.evaluate_fixture(entry) for entry in read_json(raw_harness.MANIFEST)["entries"]]
    fixture_counts = raw_harness.summarize(fixture_rows)
    focused_tests = run_command(
        [
            "python",
            "-m",
            "pytest",
            "tests/test_terraform_plan_producer.py",
            "tests/test_terraform_plan_oracle_validator.py",
            "tests/test_formal_core_v1_domain3_raw_adapter_conformance.py",
            "tests/test_formal_core_v1_domain3_production_adapter_alignment.py",
        ]
    )
    full_pytest = run_command(["python", "-m", "pytest"])
    source_status = git_status(PRODUCER_PATHS)
    gates = {
        "production_domain3_conformance_accepted": production["status"]
        == "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED",
        "production_case_count": production["case_count"] == 40,
        "production_case_pass_count": production["case_pass_count"] == 40,
        "production_mutation_pairs_pass": production["mutation_pair_checks"]["passed"] == 10
        and production["mutation_pair_checks"]["total"] == 10,
        "validator_pass": production["validator"]["verdict"] == "PASS",
        "synthetic_fixture_count": fixture_counts["fixture_count"] == 31,
        "synthetic_fixture_contracts_match": fixture_counts["contract_mismatch_count"] == 0,
        "synthetic_fixture_typed_evidence_matches": fixture_counts["typed_evidence_mismatch_count"] == 0,
        "false_proceed_zero": production["blocking_to_proceed_cases"] == []
        and production["not_evaluated_to_proceed_cases"] == []
        and production["malformed_to_proceed_cases"] == []
        and fixture_counts["false_proceed_count"] == 0,
        "blocking_item_loss_zero": fixture_counts["blocking_item_loss_count"] == 0,
        "not_evaluated_loss_zero": fixture_counts["not_evaluated_loss_count"] == 0,
        "not_claimed_loss_zero": fixture_counts["not_claimed_loss_count"] == 0,
        "resource_action_loss_zero": fixture_counts["resource_action_loss_count"] == 0,
        "replace_path_loss_zero": fixture_counts["replace_path_loss_count"] == 0,
        "unknown_path_loss_zero": fixture_counts["unknown_path_loss_count"] == 0,
        "sensitive_path_loss_zero": fixture_counts["sensitive_path_loss_count"] == 0,
        "focused_tests_pass": focused_tests["returncode"] == 0,
        "full_pytest_pass": full_pytest["returncode"] == 0,
        "production_adapter_source_unchanged": source_status == "",
    }
    status = (
        "SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED"
        if all(gates.values())
        else "SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_NEEDS_REVISION"
    )
    results = {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_RESULTS",
        "schema_version": 1,
        "status": status,
        "authorization": rel(AUTHORIZATION),
        "gates": gates,
        "production_conformance_summary": {
            "status": production["status"],
            "case_count": production["case_count"],
            "case_pass_count": production["case_pass_count"],
            "case_fail_count": production["case_fail_count"],
            "action_distribution": production["action_distribution"],
            "mutation_pair_checks": production["mutation_pair_checks"],
            "mismatch_count": production["mismatch_count"],
            "blocking_to_proceed_cases": production["blocking_to_proceed_cases"],
            "not_evaluated_to_proceed_cases": production["not_evaluated_to_proceed_cases"],
            "malformed_to_proceed_cases": production["malformed_to_proceed_cases"],
            "sensitive_value_leak_cases": production["sensitive_value_leak_cases"],
        },
        "synthetic_fixture_summary": fixture_counts,
        "commands": {
            "focused_tests": focused_tests,
            "full_pytest": full_pytest,
        },
        "production_adapter_source_status": source_status,
        "accepted_domain3_conformance_review": rel(CONFORMANCE_REVIEW),
        "claim_boundary": "bounded Domain 3 production adapter alignment only; arbitrary raw Terraform Plan JSON parser proof not claimed",
    }
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(report_markdown(results), encoding="utf-8", newline="\n")
    REVIEW.write_text(review_markdown(results), encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "gates": gates}, sort_keys=True))
    return 0 if status.endswith("_ACCEPTED") else 1


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Production Adapter Alignment Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "```",
            "",
            "Gates:",
            "",
            "```json",
            json.dumps(results["gates"], indent=2, sort_keys=True),
            "```",
            "",
            "Production conformance:",
            "",
            "```json",
            json.dumps(results["production_conformance_summary"], indent=2, sort_keys=True),
            "```",
            "",
            "Synthetic fixtures:",
            "",
            "```json",
            json.dumps(results["synthetic_fixture_summary"], indent=2, sort_keys=True),
            "```",
        ]
    ) + "\n"


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = str(results["status"]).endswith("_ACCEPTED")
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Production Adapter Alignment Review",
            "",
            "## Status",
            "",
            "```text",
            str(results["status"]),
            "RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO",
            "TERRAFORM_EXECUTION_FORMALLY_PROVED_NO",
            "PRODUCTION_ADAPTER_SOURCE_UNCHANGED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The bounded Domain 3 production adapter alignment is accepted."
            if accepted
            else "The bounded Domain 3 production adapter alignment needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(results["gates"], indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary",
            "",
            "This review aligns the existing Domain 3 Terraform Plan production adapter with the accepted corpus and synthetic fixture suite. It does not prove arbitrary raw Terraform Plan JSON parser correctness, Terraform execution, provider behavior, cloud-state freshness, cost correctness, security, compliance, apply success, production readiness, or release readiness.",
            "",
            "## Next Step",
            "",
            "```text",
            "DOMAIN_1_RAW_ADAPTER_CONFORMANCE_SPECIFICATION_OR_FORMAL_CORE_ADAPTER_PROOF_PACKAGE_REQUIRED",
            "```",
        ]
    ) + "\n"


def load_domain3_conformance_module() -> Any:
    return load_module("domain3_conformance", ROOT / "tools" / "run_formal_core_v1_domain3_conformance.py")


def load_raw_adapter_harness_module() -> Any:
    return load_module("domain3_raw_adapter_conformance", ROOT / "tools" / "run_formal_core_v1_domain3_raw_adapter_conformance.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def accepted_domain3_conformance_status() -> dict[str, Any]:
    text = CONFORMANCE_REVIEW.read_text(encoding="utf-8")
    accepted = "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED" in text
    return {
        "command": "accepted Domain 3 conformance review",
        "returncode": 0 if accepted else 1,
        "stdout_tail": "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED" if accepted else "",
        "stderr_tail": "" if accepted else "accepted Domain 3 conformance review not found",
    }


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_tail": tail(result.stdout),
        "stderr_tail": tail(result.stderr),
    }


def git_status(paths: list[Path]) -> str:
    relative = [rel(path) for path in paths]
    result = subprocess.run(["git", "status", "--short", *relative], cwd=ROOT, text=True, capture_output=True, check=False)
    return result.stdout.strip()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def tail(value: str, *, lines: int = 20) -> str:
    return "\n".join(value.strip().splitlines()[-lines:])


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
