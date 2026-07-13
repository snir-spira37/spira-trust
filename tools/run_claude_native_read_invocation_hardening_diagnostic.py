from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Mapping

import run_claude_native_readiness as readiness
from run_claude_native_reliability_diagnostic import tool_permission_denial_observed


ROOT = readiness.ROOT
TRACK_ROOT = readiness.TRACK_ROOT
RESULTS_PATH = TRACK_ROOT / "claude_native_read_invocation_hardening_diagnostic_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_read_invocation_hardening_diagnostic_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_read_invocation_hardening_diagnostic_raw_private_manifest.json"
PRIVATE_ROOT_PREFIX = "spira_claude_native_read_hardening_private_"
ALLOWED_TOOLS = "Read,Glob,Grep"


class ClaudeRunResult:
    def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, session_id: str) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.session_id = session_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Claude native read-invocation hardening diagnostic only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_diagnostic(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_PASS" else 1


def run_diagnostic(*, private_root: Path | None = None) -> dict[str, Any]:
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

    for repeat in range(1, 6):
        sessions.append(run_nonce_probe(repeat, schema, transport_schema, private_root, raw_manifest))

    plan = benchmark_plan()
    for planned in plan:
        item = planned["item"]
        sessions.append(
            run_benchmark_session(
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

    errors = diagnostic_errors(sessions)
    if readiness.repository_state() != pre_repo_state:
        errors.append("CLAUDE_NATIVE_READ_HARDENING_REPOSITORY_MUTATION_OBSERVED")
    return finalize(started_at, sessions, raw_manifest, sorted(set(errors)))


def benchmark_plan() -> list[dict[str, Any]]:
    by_key = {(item["domain"], item["case_id"], item["arm"]): item for item in readiness.readiness_inputs()}
    cells = [
        ("CRITICAL_ARM_B", ("pytest_result", "synthetic_clean_success", "B"), 10),
        ("MATCHED_ARM_C", ("pytest_result", "synthetic_clean_success", "C"), 5),
    ]
    plan: list[dict[str, Any]] = []
    for role, key, count in cells:
        for repeat_index in range(1, count + 1):
            plan.append({"role": role, "repeat_index": repeat_index, "item": by_key[key]})
    if len(plan) != 15:
        raise RuntimeError(f"Expected 15 benchmark diagnostic sessions, found {len(plan)}")
    return plan


def run_nonce_probe(
    repeat_index: int,
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    workspace = Path(tempfile.mkdtemp(prefix="spira_claude_native_read_nonce_ws_"))
    nonce = f"SPIRA_READ_NONCE_{uuid.uuid4().hex}"
    (workspace / "nonce.txt").write_text(nonce + "\n", encoding="utf-8")
    pre_digest = readiness.directory_digest(workspace)
    prompt = (
        "Use the Read tool to read nonce.txt in the current working directory. "
        "Then return only JSON matching the provided schema. If the nonce was read, "
        "set gate to PROCEED, recommended_agent_action to PROCEED, include reason_codes "
        "[\"READ_NONCE_CONFIRMED\"], empty not_evaluated/blocking_items arrays, include "
        "the nonce value in evidence_or_proof_references, and include no private paths."
    )
    try:
        result = run_claude_hardened(prompt=prompt, workspace=workspace, schema=transport_schema)
    finally:
        post_digest = readiness.directory_digest(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = readiness.record_raw_pair(private_root, raw_manifest, f"read-nonce-{repeat_index}", result)
    parsed = readiness.parse_json(result.stdout)
    output = readiness.extract_agent_output(parsed)
    events = readiness.parse_json_lines(result.stdout)
    tools = readiness.tool_calls_from_value(events if events else parsed)
    forbidden = readiness.forbidden_tools_present(tools)
    schema_errors = readiness.validate_output_schema(output, schema)
    output_for_public = sanitize_value(output) if isinstance(output, Mapping) else None
    nonce_confirmed = isinstance(output, Mapping) and nonce in json.dumps(output)
    permission_denial = tool_permission_denial_observed({"agent_output": output}) or raw_permission_denial_present(parsed)
    return {
        "session_id": result.session_id,
        "diagnostic_role": "READ_NONCE_TECHNICAL_PROBE",
        "diagnostic_repeat_index": repeat_index,
        "domain": "technical_probe",
        "case_id": "read_nonce",
        "arm": "N/A",
        "returncode": result.returncode,
        "raw_private_id": raw_id,
        "output_found": isinstance(output, dict),
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "nonce_confirmed": nonce_confirmed,
        "comparison": {
            "pass": nonce_confirmed and result.returncode == 0 and not schema_errors and not permission_denial,
            "errors": [] if nonce_confirmed and result.returncode == 0 and not schema_errors and not permission_denial else ["READ_NONCE_NOT_CONFIRMED"],
            "false_proceed": False,
        },
        "ready": nonce_confirmed and result.returncode == 0 and not schema_errors and pre_digest == post_digest and not forbidden and not permission_denial,
        "agent_output": output_for_public,
        "usage": readiness.extract_usage(parsed),
        "tools_observed": sorted(tools),
        "permission_denial_observed": permission_denial,
        "forbidden_tool_count": len(forbidden),
        "workspace_mutated": pre_digest != post_digest,
        "stdout_byte_size": len(result.stdout),
        "stderr_byte_size": len(result.stderr),
        "stdout_sha256": readiness.sha256(result.stdout),
        "stderr_sha256": readiness.sha256(result.stderr),
    }


def run_benchmark_session(
    item: Mapping[str, Any],
    expected: Mapping[str, Any],
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
    role: str,
    repeat_index: int,
) -> dict[str, Any]:
    workspace = Path(tempfile.mkdtemp(prefix="spira_claude_native_read_hardening_ws_"))
    input_path = ROOT / item["path"]
    frozen_bytes = input_path.read_bytes()
    (workspace / "frozen_input.json").write_bytes(frozen_bytes)
    pre_digest = readiness.directory_digest(workspace)
    prompt = (
        "You are running a SPIRA readiness session. Use the Read tool to read "
        "frozen_input.json in the current working directory. Then follow the "
        "system_prompt and user_prompt contained in that file. Return only JSON "
        "matching the output_schema contained in that file. Do not use web, write, "
        "shell, subagents, or files outside this workspace."
    )
    try:
        result = run_claude_hardened(prompt=prompt, workspace=workspace, schema=transport_schema)
    finally:
        post_digest = readiness.directory_digest(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = readiness.record_raw_pair(private_root, raw_manifest, f"{role.lower()}-{item['domain']}-{item['case_id']}-arm-{item['arm']}-{repeat_index}", result)
    parsed = readiness.parse_json(result.stdout)
    output = readiness.extract_agent_output(parsed)
    events = readiness.parse_json_lines(result.stdout)
    tools = readiness.tool_calls_from_value(events if events else parsed)
    forbidden = readiness.forbidden_tools_present(tools)
    schema_errors = readiness.validate_output_schema(output, schema)
    comparison = readiness.compare_to_expected(output, expected)
    permission_denial = tool_permission_denial_observed({"agent_output": output}) or raw_permission_denial_present(parsed)
    return {
        "session_id": result.session_id,
        "diagnostic_role": role,
        "diagnostic_repeat_index": repeat_index,
        "domain": item["domain"],
        "case_id": item["case_id"],
        "arm": item["arm"],
        "input_sha256_match": readiness.sha256(frozen_bytes) == item["input_sha256"],
        "prompt_sha256": item.get("prompt_sha256"),
        "returncode": result.returncode,
        "raw_private_id": raw_id,
        "output_found": isinstance(output, dict),
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "comparison": comparison,
        "ready": result.returncode == 0 and not schema_errors and comparison["pass"] and pre_digest == post_digest and not forbidden and not permission_denial,
        "agent_output": sanitize_value(output) if isinstance(output, Mapping) else None,
        "usage": readiness.extract_usage(parsed),
        "tools_observed": sorted(tools),
        "permission_denial_observed": permission_denial,
        "forbidden_tool_count": len(forbidden),
        "workspace_mutated": pre_digest != post_digest,
        "stdout_byte_size": len(result.stdout),
        "stderr_byte_size": len(result.stderr),
        "stdout_sha256": readiness.sha256(result.stdout),
        "stderr_sha256": readiness.sha256(result.stderr),
    }


def run_claude_hardened(*, prompt: str, workspace: Path, schema: Mapping[str, Any]) -> ClaudeRunResult:
    session_id = str(uuid.uuid4())
    cmd = [
        readiness.resolve_claude(),
        "--print",
        "--no-session-persistence",
        "--session-id",
        session_id,
        "--model",
        readiness.REQUESTED_MODEL,
        "--permission-mode",
        "dontAsk",
        "--tools",
        "Read,Glob,Grep",
        "--allowedTools",
        ALLOWED_TOOLS,
        "--disallowedTools",
        "Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--max-turns",
        "6",
        "--json-schema",
        readiness.canonical_json(schema),
        prompt,
    ]
    env = os.environ.copy()
    env.update({"CLAUDE_CODE_SKIP_PROMPT_HISTORY": "1"})
    for key in [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CLAUDE_CODE_SUBAGENT_MODEL",
    ]:
        env.pop(key, None)
    try:
        completed = subprocess.run(
            cmd,
            shell=False,
            cwd=str(workspace),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=180,
        )
        return ClaudeRunResult(stdout=completed.stdout, stderr=completed.stderr, returncode=completed.returncode, session_id=session_id)
    except subprocess.TimeoutExpired as exc:
        return ClaudeRunResult(stdout=exc.stdout or b"", stderr=exc.stderr or b"timeout", returncode=124, session_id=session_id)


def raw_permission_denial_present(parsed: Any) -> bool:
    return isinstance(parsed, Mapping) and bool(parsed.get("permission_denials"))


def sanitize_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): sanitize_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_value(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"[A-Za-z]:\\[^\n\r\"']+", "<REDACTED_LOCAL_PATH>", value)
    return value


def diagnostic_errors(sessions: list[Mapping[str, Any]]) -> list[str]:
    errors = []
    if len(sessions) != 20:
        errors.append("CLAUDE_NATIVE_READ_HARDENING_INCOMPLETE")
    if any(session.get("permission_denial_observed") for session in sessions):
        errors.append("CLAUDE_NATIVE_READ_HARDENING_PERMISSION_DENIAL_OBSERVED")
    if any(session.get("workspace_mutated") for session in sessions):
        errors.append("CLAUDE_NATIVE_READ_HARDENING_WORKSPACE_MUTATION")
    if any(int(session.get("forbidden_tool_count", 0)) for session in sessions):
        errors.append("CLAUDE_NATIVE_READ_HARDENING_FORBIDDEN_TOOL")
    if any(not (session.get("usage") or {}).get("input_total_available") for session in sessions):
        errors.append("CLAUDE_NATIVE_READ_HARDENING_USAGE_NOT_AVAILABLE")
    roles = {
        "READ_NONCE_TECHNICAL_PROBE": 5,
        "CRITICAL_ARM_B": 10,
        "MATCHED_ARM_C": 5,
    }
    for role, expected_count in roles.items():
        group = [session for session in sessions if session.get("diagnostic_role") == role]
        if len(group) != expected_count or any(not session.get("ready") for session in group):
            errors.append(f"CLAUDE_NATIVE_READ_HARDENING_{role}_NOT_EXACT")
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
            "usage_available_count": sum(1 for session in group if (session.get("usage") or {}).get("input_total_available")),
            "permission_denial_count": sum(1 for session in group if session.get("permission_denial_observed")),
            "false_proceed_count": sum(1 for session in group if (session.get("comparison") or {}).get("false_proceed")),
        })
    return summary


def finalize(started_at: str, sessions: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    terminal = "CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_PASS" if not errors and len(sessions) == 20 else "CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_NEEDS_REVISION"
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_RESULTS_V1",
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
        "allowed_tools_added": ALLOWED_TOOLS,
        "allowed_tools_syntax_confirmed_by_help": True,
        "session_count": len(sessions),
        "schema_valid_count": sum(1 for session in sessions if session.get("schema_valid")),
        "exact_count": sum(1 for session in sessions if session.get("ready")),
        "usage_available_count": sum(1 for session in sessions if (session.get("usage") or {}).get("input_total_available")),
        "permission_denial_count": sum(1 for session in sessions if session.get("permission_denial_observed")),
        "false_proceed_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("false_proceed")),
        "workspace_mutation_count": sum(1 for session in sessions if session.get("workspace_mutated")),
        "forbidden_tool_count": sum(int(session.get("forbidden_tool_count", 0)) for session in sessions),
        "repository_mutation_observed": "CLAUDE_NATIVE_READ_HARDENING_REPOSITORY_MUTATION_OBSERVED" in errors,
        "diagnostic_scored_for_readiness": False,
        "primary_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "errors": errors,
        "cell_summary": summarize_by_cell(sessions),
        "sessions": sessions,
        "raw_private_manifest": {
            "schema": "SPIRA_CLAUDE_NATIVE_READ_INVOCATION_HARDENING_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    rows = "\n".join(
        "- {domain} {case_id} arm {arm} {diagnostic_role}: exact={exact_count}/{session_count} schema={schema_valid_count}/{session_count} permission_denials={permission_denial_count}".format(**cell)
        for cell in results.get("cell_summary", [])
    )
    errors = "\n".join(f"- {error}" for error in results.get("errors", [])) or "- none"
    return f"""# Claude Native Read Invocation Hardening Diagnostic Report

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
allowed tools added: {results['allowed_tools_added']}
session count: {results['session_count']}
schema valid: {results['schema_valid_count']} / 20
exact: {results['exact_count']} / 20
usage available: {results['usage_available_count']} / 20
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

## Boundary

```text
These are unscored hardening diagnostic sessions.
Primary, holdout, and carryover benchmark sessions were not started.
No readiness rerun is authorized by this diagnostic.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


if __name__ == "__main__":
    raise SystemExit(main())
