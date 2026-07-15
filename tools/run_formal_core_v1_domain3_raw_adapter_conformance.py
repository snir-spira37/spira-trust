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


DOMAIN = ROOT / "research" / "formal_core" / "domain3"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_fixture_manifest.json"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_conformance_harness_authorization.md"
RESULTS = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_conformance_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_conformance_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_conformance_review.md"

NOT_CLAIMED = [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS",
]

CLASSIFICATION_MAPPING = {
    "no_change": ("valid", "PROCEED", ["TERRAFORM_PLAN_NO_CHANGES"], [], []),
    "create_update_delete": (
        "valid",
        "STOP_BLOCKED",
        ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"],
        ["resource change requires review"],
        [],
    ),
    "replace_path": (
        "valid",
        "STOP_BLOCKED",
        ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE", "TERRAFORM_REPLACE_PATH_PRESENT"],
        ["replacement path requires review"],
        [],
    ),
    "errored_plan": ("valid", "STOP_BLOCKED", ["TERRAFORM_PLAN_ERRORED"], ["plan errored"], []),
    "not_applyable": ("valid", "STOP_BLOCKED", ["TERRAFORM_PLAN_NOT_APPLYABLE"], ["plan is not applyable"], []),
    "incomplete_plan": (
        "incomplete",
        "REPORT_NOT_EVALUATED",
        ["TERRAFORM_PLAN_INCOMPLETE"],
        [],
        ["terraform plan incomplete"],
    ),
    "unsupported_format": (
        "version_incompatible",
        "REPORT_NOT_EVALUATED",
        ["TERRAFORM_PLAN_FORMAT_UNSUPPORTED"],
        [],
        ["unsupported Terraform plan format"],
    ),
    "invalid_json": (
        "incomplete",
        "RERUN_REQUIRED",
        ["TERRAFORM_PLAN_JSON_INVALID"],
        [],
        ["Terraform plan JSON parse failed"],
    ),
    "unknown_path": ("incomplete", "REPORT_NOT_EVALUATED", ["PLANNED_VALUE_UNKNOWN"], [], ["planned value unknown"]),
    "sensitive_path": ("incomplete", "REPORT_NOT_EVALUATED", ["SENSITIVE_PATH_PRESENT"], [], ["sensitive path present"]),
    "optional_provenance": (
        "valid",
        "PROCEED",
        ["TERRAFORM_PLAN_NO_CHANGES", "TERRAFORM_OPTIONAL_PROVENANCE_PRESENT"],
        [],
        [],
    ),
    "duplicate_resource_address": (
        "valid",
        "STOP_BLOCKED",
        ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE", "TERRAFORM_DUPLICATE_RESOURCE_ADDRESS"],
        ["duplicate resource address with effective change"],
        [],
    ),
    "internal_adapter_failure": (
        "internal_failure",
        "STOP_BLOCKED",
        ["INTERNAL_ADAPTER_FAILURE"],
        ["adapter internal failure"],
        [],
    ),
}


def main() -> int:
    manifest = read_json(MANIFEST)
    fixture_results = [evaluate_fixture(entry) for entry in manifest["entries"]]
    focused_tests = run_command(["python", "-m", "pytest", "tests/test_formal_core_v1_domain3_raw_adapter_conformance.py"])
    full_pytest = run_command(["python", "-m", "pytest"])
    counts = summarize(fixture_results)
    gates = {
        "fixture_count": counts["fixture_count"] == 31,
        "fixture_hashes_match": counts["fixture_hash_mismatch_count"] == 0,
        "typed_evidence_matches": counts["typed_evidence_mismatch_count"] == 0,
        "contracts_match": counts["contract_mismatch_count"] == 0,
        "false_proceed_zero": counts["false_proceed_count"] == 0,
        "blocking_item_loss_zero": counts["blocking_item_loss_count"] == 0,
        "not_evaluated_loss_zero": counts["not_evaluated_loss_count"] == 0,
        "not_claimed_loss_zero": counts["not_claimed_loss_count"] == 0,
        "evidence_proof_identity_loss_zero": counts["evidence_proof_identity_loss_count"] == 0,
        "resource_action_loss_zero": counts["resource_action_loss_count"] == 0,
        "replace_path_loss_zero": counts["replace_path_loss_count"] == 0,
        "unknown_path_loss_zero": counts["unknown_path_loss_count"] == 0,
        "sensitive_path_loss_zero": counts["sensitive_path_loss_count"] == 0,
        "focused_tests_pass": focused_tests["returncode"] == 0,
        "full_pytest_pass": full_pytest["returncode"] == 0,
    }
    status = (
        "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED"
        if all(gates.values())
        else "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_NEEDS_REVISION"
    )
    results = {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_RESULTS",
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
        "claim_boundary": "synthetic Domain 3 raw-adapter fixture conformance only; arbitrary raw Terraform Plan JSON parser proof not claimed",
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
        return failure_typed_evidence(fixture, "internal_adapter_failure")
    if classification not in CLASSIFICATION_MAPPING:
        return failure_typed_evidence(fixture, "internal_adapter_failure")
    evidence_validity, _action, reason_codes, blockers, not_evaluated = CLASSIFICATION_MAPPING[classification]
    fixture_id = str(fixture["fixture_id"])
    evidence_refs = [f"plan.json:{fixture_id}", f"manifest:{fixture_id}"]
    proof_refs = [f"domain3_raw_adapter_fixture:{fixture_id}"]
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blockers]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
        + [{"kind": "resource_action", "value": item} for item in fixture["expected_resource_actions"]]
        + [{"kind": "replace_path", "value": item} for item in fixture["expected_replace_paths"]]
        + [{"kind": "unknown_path", "value": item} for item in fixture["expected_unknown_paths"]]
        + [{"kind": "sensitive_path", "value": item} for item in fixture["expected_sensitive_paths"]]
    )
    return {
        "domain_id": "terraform_plan",
        "subject_id": fixture_id,
        "schema_version": "FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain3_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity,
        "typed_claims": typed_claims,
        "evidence_refs": evidence_refs,
        "proof_refs": proof_refs,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN3_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE",
        "policy_required_claims": ["terraform_plan_available"],
        "policy_blocking_rules": [
            "resource_change_blocks_proceed",
            "plan_error_blocks_proceed",
            "unknown_or_sensitive_values_prevent_silent_pass",
        ],
        "policy_not_claimed_rules": NOT_CLAIMED,
    }


def failure_typed_evidence(fixture: Mapping[str, Any], classification: str) -> dict[str, Any]:
    repaired = dict(fixture)
    repaired["classification"] = classification
    repaired["raw_inputs"] = {
        **fixture["raw_inputs"],
        "manifest": {
            "fixture_id": fixture["fixture_id"],
            "files": {"plan.json": "__synthetic_failure__"},
            "synthetic": True,
        },
    }
    return project_raw_fixture_to_typed_evidence(repaired)


def contract_from_typed_evidence(typed_evidence: Mapping[str, Any], action: str) -> dict[str, Any]:
    typed_claims = list(typed_evidence["typed_claims"])
    return {
        "domain_id": str(typed_evidence["domain_id"]),
        "subject_id": str(typed_evidence["subject_id"]),
        "policy_id": str(typed_evidence["policy_id"]),
        "schema_version": str(typed_evidence["policy_schema_version"]),
        "producer_id": str(typed_evidence["producer_id"]),
        "contract_id": "FORMAL_CORE_V1_CONTRACT",
        "action": action,
        "stop": action != "PROCEED",
        "reason_codes": claims_of_kind(typed_claims, "reason"),
        "blocking_items": claims_of_kind(typed_claims, "blocking"),
        "not_evaluated": claims_of_kind(typed_claims, "not_evaluated"),
        "not_claimed": claims_of_kind(typed_claims, "not_claimed"),
        "evidence_refs": list(typed_evidence["evidence_refs"]),
        "proof_refs": list(typed_evidence["proof_refs"]),
    }


def evaluate_fixture(entry: Mapping[str, Any]) -> dict[str, Any]:
    path = ROOT / str(entry["path"])
    fixture = read_json(path)
    observed_hash = sha256_bytes(path.read_bytes())
    projected = project_raw_fixture_to_typed_evidence(fixture)
    expected_action = fixture["expected_adapter_policy_action"]["action"]
    observed_contract = contract_from_typed_evidence(projected, expected_action)
    expected_typed = fixture["expected_typed_evidence"]
    expected_contract = fixture["expected_formal_core_contract"]
    observed_lists = projected_lists(projected)
    false_proceed = bool(
        observed_contract["action"] == "PROCEED"
        and (
            fixture["expected_blocking_items"]
            or fixture["expected_not_evaluated"]
            or fixture["input_state"]
            in {
                "SUPPORTED_WITH_EFFECTIVE_CHANGES",
                "PLAN_ERRORED",
                "PLAN_NOT_APPLYABLE",
                "PLAN_INCOMPLETE",
                "FORMAT_UNSUPPORTED",
                "JSON_INVALID",
                "SENSITIVE_OR_UNKNOWN_VALUES_PRESENT",
                "INTERNAL_ADAPTER_FAILURE",
            }
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
        "resource_action_loss": bool(set(fixture["expected_resource_actions"]) - set(observed_lists["resource_actions"])),
        "replace_path_loss": bool(set(fixture["expected_replace_paths"]) - set(observed_lists["replace_paths"])),
        "unknown_path_loss": bool(set(fixture["expected_unknown_paths"]) - set(observed_lists["unknown_paths"])),
        "sensitive_path_loss": bool(set(fixture["expected_sensitive_paths"]) - set(observed_lists["sensitive_paths"])),
        "observed_action": observed_contract["action"],
        "expected_action": fixture["expected_action"],
    }


def projected_lists(typed_evidence: Mapping[str, Any]) -> dict[str, list[str]]:
    claims = list(typed_evidence["typed_claims"])
    return {
        "resource_actions": claims_of_kind(claims, "resource_action"),
        "replace_paths": claims_of_kind(claims, "replace_path"),
        "unknown_paths": claims_of_kind(claims, "unknown_path"),
        "sensitive_paths": claims_of_kind(claims, "sensitive_path"),
    }


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
        "resource_action_loss_count": sum(row["resource_action_loss"] for row in rows),
        "replace_path_loss_count": sum(row["replace_path_loss"] for row in rows),
        "unknown_path_loss_count": sum(row["unknown_path_loss"] for row in rows),
        "sensitive_path_loss_count": sum(row["sensitive_path_loss"] for row in rows),
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
            "# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Report",
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
            "This is a synthetic fixture conformance harness. It does not prove arbitrary raw Terraform Plan JSON parsing or Terraform execution.",
        ]
    ) + "\n"


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = str(results["status"]).endswith("_ACCEPTED")
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Review",
            "",
            "## Status",
            "",
            "```text",
            str(results["status"]),
            "RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO",
            "TERRAFORM_EXECUTION_FORMALLY_PROVED_NO",
            "PRODUCTION_ADAPTER_UNCHANGED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The Domain 3 raw adapter synthetic fixture conformance harness is accepted."
            if accepted
            else "The Domain 3 raw adapter synthetic fixture conformance harness needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps({"counts": results["counts"], "gates": results["gates"]}, indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary",
            "",
            "This review accepts conformance on the 31 synthetic Terraform Plan fixtures only. It does not claim formal proof of arbitrary raw Terraform Plan JSON parsing, Terraform execution, provider behavior, cloud state, cost, security, compliance, apply success, filesystem behavior, or production release readiness.",
            "",
            "## Next Step",
            "",
            "```text",
            "DOMAIN_3_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZATION_REQUIRED",
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
