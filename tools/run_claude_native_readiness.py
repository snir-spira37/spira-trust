from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
TRACK_ROOT = BENCHMARK_ROOT / "claude_native"
RESULTS_PATH = TRACK_ROOT / "claude_native_readiness_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_readiness_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_readiness_raw_private_manifest.json"
INPUT_MANIFEST_PATH = BENCHMARK_ROOT / "frozen_input_manifest.json"
CASE_MANIFEST_PATH = BENCHMARK_ROOT / "case_manifest.json"
OUTPUT_SCHEMA_PATH = BENCHMARK_ROOT / "agent_output.schema.json"

REQUESTED_MODEL = "haiku"
PRIVATE_ROOT_PREFIX = "spira_claude_native_readiness_private_"
FORBIDDEN_TOOL_NAMES = {
    "bash",
    "edit",
    "write",
    "notebookedit",
    "websearch",
    "webfetch",
    "chrome",
    "agent",
    "task",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Claude native nine-session readiness only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_readiness(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_READINESS_PASS" else 1


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
    transport_schema = claude_transport_schema(schema)
    sessions: list[dict[str, Any]] = []
    pre_repo_state = repository_state()
    for item in selected:
        sessions.append(
            run_session(item, case_expectations[(item["domain"], item["case_id"])], schema, transport_schema, private_root, raw_manifest)
        )
    errors = readiness_errors(sessions)
    if repository_state() != pre_repo_state:
        errors.append("CLAUDE_NATIVE_READINESS_REPOSITORY_MUTATION_OBSERVED")
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
    out = {}
    for case in manifest["cases"]:
        out[(case["domain"], case["case_id"])] = case
    return out


def run_session(
    item: Mapping[str, Any],
    expected: Mapping[str, Any],
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
) -> dict[str, Any]:
    workspace = Path(tempfile.mkdtemp(prefix="spira_claude_native_readiness_ws_"))
    input_path = ROOT / item["path"]
    frozen_bytes = input_path.read_bytes()
    workspace_input = workspace / "frozen_input.json"
    workspace_input.write_bytes(frozen_bytes)
    pre_digest = directory_digest(workspace)
    prompt = (
        "You are running a SPIRA readiness session. Use the Read tool to read "
        "frozen_input.json in the current working directory. Then follow the "
        "system_prompt and user_prompt contained in that file. Return only JSON "
        "matching the output_schema contained in that file. Do not use web, write, "
        "shell, subagents, or files outside this workspace."
    )
    try:
        result = run_claude(prompt=prompt, workspace=workspace, schema=transport_schema)
    finally:
        post_digest = directory_digest(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_raw_pair(private_root, raw_manifest, raw_name(item), result)
    parsed = parse_json(result.stdout)
    output = extract_agent_output(parsed)
    events = parse_json_lines(result.stdout)
    tools = tool_calls_from_value(events if events else parsed)
    forbidden = forbidden_tools_present(tools)
    schema_errors = validate_output_schema(output, schema)
    comparison = compare_to_expected(output, expected)
    usage = extract_usage(parsed)
    return {
        "session_id": result.session_id,
        "domain": item["domain"],
        "case_id": item["case_id"],
        "arm": item["arm"],
        "input_path": item["path"],
        "input_sha256_expected": item["input_sha256"],
        "input_sha256_actual": sha256(frozen_bytes),
        "input_sha256_match": sha256(frozen_bytes) == item["input_sha256"],
        "prompt_sha256": item.get("prompt_sha256"),
        "returncode": result.returncode,
        "raw_private_id": raw_id,
        "output_found": isinstance(output, dict),
        "schema_transport": "INLINE_CANONICAL_JSON_WITHOUT_DRAFT_URI",
        "schema_transport_semantics_changed": False,
        "schema_valid": not schema_errors,
        "schema_errors": schema_errors,
        "comparison": comparison,
        "ready": result.returncode == 0 and not schema_errors and comparison["pass"] and pre_digest == post_digest and not forbidden and usage.get("input_total_available"),
        "agent_output": output if isinstance(output, dict) else None,
        "usage": usage,
        "tools_observed": sorted(tools),
        "forbidden_tool_count": len(forbidden),
        "workspace_mutated": pre_digest != post_digest,
        "stdout_byte_size": len(result.stdout),
        "stderr_byte_size": len(result.stderr),
        "stdout_sha256": sha256(result.stdout),
        "stderr_sha256": sha256(result.stderr),
    }


class ClaudeRunResult:
    def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, session_id: str) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.session_id = session_id


def run_claude(*, prompt: str, workspace: Path, schema: Mapping[str, Any]) -> ClaudeRunResult:
    session_id = str(uuid.uuid4())
    cmd = [
        resolve_claude(),
        "--print",
        "--no-session-persistence",
        "--session-id",
        session_id,
        "--model",
        REQUESTED_MODEL,
        "--permission-mode",
        "dontAsk",
        "--output-format",
        "json",
        "--tools",
        "Read,Glob,Grep",
        "--disallowedTools",
        "Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--max-turns",
        "6",
        "--json-schema",
        canonical_json(schema),
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


def compare_to_expected(output: Any, expected: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(output, Mapping):
        return {"pass": False, "errors": ["OUTPUT_NOT_OBJECT"]}
    expected_action = expected["expected_action"]["recommended_agent_action"]
    expected_gate = "STOP" if expected.get("expected_stop_state") else "PROCEED"
    checks = {
        "gate": output.get("gate") == expected_gate,
        "recommended_agent_action": output.get("recommended_agent_action") == expected_action,
        "reason_codes": sorted(output.get("reason_codes", [])) == sorted(expected.get("expected_reason_codes", [])),
        "not_evaluated": sorted(output.get("not_evaluated", [])) == sorted(expected.get("expected_not_evaluated", [])),
        "blocking_items": sorted(output.get("blocking_items", [])) == sorted(expected.get("expected_blocking_list", [])),
        "not_claimed": sorted(output.get("not_claimed", [])) == sorted(expected.get("expected_not_claimed", [])),
    }
    false_proceed = output.get("gate") == "PROCEED" and expected_gate == "STOP"
    errors = [key for key, ok in checks.items() if not ok]
    if false_proceed:
        errors.append("FALSE_PROCEED")
    return {
        "pass": not errors,
        "errors": errors,
        "false_proceed": false_proceed,
        "checks": checks,
        "expected_gate": expected_gate,
        "expected_action": expected_action,
    }


def readiness_errors(sessions: list[Mapping[str, Any]]) -> list[str]:
    errors = []
    if len(sessions) != 9:
        errors.append("CLAUDE_NATIVE_READINESS_INCOMPLETE")
    if any(not session.get("ready") for session in sessions):
        errors.append("CLAUDE_NATIVE_READINESS_NEEDS_REVISION")
    if any((session.get("comparison") or {}).get("false_proceed") for session in sessions):
        errors.append("CLAUDE_NATIVE_READINESS_FALSE_PROCEED")
    if any(session.get("workspace_mutated") for session in sessions):
        errors.append("CLAUDE_NATIVE_READINESS_WORKSPACE_MUTATION")
    if any(int(session.get("forbidden_tool_count", 0)) for session in sessions):
        errors.append("CLAUDE_NATIVE_READINESS_FORBIDDEN_TOOL")
    if any(not (session.get("usage") or {}).get("input_total_available") for session in sessions):
        errors.append("CLAUDE_NATIVE_READINESS_USAGE_NOT_AVAILABLE")
    return errors


def finalize(started_at: str, sessions: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    terminal = "CLAUDE_NATIVE_READINESS_PASS" if not errors and len(sessions) == 9 else (
        "CLAUDE_NATIVE_READINESS_INCOMPLETE" if len(sessions) != 9 else "CLAUDE_NATIVE_READINESS_NEEDS_REVISION"
    )
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_READINESS_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "PRIMARY_BENCHMARK_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "claude_code_version": run_local([resolve_claude(), "--version"]),
        "claude_launcher_sha256": file_sha256(Path(resolve_claude())),
        "session_count": len(sessions),
        "sessions_completed": sum(1 for session in sessions if session.get("returncode") == 0),
        "schema_valid_count": sum(1 for session in sessions if session.get("schema_valid")),
        "correct_count": sum(1 for session in sessions if (session.get("comparison") or {}).get("pass")),
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
            "schema": "SPIRA_CLAUDE_NATIVE_READINESS_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    lines = "\n".join(
        f"- {s['domain']} {s['case_id']} arm {s['arm']}: ready={s['ready']} schema={s['schema_valid']} correct={(s.get('comparison') or {}).get('pass')} rc={s['returncode']}"
        for s in results.get("sessions", [])
    )
    errors = "\n".join(f"- {e}" for e in results.get("errors", [])) or "- none"
    return f"""# Claude Native Readiness Report

## Status

```text
{results['terminal_status']}
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: {results['requested_model']}
session count: {results['session_count']}
schema valid: {results['schema_valid_count']} / 9
correct: {results['correct_count']} / 9
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
Only the 9 authorized readiness sessions were executed.
Primary, holdout, and carryover benchmark sessions were not started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


def validate_output_schema(output: Any, schema: Mapping[str, Any]) -> list[str]:
    errors = []
    if not isinstance(output, Mapping):
        return ["OUTPUT_NOT_OBJECT"]
    allowed = set(schema["properties"])
    required = set(schema["required"])
    extra = set(output) - allowed
    missing = required - set(output)
    if extra:
        errors.append(f"ADDITIONAL_PROPERTIES:{','.join(sorted(extra))}")
    if missing:
        errors.append(f"MISSING_REQUIRED:{','.join(sorted(missing))}")
    for key in ["reason_codes", "not_evaluated", "blocking_items", "evidence_or_proof_references", "not_claimed"]:
        if key in output and (not isinstance(output[key], list) or not all(isinstance(item, str) for item in output[key]) or len(output[key]) != len(set(output[key]))):
            errors.append(f"INVALID_STRING_ARRAY:{key}")
    if output.get("gate") not in {"PROCEED", "STOP"}:
        errors.append("INVALID_GATE")
    if output.get("recommended_agent_action") not in set(schema["properties"]["recommended_agent_action"]["enum"]):
        errors.append("INVALID_RECOMMENDED_ACTION")
    if "spira_verdict" in output and not isinstance(output["spira_verdict"], str):
        errors.append("INVALID_SPIRA_VERDICT")
    if "drilldown_used" in output and not isinstance(output["drilldown_used"], bool):
        errors.append("INVALID_DRILLDOWN_USED")
    return errors


def claude_transport_schema(schema: Mapping[str, Any]) -> dict[str, Any]:
    transported = json.loads(json.dumps(schema))
    transported.pop("$schema", None)
    return transported


def schema_transport_semantics_unchanged(original: Mapping[str, Any], transported: Mapping[str, Any]) -> bool:
    original_without_draft = json.loads(json.dumps(original))
    original_without_draft.pop("$schema", None)
    return original_without_draft == transported


def extract_agent_output(parsed: Any) -> Any:
    if isinstance(parsed, Mapping):
        result = parsed.get("result")
        if isinstance(result, str):
            result = strip_code_fence(result.strip())
            try:
                return json.loads(result)
            except Exception:
                return None
        for key in ["structured_output", "output"]:
            if isinstance(parsed.get(key), Mapping):
                return parsed[key]
        if "gate" in parsed:
            return parsed
    return None


def strip_code_fence(text: str) -> str:
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            body = parts[1]
            if body.lstrip().startswith("json"):
                body = body.lstrip()[4:]
            return body.strip()
    return text


def parse_json(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8", errors="replace"))
    except Exception:
        return None


def parse_json_lines(data: bytes) -> list[dict[str, Any]]:
    events = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except Exception:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def tool_calls_from_value(value: Any) -> set[str]:
    tools: set[str] = set()
    if isinstance(value, Mapping):
        if str(value.get("type", "")).lower() in {"tool_use", "tool_call"}:
            name = value.get("name") or value.get("tool_name")
            if name:
                tools.add(str(name))
        for item in value.values():
            tools.update(tool_calls_from_value(item))
    elif isinstance(value, list):
        for item in value:
            tools.update(tool_calls_from_value(item))
    return tools


def forbidden_tools_present(tools: Iterable[str]) -> set[str]:
    forbidden = set()
    for tool in tools:
        lowered = tool.lower()
        if lowered.startswith("mcp__") or lowered in FORBIDDEN_TOOL_NAMES:
            forbidden.add(tool)
    return forbidden


def extract_usage(value: Any) -> dict[str, Any]:
    usage = find_usage(value)
    if not usage:
        return {"input_total_available": False}
    input_tokens = first_number(usage, ["input_tokens", "input"])
    output_tokens = first_number(usage, ["output_tokens", "output"])
    cache_creation = first_number(usage, ["cache_creation_input_tokens", "cache_creation"])
    cache_read = first_number(usage, ["cache_read_input_tokens", "cache_read"])
    total = input_tokens
    if total is not None:
        total += cache_creation or 0
        total += cache_read or 0
    return {
        "input_tokens": input_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_input_tokens": total,
        "output_tokens": output_tokens,
        "total_cost_usd": first_number(usage, ["total_cost_usd", "cost_usd", "cost"]),
        "input_total_available": total is not None,
    }


def find_usage(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        for key in ["usage", "token_usage", "tokens"]:
            item = value.get(key)
            if isinstance(item, Mapping):
                return item
        for item in value.values():
            found = find_usage(item)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_usage(item)
            if found:
                return found
    return None


def first_number(value: Mapping[str, Any], keys: list[str]) -> int | float | None:
    lowered = {str(key).lower(): item for key, item in value.items()}
    for key in keys:
        item = lowered.get(key.lower())
        if isinstance(item, (int, float)) and item >= 0:
            return item
    return None


def raw_name(item: Mapping[str, Any]) -> str:
    return f"{item['domain']}-{item['case_id']}-arm-{item['arm']}"


def record_raw_pair(private_root: Path, manifest: list[dict[str, Any]], name: str, result: ClaudeRunResult) -> str:
    stdout_id = record_private_raw(private_root, manifest, f"{name}-stdout.raw", result.stdout, "CLAUDE_NATIVE_READINESS_STDOUT")
    record_private_raw(private_root, manifest, f"{name}-stderr.raw", result.stderr, "CLAUDE_NATIVE_READINESS_STDERR")
    return stdout_id


def record_private_raw(private_root: Path, manifest: list[dict[str, Any]], name: str, data: bytes, classification: str) -> str:
    raw_id = str(uuid.uuid4())
    (private_root / f"{raw_id}-{name}").write_bytes(data)
    manifest.append({
        "raw_private_id": raw_id,
        "classification": classification,
        "sha256": sha256(data),
        "byte_size": len(data),
        "timestamp_utc": utc_now(),
        "stored_outside_repository": True,
        "public_path_recorded": False,
    })
    return raw_id


def resolve_claude() -> str:
    link = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "claude.exe"
    if link.exists():
        return str(link)
    found = shutil.which("claude")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(local.glob("Anthropic.ClaudeCode_*/*claude.exe")) if local.exists() else []
    return str(matches[0]) if matches else "claude"


def directory_digest(path: Path) -> str:
    records = []
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        records.append({"path": file.relative_to(path).as_posix(), "sha256": sha256(file.read_bytes())})
    return sha256(canonical_json(records).encode("utf-8"))


def repository_state() -> str:
    return run_local(["git", "status", "--porcelain"]) or ""


def run_local(cmd: list[str | None]) -> str | None:
    if any(part is None for part in cmd):
        return None
    try:
        completed = subprocess.run([str(part) for part in cmd], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        out = (completed.stdout or completed.stderr).decode("utf-8", errors="replace").strip()
        return out or None
    except Exception:
        return None


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes())


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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
