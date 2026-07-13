from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DEEPSEEK_ROOT = ROOT / "research" / "multi_agent_benchmark" / "deepseek"
RESULTS_PATH = DEEPSEEK_ROOT / "read_tool_diagnostic_results.json"
REPORT_PATH = DEEPSEEK_ROOT / "read_tool_diagnostic_report.md"
PRIVATE_MANIFEST_PATH = DEEPSEEK_ROOT / "read_tool_diagnostic_raw_private_manifest.json"

REQUESTED_MODEL = "deepseek-v4-pro"
PRIVATE_ROOT_PREFIX = "spira_deepseek_read_tool_private_"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DeepSeek read-tool diagnostic probes.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_diagnostic(private_root=Path(args.private_root) if args.private_root else None)
    DEEPSEEK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "probe_count": results["probe_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] in {"READ_TOOL_INVOCATION_DEFECT_FOUND", "READ_TOOL_CONFIGURATION_DEFECT_FOUND"} else 1


def run_diagnostic(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = utc_now()
    raw_manifest: list[dict[str, Any]] = []
    probes: list[dict[str, Any]] = []
    key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not key:
        return finalize(started_at, probes, raw_manifest, ["DEEPSEEK_AUTHENTICATION_NOT_CONFIGURED"])
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if _is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, probes, raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    definitions = [
        {"name": "read_only_default_prompt", "tools": "Read", "output_format": "stream-json", "permission_mode": "dontAsk", "prompt_kind": "read"},
        {"name": "read_only_manual_permission", "tools": "Read", "output_format": "stream-json", "permission_mode": "manual", "prompt_kind": "read"},
        {"name": "glob_only_probe", "tools": "Glob", "output_format": "stream-json", "permission_mode": "dontAsk", "prompt_kind": "glob"},
        {"name": "grep_only_probe", "tools": "Grep", "output_format": "stream-json", "permission_mode": "dontAsk", "prompt_kind": "grep"},
        {"name": "read_with_json_output", "tools": "Read", "output_format": "json", "permission_mode": "dontAsk", "prompt_kind": "read"},
        {"name": "read_with_tools_syntax_space", "tools": "Read Glob Grep", "output_format": "stream-json", "permission_mode": "dontAsk", "prompt_kind": "read"},
    ]
    for definition in definitions:
        probes.append(run_probe(definition, key=key, private_root=private_root, raw_manifest=raw_manifest))
    return finalize(started_at, probes, raw_manifest, [])


def run_probe(definition: Mapping[str, Any], *, key: str, private_root: Path, raw_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    workspace = make_workspace()
    pre_digest = directory_digest(workspace)
    config_dir = Path(tempfile.mkdtemp(prefix="spira_deepseek_read_config_"))
    prompt = prompt_for(definition["prompt_kind"], workspace)
    session_id = str(uuid.uuid4())
    cmd = [
        resolve_claude(),
        "--bare",
        "--print",
        "--no-session-persistence",
        "--session-id",
        session_id,
        "--model",
        REQUESTED_MODEL,
        "--effort",
        "max",
        "--permission-mode",
        str(definition["permission_mode"]),
        "--output-format",
        str(definition["output_format"]),
        "--tools",
        str(definition["tools"]),
        "--disallowedTools",
        "Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--max-turns",
        "2",
        prompt,
    ]
    env = os.environ.copy()
    env.update(
        {
            "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
            "ANTHROPIC_MODEL": REQUESTED_MODEL,
            "ANTHROPIC_DEFAULT_OPUS_MODEL": REQUESTED_MODEL,
            "ANTHROPIC_DEFAULT_SONNET_MODEL": REQUESTED_MODEL,
            "ANTHROPIC_DEFAULT_HAIKU_MODEL": REQUESTED_MODEL,
            "CLAUDE_CODE_SUBAGENT_MODEL": REQUESTED_MODEL,
            "CLAUDE_CODE_EFFORT_LEVEL": "max",
            "ANTHROPIC_AUTH_TOKEN": key,
            "ANTHROPIC_API_KEY": key,
            "CLAUDE_CONFIG_DIR": str(config_dir),
            "CLAUDE_CODE_SKIP_PROMPT_HISTORY": "1",
        }
    )
    timed_out = False
    try:
        completed = subprocess.run(
            cmd,
            shell=False,
            cwd=str(workspace),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
        )
        stdout = completed.stdout
        stderr = completed.stderr
        returncode = completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or b""
        stderr = exc.stderr or b"timeout"
        returncode = 124
        timed_out = True
    finally:
        post_digest = directory_digest(workspace)
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(config_dir, ignore_errors=True)
    stdout_id = record_private_raw(private_root, raw_manifest, f"{definition['name']}-stdout.raw", stdout, "CLAUDE_READ_DIAGNOSTIC_STDOUT")
    stderr_id = record_private_raw(private_root, raw_manifest, f"{definition['name']}-stderr.raw", stderr, "CLAUDE_READ_DIAGNOSTIC_STDERR")
    parsed = parse_output(stdout)
    tool_calls = sorted(tool_calls_from_value(parsed))
    return {
        "name": definition["name"],
        "returncode": returncode,
        "timed_out": timed_out,
        "stdout_byte_size": len(stdout),
        "stderr_byte_size": len(stderr),
        "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr),
        "stdout_private_id": stdout_id,
        "stderr_private_id": stderr_id,
        "safe_stderr_category": categorize_stderr(stderr),
        "tool_calls_observed": tool_calls,
        "read_tool_observed": any(name.lower() == "read" for name in tool_calls),
        "glob_tool_observed": any(name.lower() == "glob" for name in tool_calls),
        "grep_tool_observed": any(name.lower() == "grep" for name in tool_calls),
        "workspace_mutated": pre_digest != post_digest,
        "usage_accounting_available": bool(extract_usage(parsed).get("input_total_available")),
        "server_tool_use": server_tool_use(parsed),
        "tools_arg": definition["tools"],
        "permission_mode": definition["permission_mode"],
    }


def make_workspace() -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="spira_deepseek_read_workspace_"))
    (workspace / "probe_readme.txt").write_text("marker: SPIRA_READ_MARKER\nnested: nested/probe_data.json\n", encoding="utf-8")
    nested = workspace / "nested"
    nested.mkdir()
    (nested / "probe_data.json").write_text('{"marker":"SPIRA_JSON_MARKER","value":17}\n', encoding="utf-8")
    return workspace


def prompt_for(kind: str, workspace: Path) -> str:
    abs_file = workspace / "probe_readme.txt"
    if kind == "glob":
        return "Use Glob to find probe_data.json. Return only the matching relative path."
    if kind == "grep":
        return "Use Grep to find SPIRA_READ_MARKER. Return only the file path and matching marker."
    return f"Use Read to read probe_readme.txt and {abs_file.name}. Return the two marker strings only."


def resolve_claude() -> str:
    found = shutil.which("claude")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(local.glob("Anthropic.ClaudeCode_*/*claude.exe")) if local.exists() else []
    if matches:
        return str(matches[0])
    return "claude"


def finalize(started_at: str, probes: list[dict[str, Any]], raw_manifest: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    any_success = any(probe["returncode"] == 0 and probe["tool_calls_observed"] for probe in probes)
    any_cli_error = any(probe["safe_stderr_category"] in {"CLI_OPTION_ERROR", "TOOL_PERMISSION_ERROR"} for probe in probes)
    if errors:
        terminal = "READ_TOOL_DIAGNOSTIC_INCOMPLETE"
    elif any_success:
        terminal = "READ_TOOL_CONFIGURATION_DEFECT_FOUND"
    elif any_cli_error:
        terminal = "READ_TOOL_INVOCATION_DEFECT_FOUND"
    else:
        terminal = "DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY"
    return {
        "schema": "SPIRA_DEEPSEEK_READ_TOOL_DIAGNOSTIC_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "NO_BENCHMARK_CASES_SENT",
            "NO_READINESS_SESSIONS_STARTED",
            "DS_R0_RERUN_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "probe_count": len(probes),
        "benchmark_cases_sent_to_model": 0,
        "readiness_sessions_started": 0,
        "errors": errors,
        "probes": probes,
        "raw_private_manifest": {
            "schema": "SPIRA_DEEPSEEK_READ_TOOL_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    probe_lines = "\n".join(
        f"- {p['name']}: rc={p['returncode']} tools={p['tool_calls_observed']} stderr={p['safe_stderr_category']} mutated={p['workspace_mutated']}"
        for p in results.get("probes", [])
    )
    return f"""# DeepSeek Read Tool Diagnostic Report

## Status

```text
{results['terminal_status']}
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: {results['requested_model']}
probe count: {results['probe_count']}
benchmark cases sent: {results['benchmark_cases_sent_to_model']}
readiness sessions: {results['readiness_sessions_started']}
```

## Probes

{probe_lines}
"""


def record_private_raw(private_root: Path, raw_manifest: list[dict[str, Any]], name: str, data: bytes, classification: str) -> str:
    raw_id = str(uuid.uuid4())
    (private_root / f"{raw_id}-{name}").write_bytes(data)
    raw_manifest.append(
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


def parse_output(stdout: bytes) -> Any:
    text = stdout.decode("utf-8", errors="replace")
    events = []
    for line in text.splitlines():
        try:
            events.append(json.loads(line))
        except Exception:
            continue
    if events:
        return events
    try:
        return json.loads(text)
    except Exception:
        return text


def tool_calls_from_value(value: Any) -> set[str]:
    calls: set[str] = set()
    if isinstance(value, Mapping):
        if str(value.get("type", "")).lower() in {"tool_use", "tool_call"}:
            name = value.get("name") or value.get("tool_name")
            if name:
                calls.add(str(name))
        for item in value.values():
            calls.update(tool_calls_from_value(item))
    elif isinstance(value, list):
        for item in value:
            calls.update(tool_calls_from_value(item))
    return calls


def categorize_stderr(stderr: bytes) -> str:
    text = stderr.decode("utf-8", errors="replace")
    lowered = text.lower()
    if not text.strip():
        return "EMPTY"
    if "permission" in lowered or "not allowed" in lowered:
        return "TOOL_PERMISSION_ERROR"
    if "error:" in lowered and "option" in lowered:
        return "CLI_OPTION_ERROR"
    if "tool" in lowered:
        return "TOOL_ERROR"
    if "auth" in lowered or "api key" in lowered:
        return "AUTH_OR_PROVIDER_ERROR"
    if "timeout" in lowered:
        return "TIMEOUT"
    return "NONEMPTY_OTHER"


def extract_usage(value: Any) -> dict[str, Any]:
    usage = find_usage(value)
    if not usage:
        return {"input_total_available": False}
    input_tokens = first_int(usage, "input_tokens", "inputTokens")
    return {"input_total_available": input_tokens is not None, "input_tokens": input_tokens}


def find_usage(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        for key in ("usage", "modelUsage"):
            item = value.get(key)
            if isinstance(item, Mapping):
                if key == "modelUsage":
                    for model_usage in item.values():
                        if isinstance(model_usage, Mapping):
                            return model_usage
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


def server_tool_use(value: Any) -> dict[str, int]:
    serialized = json.dumps(value, sort_keys=True) if not isinstance(value, str) else value
    return {
        "web_search_requests": int(re.search(r"web_search_requests\"?\s*[:=]\s*(\d+)", serialized).group(1))
        if re.search(r"web_search_requests\"?\s*[:=]\s*(\d+)", serialized)
        else 0,
        "web_fetch_requests": int(re.search(r"web_fetch_requests\"?\s*[:=]\s*(\d+)", serialized).group(1))
        if re.search(r"web_fetch_requests\"?\s*[:=]\s*(\d+)", serialized)
        else 0,
    }


def first_int(mapping: Mapping[str, Any], *keys: str) -> int | None:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, int):
            return value
    return None


def directory_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(str(item.relative_to(path)).replace("\\", "/").encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
