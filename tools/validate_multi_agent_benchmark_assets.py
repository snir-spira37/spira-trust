from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
FROZEN_INPUTS = BENCHMARK_ROOT / "frozen_inputs"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


REQUIRED_FILES = [
    BENCHMARK_ROOT / "protocol_v1.md",
    BENCHMARK_ROOT / "agent_output.schema.json",
    BENCHMARK_ROOT / "case_manifest.json",
    BENCHMARK_ROOT / "prompt_templates_v1.md",
    BENCHMARK_ROOT / "randomization_manifest_v1.json",
    BENCHMARK_ROOT / "frozen_input_manifest.json",
    BENCHMARK_ROOT / "deepseek" / "deepseek_track_plan.md",
    BENCHMARK_ROOT / "deepseek" / "deepseek_agent_config.template.json",
    BENCHMARK_ROOT / "deepseek" / "deepseek_readiness_authorization.md",
    BENCHMARK_ROOT / "deepseek" / "deepseek_readiness_manifest.template.json",
    BENCHMARK_ROOT / "deepseek" / "deepseek_protocol_deviations.md",
]

ALLOWED_STATUS = {
    "DEEPSEEK_BENCHMARK_TRACK_PREPARED",
    "DEEPSEEK_CASE_SET_FROZEN",
    "DEEPSEEK_PROMPTS_FROZEN",
    "DEEPSEEK_OUTPUT_SCHEMA_FROZEN",
    "DEEPSEEK_ARM_INPUTS_FROZEN",
    "DEEPSEEK_READINESS_PREPARED",
    "DEEPSEEK_LIVE_EXECUTION_NOT_STARTED",
    "DEEPSEEK_READINESS_REVIEW_REQUIRED",
    "MVP_CODE_UNCHANGED",
    "PUBLIC_EFFICIENCY_CLAIM_NOT_AUTHORIZED",
    "RELEASE_NOT_AUTHORIZED",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate frozen SPIRA multi-agent benchmark assets.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable validation results.")
    args = parser.parse_args(argv)

    result = validate_assets()
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        print(f"{result['status']}: {len(result['errors'])} errors, {len(result['warnings'])} warnings")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if result["status"] == "MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_PASS" else 1


def validate_assets(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f"MISSING_REQUIRED_FILE:{relative(path)}")

    if errors:
        return _result(errors, warnings)

    output_schema = _read_json(BENCHMARK_ROOT / "agent_output.schema.json", errors)
    case_manifest = _read_json(BENCHMARK_ROOT / "case_manifest.json", errors)
    randomization = _read_json(BENCHMARK_ROOT / "randomization_manifest_v1.json", errors)
    input_manifest = _read_json(BENCHMARK_ROOT / "frozen_input_manifest.json", errors)
    config = _read_json(BENCHMARK_ROOT / "deepseek" / "deepseek_agent_config.template.json", errors)
    readiness_template = _read_json(BENCHMARK_ROOT / "deepseek" / "deepseek_readiness_manifest.template.json", errors)

    _validate_output_schema(output_schema, errors)
    _validate_cases(case_manifest, errors)
    _validate_randomization(randomization, case_manifest, errors)
    _validate_inputs(input_manifest, case_manifest, errors)
    _validate_deepseek_config(config, readiness_template, errors)
    _validate_markdown_statuses(errors)

    return _result(errors, warnings)


def _validate_output_schema(schema: Mapping[str, Any], errors: list[str]) -> None:
    required = [
        "gate",
        "spira_verdict",
        "recommended_agent_action",
        "reason_codes",
        "not_evaluated",
        "blocking_items",
        "evidence_or_proof_references",
        "drilldown_used",
        "not_claimed",
    ]
    if schema.get("additionalProperties") is not False:
        errors.append("OUTPUT_SCHEMA_ALLOWS_ADDITIONAL_PROPERTIES")
    if schema.get("required") != required:
        errors.append("OUTPUT_SCHEMA_REQUIRED_FIELDS_MISMATCH")
    props = schema.get("properties") or {}
    for name in required:
        if name not in props:
            errors.append(f"OUTPUT_SCHEMA_MISSING_PROPERTY:{name}")


def _validate_cases(manifest: Mapping[str, Any], errors: list[str]) -> None:
    cases = manifest.get("cases") or []
    if manifest.get("status") != "DEEPSEEK_CASE_SET_FROZEN":
        errors.append("CASE_MANIFEST_STATUS_NOT_FROZEN")
    if len(cases) != 18:
        errors.append(f"CASE_COUNT_NOT_18:{len(cases)}")
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)):
        errors.append("CASE_IDS_NOT_UNIQUE")

    by_domain: dict[str, list[Mapping[str, Any]]] = {}
    by_allocation: dict[str, list[Mapping[str, Any]]] = {}
    readiness = []
    for case in cases:
        by_domain.setdefault(str(case.get("domain")), []).append(case)
        by_allocation.setdefault(str(case.get("allocation")), []).append(case)
        if case.get("readiness_selected") is True:
            readiness.append(case)
        _require_hex(case, "source_sha256", errors, f"CASE_SOURCE_HASH_INVALID:{case.get('case_id')}")
        action = case.get("expected_action") or {}
        if "recommended_agent_action" not in action or "stop" not in action:
            errors.append(f"CASE_ACTION_INCOMPLETE:{case.get('case_id')}")
        for list_name in ["expected_reason_codes", "expected_not_evaluated", "expected_blocking_list", "expected_not_claimed"]:
            value = case.get(list_name)
            if not isinstance(value, list):
                errors.append(f"CASE_LIST_FIELD_NOT_ARRAY:{case.get('case_id')}:{list_name}")
            elif value != sorted(set(value)):
                errors.append(f"CASE_LIST_NOT_SORTED_UNIQUE:{case.get('case_id')}:{list_name}")

    if {key: len(value) for key, value in by_domain.items()} != {
        "python_artifact": 6,
        "pytest_result": 6,
        "terraform_plan": 6,
    }:
        errors.append("CASE_DOMAIN_COUNTS_INVALID")
    if len(by_allocation.get("primary", [])) != 12 or len(by_allocation.get("holdout", [])) != 6:
        errors.append("PRIMARY_HOLDOUT_COUNTS_INVALID")
    if len(readiness) != 3:
        errors.append("READINESS_CASE_COUNT_NOT_3")
    if {case.get("domain") for case in readiness} != {"python_artifact", "pytest_result", "terraform_plan"}:
        errors.append("READINESS_DOMAIN_COVERAGE_INVALID")
    if any(case.get("allocation") == "holdout" for case in readiness):
        errors.append("HOLDOUT_CASE_SELECTED_FOR_READINESS")


def _validate_randomization(
    randomization: Mapping[str, Any], case_manifest: Mapping[str, Any], errors: list[str]
) -> None:
    if randomization.get("status") != "DEEPSEEK_RANDOMIZATION_FROZEN":
        errors.append("RANDOMIZATION_STATUS_NOT_FROZEN")
    phases = randomization.get("deepseek_track_counts") or {}
    expected = {
        "technical_probes_unscored": "NOT_COUNTED",
        "readiness_sessions": 9,
        "primary_sessions": 180,
        "holdout_sessions": 54,
        "carryover_sessions": 18,
        "scored_and_readiness_sessions": 261,
    }
    if phases != expected:
        errors.append("DEEPSEEK_TRACK_COUNTS_MISMATCH")
    cases = {case["case_id"]: case for case in case_manifest.get("cases") or []}
    readiness_ids = set(randomization.get("readiness_case_ids") or [])
    expected_readiness = {case["case_id"] for case in cases.values() if case.get("readiness_selected")}
    if readiness_ids != expected_readiness:
        errors.append("READINESS_IDS_DO_NOT_MATCH_CASE_MANIFEST")
    primary_ids = set(randomization.get("primary_case_ids") or [])
    holdout_ids = set(randomization.get("holdout_case_ids") or [])
    if primary_ids & holdout_ids:
        errors.append("PRIMARY_HOLDOUT_OVERLAP")
    if readiness_ids - primary_ids:
        errors.append("READINESS_NOT_SUBSET_OF_PRIMARY")
    if holdout_ids & readiness_ids:
        errors.append("HOLDOUT_READINESS_OVERLAP")


def _validate_inputs(
    input_manifest: Mapping[str, Any], case_manifest: Mapping[str, Any], errors: list[str]
) -> None:
    if input_manifest.get("status") != "DEEPSEEK_ARM_INPUTS_FROZEN":
        errors.append("FROZEN_INPUT_MANIFEST_STATUS_INVALID")
    entries = input_manifest.get("inputs") or []
    if len(entries) != 54:
        errors.append(f"FROZEN_INPUT_COUNT_NOT_54:{len(entries)}")
    cases = {case["case_id"]: case for case in case_manifest.get("cases") or []}
    seen = set()
    for entry in entries:
        key = (entry.get("case_id"), entry.get("arm"))
        if key in seen:
            errors.append(f"DUPLICATE_FROZEN_INPUT:{key}")
        seen.add(key)
        if entry.get("arm") not in {"A", "B", "C"}:
            errors.append(f"INVALID_ARM:{entry.get('arm')}")
        if entry.get("case_id") not in cases:
            errors.append(f"INPUT_CASE_NOT_IN_MANIFEST:{entry.get('case_id')}")
        _require_hex(entry, "input_sha256", errors, f"INPUT_HASH_INVALID:{entry.get('case_id')}:{entry.get('arm')}")
        path = ROOT / str(entry.get("path"))
        if not path.exists():
            errors.append(f"FROZEN_INPUT_FILE_MISSING:{entry.get('path')}")
            continue
        observed = _sha256(path.read_bytes())
        if observed != entry.get("input_sha256"):
            errors.append(f"FROZEN_INPUT_HASH_MISMATCH:{entry.get('path')}")
        payload = _read_json(path, errors)
        if payload.get("arm") != entry.get("arm"):
            errors.append(f"FROZEN_INPUT_ARM_MISMATCH:{entry.get('path')}")
        surface = payload.get("evidence_surface") or {}
        serialized = json.dumps(surface, sort_keys=True)
        if entry.get("arm") == "A":
            if "direct_domain_contract" in serialized or "unified_mvp_contract" in serialized:
                errors.append(f"ARM_A_LEAKS_COMPACT_CONTRACT:{entry.get('path')}")
        if entry.get("arm") == "B" and "unified_mvp_contract" in serialized:
            errors.append(f"ARM_B_LEAKS_UNIFIED_CONTRACT:{entry.get('path')}")
        if entry.get("arm") == "C" and "direct_domain_contract" in serialized:
            errors.append(f"ARM_C_LEAKS_DIRECT_CONTRACT:{entry.get('path')}")
    for case_id in cases:
        for arm in ("A", "B", "C"):
            if (case_id, arm) not in seen:
                errors.append(f"MISSING_CASE_ARM_INPUT:{case_id}:{arm}")
    for item in input_manifest.get("semantic_equivalence_checks") or []:
        if item.get("status") != "PASS":
            errors.append(f"ARM_BC_SEMANTIC_EQUIVALENCE_NOT_PASS:{item.get('case_id')}")
        if item.get("direct_semantic_hash") != item.get("unified_semantic_hash"):
            errors.append(f"ARM_BC_SEMANTIC_HASH_MISMATCH:{item.get('case_id')}")


def _validate_deepseek_config(
    config: Mapping[str, Any], readiness_template: Mapping[str, Any], errors: list[str]
) -> None:
    if config.get("evaluated_system_name") != "DeepSeek model via Claude Code harness":
        errors.append("DEEPSEEK_SYSTEM_NAME_INVALID")
    if config.get("endpoint") != "https://api.deepseek.com/anthropic":
        errors.append("DEEPSEEK_ENDPOINT_INVALID")
    if config.get("requested_model") != "deepseek-v4-pro":
        errors.append("DEEPSEEK_REQUESTED_MODEL_INVALID")
    if config.get("api_key_storage") != "PROCESS_ENVIRONMENT_ONLY":
        errors.append("DEEPSEEK_SECRET_STORAGE_INVALID")
    model_env = config.get("model_environment_mappings") or {}
    required = {
        "ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CLAUDE_CODE_SUBAGENT_MODEL",
    }
    if set(model_env) != required:
        errors.append("DEEPSEEK_MODEL_ENV_MAPPING_KEYS_INVALID")
    if set(model_env.values()) != {"deepseek-v4-pro"}:
        errors.append("DEEPSEEK_MODEL_ENV_MAPPING_VALUES_NOT_PINNED")
    forbidden_enabled = [
        key
        for key in [
            "session_persistence",
            "custom_memory",
            "claude_md_loading",
            "plugins",
            "hooks",
            "mcp",
            "web_search",
            "subagents",
            "fallback_model",
            "write_tools",
        ]
        if config.get("disabled_surfaces", {}).get(key) is not True
    ]
    if forbidden_enabled:
        errors.append(f"DEEPSEEK_DISABLED_SURFACES_INCOMPLETE:{','.join(sorted(forbidden_enabled))}")
    if readiness_template.get("live_model_calls_started") is not False:
        errors.append("READINESS_TEMPLATE_SHOULD_NOT_START_LIVE_CALLS")


def _validate_markdown_statuses(errors: list[str]) -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in REQUIRED_FILES if path.suffix == ".md")
    for status in ALLOWED_STATUS:
        if status not in combined and status not in (BENCHMARK_ROOT / "case_manifest.json").read_text(encoding="utf-8"):
            errors.append(f"MISSING_REQUIRED_STATUS_TEXT:{status}")
    forbidden = [
        "API key " + "value",
        "Authorization" + ": Bearer",
        "s" + "k-",
        "DEEPSEEK" + "_API_KEY=",
    ]
    for token in forbidden:
        if token in combined:
            errors.append(f"SECRET_LIKE_TEXT_PRESENT:{token}")


def _require_hex(item: Mapping[str, Any], key: str, errors: list[str], label: str) -> None:
    value = item.get(key)
    if not isinstance(value, str) or not HEX64.match(value):
        errors.append(label)


def _read_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive reporting path
        errors.append(f"JSON_READ_FAILED:{relative(path)}:{type(exc).__name__}")
        return {}


def _result(errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "schema": "SPIRA_MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_RESULTS_V1",
        "status": "MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_PASS" if not errors else "MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_FAIL",
        "errors": errors,
        "warnings": warnings,
    }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
