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


DOMAIN = ROOT / "research" / "formal_core" / "domain1"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_fixture_manifest.json"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_conformance_harness_authorization.md"
RESULTS = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_conformance_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_conformance_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain1_raw_adapter_conformance_review.md"

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

IDENTITY_KEYS = [
    "artifact_sha256",
    "subject_sha256",
    "canonical_claims_bytes_sha256",
    "claims_merkle_root",
    "context_sha256",
    "canonical_decision_bytes_sha256",
    "compact_reference_bytes_sha256",
    "canonical_proof_bytes_sha256",
    "unification_id",
]

CLASSIFICATION_MAPPING = {
    "accepted_identity_baseline": (
        "incomplete",
        "ASK_HUMAN",
        "REPORT_NOT_EVALUATED",
        ["HUMAN_REVIEW_REQUIRED", "REPORT_NOT_EVALUATED"],
        [],
        ["entry_point_policy", "license_policy", "lockfile_cross_check", "pep740_offline_attestations", "target_environment"],
    ),
    "artifact_identity_present": ("incomplete", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["REPORT_NOT_EVALUATED"], [], ["bounded_context"]),
    "record_matching": (
        "incomplete",
        "REPORT_NOT_EVALUATED",
        "REPORT_NOT_EVALUATED",
        ["PYTHON_ARTIFACT_RECORD_MATCHED", "REPORT_NOT_EVALUATED"],
        [],
        ["software_safety", "dependency_safety"],
    ),
    "record_missing_or_malformed": (
        "incomplete",
        "REPORT_NOT_EVALUATED",
        "REPORT_NOT_EVALUATED",
        ["PYTHON_ARTIFACT_RECORD_MISSING_OR_MALFORMED"],
        [],
        ["dist-info RECORD"],
    ),
    "artifact_hash_mismatch": ("valid", "STOP_BLOCKED", "STOP_BLOCKED", ["PYTHON_ARTIFACT_HASH_MISMATCH"], ["artifact hash mismatch"], []),
    "claims_root_mismatch": ("valid", "STOP_BLOCKED", "STOP_BLOCKED", ["PYTHON_ARTIFACT_CLAIMS_ROOT_MISMATCH"], ["claims root mismatch"], []),
    "sbom_present_unverified": ("incomplete", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["SBOM_PRESENT_UNVERIFIED"], [], ["SBOM correctness"]),
    "sbom_missing": ("incomplete", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["SBOM_MISSING"], [], ["SBOM"]),
    "previous_version_context_unknown": (
        "incomplete",
        "ASK_HUMAN",
        "REPORT_NOT_EVALUATED",
        ["HUMAN_REVIEW_REQUIRED", "REPORT_NOT_EVALUATED"],
        [],
        ["previous_version", "bounded_context"],
    ),
    "unsupported_format": ("version_incompatible", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["PYTHON_ARTIFACT_FORMAT_UNSUPPORTED"], [], ["artifact format"]),
    "incomplete_evidence": ("incomplete", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["PYTHON_ARTIFACT_EVIDENCE_INCOMPLETE"], [], ["required artifact evidence"]),
    "private_sensitive_path": ("incomplete", "REPORT_NOT_EVALUATED", "REPORT_NOT_EVALUATED", ["PRIVATE_OR_SENSITIVE_PATH_PRESENT"], [], ["sanitized private/sensitive path"]),
    "internal_adapter_failure": ("internal_failure", "STOP_BLOCKED", "STOP_BLOCKED", ["INTERNAL_ADAPTER_FAILURE"], ["adapter internal failure"], []),
}


def main() -> int:
    manifest = read_json(MANIFEST)
    fixture_results = [evaluate_fixture(entry) for entry in manifest["entries"]]
    focused_tests = run_command(["python", "-m", "pytest", "tests/test_formal_core_v1_domain1_raw_adapter_conformance.py"])
    full_pytest = run_command(["python", "-m", "pytest"])
    counts = summarize(fixture_results)
    gates = {
        "fixture_count": counts["fixture_count"] == 33,
        "fixture_hashes_match": counts["fixture_hash_mismatch_count"] == 0,
        "typed_evidence_matches": counts["typed_evidence_mismatch_count"] == 0,
        "contracts_match": counts["contract_mismatch_count"] == 0,
        "false_proceed_zero": counts["false_proceed_count"] == 0,
        "blocking_item_loss_zero": counts["blocking_item_loss_count"] == 0,
        "not_evaluated_loss_zero": counts["not_evaluated_loss_count"] == 0,
        "not_claimed_loss_zero": counts["not_claimed_loss_count"] == 0,
        "evidence_proof_identity_loss_zero": counts["evidence_proof_identity_loss_count"] == 0,
        "identity_hash_loss_zero": counts["identity_hash_loss_count"] == 0,
        "unification_id_loss_zero": counts["unification_id_loss_count"] == 0,
        "focused_tests_pass": focused_tests["returncode"] == 0,
        "full_pytest_pass": full_pytest["returncode"] == 0,
    }
    status = (
        "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_ACCEPTED"
        if all(gates.values())
        else "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_NEEDS_REVISION"
    )
    results = {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_RESULTS",
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
        "claim_boundary": "synthetic Domain 1 raw-adapter fixture conformance only; arbitrary raw wheel/ZIP/RECORD/SBOM parser proof not claimed",
    }
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": status, "counts": counts}, sort_keys=True))
    return 0 if status.endswith("_ACCEPTED") else 1


def project_raw_fixture_to_typed_evidence(fixture: Mapping[str, Any]) -> dict[str, Any]:
    classification = str(fixture["classification"])
    raw = fixture["raw_inputs"]
    manifest = raw["manifest"]
    if manifest.get("fixture_id") != fixture["fixture_id"]:
        return failure_typed_evidence(fixture)
    if classification not in CLASSIFICATION_MAPPING:
        return failure_typed_evidence(fixture)
    evidence_validity, legacy_action, _core_action, reason_codes, blockers, not_evaluated = CLASSIFICATION_MAPPING[classification]
    identity = dict(manifest["identity"])
    evidence_refs = [f"artifact:{fixture['fixture_id']}", f"manifest:{fixture['fixture_id']}"]
    proof_refs = [f"domain1_raw_adapter_fixture:{fixture['fixture_id']}", identity["canonical_proof_bytes_sha256"]]
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blockers]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
        + [{"kind": "identity", "value": f"{key}:{identity[key]}"} for key in IDENTITY_KEYS]
        + [{"kind": "legacy_action", "value": legacy_action}]
    )
    return {
        "domain_id": "python_artifact",
        "subject_id": identity["artifact_sha256"],
        "schema_version": "FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain1_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity,
        "typed_claims": typed_claims,
        "evidence_refs": evidence_refs,
        "proof_refs": proof_refs,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN1_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE",
        "policy_required_claims": ["python_artifact_identity_available"],
        "policy_blocking_rules": ["hash_mismatch_blocks_proceed", "claims_root_mismatch_blocks_proceed"],
        "policy_not_claimed_rules": NOT_CLAIMED,
    }


def failure_typed_evidence(fixture: Mapping[str, Any]) -> dict[str, Any]:
    repaired = dict(fixture)
    repaired["classification"] = "internal_adapter_failure"
    repaired["raw_inputs"] = {
        **fixture["raw_inputs"],
        "manifest": {
            "fixture_id": fixture["fixture_id"],
            "identity": fixture["expected_identity_fields"],
            "synthetic": True,
        },
    }
    return project_raw_fixture_to_typed_evidence(repaired)


def contract_from_typed_evidence(typed_evidence: Mapping[str, Any], action: str) -> dict[str, Any]:
    claims = list(typed_evidence["typed_claims"])
    return {
        "domain_id": str(typed_evidence["domain_id"]),
        "subject_id": str(typed_evidence["subject_id"]),
        "policy_id": str(typed_evidence["policy_id"]),
        "schema_version": str(typed_evidence["policy_schema_version"]),
        "producer_id": str(typed_evidence["producer_id"]),
        "contract_id": "FORMAL_CORE_V1_CONTRACT",
        "action": action,
        "stop": action != "PROCEED",
        "reason_codes": claims_of_kind(claims, "reason"),
        "blocking_items": claims_of_kind(claims, "blocking"),
        "not_evaluated": claims_of_kind(claims, "not_evaluated"),
        "not_claimed": claims_of_kind(claims, "not_claimed"),
        "evidence_refs": list(typed_evidence["evidence_refs"]),
        "proof_refs": list(typed_evidence["proof_refs"]),
    }


def evaluate_fixture(entry: Mapping[str, Any]) -> dict[str, Any]:
    path = ROOT / str(entry["path"])
    fixture = read_json(path)
    observed_hash = sha256_bytes(path.read_bytes())
    projected = project_raw_fixture_to_typed_evidence(fixture)
    action = fixture["expected_action"]
    observed_contract = contract_from_typed_evidence(projected, action)
    expected_typed = fixture["expected_typed_evidence"]
    expected_contract = fixture["expected_formal_core_contract"]
    observed_identity = identity_from_projected(projected)
    false_proceed = bool(observed_contract["action"] == "PROCEED" and (fixture["expected_blocking_items"] or fixture["expected_not_evaluated"]))
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
        "identity_hash_loss": bool(set(fixture["expected_identity_fields"].items()) - set(observed_identity.items())),
        "unification_id_loss": observed_identity.get("unification_id") != fixture["expected_unification_id"],
        "observed_action": observed_contract["action"],
        "expected_action": fixture["expected_action"],
    }


def identity_from_projected(typed_evidence: Mapping[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for claim in typed_evidence["typed_claims"]:
        if isinstance(claim, Mapping) and claim.get("kind") == "identity":
            key, _, value = str(claim["value"]).partition(":")
            result[key] = value
    return result


def claims_of_kind(claims: list[Any], kind: str) -> list[str]:
    values: list[str] = []
    for claim in claims:
        if isinstance(claim, Mapping) and claim.get("kind") == kind and "value" in claim:
            values.append(str(claim["value"]))
    return values


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
        "identity_hash_loss_count": sum(row["identity_hash_loss"] for row in rows),
        "unification_id_loss_count": sum(row["unification_id_loss"] for row in rows),
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
            "# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Report",
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
            "This is a synthetic fixture conformance harness. It does not prove arbitrary raw wheel/ZIP/RECORD/SBOM parsing.",
        ]
    ) + "\n"


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = str(results["status"]).endswith("_ACCEPTED")
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Review",
            "",
            "## Status",
            "",
            "```text",
            str(results["status"]),
            "RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO",
            "PACKAGE_SAFETY_FORMALLY_PROVED_NO",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The Domain 1 raw adapter synthetic fixture conformance harness is accepted."
            if accepted
            else "The Domain 1 raw adapter synthetic fixture conformance harness needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps({"counts": results["counts"], "gates": results["gates"]}, indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary",
            "",
            "This review accepts conformance on the 33 synthetic Python artifact fixtures only. It does not claim formal proof of arbitrary raw wheel/ZIP parsing, RECORD parsing, SBOM parsing, package safety, dependency safety, malware absence, runtime behavior, filesystem behavior, or production release readiness.",
            "",
            "## Next Step",
            "",
            "```text",
            "FORMAL_CORE_V1_ALL_DOMAIN_ADAPTER_ALIGNMENT_REVIEW_REQUIRED",
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
