from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
TRACK_ROOT = ROOT / "research" / "multi_agent_benchmark" / "claude_native"
RESULTS_PATH = TRACK_ROOT / "claude_native_c0_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_c0_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_c0_raw_private_manifest.json"

REQUESTED_MODEL = "sonnet"
TRACK_NAME = "Claude native through Claude Code"
PRIVATE_ROOT_PREFIX = "spira_claude_native_c0_private_"
READ_ONLY_TOOL_NAMES = {"read", "glob", "grep"}
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
    parser = argparse.ArgumentParser(description="Run Claude native C0 technical probes only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_c0(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "probe_count": results["probe_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS" else 1


def run_c0(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = utc_now()
    raw_manifest: list[dict[str, Any]] = []
    probe_results: dict[str, Any] = {}
    errors: list[str] = []

    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if _is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, local_inventory(), probe_results, raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    pre_repo_state = repository_state()
    inventory = local_inventory()
    if not inventory.get("claude_executable"):
        errors.append("CLAUDE_EXECUTABLE_NOT_FOUND")
        return finalize(started_at, inventory, probe_results, raw_manifest, errors)

    workspace = make_probe_workspace()
    try:
        p1 = claude_model_identity_probe(private_root, raw_manifest, workspace)
        probe_results["C0-P1"] = p1
        if not p1["ready"]:
            errors.extend(p1["errors"])
            return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)

        p2 = claude_init_probe(private_root, raw_manifest, workspace)
        probe_results["C0-P2"] = p2
        if not p2["ready"]:
            errors.extend(p2["errors"])
            return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)

        p3 = claude_structured_probe(private_root, raw_manifest, workspace)
        probe_results["C0-P3"] = p3
        if not p3["ready"]:
            errors.extend(p3["errors"])
            return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)

        p4 = claude_read_tools_probe(private_root, raw_manifest, workspace)
        probe_results["C0-P4"] = p4
        if not p4["ready"]:
            errors.extend(p4["errors"])
            return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)

        p5 = claude_denial_probe(private_root, raw_manifest, workspace)
        probe_results["C0-P5"] = p5
        if not p5["ready"]:
            errors.extend(p5["errors"])
            return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)

        p6a = claude_session_probe(private_root, raw_manifest, "A")
        p6b = claude_session_probe(private_root, raw_manifest, "B")
        probe_results["C0-P6A"] = p6a
        probe_results["C0-P6B"] = p6b
        probe_results["session_isolation_summary"] = session_isolation_summary(p6a, p6b)
        if not probe_results["session_isolation_summary"]["ready"]:
            errors.extend(probe_results["session_isolation_summary"]["errors"])

        p7 = claude_usage_probe(private_root, raw_manifest)
        probe_results["C0-P7"] = p7
        if not p7["ready"]:
            errors.extend(p7["errors"])
    except Exception as exc:  # pragma: no cover - defensive reporting path
        errors.append(f"CLAUDE_NATIVE_C0_RUNNER_EXCEPTION:{type(exc).__name__}")
        probe_results["runner_exception"] = {"type": type(exc).__name__}
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

    return finalize_with_repo_check(started_at, inventory, probe_results, raw_manifest, errors, pre_repo_state)


def claude_model_identity_probe(private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path) -> dict[str, Any]:
    result = run_claude(
        prompt="Return JSON only with probe_status PASS. Do not use tools.",
        output_format="json",
        workspace=workspace,
        max_turns=1,
        tools="",
    )
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P1-model-identity", result)
    parsed = parse_json_bytes(result.stdout)
    errors = common_auth_errors(result, parsed, "CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED")
    model = reported_model_from_json(parsed)
    if result.returncode == 0 and not model:
        errors.append("CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED")
    return {
        "probe": "C0-P1",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "requested_model": REQUESTED_MODEL,
        "reported_model": model,
        "auth_error_observed": auth_error_observed(result, parsed),
        "usage": extract_usage(parsed),
        "raw_private_id": raw_id,
    }


def claude_init_probe(private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path) -> dict[str, Any]:
    result = run_claude(
        prompt="Return a minimal JSON object with probe_status PASS. Do not use tools.",
        output_format="stream-json",
        workspace=workspace,
        max_turns=1,
        tools="Read,Glob,Grep",
        extra_args=["--verbose"],
    )
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P2-init", result)
    events = parse_json_lines(result.stdout)
    init = first_system_init(events)
    tools = extract_tool_names(init)
    errors = common_auth_errors(result, events, "CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED")
    if result.returncode == 0 and not init:
        errors.append("CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED")
    if forbidden_tools_present(tools):
        errors.append("CLAUDE_NATIVE_TOOL_ISOLATION_FAILED")
    return {
        "probe": "C0-P2",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "available_tools": sorted(tools),
        "forbidden_tool_count": len(forbidden_tools_present(tools)),
        "auth_error_observed": auth_error_observed(result, events),
        "usage": extract_usage_from_events(events),
        "raw_private_id": raw_id,
    }


def claude_structured_probe(private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path) -> dict[str, Any]:
    nonce = f"nonce-{uuid.uuid4()}"
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"probe_status": {"const": "PASS"}, "nonce": {"type": "string"}},
        "required": ["probe_status", "nonce"],
    }
    inline_schema = canonical_json(schema)
    result = run_claude(
        prompt=f"Return structured JSON with probe_status PASS and nonce {nonce}.",
        output_format="json",
        workspace=workspace,
        max_turns=1,
        tools="",
        extra_args=["--json-schema", inline_schema],
    )
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P3-structured", result)
    parsed = parse_json_bytes(result.stdout)
    structured = find_structured_output(parsed)
    errors = common_auth_errors(result, parsed, "CLAUDE_NATIVE_STRUCTURED_OUTPUT_NOT_READY")
    if result.returncode == 0 and (
        not isinstance(structured, dict)
        or structured.get("probe_status") != "PASS"
        or structured.get("nonce") != nonce
        or set(structured) != {"probe_status", "nonce"}
    ):
        errors.append("CLAUDE_NATIVE_STRUCTURED_OUTPUT_NOT_READY")
    return {
        "probe": "C0-P3",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "structured_output_found": isinstance(structured, dict),
        "schema_transport": "INLINE_CANONICAL_JSON",
        "schema_semantics_changed": False,
        "inline_schema_sha256": sha256(inline_schema.encode("utf-8")),
        "usage": extract_usage(parsed),
        "raw_private_id": raw_id,
    }


def claude_read_tools_probe(private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path) -> dict[str, Any]:
    pre = directory_digest(workspace)
    result = run_claude(
        prompt=(
            "Use Read to read probe_readme.txt, use Glob to find probe_data.json, "
            "and use Grep to find SPIRA_CLAUDE_NATIVE_READ_MARKER. "
            "Return the marker strings and matching relative path."
        ),
        output_format="stream-json",
        workspace=workspace,
        max_turns=4,
        tools="Read,Glob,Grep",
    )
    post = directory_digest(workspace)
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P4-read-tools", result)
    events = parse_json_lines(result.stdout)
    tools = tool_calls_from_value(events)
    lowered = {tool.lower() for tool in tools}
    text = result.stdout.decode("utf-8", errors="replace")
    errors = common_auth_errors(result, events, "CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY")
    if result.returncode == 0 and not READ_ONLY_TOOL_NAMES.issubset(lowered):
        errors.append("CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY")
    if result.returncode == 0 and "SPIRA_CLAUDE_NATIVE_READ_MARKER" not in text:
        errors.append("CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY")
    if pre != post:
        errors.append("CLAUDE_NATIVE_TOOL_ISOLATION_FAILED")
    if forbidden_tools_present(tools):
        errors.append("CLAUDE_NATIVE_TOOL_ISOLATION_FAILED")
    return {
        "probe": "C0-P4",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "tools_observed": sorted(tools),
        "read_tool_observed": "read" in lowered,
        "glob_tool_observed": "glob" in lowered,
        "grep_tool_observed": "grep" in lowered,
        "workspace_mutated": pre != post,
        "usage": extract_usage_from_events(events),
        "raw_private_id": raw_id,
    }


def claude_denial_probe(private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path) -> dict[str, Any]:
    pre = directory_digest(workspace)
    result = run_claude(
        prompt="Try to create a file, perform a web search, and spawn a subagent. If unavailable, report inability.",
        output_format="stream-json",
        workspace=workspace,
        max_turns=3,
        tools="Read,Glob,Grep",
    )
    post = directory_digest(workspace)
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P5-denial", result)
    events = parse_json_lines(result.stdout)
    tools = tool_calls_from_value(events)
    errors = common_auth_errors(result, events, "CLAUDE_NATIVE_TOOL_ISOLATION_FAILED")
    if pre != post or forbidden_tools_present(tools):
        errors.append("CLAUDE_NATIVE_TOOL_ISOLATION_FAILED")
    return {
        "probe": "C0-P5",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "tools_observed": sorted(tools),
        "forbidden_tool_count": len(forbidden_tools_present(tools)),
        "workspace_mutated": pre != post,
        "raw_private_id": raw_id,
    }


def claude_session_probe(private_root: Path, raw_manifest: list[dict[str, Any]], label: str) -> dict[str, Any]:
    workspace = make_probe_workspace()
    nonce = f"nonce_{label}_{uuid.uuid4()}"
    try:
        result = run_claude(
            prompt=f"Return JSON only with nonce {nonce}. Do not mention any previous nonce.",
            output_format="json",
            workspace=workspace,
            max_turns=1,
            tools="",
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_raw_pair(private_root, raw_manifest, f"C0-P6-session-{label}", result)
    parsed = parse_json_bytes(result.stdout)
    errors = common_auth_errors(result, parsed, "CLAUDE_NATIVE_C0_INCOMPLETE")
    return {
        "probe": f"C0-P6-{label}",
        "ready": not errors and nonce in result.stdout.decode("utf-8", errors="replace"),
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "session_id": result.session_id,
        "nonce_present": nonce in result.stdout.decode("utf-8", errors="replace"),
        "usage": extract_usage(parsed),
        "raw_private_id": raw_id,
    }


def claude_usage_probe(private_root: Path, raw_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    workspace = make_probe_workspace()
    try:
        result = run_claude(
            prompt="Return JSON only with usage_probe PASS.",
            output_format="json",
            workspace=workspace,
            max_turns=1,
            tools="",
        )
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_raw_pair(private_root, raw_manifest, "C0-P7-usage", result)
    parsed = parse_json_bytes(result.stdout)
    usage = extract_usage(parsed)
    errors = common_auth_errors(result, parsed, "CLAUDE_NATIVE_USAGE_ACCOUNTING_NOT_READY")
    if result.returncode == 0 and not usage.get("input_total_available"):
        errors.append("CLAUDE_NATIVE_USAGE_ACCOUNTING_NOT_READY")
    return {
        "probe": "C0-P7",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "returncode": result.returncode,
        "usage": usage,
        "raw_private_id": raw_id,
    }


class ClaudeRunResult:
    def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, session_id: str) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.session_id = session_id


def run_claude(
    *,
    prompt: str,
    output_format: str,
    workspace: Path,
    max_turns: int,
    tools: str,
    extra_args: list[str] | None = None,
) -> ClaudeRunResult:
    claude = resolve_claude()
    session_id = str(uuid.uuid4())
    config_dir = Path(tempfile.mkdtemp(prefix="spira_claude_native_config_"))
    env = os.environ.copy()
    env.update(
        {
            "CLAUDE_CONFIG_DIR": str(config_dir),
            "CLAUDE_CODE_SKIP_PROMPT_HISTORY": "1",
        }
    )
    for key in [
        "ANTHROPIC_BASE_URL",
        "ANTHROPIC_MODEL",
        "ANTHROPIC_DEFAULT_OPUS_MODEL",
        "ANTHROPIC_DEFAULT_SONNET_MODEL",
        "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        "CLAUDE_CODE_SUBAGENT_MODEL",
    ]:
        env.pop(key, None)
    cmd = [
        claude,
        "--bare",
        "--print",
        "--no-session-persistence",
        "--session-id",
        session_id,
        "--model",
        REQUESTED_MODEL,
        "--permission-mode",
        "dontAsk",
        "--output-format",
        output_format,
        "--tools",
        tools,
        "--disallowedTools",
        "Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--max-turns",
        str(max_turns),
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(prompt)
    try:
        completed = subprocess.run(
            cmd,
            shell=False,
            cwd=str(workspace),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90,
        )
        return ClaudeRunResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
            session_id=session_id,
        )
    except subprocess.TimeoutExpired as exc:
        return ClaudeRunResult(
            stdout=exc.stdout or b"",
            stderr=exc.stderr or b"timeout",
            returncode=124,
            session_id=session_id,
        )
    finally:
        shutil.rmtree(config_dir, ignore_errors=True)


def finalize_with_repo_check(
    started_at: str,
    inventory: Mapping[str, Any],
    probe_results: Mapping[str, Any],
    raw_manifest: list[dict[str, Any]],
    errors: list[str],
    pre_repo_state: str,
) -> dict[str, Any]:
    post_repo_state = repository_state()
    if pre_repo_state != post_repo_state:
        errors.append("CLAUDE_NATIVE_REPOSITORY_MUTATION_OBSERVED")
    return finalize(started_at, inventory, probe_results, raw_manifest, errors)


def finalize(
    started_at: str,
    inventory: Mapping[str, Any],
    probe_results: Mapping[str, Any],
    raw_manifest: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    blockers = sorted(set(errors))
    terminal = terminal_status(blockers, probe_results)
    usage_ready = bool((probe_results.get("C0-P7") or {}).get("ready"))
    forbidden_tool_count = sum(
        int(item.get("forbidden_tool_count", 0))
        for item in probe_results.values()
        if isinstance(item, Mapping)
    )
    workspace_mutation_count = sum(
        1 for item in probe_results.values() if isinstance(item, Mapping) and item.get("workspace_mutated")
    )
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_C0_RESULTS_V1",
        "track": TRACK_NAME,
        "phase": "C0",
        "scored": False,
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "claude_code_version": inventory.get("claude_version"),
        "claude_launcher_sha256": inventory.get("claude_launcher_sha256"),
        "probe_count": len([key for key in probe_results if str(key).startswith("C0-")]),
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "BENCHMARK_CASES_NOT_EXECUTED",
            "READINESS_SESSIONS_NOT_STARTED",
            "PRIMARY_BENCHMARK_NOT_STARTED",
            "MVP_CODE_UNCHANGED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "blockers": blockers,
        "authentication_ready": not any("AUTHENTICATION" in item for item in blockers),
        "model_identity_ready": terminal == "CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS" or bool((probe_results.get("C0-P1") or {}).get("ready")),
        "structured_output_ready": bool((probe_results.get("C0-P3") or {}).get("ready")),
        "read_only_tools_ready": bool((probe_results.get("C0-P4") or {}).get("ready")),
        "tool_isolation_ready": bool((probe_results.get("C0-P5") or {}).get("ready")),
        "usage_accounting_ready": usage_ready,
        "workspace_mutation_count": workspace_mutation_count,
        "forbidden_tool_call_count": forbidden_tool_count,
        "benchmark_cases_sent_to_model": 0,
        "readiness_sessions_started": 0,
        "primary_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "inventory": dict(inventory),
        "probe_results": probe_results,
        "raw_private_manifest": {
            "schema": "SPIRA_CLAUDE_NATIVE_C0_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def terminal_status(blockers: Iterable[str], probe_results: Mapping[str, Any]) -> str:
    blockers = set(blockers)
    if not blockers and all(
        bool((probe_results.get(key) or {}).get("ready"))
        for key in ["C0-P1", "C0-P2", "C0-P3", "C0-P4", "C0-P5", "C0-P7"]
    ) and bool((probe_results.get("session_isolation_summary") or {}).get("ready")):
        return "CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS"
    if any("AUTHENTICATION" in item or "MODEL_IDENTITY" in item for item in blockers):
        return "CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED"
    if "CLAUDE_NATIVE_STRUCTURED_OUTPUT_NOT_READY" in blockers:
        return "CLAUDE_NATIVE_STRUCTURED_OUTPUT_NOT_READY"
    if "CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY" in blockers:
        return "CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY"
    if "CLAUDE_NATIVE_USAGE_ACCOUNTING_NOT_READY" in blockers:
        return "CLAUDE_NATIVE_USAGE_ACCOUNTING_NOT_READY"
    if "CLAUDE_NATIVE_TOOL_ISOLATION_FAILED" in blockers:
        return "CLAUDE_NATIVE_TOOL_ISOLATION_FAILED"
    return "CLAUDE_NATIVE_C0_INCOMPLETE"


def common_auth_errors(result: ClaudeRunResult, parsed: Any, default_error: str) -> list[str]:
    text = result.stdout.decode("utf-8", errors="replace") + "\n" + result.stderr.decode("utf-8", errors="replace")
    errors: list[str] = []
    if "not logged in" in text.lower() or "please run /login" in text.lower():
        errors.append("CLAUDE_NATIVE_AUTHENTICATION_NOT_READY")
    elif result.returncode != 0:
        errors.append(default_error)
    if auth_error_observed(result, parsed) and "CLAUDE_NATIVE_AUTHENTICATION_NOT_READY" not in errors:
        errors.append("CLAUDE_NATIVE_AUTHENTICATION_NOT_READY")
    return errors


def auth_error_observed(result: ClaudeRunResult, parsed: Any) -> bool:
    text = result.stdout.decode("utf-8", errors="replace") + "\n" + result.stderr.decode("utf-8", errors="replace")
    if "not logged in" in text.lower() or "please run /login" in text.lower():
        return True
    if isinstance(parsed, Mapping):
        result_text = str(parsed.get("result") or "")
        return "not logged in" in result_text.lower()
    return False


def report_markdown(results: Mapping[str, Any]) -> str:
    blockers = "\n".join(f"- {item}" for item in results.get("blockers", [])) or "- none"
    probes = results.get("probe_results", {})
    probe_lines = "\n".join(
        f"- {key}: ready={value.get('ready')} rc={value.get('returncode')} errors={value.get('errors')}"
        for key, value in probes.items()
        if isinstance(value, Mapping) and str(key).startswith("C0-")
    )
    return f"""# Claude Native C0 Technical Probes Report

## Status

```text
{results['terminal_status']}
BENCHMARK_CASES_NOT_EXECUTED
READINESS_SESSIONS_NOT_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Identity

```text
track: {results['track']}
requested model: {results['requested_model']}
Claude Code version: {results.get('claude_code_version')}
Claude Code binary sha256: {results.get('claude_launcher_sha256')}
```

## Probe Summary

```text
probe count: {results['probe_count']}
structured output ready: {results['structured_output_ready']}
read-only tools ready: {results['read_only_tools_ready']}
tool isolation ready: {results['tool_isolation_ready']}
usage accounting ready: {results['usage_accounting_ready']}
workspace mutations: {results['workspace_mutation_count']}
forbidden tool calls: {results['forbidden_tool_call_count']}
benchmark cases sent: {results['benchmark_cases_sent_to_model']}
readiness sessions: {results['readiness_sessions_started']}
```

## Probes

{probe_lines or "- none"}

## Blockers

{blockers}

## Boundary

```text
No benchmark cases were sent.
No readiness, primary, holdout, or carryover benchmark was started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


def local_inventory() -> dict[str, Any]:
    claude = resolve_claude_or_none()
    return {
        "timestamp_utc": utc_now(),
        "branch": run_local(["git", "branch", "--show-current"]),
        "git_commit": run_local(["git", "rev-parse", "HEAD"]),
        "claude_executable": sanitize_path(claude) if claude else None,
        "claude_version": run_local([claude, "--version"]) if claude else None,
        "claude_launcher_sha256": file_sha256(Path(claude)) if claude and Path(claude).exists() else None,
        "node_version": run_local(["node", "--version"]),
        "python_version": sys.version.split()[0],
        "windows_version": platform.platform(),
    }


def resolve_claude() -> str:
    found = resolve_claude_or_none()
    return found or "claude"


def resolve_claude_or_none() -> str | None:
    found = shutil.which("claude")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(local.glob("Anthropic.ClaudeCode_*/*claude.exe")) if local.exists() else []
    return str(matches[0]) if matches else None


def make_probe_workspace() -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="spira_claude_native_c0_workspace_"))
    (workspace / "nested").mkdir()
    (workspace / "probe_readme.txt").write_text(
        "marker=SPIRA_CLAUDE_NATIVE_READ_MARKER\nnested=nested/probe_data.json\n",
        encoding="utf-8",
    )
    (workspace / "nested" / "probe_data.json").write_text(
        json.dumps({"marker": "SPIRA_CLAUDE_NATIVE_JSON_MARKER"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (workspace / "write_sentinel.txt").write_text("DO_NOT_MODIFY\n", encoding="utf-8")
    return workspace


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


def record_raw_pair(private_root: Path, manifest: list[dict[str, Any]], name: str, result: ClaudeRunResult) -> str:
    stdout_id = record_private_raw(private_root, manifest, f"{name}-stdout.raw", result.stdout, "CLAUDE_NATIVE_C0_STDOUT")
    record_private_raw(private_root, manifest, f"{name}-stderr.raw", result.stderr, "CLAUDE_NATIVE_C0_STDERR")
    return stdout_id


def record_private_raw(private_root: Path, manifest: list[dict[str, Any]], name: str, data: bytes, classification: str) -> str:
    raw_id = str(uuid.uuid4())
    (private_root / f"{raw_id}-{name}").write_bytes(data)
    manifest.append(
        {
            "raw_private_id": raw_id,
            "classification": classification,
            "sha256": sha256(data),
            "byte_size": len(data),
            "timestamp_utc": utc_now(),
            "stored_outside_repository": True,
            "public_path_recorded": False,
        }
    )
    return raw_id


def parse_json_bytes(data: bytes) -> Any:
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


def first_system_init(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    for event in events:
        haystack = json.dumps(event, sort_keys=True).lower()
        if "system" in haystack and "init" in haystack:
            return dict(event)
    return {}


def extract_tool_names(value: Any) -> set[str]:
    tools: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key).lower() in {"tools", "available_tools", "availabletools"}:
                if isinstance(item, list):
                    for tool in item:
                        if isinstance(tool, str):
                            tools.add(tool)
                        elif isinstance(tool, Mapping) and (tool.get("name") or tool.get("tool_name")):
                            tools.add(str(tool.get("name") or tool.get("tool_name")))
            tools.update(extract_tool_names(item))
    elif isinstance(value, list):
        for item in value:
            tools.update(extract_tool_names(item))
    return tools


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


def reported_model_from_json(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key in ["model", "model_name", "requested_model"]:
            if value.get(key):
                return str(value[key])
        for item in value.values():
            found = reported_model_from_json(item)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = reported_model_from_json(item)
            if found:
                return found
    return None


def find_structured_output(value: Any) -> Any:
    if isinstance(value, Mapping):
        for key in ["structured_output", "result", "output"]:
            item = value.get(key)
            if isinstance(item, Mapping) and ("probe_status" in item or "nonce" in item):
                return item
        if "probe_status" in value and "nonce" in value:
            return value
        for item in value.values():
            found = find_structured_output(item)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = find_structured_output(item)
            if found is not None:
                return found
    return None


def extract_usage_from_events(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    for event in reversed(list(events)):
        usage = extract_usage(event)
        if usage.get("input_total_available"):
            return usage
    return extract_usage(None)


def extract_usage(value: Any) -> dict[str, Any]:
    usage = find_usage(value)
    if not usage:
        return {"input_total_available": False, "cache_decomposition_status": "NOT_EVALUATED"}
    input_tokens = first_number(usage, ["input_tokens", "input"])
    output_tokens = first_number(usage, ["output_tokens", "output"])
    cache_creation = first_number(usage, ["cache_creation_input_tokens", "cache_creation"])
    cache_read = first_number(usage, ["cache_read_input_tokens", "cache_read"])
    total = input_tokens
    if total is not None:
        total += cache_creation or 0
        total += cache_read or 0
    return {
        "usage_keys": sorted(str(key) for key in usage.keys()),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_input_tokens": total,
        "input_total_available": total is not None,
        "cache_decomposition_status": "AVAILABLE" if cache_creation is not None or cache_read is not None else "NOT_EVALUATED",
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


def session_isolation_summary(a: Mapping[str, Any] | None, b: Mapping[str, Any] | None) -> dict[str, Any]:
    errors = []
    if not a or not b:
        errors.append("CLAUDE_NATIVE_C0_INCOMPLETE")
    else:
        if a.get("session_id") == b.get("session_id"):
            errors.append("CLAUDE_NATIVE_C0_INCOMPLETE")
        if not a.get("nonce_present") or not b.get("nonce_present"):
            errors.append("CLAUDE_NATIVE_C0_INCOMPLETE")
    return {"ready": not errors, "errors": errors}


def directory_digest(path: Path) -> str:
    records = []
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        records.append({"path": file.relative_to(path).as_posix(), "sha256": sha256(file.read_bytes())})
    return sha256(canonical_json(records).encode("utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def sanitize_path(path: str | None) -> str | None:
    if not path:
        return None
    return f"REDACTED_PATH/{Path(path).name}"


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
