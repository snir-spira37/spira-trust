from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

import run_claude_native_read_invocation_hardening_diagnostic as hardening
import run_claude_native_readiness as readiness


ROOT = readiness.ROOT
TRACK_ROOT = readiness.TRACK_ROOT
RESULTS_PATH = TRACK_ROOT / "claude_native_usage_telemetry_invocation_repair_probe_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_usage_telemetry_invocation_repair_probe_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_usage_telemetry_invocation_repair_probe_raw_private_manifest.json"
PRIVATE_ROOT_PREFIX = "spira_claude_native_usage_repair_probe_private_"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Claude native six-session usage telemetry repair probe only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_probe(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_PASS" else 1


def run_probe(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = readiness.utc_now()
    raw_manifest: list[dict[str, Any]] = []
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if readiness._is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, [], raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    schema = json.loads(readiness.OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    transport_schema = readiness.claude_transport_schema(schema)
    expectations = readiness.expected_by_case()
    sessions: list[dict[str, Any]] = []
    pre_repo_state = readiness.repository_state()

    for repeat in range(1, 4):
        sessions.append(hardening.run_nonce_probe(repeat, schema, transport_schema, private_root, raw_manifest))

    for planned in probe_plan():
        item = planned["item"]
        sessions.append(
            hardening.run_benchmark_session(
                item,
                expectations[(item["domain"], item["case_id"])],
                schema,
                transport_schema,
                private_root,
                raw_manifest,
                planned["role"],
                planned["repeat_index"],
            )
        )

    errors = probe_errors(sessions)
    if readiness.repository_state() != pre_repo_state:
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_REPOSITORY_MUTATION_OBSERVED")
    return finalize(started_at, sessions, raw_manifest, sorted(set(errors)))


def probe_plan() -> list[dict[str, Any]]:
    by_key = {(item["domain"], item["case_id"], item["arm"]): item for item in readiness.readiness_inputs()}
    cells = [
        ("CRITICAL_ARM_B", ("pytest_result", "synthetic_clean_success", "B"), 2),
        ("MATCHED_ARM_C", ("pytest_result", "synthetic_clean_success", "C"), 1),
    ]
    plan: list[dict[str, Any]] = []
    for role, key, count in cells:
        for repeat_index in range(1, count + 1):
            plan.append({"role": role, "repeat_index": repeat_index, "item": by_key[key]})
    if len(plan) != 3:
        raise RuntimeError(f"Expected 3 benchmark probe sessions, found {len(plan)}")
    return plan


def result_envelope_present(session: Mapping[str, Any]) -> bool:
    return bool(session.get("result_envelope_present"))


def structured_output_present(session: Mapping[str, Any]) -> bool:
    return bool(session.get("structured_output_present"))


def usage_available(session: Mapping[str, Any]) -> bool:
    usage = session.get("usage") or {}
    return (
        bool(usage.get("input_total_available"))
        and isinstance(usage.get("input_tokens"), (int, float))
        and isinstance(usage.get("output_tokens"), (int, float))
        and usage.get("input_tokens") >= 0
        and usage.get("output_tokens") >= 0
    )


def augment_session(session: dict[str, Any]) -> dict[str, Any]:
    raw_id = session["raw_private_id"]
    raw_file = find_private_raw_file(raw_id)
    parsed = readiness.parse_json(raw_file.read_bytes()) if raw_file else None
    session["result_envelope_present"] = isinstance(parsed, Mapping) and parsed.get("type") == "result"
    session["structured_output_present"] = isinstance(parsed, Mapping) and isinstance(parsed.get("structured_output"), Mapping)
    session["model_identity_present"] = isinstance(parsed, Mapping) and bool((parsed.get("modelUsage") or parsed.get("usage") or parsed).get("model") if isinstance(parsed, Mapping) else None)
    session["usage_available_strict"] = usage_available(session)
    return session


def find_private_raw_file(raw_id: str) -> Path | None:
    matches = list(Path(tempfile.gettempdir()).rglob(raw_id + "*"))
    return matches[0] if matches else None


def probe_errors(sessions: list[Mapping[str, Any]]) -> list[str]:
    errors = []
    for session in sessions:
        augment_session(session)  # type: ignore[arg-type]
    if len(sessions) != 6:
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_INCOMPLETE")
    if any(not session.get("ready") for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_CORRECTNESS_NOT_EXACT")
    if any(not session.get("schema_valid") for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_SCHEMA_INVALID")
    if any(not result_envelope_present(session) for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_RESULT_ENVELOPE_MISSING")
    if any(not structured_output_present(session) for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_STRUCTURED_OUTPUT_MISSING")
    if any(not usage_available(session) for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_USAGE_NOT_AVAILABLE")
    if any(session.get("permission_denial_observed") for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_PERMISSION_DENIAL")
    if any((session.get("comparison") or {}).get("false_proceed") for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_FALSE_PROCEED")
    if any(session.get("workspace_mutated") for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_WORKSPACE_MUTATION")
    if any(int(session.get("forbidden_tool_count", 0)) for session in sessions):
        errors.append("CLAUDE_NATIVE_USAGE_REPAIR_PROBE_FORBIDDEN_TOOL")
    return errors


def summarize_by_cell(sessions: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[Mapping[str, Any]]] = {}
    for session in sessions:
        key = (session["diagnostic_role"], session["domain"], session["case_id"], session["arm"])
        groups.setdefault(key, []).append(session)
    summary = []
    for (role, domain, case_id, arm), group in sorted(groups.items()):
        summary.append({
            "diagnostic_role": role,
            "domain": domain,
            "case_id": case_id,
            "arm": arm,
            "session_count": len(group),
            "exact_count": sum(1 for session in group if session.get("ready")),
            "schema_valid_count": sum(1 for session in group if session.get("schema_valid")),
            "result_envelope_count": sum(1 for session in group if result_envelope_present(session)),
            "structured_output_count": sum(1 for session in group if structured_output_present(session)),
            "usage_available_count": sum(1 for session in group if usage_available(session)),
            "permission_denial_count": sum(1 for session in group if session.get("permission_denial_observed")),
        })
    return summary


def finalize(started_at: str, sessions: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    terminal = "CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_PASS" if not errors and len(sessions) == 6 else "CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_NEEDS_REVISION"
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "SIX_UNSCORED_TELEMETRY_PROBES_ONLY",
            "READINESS_RERUN_NOT_AUTHORIZED",
            "PRIMARY_BENCHMARK_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": readiness.utc_now(),
        "session_count": len(sessions),
        "schema_valid_count": sum(1 for session in sessions if session.get("schema_valid")),
        "exact_count": sum(1 for session in sessions if session.get("ready")),
        "result_envelope_count": sum(1 for session in sessions if result_envelope_present(session)),
        "structured_output_count": sum(1 for session in sessions if structured_output_present(session)),
        "usage_available_count": sum(1 for session in sessions if usage_available(session)),
        "permission_denial_count": sum(1 for session in sessions if session.get("permission_denial_observed")),
        "false_proceed_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("false_proceed")),
        "workspace_mutation_count": sum(1 for session in sessions if session.get("workspace_mutated")),
        "forbidden_tool_count": sum(int(session.get("forbidden_tool_count", 0)) for session in sessions),
        "repository_mutation_observed": "CLAUDE_NATIVE_USAGE_REPAIR_PROBE_REPOSITORY_MUTATION_OBSERVED" in errors,
        "errors": errors,
        "cell_summary": summarize_by_cell(sessions),
        "sessions": sessions,
        "raw_private_manifest": {
            "schema": "SPIRA_CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    rows = "\n".join(
        "- {domain} {case_id} arm {arm} {diagnostic_role}: exact={exact_count}/{session_count} envelope={result_envelope_count}/{session_count} structured={structured_output_count}/{session_count} usage={usage_available_count}/{session_count}".format(**cell)
        for cell in results.get("cell_summary", [])
    )
    errors = "\n".join(f"- {error}" for error in results.get("errors", [])) or "- none"
    return f"""# Claude Native Usage Telemetry Invocation Repair Probe Report

## Status

```text
{results['terminal_status']}
SIX_UNSCORED_TELEMETRY_PROBES_ONLY
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count: {results['session_count']}
schema valid: {results['schema_valid_count']} / 6
correct: {results['exact_count']} / 6
JSON result envelope present: {results['result_envelope_count']} / 6
structured_output present: {results['structured_output_count']} / 6
usage available: {results['usage_available_count']} / 6
permission denials: {results['permission_denial_count']}
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
repository mutation observed: {str(results['repository_mutation_observed']).lower()}
forbidden tool calls: {results['forbidden_tool_count']}
```

## Cell Summary

{rows}

## Errors

{errors}
"""


if __name__ == "__main__":
    raise SystemExit(main())
