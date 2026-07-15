from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DOMAIN = ROOT / "research" / "formal_core" / "domain1"
FIXTURE_ROOT = DOMAIN / "raw_adapter_fixtures"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_fixture_manifest.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_fixture_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_fixture_review.md"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_fixture_authorization.md"

NOT_CLAIMED = [
    "producer_correctness",
    "software_safety",
    "package_safety",
    "dependency_safety",
    "license_compliance",
    "malware_absence",
    "universal_supply_chain_coverage",
    "runtime_behavior",
]


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
    specs: list[tuple[str, int, str, str, str, list[str], list[str], list[str]]] = [
        (
            "accepted_identity_baseline",
            3,
            "SUPPORTED_IDENTITY_BASELINE_RECORD",
            "ASK_HUMAN",
            "REPORT_NOT_EVALUATED",
            ["HUMAN_REVIEW_REQUIRED", "REPORT_NOT_EVALUATED"],
            [],
            ["entry_point_policy", "license_policy", "lockfile_cross_check", "pep740_offline_attestations", "target_environment"],
        ),
        (
            "artifact_identity_present",
            3,
            "SUPPORTED_ARTIFACT_IDENTITY_PRESENT",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["REPORT_NOT_EVALUATED"],
            [],
            ["bounded_context"],
        ),
        (
            "record_matching",
            3,
            "RECORD_PRESENT_AND_MATCHING",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["PYTHON_ARTIFACT_RECORD_MATCHED", "REPORT_NOT_EVALUATED"],
            [],
            ["software_safety", "dependency_safety"],
        ),
        (
            "record_missing_or_malformed",
            3,
            "RECORD_MISSING_OR_MALFORMED",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["PYTHON_ARTIFACT_RECORD_MISSING_OR_MALFORMED"],
            [],
            ["dist-info RECORD"],
        ),
        (
            "artifact_hash_mismatch",
            3,
            "ARTIFACT_HASH_MISMATCH",
            "STOP_BLOCKED",
            "STOP_BLOCKED",
            ["PYTHON_ARTIFACT_HASH_MISMATCH"],
            ["artifact hash mismatch"],
            [],
        ),
        (
            "claims_root_mismatch",
            3,
            "CLAIMS_ROOT_MISMATCH",
            "STOP_BLOCKED",
            "STOP_BLOCKED",
            ["PYTHON_ARTIFACT_CLAIMS_ROOT_MISMATCH"],
            ["claims root mismatch"],
            [],
        ),
        (
            "sbom_present_unverified",
            2,
            "SBOM_PRESENT_UNVERIFIED",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["SBOM_PRESENT_UNVERIFIED"],
            [],
            ["SBOM correctness"],
        ),
        (
            "sbom_missing",
            2,
            "SBOM_MISSING",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["SBOM_MISSING"],
            [],
            ["SBOM"],
        ),
        (
            "previous_version_context_unknown",
            3,
            "PREVIOUS_VERSION_OR_CONTEXT_UNKNOWN",
            "ASK_HUMAN",
            "REPORT_NOT_EVALUATED",
            ["HUMAN_REVIEW_REQUIRED", "REPORT_NOT_EVALUATED"],
            [],
            ["previous_version", "bounded_context"],
        ),
        (
            "unsupported_format",
            2,
            "FORMAT_UNSUPPORTED",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["PYTHON_ARTIFACT_FORMAT_UNSUPPORTED"],
            [],
            ["artifact format"],
        ),
        (
            "incomplete_evidence",
            2,
            "INCOMPLETE_EVIDENCE",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["PYTHON_ARTIFACT_EVIDENCE_INCOMPLETE"],
            [],
            ["required artifact evidence"],
        ),
        (
            "private_sensitive_path",
            2,
            "PRIVATE_OR_SENSITIVE_PATH_PRESENT",
            "REPORT_NOT_EVALUATED",
            "REPORT_NOT_EVALUATED",
            ["PRIVATE_OR_SENSITIVE_PATH_PRESENT"],
            [],
            ["sanitized private/sensitive path"],
        ),
        (
            "internal_adapter_failure",
            2,
            "INTERNAL_ADAPTER_FAILURE",
            "STOP_BLOCKED",
            "STOP_BLOCKED",
            ["INTERNAL_ADAPTER_FAILURE"],
            ["adapter internal failure"],
            [],
        ),
    ]
    fixtures: list[dict[str, Any]] = []
    for classification, count, state, legacy_action, core_action, reasons, blockers, not_eval in specs:
        for index in range(1, count + 1):
            fixture_id = f"{classification}_{index:02d}"
            fixtures.append(
                make_fixture(
                    fixture_id,
                    classification,
                    state,
                    legacy_action,
                    core_action,
                    reasons,
                    blockers,
                    not_eval,
                )
            )
    return fixtures


def make_fixture(
    fixture_id: str,
    classification: str,
    input_state: str,
    legacy_action: str,
    core_action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
) -> dict[str, Any]:
    identity = identity_fields(fixture_id)
    evidence_refs = [f"artifact:{fixture_id}", f"manifest:{fixture_id}"]
    proof_refs = [f"domain1_raw_adapter_fixture:{fixture_id}", identity["canonical_proof_bytes_sha256"]]
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blocking_items]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
        + [{"kind": "identity", "value": f"{key}:{value}"} for key, value in identity.items()]
        + [{"kind": "legacy_action", "value": legacy_action}]
    )
    typed_evidence = {
        "domain_id": "python_artifact",
        "subject_id": identity["artifact_sha256"],
        "schema_version": "FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain1_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity(input_state),
        "typed_claims": typed_claims,
        "evidence_refs": evidence_refs,
        "proof_refs": proof_refs,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN1_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE",
        "policy_required_claims": ["python_artifact_identity_available"],
        "policy_blocking_rules": ["hash_mismatch_blocks_proceed", "claims_root_mismatch_blocks_proceed"],
        "policy_not_claimed_rules": NOT_CLAIMED,
    }
    contract = machine_contract(identity, core_action, reason_codes, blocking_items, not_evaluated, evidence_refs, proof_refs)
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE_V1",
        "fixture_id": fixture_id,
        "classification": classification,
        "input_state": input_state,
        "raw_inputs": raw_inputs(fixture_id, classification, input_state, identity),
        "expected_typed_evidence": typed_evidence,
        "expected_formal_core_contract": contract,
        "expected_legacy_action": legacy_action,
        "expected_action": contract["action"],
        "expected_stop": contract["stop"],
        "expected_reason_codes": contract["reason_codes"],
        "expected_blocking_items": contract["blocking_items"],
        "expected_not_evaluated": contract["not_evaluated"],
        "expected_not_claimed": NOT_CLAIMED,
        "expected_evidence_refs": contract["evidence_refs"],
        "expected_proof_refs": contract["proof_refs"],
        "expected_identity_fields": identity,
        "expected_unification_id": identity["unification_id"],
        "expected_claim_boundary": "fixture specifies expected adapter behavior only; raw wheel/ZIP/RECORD/SBOM parser proof is not claimed",
    }


def evidence_validity(input_state: str) -> str:
    return {
        "SUPPORTED_IDENTITY_BASELINE_RECORD": "incomplete",
        "SUPPORTED_ARTIFACT_IDENTITY_PRESENT": "incomplete",
        "RECORD_PRESENT_AND_MATCHING": "incomplete",
        "RECORD_MISSING_OR_MALFORMED": "incomplete",
        "ARTIFACT_HASH_MISMATCH": "valid",
        "CLAIMS_ROOT_MISMATCH": "valid",
        "SBOM_PRESENT_UNVERIFIED": "incomplete",
        "SBOM_MISSING": "incomplete",
        "PREVIOUS_VERSION_OR_CONTEXT_UNKNOWN": "incomplete",
        "FORMAT_UNSUPPORTED": "version_incompatible",
        "INCOMPLETE_EVIDENCE": "incomplete",
        "PRIVATE_OR_SENSITIVE_PATH_PRESENT": "incomplete",
        "INTERNAL_ADAPTER_FAILURE": "internal_failure",
    }[input_state]


def identity_fields(fixture_id: str) -> dict[str, str]:
    return {
        "artifact_sha256": sha256_text(f"{fixture_id}:artifact"),
        "subject_sha256": sha256_text(f"{fixture_id}:subject"),
        "canonical_claims_bytes_sha256": sha256_text(f"{fixture_id}:claims"),
        "claims_merkle_root": sha256_text(f"{fixture_id}:claims_root"),
        "context_sha256": sha256_text(f"{fixture_id}:context"),
        "canonical_decision_bytes_sha256": sha256_text(f"{fixture_id}:decision"),
        "compact_reference_bytes_sha256": sha256_text(f"{fixture_id}:compact"),
        "canonical_proof_bytes_sha256": sha256_text(f"{fixture_id}:proof"),
        "unification_id": sha256_text(f"{fixture_id}:unification"),
    }


def machine_contract(
    identity: dict[str, str],
    action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
    evidence_refs: list[str],
    proof_refs: list[str],
) -> dict[str, Any]:
    return {
        "domain_id": "python_artifact",
        "subject_id": identity["artifact_sha256"],
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN1_POLICY",
        "schema_version": "FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain1_raw_adapter_fixture_spec",
        "contract_id": "FORMAL_CORE_V1_CONTRACT",
        "action": action,
        "stop": action != "PROCEED",
        "reason_codes": list(reason_codes),
        "blocking_items": list(blocking_items),
        "not_evaluated": list(not_evaluated),
        "not_claimed": list(NOT_CLAIMED),
        "evidence_refs": list(evidence_refs),
        "proof_refs": list(proof_refs),
    }


def raw_inputs(fixture_id: str, classification: str, input_state: str, identity: dict[str, str]) -> dict[str, Any]:
    return {
        "artifact_summary": {
            "fixture_id": fixture_id,
            "classification": classification,
            "input_state": input_state,
            "subject_type": "python_wheel",
            "artifact_sha256": identity["artifact_sha256"],
            "subject_sha256": identity["subject_sha256"],
        },
        "wheel_zip_summary": {
            "synthetic": True,
            "format": "wheel" if classification != "unsupported_format" else "unsupported",
            "contains_dist_info": classification not in {"unsupported_format", "incomplete_evidence"},
        },
        "record_summary": {
            "state": "present_and_matching" if classification == "record_matching" else "synthetic",
            "malformed": classification == "record_missing_or_malformed",
        },
        "sbom_summary": {
            "state": "present_unverified" if classification == "sbom_present_unverified" else "missing",
        },
        "private_or_sensitive_path_summary": {
            "present": classification == "private_sensitive_path",
            "public_value": "__redacted_private_or_sensitive_path__" if classification == "private_sensitive_path" else None,
        },
        "manifest": {
            "fixture_id": fixture_id,
            "identity": identity,
            "synthetic": True,
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
                "expected_legacy_action": fixture["expected_legacy_action"],
                "expected_action": fixture["expected_action"],
                "expected_stop": fixture["expected_stop"],
                "expected_reason_codes": fixture["expected_reason_codes"],
                "expected_blocking_items": fixture["expected_blocking_items"],
                "expected_not_evaluated": fixture["expected_not_evaluated"],
                "expected_not_claimed": fixture["expected_not_claimed"],
                "expected_identity_fields": fixture["expected_identity_fields"],
                "expected_unification_id": fixture["expected_unification_id"],
            }
        )
    required = {
        "accepted_identity_baseline": 3,
        "artifact_identity_present": 3,
        "record_matching": 3,
        "record_missing_or_malformed": 3,
        "artifact_hash_mismatch": 3,
        "claims_root_mismatch": 3,
        "sbom_present_unverified": 2,
        "sbom_missing": 2,
        "previous_version_context_unknown": 3,
        "unsupported_format": 2,
        "incomplete_evidence": 2,
        "private_sensitive_path": 2,
        "internal_adapter_failure": 2,
    }
    coverage_pass = all(coverage.get(key) == value for key, value in required.items())
    action_distribution: dict[str, int] = {}
    for fixture in fixtures:
        action_distribution[fixture["expected_action"]] = action_distribution.get(fixture["expected_action"], 0) + 1
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE_MANIFEST_V1",
        "status": (
            "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURES_ACCEPTED"
            if coverage_pass
            else "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURES_NEED_REVISION"
        ),
        "authorization": rel(AUTHORIZATION),
        "fixture_count": len(fixtures),
        "coverage": coverage,
        "required_coverage": required,
        "coverage_pass": coverage_pass,
        "action_distribution": action_distribution,
        "entries": entries,
        "claim_boundary": "synthetic fixtures only; raw wheel/ZIP/RECORD/SBOM parser proof not claimed",
        "next_recommended_authorization": "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_HARNESS_AUTHORIZATION",
    }


def report_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 1 Raw Adapter Fixture Report",
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
                    "action_distribution": manifest["action_distribution"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "The corpus contains synthetic raw Python artifact adapter fixtures with expected typed-evidence and Formal Core contract outcomes.",
            "",
            "No adapter implementation, Lean proof, benchmark, live agent session, production claim, or release is authorized by this fixture corpus.",
        ]
    ) + "\n"


def review_markdown(manifest: dict[str, Any]) -> str:
    decision = (
        "The Domain 1 raw adapter fixture corpus is accepted."
        if manifest["coverage_pass"]
        else "The Domain 1 raw adapter fixture corpus needs revision."
    )
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 1 Raw Adapter Fixture Review",
            "",
            "## Status",
            "",
            "```text",
            manifest["status"],
            "RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO",
            "PACKAGE_SAFETY_FORMALLY_PROVED_NO",
            "DOMAIN_1_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            decision,
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "fixture_count": manifest["fixture_count"],
                    "coverage": manifest["coverage"],
                    "coverage_pass": manifest["coverage_pass"],
                    "action_distribution": manifest["action_distribution"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundary",
            "",
            "The fixtures specify expected raw-to-typed behavior for a future Domain 1 adapter implementation. They do not prove raw wheel/ZIP parsing, RECORD parsing, SBOM parsing, package safety, dependency safety, malware absence, or runtime behavior.",
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


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
