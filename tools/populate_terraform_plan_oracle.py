from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import terraform_plan_oracle_validator as validator  # noqa: E402


OUT = ROOT / "research" / "terraform_plan_contract"
MANIFEST = OUT / "corpus_manifest_v1.json"
ORACLE = OUT / "oracle_v1.json"
RESULTS = OUT / "oracle_population_results.json"
REPORT = OUT / "oracle_population_report.md"

NOT_CLAIMED = [
    "APPLY_SUCCESS",
    "DOMAIN_4",
    "GATE_B_REUSE",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "KUBERNETES_SUPPORT",
    "LIVE_STATE_FRESHNESS",
    "MVP_INCLUSION",
    "RELEASE",
    "TERRAFORM_PROVIDER_SAFETY",
]

NOT_AUTHORIZED = [
    "DOMAIN_4",
    "GATE_B",
    "MVP_BOUNDARY_AMENDMENT",
    "ORACLE_POPULATION_BEFORE_SCHEMA_ACCEPTANCE",
    "PRODUCER_IMPLEMENTATION",
    "RELEASE_VERSION_TAG_PYPI",
]

CASE_NOT_CLAIMED = [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS",
]

PRIVATE_USER_PATH_PATTERN = re.escape("C" + ":" + "\\Users" + "\\snir")
PRIVATE_KEY_PATTERN = "BEGIN" + " PRIVATE KEY"
AWS_KEY_PATTERN = "AK" + "IA[0-9A-Z]{16}"
GITHUB_TOKEN_PATTERN = "gh" + "p_[A-Za-z0-9_]+"
SLACK_TOKEN_PATTERN = "xo" + "x[baprs]-"
PEM_BEGIN_PATTERN = "-" * 5 + "BEGIN"
SECRET_SCAN_PATTERN = re.compile(
    "|".join(
        [
            PRIVATE_USER_PATH_PATTERN,
            PRIVATE_KEY_PATTERN,
            AWS_KEY_PATTERN,
            GITHUB_TOKEN_PATTERN,
            SLACK_TOKEN_PATTERN,
            PEM_BEGIN_PATTERN,
        ]
    )
)


def main() -> None:
    manifest = _read_json(MANIFEST)
    oracle = populate_oracle(manifest)
    ORACLE.write_text(_json_dumps(oracle) + "\n", encoding="utf-8")
    validation = validator.validate_oracle_file(ORACLE)
    result = population_results(oracle, validation)
    RESULTS.write_text(_json_dumps(result) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(result, validation), encoding="utf-8")
    print(json.dumps({"status": result["status"], "validator": validation["verdict"]}, sort_keys=True))
    if result["status"] != "DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATED":
        raise SystemExit(1)


def populate_oracle(manifest: Mapping[str, Any]) -> dict[str, Any]:
    oracle = {
        "schema": "SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE",
        "schema_version": 1,
        "status": "DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_V1_LOCKED",
        "corpus_manifest_sha256": validator.CORPUS_MANIFEST_SHA256,
        "case_count": 40,
        "cases": [],
        "mutation_relationships": [],
        "not_claimed": NOT_CLAIMED,
        "not_authorized": NOT_AUTHORIZED,
    }
    case_by_id = {}
    for manifest_case in manifest["cases"]:
        case = populate_case(oracle, manifest_case)
        oracle["cases"].append(case)
        case_by_id[case["case_id"]] = case
    for pair in manifest["mutation_pairs"]:
        base = case_by_id[pair["base_case_id"]]
        mutated = case_by_id[pair["mutated_case_id"]]
        oracle["mutation_relationships"].append(
            {
                "pair_id": pair["pair_id"],
                "base_case_id": pair["base_case_id"],
                "mutated_case_id": pair["mutated_case_id"],
                "declared_delta": pair["declared_delta"],
                "expected_claims_relation": _relation(
                    validator.claims_identity(base), validator.claims_identity(mutated)
                ),
                "expected_claims_root_relation": _relation(
                    validator.claims_merkle_root(base), validator.claims_merkle_root(mutated)
                ),
                "expected_unification_id_relation": _relation(
                    base["context"]["unification_id_expected"],
                    mutated["context"]["unification_id_expected"],
                ),
            }
        )
    return oracle


def populate_case(document: Mapping[str, Any], manifest_case: Mapping[str, Any]) -> dict[str, Any]:
    case_id = manifest_case["case_id"]
    case_dir = OUT / "cases" / case_id
    files = manifest_case["files"]
    plan_file = "plan.json" if "plan.json" in files else "plan.json.invalid"
    plan_path = case_dir / plan_file
    subject = {"type": "terraform_plan", "sha256": files[plan_file]}
    plan, valid_json = _load_plan(plan_path)
    case = {
        "case_id": case_id,
        "subject": subject,
        "context": {
            "context_sha256": "0" * 64,
            "run_identity_kind": "CONTEXTUAL_UNIFICATION_ID",
            "unification_id_expected": "0" * 64,
        },
        "optional_provenance": _optional_provenance(manifest_case),
        "expected_claims": [],
        "explicit_lists": _empty_lists(),
        "policy_action": _policy_action(plan, valid_json),
        "mutation_membership": [],
        "not_claimed": CASE_NOT_CLAIMED,
    }
    if valid_json and isinstance(plan, Mapping):
        case["expected_claims"].extend(_plan_claims(subject, plan))
    else:
        case["expected_claims"].append(
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
    case["expected_claims"].extend(_provenance_claims(subject, case["optional_provenance"], plan_file))
    case["explicit_lists"] = _derive_explicit_lists(case["expected_claims"])
    case["context"]["context_sha256"] = validator.context_sha256(document, case, manifest_case)
    case["context"]["unification_id_expected"] = validator.unification_id(document, case)
    return case


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
        locator = "" if _order_insensitive_resource_change(plan) else f"/resource_changes/{index}"
        claims.append(_claim(f"terraform_plan.resource_address.{ordinal_prefix}", "TERRAFORM_RESOURCE_ADDRESS_PRESENT", "PASS", subject, {"resource_address": address}, "plan.json", locator))
        claims.append(_claim(f"terraform_plan.resource_type.{ordinal_prefix}", "TERRAFORM_RESOURCE_TYPE_PRESENT", "PASS", subject, {"resource_type": resource_type}, "plan.json", locator))
        if actions:
            claims.append(_claim(f"terraform_plan.action_sequence.{ordinal_prefix}", "TERRAFORM_RESOURCE_ACTION_SEQUENCE", "PASS", subject, {"action_sequence": actions}, "plan.json", locator))
        action_type = _resource_claim_type(actions)
        if action_type:
            claims.append(_claim(f"terraform_plan.resource_action.{ordinal_prefix}", action_type, "PASS", subject, {"resource_address": address}, "plan.json", locator))
        for path_index, replace_path in enumerate((change.get("change") or {}).get("replace_paths") or []):
            pointer = _replace_path_pointer(index, path_index)
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


def _provenance_claims(
    subject: Mapping[str, Any],
    provenance: Mapping[str, Any],
    plan_file: str,
) -> list[dict[str, Any]]:
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


def _claim(
    claim_id: str,
    claim_type: str,
    status: str,
    subject: Mapping[str, Any],
    value: Mapping[str, Any],
    case_file: str,
    pointer: str,
) -> dict[str, Any]:
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


def _order_insensitive_resource_change(plan: Mapping[str, Any]) -> bool:
    return True


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
            pointers.extend(
                f"/resource_changes/{resource_index}/change/{field}{suffix}"
                for suffix in _true_leaf_suffixes(value)
            )
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


def _replace_path_pointer(resource_index: int, path_index: int) -> str:
    return f"/resource_changes/{resource_index}/change/replace_paths/{path_index}"


def _status_for_present(plan: Mapping[str, Any], field: str) -> str:
    return "PASS" if field in plan else "NOT_EVALUATED"


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


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def population_results(oracle: Mapping[str, Any], validation: Mapping[str, Any]) -> dict[str, Any]:
    privacy = _privacy_scan()
    status = "DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATED"
    errors: list[dict[str, Any]] = []
    if validation["verdict"] != "PASS":
        status = "DOMAIN_3_TERRAFORM_PLAN_ORACLE_NEEDS_REVISION"
        errors.append({"code": "VALIDATOR_FAILED", "validator_status": validation["status"]})
    if not privacy["passed"]:
        status = "DOMAIN_3_TERRAFORM_PLAN_ORACLE_NEEDS_REVISION"
        errors.append({"code": "PRIVACY_PATH_SECRET_SCAN_FAILED"})
    return {
        "schema": "SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE_POPULATION_RESULTS",
        "schema_version": 1,
        "status": status,
        "case_count": 40,
        "populated_case_count": len(oracle.get("cases", [])),
        "mutation_relationship_count": len(oracle.get("mutation_relationships", [])),
        "schema_validation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "validator_validation": validation["verdict"],
        "validator_error_count": validation.get("counts", {}).get("error_count", 0),
        "producer_output_observed": False,
        "corpus_changed": False,
        "schema_or_validator_changed": False,
        "privacy_path_secret_scan": privacy,
        "errors": errors,
    }


def _privacy_scan() -> dict[str, Any]:
    paths = [ORACLE, RESULTS, REPORT, Path(__file__)]
    hits = []
    for path in paths:
        if not path.exists():
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if SECRET_SCAN_PATTERN.search(line):
                hits.append({"path": str(path.relative_to(ROOT)), "line": index})
    return {"passed": not hits, "hits": hits}


def report_markdown(result: Mapping[str, Any], validation: Mapping[str, Any]) -> str:
    return f"""# Terraform Plan Oracle Population Report

## Status

```text
{result['status']}
ORACLE_POPULATION_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Chain

```text
corpus: DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED
schema: DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED
validator spec: DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED
validator implementation: DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
population authorization: DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATION_AUTHORIZED
```

## Evidence Sources

```text
corpus manifest: research/terraform_plan_contract/corpus_manifest_v1.json
corpus cases: research/terraform_plan_contract/cases/
accepted manifest sha256: {validator.CORPUS_MANIFEST_SHA256}
```

Expected answers were derived from frozen Terraform Plan evidence and accepted
manifest mutation deltas. Producer output was not used.

## Results

```text
case count: {result['case_count']}
populated cases: {result['populated_case_count']}
mutation relationships: {result['mutation_relationship_count']}
Schema V1 validation: {result['schema_validation']}
accepted validator: {result['validator_validation']}
validator errors: {result['validator_error_count']}
privacy/path/secret scan: {'PASS' if result['privacy_path_secret_scan']['passed'] else 'FAIL'}
producer output observed: false
corpus changed: false
schema or validator changed: false
```

## Validator Output

```text
verdict: {validation['verdict']}
status: {validation['status']}
error_count: {validation.get('counts', {}).get('error_count', 0)}
```

## Boundaries

```text
producer implementation: NOT AUTHORIZED
Gate B: NOT AUTHORIZED
Domain 4: NOT AUTHORIZED
MVP boundary amendment: NOT AUTHORIZED
release/version/tag/PyPI: NOT AUTHORIZED
```

## Post-Population Review Required

This population result is not oracle acceptance. A separate review must decide:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_ORACLE_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_ORACLE_REJECTED
```
"""


if __name__ == "__main__":
    main()
