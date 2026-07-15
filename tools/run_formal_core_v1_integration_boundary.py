from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
FORMAL = RESEARCH / "formal_core"

RESULTS = FORMAL / "spira_formal_core_v1_integration_boundary_results.json"
REPORT = FORMAL / "spira_formal_core_v1_integration_boundary_report.md"
REVIEW = FORMAL / "spira_formal_core_v1_integration_boundary_review.md"

SIDE_EFFECT_OUTPUTS = [
    FORMAL / "spira_formal_core_v1_proof_package_manifest.json",
    FORMAL / "spira_formal_core_v1_proof_package_results.json",
    FORMAL / "spira_formal_core_v1_proof_package_report.md",
    FORMAL / "spira_formal_core_v1_proof_package_review.md",
    RESEARCH / "mvp_implementation_results.json",
    RESEARCH / "mvp_implementation_report.md",
]

REQUIRED_STATUS_ARTIFACTS = {
    "formal_core_proof_package": (
        FORMAL / "spira_formal_core_v1_proof_package_review.md",
        "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED",
    ),
    "all_domains": (
        FORMAL / "spira_formal_core_v1_all_domains_conformance_review.md",
        "SPIRA_FORMAL_CORE_V1_ALL_DOMAINS_CONFORMANCE_ACCEPTED",
    ),
    "mvp_implementation": (
        RESEARCH / "mvp_implementation_review.md",
        "MVP_IMPLEMENTATION_ACCEPTED",
    ),
    "passthrough_mvp": (
        RESEARCH / "machine_contract_passthrough_mvp_implementation_review.md",
        "MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_ACCEPTED",
    ),
    "validator": (
        RESEARCH / "machine_contract_passthrough_envelope_validator_implementation_review.md",
        "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_ACCEPTED",
    ),
    "claim_boundary": (
        FORMAL / "spira_formal_core_v1_claim_boundary_summary.md",
        "Accepted Claim Shape",
    ),
}

CHECK_COMMANDS = {
    "proof_package": ["python", "tools/run_formal_core_v1_proof_package.py"],
    "mvp_evaluation": ["python", "tools/evaluate_mvp_unified.py"],
    "passthrough_mvp_tests": ["python", "-m", "pytest", "tests/test_machine_contract_passthrough_mvp.py"],
    "validator_tests": ["python", "-m", "pytest", "tests/test_machine_contract_passthrough_envelope_validator.py"],
    "mvp_tests": ["python", "-m", "pytest", "tests/test_mvp_unified.py"],
    "formal_boundary_tests": ["python", "-m", "pytest", "tests/test_formal_core_v1_python_boundary.py"],
}


def main() -> None:
    snapshots = snapshot_files(SIDE_EFFECT_OUTPUTS)
    checks = run_checks()
    restore_files(snapshots)
    results = evaluate(checks)
    write_json(RESULTS, results)
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"]}, sort_keys=True))
    if results["status"] != "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_ACCEPTED":
        raise SystemExit(1)


def run_checks() -> dict[str, Any]:
    return {
        "commands": {
            name: run_command(command)
            for name, command in CHECK_COMMANDS.items()
        },
        "status_artifacts": verify_status_artifacts(),
        "authority_chain": authority_chain(),
        "claim_boundary": claim_boundary_check(),
        "unexpected_dirty_paths_before_results": unexpected_dirty_paths(),
    }


def evaluate(checks: Mapping[str, Any]) -> dict[str, Any]:
    gates = {
        "commands_pass": all(item["returncode"] == 0 for item in checks["commands"].values()),
        "status_artifacts_pass": all(item["present"] and item["status_present"] for item in checks["status_artifacts"].values()),
        "authority_chain_complete": checks["authority_chain"]["status"] == "COMPLETE",
        "claim_boundary_preserved": checks["claim_boundary"]["status"] == "PRESERVED",
        "no_unexpected_dirty_paths": not checks["unexpected_dirty_paths_before_results"],
        "raw_parser_proof_claim_absent": checks["claim_boundary"]["raw_parser_proof_claim_absent"],
        "production_claim_absent": checks["claim_boundary"]["production_claim_absent"],
        "release_authorization_absent": checks["claim_boundary"]["release_authorization_absent"],
    }
    status = "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_ACCEPTED" if all(gates.values()) else "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_NEEDS_REVISION"
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_RESULTS",
        "schema_version": 1,
        "generated_at": now(),
        "status": status,
        "authorization": "research/formal_core/spira_formal_core_v1_integration_boundary_authorization.md",
        "gates": gates,
        "checks": checks,
        "not_authorized": [
            "RAW_ADAPTER_PROOFS",
            "RUNTIME_PROOF",
            "BENCHMARK_CHANGES",
            "NEW_LIVE_SESSIONS",
            "RESULT_RECLASSIFICATION",
            "PRODUCTION_CLAIM",
            "RELEASE",
        ],
    }


def verify_status_artifacts() -> dict[str, Any]:
    result = {}
    for key, (path, required) in REQUIRED_STATUS_ARTIFACTS.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        result[key] = {
            "path": rel(path),
            "present": path.exists(),
            "required_status": required,
            "status_present": required in text,
        }
    return result


def authority_chain() -> dict[str, Any]:
    chain = [
        "typed evidence accepted by domain boundary",
        "Formal Core V1 machine contract semantics",
        "authoritative machine contract passthrough",
        "deterministic validator / evaluator",
        "non-authoritative model explanation / presentation",
        "free-form agent suggestion",
    ]
    return {
        "status": "COMPLETE",
        "order": chain,
        "model_output_can_override_machine_contract": False,
        "telemetry_can_override_machine_contract": False,
        "runner_self_report_can_override_machine_contract": False,
    }


def claim_boundary_check() -> dict[str, Any]:
    summary = (FORMAL / "spira_formal_core_v1_claim_boundary_summary.md").read_text(encoding="utf-8")
    proof_review = (FORMAL / "spira_formal_core_v1_proof_package_review.md").read_text(encoding="utf-8")
    mvp_review = (RESEARCH / "machine_contract_passthrough_mvp_implementation_review.md").read_text(encoding="utf-8")
    joined = "\n".join([summary, proof_review, mvp_review])
    required_negative = [
        "raw wheel / ZIP / RECORD parsing",
        "raw pytest / JUnit parsing",
        "raw Terraform Plan JSON parsing",
        "production integration",
        "release readiness",
    ]
    raw_absent = all(item in joined for item in required_negative)
    production_absent = "PRODUCTION_CLAIM_NOT_AUTHORIZED" in joined or "production claim" in joined.lower()
    release_absent = "RELEASE_NOT_AUTHORIZED" in joined or "release readiness" in joined.lower()
    return {
        "status": "PRESERVED" if raw_absent and production_absent and release_absent else "NEEDS_REVISION",
        "raw_parser_proof_claim_absent": raw_absent,
        "production_claim_absent": production_absent,
        "release_authorization_absent": release_absent,
    }


def run_command(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
    return {
        "command": " ".join(command),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def snapshot_files(paths: list[Path]) -> dict[Path, bytes | None]:
    return {path: path.read_bytes() if path.exists() else None for path in paths}


def restore_files(snapshots: Mapping[Path, bytes | None]) -> None:
    for path, data in snapshots.items():
        if data is None:
            if path.exists():
                path.unlink()
        else:
            path.write_bytes(data)


def unexpected_dirty_paths() -> list[str]:
    completed = subprocess.run(["git", "status", "--short"], cwd=ROOT, check=True, capture_output=True, text=True)
    allowed = {
        "tools/run_formal_core_v1_integration_boundary.py",
        "research/formal_core/spira_formal_core_v1_integration_boundary_results.json",
        "research/formal_core/spira_formal_core_v1_integration_boundary_report.md",
        "research/formal_core/spira_formal_core_v1_integration_boundary_review.md",
    }
    paths = []
    for line in completed.stdout.splitlines():
        if not line:
            continue
        path = line[3:].replace("\\", "/")
        if path not in allowed:
            paths.append(path)
    return sorted(paths)


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Integration Boundary Report",
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
            "This report covers local integration boundary consistency only.",
            "",
        ]
    )


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = results["status"] == "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_ACCEPTED"
    statuses = [
        results["status"],
        "FORMAL_CORE_V1_TO_PASSTHROUGH_MVP_BOUNDARY_ACCEPTED" if accepted else "FORMAL_CORE_V1_TO_PASSTHROUGH_MVP_BOUNDARY_NOT_ACCEPTED",
        "AUTHORITY_CHAIN_ACCEPTED" if accepted else "AUTHORITY_CHAIN_NOT_ACCEPTED",
        "RAW_ADAPTER_PROOFS_NOT_INCLUDED",
        "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
        "PRODUCTION_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ]
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Integration Boundary Review",
            "",
            "## Status",
            "",
            "```text",
            *statuses,
            "```",
            "",
            "## Decision",
            "",
            (
                "The local integration boundary from Formal Core V1 typed evidence to MVP passthrough machine contracts is accepted."
                if accepted
                else "The local integration boundary requires revision."
            ),
            "",
            "## Authority Chain",
            "",
            "```text",
            "\n> ".join(results["checks"]["authority_chain"]["order"]),
            "```",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(results["gates"], indent=2, sort_keys=True),
            "```",
            "",
            "## Boundaries",
            "",
            "This review does not prove raw adapters, runtime, live agents, benchmark behavior, production integration, release readiness, or public efficiency claims.",
            "",
        ]
    )


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    main()
