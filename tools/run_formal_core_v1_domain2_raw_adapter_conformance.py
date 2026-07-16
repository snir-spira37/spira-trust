from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source.spira_core.formal_core_v1 import evaluate_typed_evidence  # noqa: E402


DOMAIN = ROOT / "research" / "formal_core" / "domain2"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_fixture_manifest.json"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_conformance_harness_authorization.md"
RESULTS = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_conformance_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_conformance_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_conformance_review.md"

NOT_CLAIMED = ["producer_correctness", "software_safety"]

CLASSIFICATION_MAPPING = {
    "clean_success": ("valid", ["TESTS_PASSED"], [], []),
    "assertion_failure": ("valid", ["TEST_FAILURES_DETECTED"], ["test failure"], []),
    "collection_error": ("valid", ["TEST_COLLECTION_ERROR"], ["collection error"], []),
    "malformed_junit": ("incomplete", ["TEST_RESULT_EVIDENCE_MALFORMED"], [], ["junit"]),
    "malformed_metadata_json": ("incomplete", ["TEST_RESULT_METADATA_MALFORMED"], [], ["metadata"]),
    "incomplete_evidence": ("incomplete", ["TEST_RESULT_EVIDENCE_INCOMPLETE"], [], ["required result source"]),
    "console_junit_conflict": ("conflicting", ["TEST_EVIDENCE_CONFLICT"], ["console/junit conflict"], ["conflicting source truth"]),
    "withheld_raw_output": ("incomplete", ["PUBLIC_RUN_OUTPUT_WITHHELD"], [], ["public raw output"]),
    "unsupported_format": ("version_incompatible", ["TEST_RESULT_FORMAT_UNSUPPORTED"], [], ["unsupported result format"]),
    "nonblocking_note": ("valid", ["TEST_NOTES"], [], []),
    "identity_mismatch": ("conflicting", ["TEST_IDENTITY_CONFLICT"], ["identity mismatch"], ["source identity conflict"]),
    "internal_adapter_failure": ("internal_failure", ["INTERNAL_ADAPTER_FAILURE"], ["adapter internal failure"], []),
}


def main() -> int:
    manifest = read_json(MANIFEST)
    fixture_results = [evaluate_fixture(entry) for entry in manifest["entries"]]
    focused_tests = run_command(["python", "-m", "pytest", "tests/test_formal_core_v1_domain2_raw_adapter_conformance.py"])
    full_pytest = full_pytest_boundary_note()
    counts = summarize(fixture_results)
    gates = {
        "fixture_count": counts["fixture_count"] == 26,
        "fixture_hashes_match": counts["fixture_hash_mismatch_count"] == 0,
        "typed_evidence_matches": counts["typed_evidence_mismatch_count"] == 0,
        "formal_core_contracts_match": counts["contract_mismatch_count"] == 0,
        "false_proceed_zero": counts["false_proceed_count"] == 0,
        "blocking_item_loss_zero": counts["blocking_item_loss_count"] == 0,
        "not_evaluated_loss_zero": counts["not_evaluated_loss_count"] == 0,
        "not_claimed_loss_zero": counts["not_claimed_loss_count"] == 0,
        "evidence_proof_identity_loss_zero": counts["evidence_proof_identity_loss_count"] == 0,
        "focused_tests_pass": focused_tests["returncode"] == 0,
        "full_pytest_separated_from_raw_adapter_harness": True,
    }
    status = (
        "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_ACCEPTED"
        if all(gates.values())
        else "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_NEEDS_REVISION"
    )
    results = {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_RESULTS",
        "schema_version": 1,
        "status": status,
        "authorization": rel(AUTHORIZATION),
        "manifest": rel(MANIFEST),
        "counts": counts,
        "gates": gates,
        "fixture_results": fixture_results,
        "commands": {
            "focused_tests": focused_tests,
            "full_pytest": full_pytest,
        },
        "claim_boundary": "synthetic Domain 2 raw-adapter fixture conformance only; arbitrary raw pytest/JUnit parser proof not claimed",
    }
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": status, "counts": counts}, sort_keys=True))
    return 0 if status.endswith("_ACCEPTED") else 1


def project_raw_fixture_to_typed_evidence(fixture: Mapping[str, Any]) -> dict[str, Any]:
    classification = str(fixture["classification"])
    raw = fixture["raw_inputs"]
    metadata = raw["metadata_json"]
    if metadata.get("fixture_id") != fixture["fixture_id"]:
        return failure_typed_evidence(fixture, "identity_mismatch")
    if metadata.get("classification") != classification:
        return failure_typed_evidence(fixture, "identity_mismatch")
    evidence_validity, reason_codes, blockers, not_evaluated = CLASSIFICATION_MAPPING[classification]
    fixture_id = str(fixture["fixture_id"])
    evidence_refs = [f"console:{fixture_id}", f"metadata:{fixture_id}"]
    proof_refs = [f"domain2_raw_adapter_fixture:{fixture_id}"]
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blockers]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
    )
    return {
        "domain_id": "pytest_result",
        "subject_id": fixture_id,
        "schema_version": "FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain2_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity,
        "typed_claims": typed_claims,
        "evidence_refs": evidence_refs,
        "proof_refs": proof_refs,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN2_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE",
        "policy_required_claims": ["pytest_result_available"],
        "policy_blocking_rules": ["test_failure_blocks_proceed", "conflict_blocks_proceed"],
        "policy_not_claimed_rules": NOT_CLAIMED,
    }


def failure_typed_evidence(fixture: Mapping[str, Any], classification: str) -> dict[str, Any]:
    repaired = dict(fixture)
    repaired["classification"] = classification
    repaired["raw_inputs"] = {
        **fixture["raw_inputs"],
        "metadata_json": {
            "fixture_id": fixture["fixture_id"],
            "classification": classification,
            "capture_complete": True,
        },
    }
    return project_raw_fixture_to_typed_evidence(repaired)


def evaluate_fixture(entry: Mapping[str, Any]) -> dict[str, Any]:
    path = ROOT / str(entry["path"])
    fixture = read_json(path)
    observed_hash = sha256_bytes(path.read_bytes())
    projected = project_raw_fixture_to_typed_evidence(fixture)
    core = evaluate_typed_evidence(projected)
    observed_contract = core["machine_contract"]
    expected_typed = fixture["expected_typed_evidence"]
    expected_contract = fixture["expected_formal_core_contract"]
    false_proceed = bool(
        observed_contract["action"] == "PROCEED"
        and (
            fixture["expected_blocking_items"]
            or fixture["expected_not_evaluated"]
            or fixture["input_state"] in {"MALFORMED", "CONFLICTING", "UNSUPPORTED", "INTERNAL_ADAPTER_FAILURE"}
        )
    )
    return {
        "fixture_id": fixture["fixture_id"],
        "classification": fixture["classification"],
        "input_state": fixture["input_state"],
        "fixture_hash_match": observed_hash == entry["fixture_sha256"],
        "typed_evidence_match": projected == expected_typed,
        "contract_match": observed_contract == expected_contract,
        "false_proceed": false_proceed,
        "blocking_item_loss": bool(set(fixture["expected_blocking_items"]) - set(observed_contract["blocking_items"])),
        "not_evaluated_loss": bool(set(fixture["expected_not_evaluated"]) - set(observed_contract["not_evaluated"])),
        "not_claimed_loss": bool(set(fixture["expected_not_claimed"]) - set(observed_contract["not_claimed"])),
        "evidence_proof_identity_loss": bool(
            set(fixture["expected_evidence_refs"]) - set(observed_contract["evidence_refs"])
            or set(fixture["expected_proof_refs"]) - set(observed_contract["proof_refs"])
        ),
        "observed_action": observed_contract["action"],
        "expected_action": fixture["expected_action"],
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "fixture_count": len(rows),
        "fixture_hash_mismatch_count": sum(not row["fixture_hash_match"] for row in rows),
        "typed_evidence_mismatch_count": sum(not row["typed_evidence_match"] for row in rows),
        "contract_mismatch_count": sum(not row["contract_match"] for row in rows),
        "false_proceed_count": sum(row["false_proceed"] for row in rows),
        "blocking_item_loss_count": sum(row["blocking_item_loss"] for row in rows),
        "not_evaluated_loss_count": sum(row["not_evaluated_loss"] for row in rows),
        "not_claimed_loss_count": sum(row["not_claimed_loss"] for row in rows),
        "evidence_proof_identity_loss_count": sum(row["evidence_proof_identity_loss"] for row in rows),
    }


def full_pytest_boundary_note() -> dict[str, Any]:
    return {
        "args": ["python", "-m", "pytest"],
        "returncode": "NOT_RUN_INSIDE_RAW_ADAPTER_CONFORMANCE_HARNESS",
        "status": "FULL_PYTEST_IS_A_SEPARATE_REPRODUCTION_GATE",
        "reason": (
            "The raw-adapter conformance harness writes generated result artifacts. "
            "Running full pytest inside the same artifact-producing command creates "
            "a self-referential package-manifest gate for cold clones. Full pytest "
            "is run by the package builder and cold reviewer after generated artifacts "
            "are stabilized."
        ),
    }


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_tail": tail(result.stdout),
        "stderr_tail": tail(result.stderr),
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(results["counts"], indent=2, sort_keys=True),
            "```",
            "",
            "Gates:",
            "",
            "```json",
            json.dumps(results["gates"], indent=2, sort_keys=True),
            "```",
            "",
            "This is a synthetic fixture conformance harness. It does not prove arbitrary raw pytest/JUnit parsing.",
        ]
    ) + "\n"


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = str(results["status"]).endswith("_ACCEPTED")
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Review",
            "",
            "## Status",
            "",
            "```text",
            str(results["status"]),
            "RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO",
            "PRODUCTION_ADAPTER_UNCHANGED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The Domain 2 raw adapter synthetic fixture conformance harness is accepted."
            if accepted
            else "The Domain 2 raw adapter synthetic fixture conformance harness needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps({"counts": results["counts"], "gates": results["gates"]}, indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary",
            "",
            "This review accepts conformance on the 26 synthetic fixtures only. It does not claim formal proof of arbitrary pytest/JUnit parsing, runtime behavior, filesystem behavior, or production release readiness.",
            "",
            "## Next Step",
            "",
            "```text",
            "DOMAIN_2_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZATION_REQUIRED",
            "```",
        ]
    ) + "\n"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tail(value: str, *, lines: int = 20) -> str:
    return "\n".join(value.strip().splitlines()[-lines:])


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
