from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Mapping

import run_claude_native_readiness as readiness


ROOT = readiness.ROOT
TRACK_ROOT = readiness.TRACK_ROOT
RESULTS_PATH = TRACK_ROOT / "claude_native_readiness_reliability_diagnostic_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_readiness_reliability_diagnostic_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_readiness_reliability_diagnostic_raw_private_manifest.json"
PRIVATE_ROOT_PREFIX = "spira_claude_native_reliability_diagnostic_private_"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Claude native readiness reliability diagnostic only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)

    results = run_diagnostic(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE" else 1


def run_diagnostic(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = readiness.utc_now()
    raw_manifest: list[dict[str, Any]] = []
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if readiness._is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, [], raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    selected = diagnostic_plan()
    expectations = readiness.expected_by_case()
    schema = json.loads(readiness.OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    transport_schema = readiness.claude_transport_schema(schema)
    sessions: list[dict[str, Any]] = []
    pre_repo_state = readiness.repository_state()

    for planned in selected:
        item = dict(planned["item"])
        session = readiness.run_session(
            item,
            expectations[(item["domain"], item["case_id"])],
            schema,
            transport_schema,
            private_root,
            raw_manifest,
        )
        session["diagnostic_role"] = planned["role"]
        session["diagnostic_repeat_index"] = planned["repeat_index"]
        session["diagnostic_scored_for_readiness"] = False
        sessions.append(session)

    errors = diagnostic_errors(sessions)
    if readiness.repository_state() != pre_repo_state:
        errors.append("CLAUDE_NATIVE_RELIABILITY_DIAGNOSTIC_REPOSITORY_MUTATION_OBSERVED")
    return finalize(started_at, sessions, raw_manifest, sorted(set(errors)))


def diagnostic_plan() -> list[dict[str, Any]]:
    by_key = {(item["domain"], item["case_id"], item["arm"]): item for item in readiness.readiness_inputs()}
    cells = [
        ("CRITICAL_ARM_B", ("pytest_result", "synthetic_clean_success", "B"), 10),
        ("FAILED_ARM_A_PYTEST", ("pytest_result", "synthetic_clean_success", "A"), 5),
        (
            "FAILED_ARM_A_PYTHON_ARTIFACT",
            ("python_artifact", "0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4", "A"),
            5,
        ),
        ("FAILED_ARM_A_TERRAFORM", ("terraform_plan", "auth_no_changes", "A"), 5),
        ("MATCHED_ARM_C_CONTROL", ("pytest_result", "synthetic_clean_success", "C"), 5),
    ]
    plan: list[dict[str, Any]] = []
    for role, key, count in cells:
        item = by_key[key]
        for repeat_index in range(1, count + 1):
            plan.append({"role": role, "repeat_index": repeat_index, "item": item})
    if len(plan) != 30:
        raise RuntimeError(f"Expected 30 diagnostic sessions, found {len(plan)}")
    return plan


def diagnostic_errors(sessions: list[Mapping[str, Any]]) -> list[str]:
    errors = []
    if len(sessions) != 30:
        errors.append("CLAUDE_NATIVE_RELIABILITY_DIAGNOSTIC_INCOMPLETE")
    if any(session.get("workspace_mutated") for session in sessions):
        errors.append("CLAUDE_NATIVE_RELIABILITY_DIAGNOSTIC_WORKSPACE_MUTATION")
    if any(int(session.get("forbidden_tool_count", 0)) for session in sessions):
        errors.append("CLAUDE_NATIVE_RELIABILITY_DIAGNOSTIC_FORBIDDEN_TOOL")
    if any(not (session.get("usage") or {}).get("input_total_available") for session in sessions):
        errors.append("CLAUDE_NATIVE_RELIABILITY_DIAGNOSTIC_USAGE_NOT_AVAILABLE")
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
            "returncode_zero_count": sum(1 for session in group if session.get("returncode") == 0),
            "output_found_count": sum(1 for session in group if session.get("output_found")),
            "schema_valid_count": sum(1 for session in group if session.get("schema_valid")),
            "correct_count": sum(1 for session in group if (session.get("comparison") or {}).get("pass")),
            "output_not_object_count": sum(1 for session in group if "OUTPUT_NOT_OBJECT" in ((session.get("comparison") or {}).get("errors") or [])),
            "tool_permission_denial_count": sum(1 for session in group if tool_permission_denial_observed(session)),
            "false_proceed_count": sum(1 for session in group if (session.get("comparison") or {}).get("false_proceed")),
        })
    return summary


def tool_permission_denial_observed(session: Mapping[str, Any]) -> bool:
    output = session.get("agent_output")
    if not isinstance(output, Mapping):
        return False
    reason_codes = {str(item) for item in output.get("reason_codes", [])}
    text_fields = []
    for key in ["spira_verdict", "blocking_items", "evidence_or_proof_references"]:
        value = output.get(key)
        if isinstance(value, str):
            text_fields.append(value)
        elif isinstance(value, list):
            text_fields.extend(str(item) for item in value)
    lowered_text = "\n".join(text_fields).lower()
    return bool({"MISSING_PERMISSIONS", "BLOCKED_BY_TOOL_DENIAL"} & reason_codes) or "permission denied" in lowered_text


def finalize(started_at: str, sessions: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    terminal = (
        "CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE"
        if not errors and len(sessions) == 30
        else "CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INCOMPLETE"
    )
    cell_summary = summarize_by_cell(sessions)
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "UNSCORED_DIAGNOSTIC_SESSIONS_ONLY",
            "PRIMARY_BENCHMARK_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": readiness.utc_now(),
        "requested_model": readiness.REQUESTED_MODEL,
        "claude_code_version": readiness.run_local([readiness.resolve_claude(), "--version"]),
        "claude_launcher_sha256": readiness.file_sha256(Path(readiness.resolve_claude())),
        "session_count": len(sessions),
        "sessions_completed": sum(1 for session in sessions if session.get("returncode") == 0),
        "schema_valid_count": sum(1 for session in sessions if session.get("schema_valid")),
        "correct_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("pass")),
        "output_not_object_count": sum(1 for session in sessions if "OUTPUT_NOT_OBJECT" in ((session.get("comparison") or {}).get("errors") or [])),
        "tool_permission_denial_count": sum(1 for session in sessions if tool_permission_denial_observed(session)),
        "false_proceed_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("false_proceed")),
        "usage_available_count": sum(1 for session in sessions if (session.get("usage") or {}).get("input_total_available")),
        "workspace_mutation_count": sum(1 for session in sessions if session.get("workspace_mutated")),
        "forbidden_tool_count": sum(int(session.get("forbidden_tool_count", 0)) for session in sessions),
        "new_live_sessions": len(sessions),
        "diagnostic_scored_for_readiness": False,
        "primary_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "errors": errors,
        "cell_summary": cell_summary,
        "sessions": sessions,
        "raw_private_manifest": {
            "schema": "SPIRA_CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    rows = "\n".join(
        "- {domain} {case_id} arm {arm} {diagnostic_role}: correct={correct_count}/{session_count} schema={schema_valid_count}/{session_count} output_not_object={output_not_object_count} tool_permission_denial={tool_permission_denial_count}".format(**cell)
        for cell in results.get("cell_summary", [])
    )
    errors = "\n".join(f"- {error}" for error in results.get("errors", [])) or "- none"
    return f"""# Claude Native Readiness Reliability Diagnostic Report

## Status

```text
{results['terminal_status']}
UNSCORED_DIAGNOSTIC_SESSIONS_ONLY
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: {results['requested_model']}
session count: {results['session_count']}
schema valid: {results['schema_valid_count']} / 30
correct: {results['correct_count']} / 30
usage available: {results['usage_available_count']} / 30
OUTPUT_NOT_OBJECT: {results['output_not_object_count']}
tool permission denials: {results['tool_permission_denial_count']}
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_count']}
```

## Cell Summary

{rows}

## Errors

{errors}

## Boundary

```text
These are unscored diagnostic sessions.
Primary, holdout, and carryover benchmark sessions were not started.
No readiness acceptance is granted by this diagnostic.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
