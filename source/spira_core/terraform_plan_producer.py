from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from . import terraform_plan_oracle_validator as validator


NOT_CLAIMED = [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS",
]


def produce_cases(manifest: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    cases = [produce_case(case, root=root) for case in manifest.get("cases", [])]
    by_id = {case["case_id"]: case for case in cases}
    relationships = []
    for pair in manifest.get("mutation_pairs", []):
        base = by_id[pair["base_case_id"]]
        mutated = by_id[pair["mutated_case_id"]]
        relationships.append(
            {
                "pair_id": pair["pair_id"],
                "base_case_id": pair["base_case_id"],
                "mutated_case_id": pair["mutated_case_id"],
                "declared_delta": pair["declared_delta"],
                "expected_claims_relation": _relation(
                    validator.claims_identity(_candidate_case(base)),
                    validator.claims_identity(_candidate_case(mutated)),
                ),
                "expected_claims_root_relation": _relation(
                    validator.claims_merkle_root(_candidate_case(base)),
                    validator.claims_merkle_root(_candidate_case(mutated)),
                ),
                "expected_unification_id_relation": _relation(
                    base["produced_context"]["unification_id_expected"],
                    mutated["produced_context"]["unification_id_expected"],
                ),
            }
        )
    return {"cases": sorted(cases, key=lambda item: item["case_id"]), "mutation_relationships": relationships}


def produce_case(manifest_case: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    repo_root = Path(root)
    case_id = str(manifest_case["case_id"])
    files = manifest_case["files"]
    plan_file = "plan.json" if "plan.json" in files else "plan.json.invalid"
    plan_path = repo_root / "research" / "terraform_plan_contract" / "cases" / case_id / plan_file
    subject = {"type": "terraform_plan", "sha256": files[plan_file]}
    plan, valid_json = _load_plan(plan_path)
    produced = {
        "case_id": case_id,
        "produced_subject": subject,
        "produced_context": {
            "context_sha256": "0" * 64,
            "run_identity_kind": "CONTEXTUAL_UNIFICATION_ID",
            "unification_id_expected": "0" * 64,
        },
        "produced_optional_provenance": _optional_provenance(manifest_case),
        "produced_claims": [],
        "produced_explicit_lists": _empty_lists(),
        "produced_policy_action": _policy_action(plan, valid_json),
        "produced_mutation_membership": [],
        "produced_not_claimed": NOT_CLAIMED,
        "produced_evidence_locators": [],
    }
    if valid_json and isinstance(plan, Mapping):
        produced["produced_claims"].extend(_plan_claims(subject, plan))
    else:
        produced["produced_claims"].append(
            _claim(
                "terraform_plan.json_invalid",
                "TERRAFORM_PLAN_FORMAT_VERSION",
                "NOT_EVALUATED",
                subject,
                {"string": "JSON_PARSE_FAILED"},
                plan_file,
                "",
            )
        )
    produced["produced_claims"].extend(
        _provenance_claims(subject, produced["produced_optional_provenance"], plan_file)
    )
    produced["produced_explicit_lists"] = _derive_explicit_lists(produced["produced_claims"])
    candidate = _candidate_case(produced)
    produced["produced_context"]["context_sha256"] = validator.context_sha256(
        {"corpus_manifest_sha256": validator.CORPUS_MANIFEST_SHA256}, candidate, manifest_case
    )
    produced["produced_context"]["unification_id_expected"] = validator.unification_id(
        {"corpus_manifest_sha256": validator.CORPUS_MANIFEST_SHA256}, _candidate_case(produced)
    )
    produced["produced_evidence_locators"] = _evidence_locators(produced["produced_claims"])
    return produced


def candidate_oracle_from_produced(oracle: Mapping[str, Any], produced: Mapping[str, Any]) -> dict[str, Any]:
    candidate = {key: value for key, value in oracle.items() if key not in {"cases", "mutation_relationships"}}
    candidate["cases"] = [_candidate_case(item) for item in produced["cases"]]
    candidate["mutation_relationships"] = list(produced["mutation_relationships"])
    return candidate


def _candidate_case(produced: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": produced["case_id"],
        "subject": produced["produced_subject"],
        "context": produced["produced_context"],
        "optional_provenance": produced["produced_optional_provenance"],
        "expected_claims": produced["produced_claims"],
        "explicit_lists": produced["produced_explicit_lists"],
        "policy_action": produced["produced_policy_action"],
        "mutation_membership": produced["produced_mutation_membership"],
        "not_claimed": produced["produced_not_claimed"],
    }


def _plan_claims(subject: Mapping[str, Any], plan: Mapping[str, Any]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    claims.append(_claim("terraform_plan.format_version", "TERRAFORM_PLAN_FORMAT_VERSION", "PASS", subject, {"string": str(plan.get("format_version", "MISSING"))}, "plan.json", "/format_version" if "format_version" in plan else ""))
    claims.append(_claim("terraform_plan.terraform_version", "TERRAFORM_VERSION", "PASS", subject, {"string": str(plan.get("terraform_version", "MISSING"))}, "plan.json", "/terraform_version" if "terraform_version" in plan else ""))
    if "applyable" in plan and plan.get("applyable") is False:
        claims.append(_claim("terraform_plan.applyable_false", "TERRAFORM_PLAN_APPLYABLE", "FAIL", subject, {"boolean": False}, "plan.json", "/applyable"))
    if "complete" in plan and plan.get("complete") is False:
        claims.append(_claim("terraform_plan.complete_false", "TERRAFORM_PLAN_COMPLETE", "NOT_EVALUATED", subject, {"boolean": False}, "plan.json", "/complete"))
    if "errored" in plan and plan.get("errored") is True:
        claims.append(_claim("terraform_plan.errored_true", "TERRAFORM_PLAN_ERRORED", "BLOCK", subject, {"boolean": True}, "plan.json", "/errored"))
    resource_changes = list(plan.get("resource_changes") or [])
    addresses = [str(change.get("address", "")) for change in resource_changes if isinstance(change, Mapping)]
    duplicate_addresses = {address for address in addresses if addresses.count(address) > 1}
    for index, change in enumerate(resource_changes):
        if not isinstance(change, Mapping):
            continue
        address = str(change.get("address", f"resource_{index}"))
        resource_type = str(change.get("type", "unknown"))
        actions = list(((change.get("change") or {}).get("actions") or []))
        prefix = _claim_id_fragment(address)
        ordinal_prefix = f"{prefix}.{index}" if address in duplicate_addresses else prefix
        locator = ""
        claims.append(_claim(f"terraform_plan.resource_address.{ordinal_prefix}", "TERRAFORM_RESOURCE_ADDRESS_PRESENT", "PASS", subject, {"resource_address": address}, "plan.json", locator))
        claims.append(_claim(f"terraform_plan.resource_type.{ordinal_prefix}", "TERRAFORM_RESOURCE_TYPE_PRESENT", "PASS", subject, {"resource_type": resource_type}, "plan.json", locator))
        if actions:
            claims.append(_claim(f"terraform_plan.action_sequence.{ordinal_prefix}", "TERRAFORM_RESOURCE_ACTION_SEQUENCE", "PASS", subject, {"action_sequence": actions}, "plan.json", locator))
        action_type = _resource_claim_type(actions)
        if action_type:
            claims.append(_claim(f"terraform_plan.resource_action.{ordinal_prefix}", action_type, "PASS", subject, {"resource_address": address}, "plan.json", locator))
        for path_index, _replace_path in enumerate((change.get("change") or {}).get("replace_paths") or []):
            pointer = f"/resource_changes/{index}/change/replace_paths/{path_index}"
            claims.append(_claim(f"terraform_plan.replace_path.{ordinal_prefix}.{path_index}", "TERRAFORM_REPLACE_PATH_PRESENT", "PASS", subject, {"json_pointer": pointer}, "plan.json", pointer))
        for pointer in _unknown_paths(change, index):
            claims.append(_claim(f"terraform_plan.unknown.{ordinal_prefix}.{_claim_id_fragment(pointer)}", "PLANNED_VALUE_UNKNOWN", "NOT_EVALUATED", subject, {"json_pointer": pointer}, "plan.json", pointer))
        for pointer in _sensitive_paths(change, index):
            claims.append(_claim(f"terraform_plan.sensitive.{ordinal_prefix}.{_claim_id_fragment(pointer)}", "SENSITIVE_PATH_PRESENT", "NOT_EVALUATED", subject, {"json_pointer": pointer}, "plan.json", pointer))
    if isinstance(plan.get("spira_optional_provenance"), Mapping):
        for name, entry in sorted(plan["spira_optional_provenance"].items()):
            if isinstance(entry, Mapping) and "state" in entry:
                claims.append(
                    _claim(
                        f"terraform_plan.embedded_provenance.{_claim_id_fragment(name)}",
                        "OPTIONAL_PROVENANCE_STATE",
                        "PASS",
                        subject,
                        {"provenance_state": str(entry["state"])},
                        "plan.json",
                        f"/spira_optional_provenance/{_escape_pointer(str(name))}/state",
                    )
                )
    return claims


def _provenance_claims(subject: Mapping[str, Any], provenance: Mapping[str, Any], plan_file: str) -> list[dict[str, Any]]:
    claims = []
    for name, entry in provenance.items():
        claims.append(
            _claim(
                f"terraform_plan.provenance.{_claim_id_fragment(name)}",
                "OPTIONAL_PROVENANCE_STATE",
                "PASS",
                subject,
                {"provenance_state": entry["state"]},
                "main.tf" if entry["state"] == "BOUND" and name == "configuration_sha256" else plan_file,
                "",
            )
        )
    return claims


def _policy_action(plan: Any, valid_json: bool) -> dict[str, Any]:
    if not valid_json:
        return _action(True, "RERUN_REQUIRED", ["TERRAFORM_PLAN_JSON_INVALID"])
    if not isinstance(plan, Mapping):
        return _action(True, "REPORT_NOT_EVALUATED", ["TERRAFORM_PLAN_INCOMPLETE"])
    if str(plan.get("format_version", "")).split(".")[0] not in ("0", "1"):
        return _action(True, "REPORT_NOT_EVALUATED", ["TERRAFORM_PLAN_FORMAT_UNSUPPORTED"])
    if plan.get("errored") is True:
        return _action(True, "STOP_BLOCKED", ["TERRAFORM_PLAN_ERRORED"])
    if plan.get("complete") is False:
        return _action(True, "REPORT_NOT_EVALUATED", ["TERRAFORM_PLAN_INCOMPLETE"])
    changes = list(plan.get("resource_changes") or [])
    has_effective_change = any(((change.get("change") or {}).get("actions") or []) not in ([], ["no-op"]) for change in changes if isinstance(change, Mapping))
    if plan.get("applyable") is False and has_effective_change:
        return _action(True, "STOP_BLOCKED", ["TERRAFORM_PLAN_NOT_APPLYABLE"])
    if has_effective_change:
        return _action(True, "STOP_BLOCKED", ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"])
    return _action(False, "PROCEED", ["TERRAFORM_PLAN_NO_CHANGES"])


def _action(stop: bool, recommended: str, reasons: list[str]) -> dict[str, Any]:
    return {
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        "stop": stop,
        "recommended_agent_action": recommended,
        "reason_codes": sorted(reasons),
    }


def _optional_provenance(manifest_case: Mapping[str, Any]) -> dict[str, Any]:
    files = manifest_case["files"]
    configuration = {"state": "BOUND", "sha256": files["main.tf"]} if "main.tf" in files else {"state": "NOT_APPLICABLE"}
    return {
        "configuration_sha256": configuration,
        "generation_command_fingerprint": {"state": "NOT_APPLICABLE"},
        "prior_state_sha256": {"state": "NOT_APPLICABLE"},
        "provider_lockfile_sha256": {"state": "NOT_APPLICABLE"},
        "variables_manifest_sha256": {"state": "NOT_APPLICABLE"},
        "workspace_or_fixture_identity": {"state": "NOT_APPLICABLE"},
    }


def _derive_explicit_lists(claims: list[Mapping[str, Any]]) -> dict[str, list[str]]:
    lists = _empty_lists()
    for claim in claims:
        value = claim.get("value") if isinstance(claim.get("value"), Mapping) else {}
        claim_type = claim.get("claim_type")
        if claim_type == "TERRAFORM_RESOURCE_CREATE" and "resource_address" in value:
            lists["create_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_RESOURCE_UPDATE" and "resource_address" in value:
            lists["update_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_RESOURCE_DELETE" and "resource_address" in value:
            lists["delete_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_RESOURCE_REPLACE" and "resource_address" in value:
            lists["replace_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_RESOURCE_READ" and "resource_address" in value:
            lists["read_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_RESOURCE_NOOP" and "resource_address" in value:
            lists["noop_resources"].append(value["resource_address"])
        if claim_type == "TERRAFORM_REPLACE_PATH_PRESENT" and "json_pointer" in value:
            lists["replace_paths"].append(value["json_pointer"])
        if claim_type == "PLANNED_VALUE_UNKNOWN" and "json_pointer" in value:
            lists["unknown_paths"].append(value["json_pointer"])
        if claim_type == "SENSITIVE_PATH_PRESENT" and "json_pointer" in value:
            lists["sensitive_paths"].append(value["json_pointer"])
        if claim.get("status") == "NOT_EVALUATED":
            lists["not_evaluated"].append(claim["claim_id"])
    return {name: sorted(set(values)) for name, values in lists.items()}


def _evidence_locators(claims: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    locators = []
    for claim in claims:
        for locator in claim.get("evidence", []):
            key = (locator["case_file"], locator["json_pointer"])
            if key not in seen:
                seen.add(key)
                locators.append(dict(locator))
    return sorted(locators, key=lambda item: (item["case_file"], item["json_pointer"]))


def _empty_lists() -> dict[str, list[str]]:
    return {
        "create_resources": [],
        "delete_resources": [],
        "noop_resources": [],
        "not_evaluated": [],
        "read_resources": [],
        "replace_paths": [],
        "replace_resources": [],
        "sensitive_paths": [],
        "unknown_paths": [],
        "update_resources": [],
    }


def _claim(claim_id: str, claim_type: str, status: str, subject: Mapping[str, Any], value: Mapping[str, Any], case_file: str, pointer: str) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "status": status,
        "subject": dict(subject),
        "value": dict(value),
        "evidence": [{"case_file": case_file, "json_pointer": pointer}],
    }


def _resource_claim_type(actions: list[str]) -> str | None:
    return {
        ("create",): "TERRAFORM_RESOURCE_CREATE",
        ("update",): "TERRAFORM_RESOURCE_UPDATE",
        ("delete",): "TERRAFORM_RESOURCE_DELETE",
        ("read",): "TERRAFORM_RESOURCE_READ",
        ("no-op",): "TERRAFORM_RESOURCE_NOOP",
        ("delete", "create"): "TERRAFORM_RESOURCE_REPLACE",
        ("create", "delete"): "TERRAFORM_RESOURCE_REPLACE",
    }.get(tuple(actions))


def _unknown_paths(change: Mapping[str, Any], resource_index: int) -> list[str]:
    return [
        f"/resource_changes/{resource_index}/change/after_unknown{suffix}"
        for suffix in _true_leaf_suffixes((change.get("change") or {}).get("after_unknown"))
    ]


def _sensitive_paths(change: Mapping[str, Any], resource_index: int) -> list[str]:
    pointers: list[str] = []
    change_body = change.get("change") or {}
    for field in ("after_sensitive", "before_sensitive"):
        value = change_body.get(field)
        if value is True:
            pointers.append(f"/resource_changes/{resource_index}/change/{field}")
        else:
            pointers.extend(f"/resource_changes/{resource_index}/change/{field}{suffix}" for suffix in _true_leaf_suffixes(value))
    return sorted(set(pointers))


def _true_leaf_suffixes(value: Any, prefix: str = "") -> list[str]:
    if value is True:
        return [prefix]
    if isinstance(value, Mapping):
        paths: list[str] = []
        for key, item in value.items():
            paths.extend(_true_leaf_suffixes(item, f"{prefix}/{_escape_pointer(str(key))}"))
        return paths
    if isinstance(value, list):
        paths = []
        for index, item in enumerate(value):
            paths.extend(_true_leaf_suffixes(item, f"{prefix}/{index}"))
        return paths
    return []


def _load_plan(path: Path) -> tuple[Any, bool]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), True
    except Exception:
        return None, False


def _relation(left: Any, right: Any) -> str:
    return "SAME" if left == right else "DIFFERENT"


def _claim_id_fragment(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "root"


def _escape_pointer(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")
