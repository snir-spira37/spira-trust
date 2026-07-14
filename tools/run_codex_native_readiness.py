from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import run_claude_native_readiness as shared


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
TRACK_ROOT = BENCHMARK_ROOT / "codex_native"
AUTHORIZATION_PATH = TRACK_ROOT / "codex_native_readiness_authorization.md"
RESULTS_PATH = TRACK_ROOT / "codex_native_readiness_results.json"
REPORT_PATH = TRACK_ROOT / "codex_native_readiness_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "codex_native_readiness_raw_private_manifest.json"
REVIEW_PATH = TRACK_ROOT / "codex_native_readiness_review.md"
INPUT_MANIFEST_PATH = BENCHMARK_ROOT / "frozen_input_manifest.json"
CASE_MANIFEST_PATH = BENCHMARK_ROOT / "case_manifest.json"
OUTPUT_SCHEMA_PATH = BENCHMARK_ROOT / "agent_output.schema.json"

REQUESTED_MODEL = "gpt-5.5"
REASONING_EFFORT = "xhigh"
CODEX_EXE = Path(os.environ.get("CODEX_CLI_PATH") or Path.home() / "AppData" / "Local" / "OpenAI" / "Codex" / "bin" / "codex.exe")
PRIVATE_ROOT_PREFIX = "spira_codex_native_readiness_private_"
SAFE_READ_COMMAND_MARKERS = (
    "Get-Content",
    "Select-String",
    "Test-Path",
    "Get-ChildItem",
    "type ",
    "dir ",
)
FORBIDDEN_COMMAND_MARKERS = (
    "Set-Content",
    "Out-File",
    "Add-Content",
    "New-Item",
    "Remove-Item",
    "Move-Item",
    "Copy-Item",
    "Invoke-WebRequest",
    "Invoke-RestMethod",
    "curl",
    "wget",
    "git ",
    "python ",
    "node ",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Codex native nine-session readiness only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_readiness(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    REVIEW_PATH.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CODEX_NATIVE_READINESS_PASS" else 1


def run_readiness(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = utc_now()
    raw_manifest: list[dict[str, Any]] = []
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if _is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, [], raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    selected = readiness_inputs()
    case_expectations = expected_by_case()
    schema = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    transport_schema = codex_transport_schema(schema)
    sessions: list[dict[str, Any]] = []
    pre_repo_state = repository_state()
    technical_errors = technical_readiness_errors()
    if technical_errors:
        return finalize(started_at, sessions, raw_manifest, technical_errors)
    for item in selected:
        sessions.append(
            run_session(item, case_expectations[(item["domain"], item["case_id"])], schema, transport_schema, private_root, raw_manifest)
        )
    errors = readiness_errors(sessions)
    if repository_state() != pre_repo_state:
        errors.append("CODEX_NATIVE_READINESS_REPOSITORY_MUTATION_OBSERVED")
    return finalize(started_at, sessions, raw_manifest, sorted(set(errors)))


def readiness_inputs() -> list[dict[str, Any]]:
    manifest = json.loads(INPUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    selected = [item for item in manifest["inputs"] if item.get("readiness_selected") is True]
    selected.sort(key=lambda item: (item["domain"], item["case_id"], item["arm"]))
    if len(selected) != 9:
        raise RuntimeError(f"Expected 9 readiness inputs, found {len(selected)}")
    return selected


def expected_by_case() -> dict[tuple[str, str], dict[str, Any]]:
    manifest = json.loads(CASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {(case["domain"], case["case_id"]): case for case in manifest["cases"]}


def run_session(
    item: Mapping[str, Any],
    expected: Mapping[str, Any],
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    workspace = Path(tempfile.mkdtemp(prefix="spira_codex_native_readiness_ws_"))
    input_path = ROOT / item["path"]
    frozen_bytes = input_path.read_bytes()
    workspace_input = workspace / "frozen_input.json"
    workspace_input.write_bytes(frozen_bytes)
    schema_path = workspace / "agent_output_transport.schema.json"
    schema_path.write_text(json.dumps(transport_schema, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    pre_digest = shared.directory_digest(workspace)
    prompt = (
        "You are running a SPIRA Codex Native readiness session. Read "
        "frozen_input.json in the current working directory. Then follow the "
        "system_prompt and user_prompt contained in that file. Return only JSON "
        "matching the output_schema contained in that file. Do not use web, write, "
        "network, subagents, or files outside this workspace."
    )
    try:
        result = run_codex(prompt=prompt, workspace=workspace, schema_path=schema_path)
    finally:
        post_digest = shared.directory_digest(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_raw_pair(private_root, raw_manifest, raw_name(item), result)
    events = parse_json_lines(result.stdout)
    output = extract_agent_output(events)
    tools = tool_calls_from_events(events)
    forbidden = forbidden_tools_present(tools)
    schema_errors = shared.validate_output_schema(output, schema)
    comparison = shared.compare_to_expected(output, expected)
    usage = extract_usage(events)
    ready = (
        result.returncode == 0
        and not schema_errors
        and pre_digest == post_digest
        and not forbidden
        and usage.get("input_total_available")
        and (comparison["pass"] if item["arm"] in {"B", "C"} else arm_a_operational_pass({"comparison": comparison}))
    )
    return {
        "session_id": thread_id_from_events(events) or result.session_id,
        "domain": item["domain"],
        "case_id": item["case_id"],
        "arm": item["arm"],
        "input_path": item["path"],
        "input_sha256_expected": item["input_sha256"],
        "input_sha256_actual": shared.sha256(frozen_bytes),
        "input_sha256_match": shared.sha256(frozen_bytes) == item["input_sha256"],
        "prompt_sha256": item.get("prompt_sha256"),
        "returncode": result.returncode,
        "raw_private_id": raw_id,
        "output_found": isinstance(output, dict),
        "schema_transport": "CODEX_OUTPUT_SCHEMA_WITH_UNIQUEITEMS_REMOVED_LOCAL_VALIDATION_ENFORCED",
        "schema_transport_semantics_changed": False,
        "transport_schema_weakened_for_provider": True,
        "local_schema_validation_enforced": True,
        "result_envelope_present": result_envelope_present(events),
        "structured_output_present": isinstance(output, dict),
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "comparison": comparison,
        "ready": ready,
        "agent_output": output if isinstance(output, dict) else None,
        "usage": usage,
        "tools_observed": tools,
        "forbidden_tool_count": len(forbidden),
        "forbidden_tools_observed": forbidden,
        "workspace_mutated": pre_digest != post_digest,
        "stdout_byte_size": len(result.stdout),
        "stderr_byte_size": len(result.stderr),
        "stdout_sha256": shared.sha256(result.stdout),
        "stderr_sha256": shared.sha256(result.stderr),
    }


class CodexRunResult:
    def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, session_id: str) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.session_id = session_id


def run_codex(*, prompt: str, workspace: Path, schema_path: Path) -> CodexRunResult:
    session_id = str(uuid.uuid4())
    cmd = [
        str(CODEX_EXE),
        "--ask-for-approval",
        "never",
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--cd",
        str(workspace),
        "--sandbox",
        "read-only",
        "--model",
        REQUESTED_MODEL,
        "-c",
        f'model_reasoning_effort="{REASONING_EFFORT}"',
        "--output-schema",
        str(schema_path),
        prompt,
    ]
    env = os.environ.copy()
    env["CODEX_CLI_PATH"] = str(CODEX_EXE)
    try:
        completed = subprocess.run(
            cmd,
            shell=False,
            cwd=str(workspace),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=240,
        )
        return CodexRunResult(stdout=completed.stdout, stderr=completed.stderr, returncode=completed.returncode, session_id=session_id)
    except subprocess.TimeoutExpired as exc:
        return CodexRunResult(stdout=exc.stdout or b"", stderr=exc.stderr or b"timeout", returncode=124, session_id=session_id)


def parse_json_lines(data: bytes) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def extract_agent_output(events: Iterable[Mapping[str, Any]]) -> Any:
    for event in events:
        item = event.get("item")
        if isinstance(item, Mapping) and item.get("type") == "agent_message":
            text = item.get("text")
            if isinstance(text, str):
                try:
                    return json.loads(shared.strip_code_fence(text.strip()))
                except Exception:
                    return None
    return None


def result_envelope_present(events: list[Mapping[str, Any]]) -> bool:
    return any(event.get("type") == "thread.started" for event in events) and any(event.get("type") == "turn.completed" for event in events)


def thread_id_from_events(events: Iterable[Mapping[str, Any]]) -> str | None:
    for event in events:
        if event.get("type") == "thread.started" and isinstance(event.get("thread_id"), str):
            return str(event["thread_id"])
    return None


def extract_usage(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    for event in events:
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), Mapping):
            usage = event["usage"]
            input_tokens = usage.get("input_tokens")
            cached_input_tokens = usage.get("cached_input_tokens")
            output_tokens = usage.get("output_tokens")
            reasoning_output_tokens = usage.get("reasoning_output_tokens")
            return {
                "input_tokens": input_tokens if isinstance(input_tokens, int) else None,
                "cached_input_tokens": cached_input_tokens if isinstance(cached_input_tokens, int) else None,
                "output_tokens": output_tokens if isinstance(output_tokens, int) else None,
                "reasoning_output_tokens": reasoning_output_tokens if isinstance(reasoning_output_tokens, int) else None,
                "input_total_available": isinstance(input_tokens, int),
                "usage_source": "turn.completed.usage",
            }
    return {
        "input_tokens": None,
        "cached_input_tokens": None,
        "output_tokens": None,
        "reasoning_output_tokens": None,
        "input_total_available": False,
        "usage_source": "NOT_AVAILABLE",
    }


def tool_calls_from_events(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for event in events:
        item = event.get("item")
        if isinstance(item, Mapping) and item.get("type") == "command_execution":
            tools.append(
                {
                    "type": "command_execution",
                    "command": item.get("command"),
                    "exit_code": item.get("exit_code"),
                    "status": item.get("status"),
                    "read_only_classification": classify_command(str(item.get("command") or "")),
                }
            )
    return tools


def classify_command(command: str) -> str:
    lowered = command.lower()
    if any(marker.lower() in lowered for marker in FORBIDDEN_COMMAND_MARKERS):
        return "FORBIDDEN"
    if any(marker.lower() in lowered for marker in SAFE_READ_COMMAND_MARKERS):
        return "READ_ONLY"
    return "UNKNOWN"


def forbidden_tools_present(tools: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [tool for tool in tools if tool.get("read_only_classification") != "READ_ONLY"]


def technical_readiness_errors() -> list[str]:
    errors: list[str] = []
    if not CODEX_EXE.exists():
        errors.append("CODEX_CLI_EXECUTABLE_NOT_FOUND")
        return errors
    version = run_local([str(CODEX_EXE), "--version"])
    if "codex-cli" not in version:
        errors.append("CODEX_CLI_VERSION_NOT_CONFIRMED")
    catalog = run_local([str(CODEX_EXE), "debug", "models", "-c", f'model="{REQUESTED_MODEL}"', "-c", f'model_reasoning_effort="{REASONING_EFFORT}"'])
    if f'"slug":"{REQUESTED_MODEL}"' not in catalog:
        errors.append("CODEX_MODEL_ID_NOT_CONFIRMED")
    if f'"effort":"{REASONING_EFFORT}"' not in catalog:
        errors.append("CODEX_REASONING_EFFORT_NOT_CONFIRMED")
    return errors


def readiness_errors(sessions: list[Mapping[str, Any]]) -> list[str]:
    errors: list[str] = []
    if len(sessions) != 9:
        errors.append("CODEX_NATIVE_READINESS_INCOMPLETE")
    if any(session.get("arm") in {"B", "C"} and not session.get("ready") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_NEEDS_REVISION")
    if any(session.get("arm") == "A" and not arm_a_operational_pass(session) for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_ARM_A_OPERATIONAL_FAILURE")
    if any((session.get("comparison") or {}).get("false_proceed") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_FALSE_PROCEED")
    if any(session.get("workspace_mutated") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_WORKSPACE_MUTATION")
    if any(int(session.get("forbidden_tool_count", 0)) for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_FORBIDDEN_TOOL")
    if any(not (session.get("usage") or {}).get("input_total_available") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_USAGE_NOT_AVAILABLE")
    if any(not session.get("result_envelope_present") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_RESULT_ENVELOPE_MISSING")
    if any(not session.get("structured_output_present") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_STRUCTURED_OUTPUT_MISSING")
    if any(not session.get("schema_valid") for session in sessions):
        errors.append("CODEX_NATIVE_READINESS_SCHEMA_INVALID")
    return errors


def finalize(started_at: str, sessions: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    technical_blocked = any(error.startswith("CODEX_") and "NOT_CONFIRMED" in error or error == "CODEX_CLI_EXECUTABLE_NOT_FOUND" for error in errors)
    terminal = "CODEX_NATIVE_READINESS_PASS" if not errors and len(sessions) == 9 else (
        "CODEX_NATIVE_TECHNICAL_READINESS_NOT_READY" if technical_blocked else (
            "CODEX_NATIVE_READINESS_INCOMPLETE" if len(sessions) != 9 else "CODEX_NATIVE_CONTRACT_READINESS_NOT_READY"
        )
    )
    return {
        "schema": "SPIRA_CODEX_NATIVE_READINESS_RESULTS_V1",
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
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "resolved_model_id": REQUESTED_MODEL,
        "model_identity_source": "codex debug models catalog slug and successful codex exec invocation",
        "reasoning_effort": REASONING_EFFORT,
        "codex_cli_version": run_local([str(CODEX_EXE), "--version"]) if CODEX_EXE.exists() else "NOT_AVAILABLE",
        "codex_cli_invocation_identity": "LOCAL_OPENAI_CODEX_BIN/codex.exe",
        "codex_cli_sha256": file_sha256(CODEX_EXE) if CODEX_EXE.exists() else "NOT_AVAILABLE",
        "platform": platform.platform(),
        "session_count": len(sessions),
        "sessions_completed": sum(1 for session in sessions if session.get("returncode") == 0),
        "schema_valid_count": sum(1 for session in sessions if session.get("schema_valid")),
        "correct_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("pass")),
        "arm_b_strict_count": sum(1 for session in sessions if session.get("arm") == "B" and (session.get("comparison") or {}).get("pass")),
        "arm_c_strict_count": sum(1 for session in sessions if session.get("arm") == "C" and (session.get("comparison") or {}).get("pass")),
        "arm_a_operational_pass_count": sum(1 for session in sessions if session.get("arm") == "A" and arm_a_operational_pass(session)),
        "result_envelope_count": sum(1 for session in sessions if session.get("result_envelope_present")),
        "structured_output_count": sum(1 for session in sessions if session.get("structured_output_present")),
        "false_proceed_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("false_proceed")),
        "usage_available_count": sum(1 for session in sessions if (session.get("usage") or {}).get("input_total_available")),
        "workspace_mutation_count": sum(1 for session in sessions if session.get("workspace_mutated")),
        "forbidden_tool_count": sum(int(session.get("forbidden_tool_count", 0)) for session in sessions),
        "benchmark_cases_sent_to_model": len(sessions),
        "primary_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "errors": errors,
        "sessions": sessions,
        "raw_private_manifest": {
            "schema": "SPIRA_CODEX_NATIVE_READINESS_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def arm_a_operational_pass(session: Mapping[str, Any]) -> bool:
    comp = session.get("comparison") or {}
    checks = comp.get("checks") or {}
    return bool(checks.get("gate")) and bool(checks.get("recommended_agent_action")) and not comp.get("false_proceed")


def report_markdown(results: Mapping[str, Any]) -> str:
    lines = "\n".join(
        f"- {s['domain']} {s['case_id']} arm {s['arm']}: ready={s['ready']} schema={s['schema_valid']} correct={(s.get('comparison') or {}).get('pass')} rc={s['returncode']}"
        for s in results.get("sessions", [])
    )
    errors = "\n".join(f"- {e}" for e in results.get("errors", [])) or "- none"
    return f"""# Codex Native Readiness Report

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
requested model: {results['requested_model']}
resolved model ID: {results['resolved_model_id']}
reasoning effort: {results['reasoning_effort']}
Codex CLI: {results['codex_cli_version']}
session count: {results['session_count']}
schema valid: {results['schema_valid_count']} / 9
correct: {results['correct_count']} / 9
Arm B strict: {results['arm_b_strict_count']} / 3
Arm C strict: {results['arm_c_strict_count']} / 3
Arm A operational pass: {results['arm_a_operational_pass_count']} / 3
JSONL result envelope: {results['result_envelope_count']} / 9
structured output: {results['structured_output_count']} / 9
usage available: {results['usage_available_count']} / 9
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_count']}
```

## Sessions

{lines}

## Errors

{errors}

## Boundary

```text
Only the 9 authorized Codex readiness sessions were executed.
Codex primary, holdout, and carryover benchmark sessions were not started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = (
        results.get("terminal_status") == "CODEX_NATIVE_READINESS_PASS"
        and results.get("arm_b_strict_count") == 3
        and results.get("arm_c_strict_count") == 3
        and results.get("false_proceed_count") == 0
        and results.get("usage_available_count") == 9
        and results.get("workspace_mutation_count") == 0
        and results.get("forbidden_tool_count") == 0
    )
    verdict = "CODEX_NATIVE_READINESS_ACCEPTED" if accepted else (
        "CODEX_NATIVE_TECHNICAL_READINESS_NOT_READY" if results.get("terminal_status") == "CODEX_NATIVE_TECHNICAL_READINESS_NOT_READY" else "CODEX_NATIVE_CONTRACT_READINESS_NOT_READY"
    )
    mismatch_lines = []
    for session in results.get("sessions", []):
        comp = session.get("comparison") or {}
        if not comp.get("pass"):
            mismatch_lines.append(
                f"- {session['domain']} {session['case_id']} arm {session['arm']}: errors={comp.get('errors')} false_proceed={comp.get('false_proceed')}"
            )
    mismatches = "\n".join(mismatch_lines) or "- none"
    primary_status = "CODEX_PRIMARY_AUTHORIZATION_REQUIRED_NEXT" if accepted else "CODEX_PRIMARY_NOT_AUTHORIZED"
    return f"""# Codex Native Readiness Review

## Status

```text
{verdict}
{primary_status}
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_authorization.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_results.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_report.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_raw_private_manifest.json
```

## Summary

```text
sessions: {results['session_count']} / 9
schema valid: {results['schema_valid_count']} / 9
usage available: {results['usage_available_count']} / 9
Arm B strict: {results['arm_b_strict_count']} / 3
Arm C strict: {results['arm_c_strict_count']} / 3
Arm A operational pass: {results['arm_a_operational_pass_count']} / 3
false PROCEED: {results['false_proceed_count']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_count']}
```

## Mismatches

{mismatches}

## Decision

The Codex primary benchmark remains unauthorized unless this review status is:

```text
CODEX_NATIVE_READINESS_ACCEPTED
```

and a separate primary benchmark authorization is committed.
"""


def codex_transport_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    def strip(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {k: strip(v) for k, v in value.items() if k not in {"$schema", "uniqueItems", "title"}}
        if isinstance(value, list):
            return [strip(item) for item in value]
        return value

    return strip(json.loads(json.dumps(schema)))


def raw_name(item: Mapping[str, Any]) -> str:
    return f"{item['domain']}__{item['case_id']}__{item['arm']}"


def record_raw_pair(private_root: Path, raw_manifest: list[dict[str, Any]], name: str, result: CodexRunResult) -> str:
    raw_id = str(uuid.uuid4())
    stdout_path = private_root / f"{raw_id}.stdout.jsonl"
    stderr_path = private_root / f"{raw_id}.stderr.txt"
    stdout_path.write_bytes(result.stdout)
    stderr_path.write_bytes(result.stderr)
    raw_manifest.append(
        {
            "raw_private_id": raw_id,
            "logical_name": name,
            "stdout_sha256": shared.sha256(result.stdout),
            "stderr_sha256": shared.sha256(result.stderr),
            "stdout_byte_size": len(result.stdout),
            "stderr_byte_size": len(result.stderr),
            "stored_outside_repository": True,
        }
    )
    return raw_id


def technical_model_catalog_excerpt() -> str:
    return run_local([str(CODEX_EXE), "debug", "models", "-c", f'model="{REQUESTED_MODEL}"', "-c", f'model_reasoning_effort="{REASONING_EFFORT}"'])


def run_local(cmd: list[str]) -> str:
    try:
        completed = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
    except Exception as exc:
        return f"ERROR:{exc}"
    return (completed.stdout or completed.stderr).decode("utf-8", errors="replace").strip()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def repository_state() -> str:
    return run_local(["git", "status", "--short"])


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
