from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

import run_codex_native_readiness as readiness


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
TRACK_ROOT = BENCHMARK_ROOT / "codex_native"
RESULTS_PATH = TRACK_ROOT / "codex_native_readiness_reliability_diagnostic_results.json"
REPORT_PATH = TRACK_ROOT / "codex_native_readiness_reliability_diagnostic_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "codex_native_readiness_reliability_diagnostic_raw_private_manifest.json"
REVIEW_PATH = TRACK_ROOT / "codex_native_readiness_reliability_diagnostic_review.md"
PRIVATE_ROOT_PREFIX = "spira_codex_native_readiness_reliability_private_"


def main() -> int:
    results = run_diagnostic()
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    REVIEW_PATH.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE" else 1


def run_diagnostic() -> dict[str, Any]:
    started_at = readiness.utc_now()
    raw_manifest: list[dict[str, Any]] = []
    private_root = Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    selected = readiness.readiness_inputs()
    selected_by_arm = {
        item["arm"]: item
        for item in selected
        if item["domain"] == "pytest_result" and item["case_id"] == "synthetic_clean_success" and item["arm"] in {"B", "C"}
    }
    expected = readiness.expected_by_case()[("pytest_result", "synthetic_clean_success")]
    schema = json.loads(readiness.OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    transport_schema = readiness.codex_transport_schema(schema)
    sessions: list[dict[str, Any]] = []

    for repetition in range(1, 11):
        session = readiness.run_session(selected_by_arm["B"], expected, schema, transport_schema, private_root, raw_manifest)
        session["diagnostic_repetition"] = repetition
        session["diagnostic_scored"] = False
        sessions.append(enrich_diagnostic_session(session, expected))
    for repetition in range(1, 6):
        session = readiness.run_session(selected_by_arm["C"], expected, schema, transport_schema, private_root, raw_manifest)
        session["diagnostic_repetition"] = repetition
        session["diagnostic_scored"] = False
        sessions.append(enrich_diagnostic_session(session, expected))

    arm_b = [s for s in sessions if s["arm"] == "B"]
    arm_c = [s for s in sessions if s["arm"] == "C"]
    errors: list[str] = []
    if len(sessions) != 15:
        errors.append("CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INCOMPLETE")
    if any(not s.get("exact") for s in arm_b):
        errors.append("CODEX_NATIVE_DIRECT_CONTRACT_RELIABILITY_NOT_READY")
    if any(not s.get("exact") for s in arm_c):
        errors.append("CODEX_NATIVE_MATCHED_ARM_C_CONTROL_NOT_EXACT")
    if any(s.get("persistent_infrastructure_failure") for s in sessions):
        errors.append("CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INFRASTRUCTURE_BLOCKED")

    terminal = (
        "CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE"
        if len(sessions) == 15 and not any(s.get("persistent_infrastructure_failure") for s in sessions)
        else "CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INFRASTRUCTURE_BLOCKED"
    )
    return {
        "schema": "SPIRA_CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "CODEX_PRIMARY_NOT_AUTHORIZED",
            "HOLDOUT_NOT_AUTHORIZED",
            "CARRYOVER_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": readiness.utc_now(),
        "requested_model": readiness.REQUESTED_MODEL,
        "resolved_model_id": readiness.REQUESTED_MODEL,
        "reasoning_effort": readiness.REASONING_EFFORT,
        "codex_cli_version": readiness.run_local([str(readiness.CODEX_EXE), "--version"]),
        "codex_cli_invocation_identity": "LOCAL_OPENAI_CODEX_BIN/codex.exe",
        "codex_cli_sha256": readiness.file_sha256(readiness.CODEX_EXE),
        "session_count": len(sessions),
        "arm_b_exact_count": sum(1 for s in arm_b if s.get("exact")),
        "arm_c_exact_count": sum(1 for s in arm_c if s.get("exact")),
        "schema_valid_count": sum(1 for s in sessions if s.get("schema_valid")),
        "usage_available_count": sum(1 for s in sessions if (s.get("usage") or {}).get("input_total_available")),
        "false_proceed_count": sum(1 for s in sessions if (s.get("comparison") or {}).get("false_proceed")),
        "workspace_mutation_count": sum(1 for s in sessions if s.get("workspace_mutated")),
        "forbidden_tool_count": sum(int(s.get("forbidden_tool_count", 0)) for s in sessions),
        "errors": sorted(set(errors)),
        "sessions": sessions,
        "raw_private_manifest": {
            "schema": "SPIRA_CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def enrich_diagnostic_session(session: dict[str, Any], expected: Mapping[str, Any]) -> dict[str, Any]:
    output = session.get("agent_output") or {}
    comparison = session.get("comparison") or {}
    session["expected_reason_codes"] = sorted(expected.get("expected_reason_codes") or [])
    session["observed_reason_codes"] = sorted(output.get("reason_codes") or [])
    session["missing_reason_codes"] = sorted(set(session["expected_reason_codes"]) - set(session["observed_reason_codes"]))
    session["expected_not_claimed"] = sorted(expected.get("expected_not_claimed") or [])
    session["observed_not_claimed"] = sorted(output.get("not_claimed") or [])
    session["missing_not_claimed"] = sorted(set(session["expected_not_claimed"]) - set(session["observed_not_claimed"]))
    session["action_preserved"] = bool((comparison.get("checks") or {}).get("recommended_agent_action"))
    session["stop_state_preserved"] = bool((comparison.get("checks") or {}).get("gate"))
    session["blocking_items_preserved"] = bool((comparison.get("checks") or {}).get("blocking_items"))
    session["not_evaluated_preserved"] = bool((comparison.get("checks") or {}).get("not_evaluated"))
    session["exact"] = bool(comparison.get("pass"))
    session["persistent_infrastructure_failure"] = not session.get("result_envelope_present") or not session.get("structured_output_present") or not (session.get("usage") or {}).get("input_total_available")
    return session


def report_markdown(results: Mapping[str, Any]) -> str:
    lines = "\n".join(
        f"- arm {s['arm']} rep {s['diagnostic_repetition']}: exact={s['exact']} missing_reason={s['missing_reason_codes']} missing_not_claimed={s['missing_not_claimed']}"
        for s in results.get("sessions", [])
    )
    return f"""# Codex Native Readiness Reliability Diagnostic Report

## Status

```text
{results['terminal_status']}
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count: {results['session_count']} / 15
Arm B exact: {results['arm_b_exact_count']} / 10
Arm C exact: {results['arm_c_exact_count']} / 5
schema valid: {results['schema_valid_count']} / 15
usage available: {results['usage_available_count']} / 15
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_count']}
```

## Sessions

{lines}
"""


def review_markdown(results: Mapping[str, Any]) -> str:
    if results.get("arm_b_exact_count") == 10 and results.get("arm_c_exact_count") == 5:
        verdict = "ORIGINAL_ARM_B_OMISSION_NOT_REPRODUCED"
        next_step = "FULL_NINE_CELL_CODEX_READINESS_RERUN_JUSTIFIED"
    else:
        verdict = "CODEX_NATIVE_DIRECT_CONTRACT_RELIABILITY_NOT_READY"
        next_step = "CONTRACT_PRESENTATION_AMBIGUITY_STRENGTHENED"
    return f"""# Codex Native Readiness Reliability Diagnostic Review

## Status

```text
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_REVIEW_COMPLETE
{verdict}
{next_step}
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_authorization.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_results.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_report.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_raw_private_manifest.json
```

## Summary

```text
Arm B exact: {results['arm_b_exact_count']} / 10
Arm C exact: {results['arm_c_exact_count']} / 5
schema valid: {results['schema_valid_count']} / 15
usage available: {results['usage_available_count']} / 15
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_count']}
```

This diagnostic is unscored and does not replace the original readiness result.
Codex primary remains unauthorized.
"""


if __name__ == "__main__":
    raise SystemExit(main())
