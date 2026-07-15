from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DOMAIN = ROOT / "research" / "formal_core" / "domain3"
FIXTURE_ROOT = DOMAIN / "raw_adapter_fixtures"
MANIFEST = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_fixture_manifest.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_fixture_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_fixture_review.md"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_domain3_raw_adapter_fixture_authorization.md"

NOT_CLAIMED = [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS",
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
    specs: list[tuple[str, int, str, str, list[str], list[str], list[str]]] = [
        ("no_change", 3, "SUPPORTED_NO_CHANGES", "PROCEED", ["TERRAFORM_PLAN_NO_CHANGES"], [], []),
        (
            "create_update_delete",
            3,
            "SUPPORTED_WITH_EFFECTIVE_CHANGES",
            "STOP_BLOCKED",
            ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"],
            ["resource change requires review"],
            [],
        ),
        (
            "replace_path",
            3,
            "SUPPORTED_WITH_EFFECTIVE_CHANGES",
            "STOP_BLOCKED",
            ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE", "TERRAFORM_REPLACE_PATH_PRESENT"],
            ["replacement path requires review"],
            [],
        ),
        ("errored_plan", 2, "PLAN_ERRORED", "STOP_BLOCKED", ["TERRAFORM_PLAN_ERRORED"], ["plan errored"], []),
        (
            "not_applyable",
            2,
            "PLAN_NOT_APPLYABLE",
            "STOP_BLOCKED",
            ["TERRAFORM_PLAN_NOT_APPLYABLE"],
            ["plan is not applyable"],
            [],
        ),
        (
            "incomplete_plan",
            2,
            "PLAN_INCOMPLETE",
            "REPORT_NOT_EVALUATED",
            ["TERRAFORM_PLAN_INCOMPLETE"],
            [],
            ["terraform plan incomplete"],
        ),
        (
            "unsupported_format",
            2,
            "FORMAT_UNSUPPORTED",
            "REPORT_NOT_EVALUATED",
            ["TERRAFORM_PLAN_FORMAT_UNSUPPORTED"],
            [],
            ["unsupported Terraform plan format"],
        ),
        (
            "invalid_json",
            2,
            "JSON_INVALID",
            "RERUN_REQUIRED",
            ["TERRAFORM_PLAN_JSON_INVALID"],
            [],
            ["Terraform plan JSON parse failed"],
        ),
        (
            "unknown_path",
            3,
            "SENSITIVE_OR_UNKNOWN_VALUES_PRESENT",
            "REPORT_NOT_EVALUATED",
            ["PLANNED_VALUE_UNKNOWN"],
            [],
            ["planned value unknown"],
        ),
        (
            "sensitive_path",
            3,
            "SENSITIVE_OR_UNKNOWN_VALUES_PRESENT",
            "REPORT_NOT_EVALUATED",
            ["SENSITIVE_PATH_PRESENT"],
            [],
            ["sensitive path present"],
        ),
        (
            "optional_provenance",
            2,
            "OPTIONAL_PROVENANCE_PRESENT",
            "PROCEED",
            ["TERRAFORM_PLAN_NO_CHANGES", "TERRAFORM_OPTIONAL_PROVENANCE_PRESENT"],
            [],
            [],
        ),
        (
            "duplicate_resource_address",
            2,
            "SUPPORTED_WITH_EFFECTIVE_CHANGES",
            "STOP_BLOCKED",
            ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE", "TERRAFORM_DUPLICATE_RESOURCE_ADDRESS"],
            ["duplicate resource address with effective change"],
            [],
        ),
        (
            "internal_adapter_failure",
            2,
            "INTERNAL_ADAPTER_FAILURE",
            "STOP_BLOCKED",
            ["INTERNAL_ADAPTER_FAILURE"],
            ["adapter internal failure"],
            [],
        ),
    ]
    fixtures: list[dict[str, Any]] = []
    for classification, count, state, action, reasons, blockers, not_eval in specs:
        for index in range(1, count + 1):
            fixture_id = f"{classification}_{index:02d}"
            fixtures.append(make_fixture(fixture_id, classification, state, action, reasons, blockers, not_eval, index))
    return fixtures


def make_fixture(
    fixture_id: str,
    classification: str,
    input_state: str,
    action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
    index: int,
) -> dict[str, Any]:
    evidence_refs = [f"plan.json:{fixture_id}", f"manifest:{fixture_id}"]
    proof_refs = [f"domain3_raw_adapter_fixture:{fixture_id}"]
    resource_actions = resource_actions_for(classification, index)
    replace_paths = replace_paths_for(classification, index)
    unknown_paths = unknown_paths_for(classification, index)
    sensitive_paths = sensitive_paths_for(classification, index)
    typed_claims = (
        [{"kind": "reason", "value": item} for item in reason_codes]
        + [{"kind": "blocking", "value": item} for item in blocking_items]
        + [{"kind": "not_evaluated", "value": item} for item in not_evaluated]
        + [{"kind": "not_claimed", "value": item} for item in NOT_CLAIMED]
        + [{"kind": "evidence_ref", "value": item} for item in evidence_refs]
        + [{"kind": "proof_ref", "value": item} for item in proof_refs]
        + [{"kind": "resource_action", "value": item} for item in resource_actions]
        + [{"kind": "replace_path", "value": item} for item in replace_paths]
        + [{"kind": "unknown_path", "value": item} for item in unknown_paths]
        + [{"kind": "sensitive_path", "value": item} for item in sensitive_paths]
    )
    typed_evidence = {
        "domain_id": "terraform_plan",
        "subject_id": fixture_id,
        "schema_version": "FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain3_raw_adapter_fixture_spec",
        "evidence_validity": evidence_validity(input_state),
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
    contract = machine_contract(
        fixture_id,
        action,
        reason_codes,
        blocking_items,
        not_evaluated,
        evidence_refs,
        proof_refs,
    )
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE_V1",
        "fixture_id": fixture_id,
        "classification": classification,
        "input_state": input_state,
        "raw_inputs": raw_inputs(fixture_id, classification, input_state, index),
        "expected_typed_evidence": typed_evidence,
        "expected_adapter_policy_action": {
            "action": action,
            "stop": action != "PROCEED",
            "reason_codes": reason_codes,
        },
        "expected_formal_core_contract": contract,
        "expected_action": contract["action"],
        "expected_stop": contract["stop"],
        "expected_reason_codes": contract["reason_codes"],
        "expected_blocking_items": contract["blocking_items"],
        "expected_not_evaluated": contract["not_evaluated"],
        "expected_not_claimed": NOT_CLAIMED,
        "expected_evidence_refs": contract["evidence_refs"],
        "expected_proof_refs": contract["proof_refs"],
        "expected_resource_actions": resource_actions,
        "expected_replace_paths": replace_paths,
        "expected_unknown_paths": unknown_paths,
        "expected_sensitive_paths": sensitive_paths,
        "expected_claim_boundary": "fixture specifies expected adapter behavior only; raw Terraform JSON parser proof is not claimed",
    }


def evidence_validity(input_state: str) -> str:
    return {
        "SUPPORTED_NO_CHANGES": "valid",
        "SUPPORTED_WITH_EFFECTIVE_CHANGES": "valid",
        "PLAN_ERRORED": "valid",
        "PLAN_NOT_APPLYABLE": "valid",
        "PLAN_INCOMPLETE": "incomplete",
        "FORMAT_UNSUPPORTED": "version_incompatible",
        "JSON_INVALID": "incomplete",
        "SENSITIVE_OR_UNKNOWN_VALUES_PRESENT": "incomplete",
        "OPTIONAL_PROVENANCE_PRESENT": "valid",
        "INTERNAL_ADAPTER_FAILURE": "internal_failure",
    }[input_state]


def machine_contract(
    fixture_id: str,
    action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
    evidence_refs: list[str],
    proof_refs: list[str],
) -> dict[str, Any]:
    return {
        "domain_id": "terraform_plan",
        "subject_id": fixture_id,
        "policy_id": "SPIRA_FORMAL_CORE_V1_DOMAIN3_POLICY",
        "schema_version": "FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE",
        "producer_id": "domain3_raw_adapter_fixture_spec",
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


def raw_inputs(fixture_id: str, classification: str, input_state: str, index: int) -> dict[str, Any]:
    if classification == "invalid_json":
        return {
            "plan_json_invalid": "{ \"format_version\": \"1.0\", \"resource_changes\": [",
            "manifest": manifest_input(fixture_id, "plan.json.invalid"),
        }
    plan = {
        "format_version": "1.0" if classification != "unsupported_format" else "99.0",
        "terraform_version": "1.8.0",
        "applyable": classification != "not_applyable",
        "complete": classification != "incomplete_plan",
        "errored": classification == "errored_plan",
        "resource_changes": resource_changes(classification, index),
    }
    if classification == "optional_provenance":
        plan["spira_optional_provenance"] = {
            "main_tf": {
                "state": "PRESENT",
                "sha256": sha256_text(f"synthetic main.tf for {fixture_id}"),
            }
        }
    return {
        "plan_json": plan,
        "manifest": manifest_input(fixture_id, "plan.json"),
        "main_tf": f"# synthetic Terraform provenance for {fixture_id}\n" if classification == "optional_provenance" else None,
    }


def resource_changes(classification: str, index: int) -> list[dict[str, Any]]:
    if classification in {"no_change", "optional_provenance", "unsupported_format", "incomplete_plan", "errored_plan"}:
        return [
            change(f"aws_iam_role.noop_{index}", ["no-op"]),
        ]
    if classification == "create_update_delete":
        actions = [["create"], ["update"], ["delete"]][(index - 1) % 3]
        return [change(f"aws_iam_role.change_{index}", actions)]
    if classification == "replace_path":
        return [change(f"aws_iam_policy.replace_{index}", ["delete", "create"], replace_paths=[["name"]])]
    if classification == "not_applyable":
        return [change(f"aws_iam_role.not_applyable_{index}", ["create"])]
    if classification == "unknown_path":
        return [change(f"aws_iam_role.unknown_{index}", ["no-op"], after_unknown={"arn": True})]
    if classification == "sensitive_path":
        return [change(f"aws_iam_role.sensitive_{index}", ["no-op"], after_sensitive={"secret": True})]
    if classification == "duplicate_resource_address":
        address = "aws_iam_role.duplicate"
        return [change(address, ["update"]), change(address, ["delete"])]
    if classification == "internal_adapter_failure":
        return [change(f"aws_iam_role.internal_failure_{index}", ["no-op"])]
    return []


def change(
    address: str,
    actions: list[str],
    *,
    replace_paths: list[list[str]] | None = None,
    after_unknown: dict[str, Any] | None = None,
    after_sensitive: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "address": address,
        "type": address.split(".")[0],
        "name": address.split(".")[-1],
        "change": {
            "actions": actions,
            "replace_paths": replace_paths or [],
            "after_unknown": after_unknown or {},
            "after_sensitive": after_sensitive or {},
        },
    }


def manifest_input(fixture_id: str, plan_file: str) -> dict[str, Any]:
    return {
        "fixture_id": fixture_id,
        "files": {
            plan_file: sha256_text(f"{fixture_id}:{plan_file}"),
        },
        "synthetic": True,
    }


def resource_actions_for(classification: str, index: int) -> list[str]:
    if classification == "create_update_delete":
        action = ["create", "update", "delete"][(index - 1) % 3]
        return [f"aws_iam_role.change_{index}:{action}"]
    if classification == "replace_path":
        return [f"aws_iam_policy.replace_{index}:delete,create"]
    if classification == "not_applyable":
        return [f"aws_iam_role.not_applyable_{index}:create"]
    if classification == "duplicate_resource_address":
        return ["aws_iam_role.duplicate:update", "aws_iam_role.duplicate:delete"]
    return []


def replace_paths_for(classification: str, index: int) -> list[str]:
    if classification == "replace_path":
        return [f"/resource_changes/0/change/replace_paths/0#aws_iam_policy.replace_{index}"]
    return []


def unknown_paths_for(classification: str, index: int) -> list[str]:
    if classification == "unknown_path":
        return [f"/resource_changes/0/change/after_unknown/arn#aws_iam_role.unknown_{index}"]
    return []


def sensitive_paths_for(classification: str, index: int) -> list[str]:
    if classification == "sensitive_path":
        return [f"/resource_changes/0/change/after_sensitive/secret#aws_iam_role.sensitive_{index}"]
    return []


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
                "expected_resource_actions": fixture["expected_resource_actions"],
                "expected_replace_paths": fixture["expected_replace_paths"],
                "expected_unknown_paths": fixture["expected_unknown_paths"],
                "expected_sensitive_paths": fixture["expected_sensitive_paths"],
            }
        )
    required = {
        "no_change": 3,
        "create_update_delete": 3,
        "replace_path": 3,
        "errored_plan": 2,
        "not_applyable": 2,
        "incomplete_plan": 2,
        "unsupported_format": 2,
        "invalid_json": 2,
        "unknown_path": 3,
        "sensitive_path": 3,
        "optional_provenance": 2,
        "duplicate_resource_address": 2,
        "internal_adapter_failure": 2,
    }
    coverage_pass = all(coverage.get(key) == value for key, value in required.items())
    action_distribution: dict[str, int] = {}
    for fixture in fixtures:
        action_distribution[fixture["expected_action"]] = action_distribution.get(fixture["expected_action"], 0) + 1
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE_MANIFEST_V1",
        "status": (
            "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURES_ACCEPTED"
            if coverage_pass
            else "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURES_NEED_REVISION"
        ),
        "authorization": rel(AUTHORIZATION),
        "fixture_count": len(fixtures),
        "coverage": coverage,
        "required_coverage": required,
        "coverage_pass": coverage_pass,
        "action_distribution": action_distribution,
        "entries": entries,
        "claim_boundary": "synthetic fixtures only; raw Terraform JSON parser proof not claimed",
        "note": "expected_formal_core_contract records the accepted Domain 3 action algebra target; current Python reference conformance remains a later differential implementation question",
        "next_recommended_authorization": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_IMPLEMENTATION_AUTHORIZATION",
    }


def report_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Raw Adapter Fixture Report",
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
            "The corpus contains synthetic raw Terraform Plan adapter fixtures with expected typed-evidence and Formal Core contract outcomes.",
            "",
            "Invalid JSON fixtures expect `RERUN_REQUIRED` according to the accepted Domain 3 policy/action algebra. This is a fixture target for the later adapter implementation phase, not a raw parser proof.",
            "",
            "No adapter implementation, Lean proof, benchmark, live agent session, production claim, or release is authorized by this fixture corpus.",
        ]
    ) + "\n"


def review_markdown(manifest: dict[str, Any]) -> str:
    decision = (
        "The Domain 3 raw adapter fixture corpus is accepted."
        if manifest["coverage_pass"]
        else "The Domain 3 raw adapter fixture corpus needs revision."
    )
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Raw Adapter Fixture Review",
            "",
            "## Status",
            "",
            "```text",
            manifest["status"],
            "RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO",
            "TERRAFORM_EXECUTION_FORMALLY_PROVED_NO",
            "DOMAIN_3_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED",
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
            "The fixtures specify expected raw-to-typed behavior for a future Domain 3 adapter implementation. They do not prove raw Terraform JSON parsing, Terraform execution, provider behavior, live cloud state, security, compliance, cost, or apply success.",
            "",
            "The fixture corpus preserves `RERUN_REQUIRED` as the accepted Domain 3 policy/action target for invalid JSON. A later implementation must reconcile this target with the Formal Core V1 Python reference and accepted action algebra without weakening fail-closed behavior.",
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
