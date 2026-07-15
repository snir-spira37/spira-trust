from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from source.spira_core.formal_core_v1 import evaluate_typed_evidence  # noqa: E402

DOMAIN = ROOT / "research" / "formal_core" / "domain2"
FIXTURE_ROOT = DOMAIN / "raw_adapter_fixtures"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_fixture_manifest.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_fixture_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_fixture_review.md"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain2_raw_adapter_fixture_authorization.md"

NOT_CLAIMED = ["producer_correctness", "software_safety"]


def main() -> int:
    fixtures = build_fixtures()
    for fixture in fixtures:
        path = FIXTURE_ROOT / fixture["classification"] / f"{fixture['fixture_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    manifest = build_manifest(fixtures)
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(manifest), encoding="utf-8")
    REVIEW.write_text(review_markdown(manifest), encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "fixture_count": manifest["fixture_count"]}, sort_keys=True))
    return 0 if manifest["status"].endswith("_ACCEPTED") else 1


def build_fixtures() -> list[dict[str, Any]]:
    specs: list[tuple[str, int, str, str, list[str], list[str], list[str]]] = [
        ("clean_success", 3, "SUPPORTED_COMPLETE", "PROCEED", ["TESTS_PASSED"], [], []),
        ("assertion_failure", 3, "SUPPORTED_COMPLETE", "STOP_BLOCKED", ["TEST_FAILURES_DETECTED"], ["test failure"], []),
        ("collection_error", 2, "SUPPORTED_COMPLETE", "STOP_BLOCKED", ["TEST_COLLECTION_ERROR"], ["collection error"], []),
        ("malformed_junit", 2, "MALFORMED", "REPORT_NOT_EVALUATED", ["TEST_RESULT_EVIDENCE_MALFORMED"], [], ["junit"]),
        ("malformed_metadata_json", 2, "MALFORMED", "REPORT_NOT_EVALUATED", ["TEST_RESULT_METADATA_MALFORMED"], [], ["metadata"]),
        ("incomplete_evidence", 2, "INCOMPLETE", "REPORT_NOT_EVALUATED", ["TEST_RESULT_EVIDENCE_INCOMPLETE"], [], ["required result source"]),
        ("console_junit_conflict", 2, "CONFLICTING", "STOP_BLOCKED", ["TEST_EVIDENCE_CONFLICT"], ["console/junit conflict"], ["conflicting source truth"]),
        ("withheld_raw_output", 2, "INCOMPLETE", "REPORT_NOT_EVALUATED", ["PUBLIC_RUN_OUTPUT_WITHHELD"], [], ["public raw output"]),
        ("unsupported_format", 2, "UNSUPPORTED", "REPORT_NOT_EVALUATED", ["TEST_RESULT_FORMAT_UNSUPPORTED"], [], ["unsupported result format"]),
        ("nonblocking_note", 2, "SUPPORTED_WITH_NONBLOCKING_NOTES", "PROCEED", ["TEST_NOTES"], [], []),
        ("identity_mismatch", 2, "CONFLICTING", "STOP_BLOCKED", ["TEST_IDENTITY_CONFLICT"], ["identity mismatch"], ["source identity conflict"]),
        ("internal_adapter_failure", 2, "INTERNAL_ADAPTER_FAILURE", "STOP_BLOCKED", ["INTERNAL_ADAPTER_FAILURE"], ["adapter internal failure"], []),
    ]
    fixtures: list[dict[str, Any]] = []
    for classification, count, state, action, reasons, blockers, not_eval in specs:
        for index in range(1, count + 1):
            fixture_id = f"{classification}_{index:02d}"
            fixtures.append(make_fixture(fixture_id, classification, state, action, reasons, blockers, not_eval))
    return fixtures


def make_fixture(
    fixture_id: str,
    classification: str,
    input_state: str,
    action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
) -> dict[str, Any]:
    stop = action != "PROCEED"
    evidence_refs = [f"console:{fixture_id}", f"metadata:{fixture_id}"]
    proof_refs = [f"domain2_raw_adapter_fixture:{fixture_id}"]
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blocking_items]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
    )
    typed_evidence = {
        "domain_id": "pytest_result",
        "subject_id": fixture_id,
        "schema_version": "FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain2_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity(input_state),
        "typed_claims": typed_claims,
        "evidence_refs": evidence_refs,
        "proof_refs": proof_refs,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN2_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE",
        "policy_required_claims": ["pytest_result_available"],
        "policy_blocking_rules": ["test_failure_blocks_proceed", "conflict_blocks_proceed"],
        "policy_not_claimed_rules": NOT_CLAIMED,
    }
    contract = evaluate_typed_evidence(typed_evidence)["machine_contract"]
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE_V1",
        "fixture_id": fixture_id,
        "classification": classification,
        "input_state": input_state,
        "raw_inputs": raw_inputs(fixture_id, classification, input_state),
        "expected_typed_evidence": typed_evidence,
        "expected_formal_core_contract": contract,
        "expected_action": contract["action"],
        "expected_stop": contract["stop"],
        "expected_reason_codes": contract["reason_codes"],
        "expected_blocking_items": contract["blocking_items"],
        "expected_not_evaluated": contract["not_evaluated"],
        "expected_not_claimed": NOT_CLAIMED,
        "expected_evidence_refs": contract["evidence_refs"],
        "expected_proof_refs": contract["proof_refs"],
        "expected_claim_boundary": "fixture specifies expected adapter behavior only; raw parser proof is not claimed",
    }


def evidence_validity(input_state: str) -> str:
    return {
        "SUPPORTED_COMPLETE": "valid",
        "SUPPORTED_WITH_NONBLOCKING_NOTES": "valid",
        "INCOMPLETE": "incomplete",
        "MALFORMED": "incomplete",
        "CONFLICTING": "conflicting",
        "UNSUPPORTED": "version_incompatible",
        "INTERNAL_ADAPTER_FAILURE": "internal_failure",
    }[input_state]


def raw_inputs(fixture_id: str, classification: str, input_state: str) -> dict[str, Any]:
    return {
        "console_text": f"synthetic pytest console for {fixture_id} ({classification})",
        "junit_xml_text": f"<testsuite name=\"{fixture_id}\" spira_state=\"{input_state}\" />",
        "metadata_json": {
            "fixture_id": fixture_id,
            "classification": classification,
            "capture_complete": input_state not in {"INCOMPLETE"},
        },
        "public_run_materialization_json": {
            "synthetic": True,
            "exit_code": 0 if classification in {"clean_success", "nonblocking_note"} else 1,
        },
    }


def build_manifest(fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    coverage: dict[str, int] = {}
    for fixture in fixtures:
        coverage[fixture["classification"]] = coverage.get(fixture["classification"], 0) + 1
        path = FIXTURE_ROOT / fixture["classification"] / f"{fixture['fixture_id']}.json"
        entries.append(
            {
                "fixture_id": fixture["fixture_id"],
                "classification": fixture["classification"],
                "input_state": fixture["input_state"],
                "path": rel(path),
                "fixture_sha256": sha256_bytes(path.read_bytes()),
                "expected_action": fixture["expected_action"],
                "expected_stop": fixture["expected_stop"],
                "expected_reason_codes": fixture["expected_reason_codes"],
                "expected_blocking_items": fixture["expected_blocking_items"],
                "expected_not_evaluated": fixture["expected_not_evaluated"],
                "expected_not_claimed": fixture["expected_not_claimed"],
            }
        )
    required = {
        "clean_success": 3,
        "assertion_failure": 3,
        "collection_error": 2,
        "malformed_junit": 2,
        "malformed_metadata_json": 2,
        "incomplete_evidence": 2,
        "console_junit_conflict": 2,
        "withheld_raw_output": 2,
        "unsupported_format": 2,
        "nonblocking_note": 2,
        "identity_mismatch": 2,
        "internal_adapter_failure": 2,
    }
    coverage_pass = all(coverage.get(key) == value for key, value in required.items())
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE_MANIFEST_V1",
        "status": (
            "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURES_ACCEPTED"
            if coverage_pass
            else "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURES_NEED_REVISION"
        ),
        "authorization": rel(AUTHORIZATION),
        "fixture_count": len(fixtures),
        "coverage": coverage,
        "required_coverage": required,
        "coverage_pass": coverage_pass,
        "entries": entries,
        "claim_boundary": "synthetic fixtures only; raw parser proof not claimed",
        "next_recommended_authorization": "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_IMPLEMENTATION_AUTHORIZATION",
    }


def report_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Raw Adapter Fixture Report",
            "",
            "Status:",
            "",
            "```text",
            manifest["status"],
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(
                {
                    "fixture_count": manifest["fixture_count"],
                    "coverage": manifest["coverage"],
                    "coverage_pass": manifest["coverage_pass"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "The corpus contains synthetic raw pytest/JUnit adapter fixtures with expected typed-evidence and Formal Core contract outcomes.",
            "",
            "No adapter implementation, Lean proof, benchmark, live agent session, production claim, or release is authorized by this fixture corpus.",
        ]
    ) + "\n"


def review_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Raw Adapter Fixture Review",
            "",
            "## Status",
            "",
            "```text",
            manifest["status"],
            "RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO",
            "DOMAIN_2_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The Domain 2 raw adapter fixture corpus is accepted." if manifest["coverage_pass"] else "The Domain 2 raw adapter fixture corpus needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "fixture_count": manifest["fixture_count"],
                    "coverage": manifest["coverage"],
                    "coverage_pass": manifest["coverage_pass"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundary",
            "",
            "The fixtures specify expected raw-to-typed behavior for a future Domain 2 adapter implementation. They do not prove raw parser correctness.",
            "",
            "## Next Step",
            "",
            "```text",
            manifest["next_recommended_authorization"],
            "```",
        ]
    ) + "\n"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
