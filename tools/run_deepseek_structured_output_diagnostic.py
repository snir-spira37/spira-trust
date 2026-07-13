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
RESULTS_PATH = DEEPSEEK_ROOT / "structured_output_diagnostic_results.json"
REPORT_PATH = DEEPSEEK_ROOT / "structured_output_diagnostic_report.md"
PRIVATE_MANIFEST_PATH = DEEPSEEK_ROOT / "structured_output_diagnostic_raw_private_manifest.json"

REQUESTED_MODEL = "deepseek-v4-pro"
PRIVATE_ROOT_PREFIX = "spira_deepseek_structured_output_private_"
REQUIRED_SCHEMA = ROOT / "research" / "multi_agent_benchmark" / "agent_output.schema.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DeepSeek structured-output diagnostic probes.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)

    results = run_diagnostic(private_root=Path(args.private_root) if args.private_root else None)
    DEEPSEEK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "probe_count": results["probe_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "STRUCTURED_OUTPUT_INVOCATION_DEFECT_FOUND" else 1


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

    probe_defs = [
        {
            "name": "json_without_schema_tools_empty",
            "output_format": "json",
            "tools": "",
            "extra_args": [],
            "prompt": 'Return exactly {"probe_status":"PASS","nonce":"spira-diagnostic-json"} as JSON.',
        },
        {
            "name": "stream_json_without_schema_tools_empty",
            "output_format": "stream-json",
            "tools": "",
            "extra_args": ["--verbose"],
            "prompt": 'Return exactly {"probe_status":"PASS","nonce":"spira-diagnostic-stream"} as JSON.',
        },
        {
            "name": "json_with_minimal_inline_schema",
            "output_format": "json",
            "tools": "",
            "extra_args": [
                "--json-schema",
                json.dumps(
                    {
                        "type": "object",
                        "properties": {
                            "probe_status": {"type": "string"},
                            "nonce": {"type": "string"},
                        },
                        "required": ["probe_status", "nonce"],
                        "additionalProperties": False,
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            ],
            "prompt": 'Return exactly {"probe_status":"PASS","nonce":"spira-diagnostic-inline-schema"} as JSON.',
        },
        {
            "name": "json_with_minimal_schema_file",
            "output_format": "json",
            "tools": "",
            "extra_args": ["--json-schema", str(write_minimal_schema())],
            "prompt": 'Return exactly {"probe_status":"PASS","nonce":"spira-diagnostic-file-schema"} as JSON.',
        },
        {
            "name": "json_with_benchmark_schema_file",
            "output_format": "json",
            "tools": "",
            "extra_args": ["--json-schema", str(REQUIRED_SCHEMA)],
            "prompt": 'Return a valid object for the provided schema using synthetic diagnostic values only.',
        },
    ]
    for definition in probe_defs:
        probes.append(run_probe(definition, key=key, private_root=private_root, raw_manifest=raw_manifest))
    return finalize(started_at, probes, raw_manifest, [])


def write_minimal_schema() -> Path:
    path = Path(tempfile.mkdtemp(prefix="spira_deepseek_schema_")) / "minimal_schema.json"
    path.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "probe_status": {"type": "string"},
                    "nonce": {"type": "string"},
                },
                "required": ["probe_status", "nonce"],
                "additionalProperties": False,
            },
            sort_keys=True,
            indent=2,
        ),
        encoding="utf-8",
    )
    return path


def run_probe(definition: Mapping[str, Any], *, key: str, private_root: Path, raw_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    workspace = Path(tempfile.mkdtemp(prefix="spira_deepseek_structured_workspace_"))
    config_dir = Path(tempfile.mkdtemp(prefix="spira_deepseek_structured_config_"))
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
        "dontAsk",
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
        "1",
    ]
    cmd.extend(str(arg) for arg in definition.get("extra_args", []))
    cmd.append(str(definition["prompt"]))
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
    started = utc_now()
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
        shutil.rmtree(workspace, ignore_errors=True)
        shutil.rmtree(config_dir, ignore_errors=True)
    stdout_id = record_private_raw(private_root, raw_manifest, f"{definition['name']}-stdout.raw", stdout, "CLAUDE_DIAGNOSTIC_STDOUT")
    stderr_id = record_private_raw(private_root, raw_manifest, f"{definition['name']}-stderr.raw", stderr, "CLAUDE_DIAGNOSTIC_STDERR")
    parsed_stdout = parse_stdout(stdout, str(definition["output_format"]))
    usage = extract_usage(parsed_stdout)
    return {
        "name": definition["name"],
        "started_at_utc": started,
        "completed_at_utc": utc_now(),
        "returncode": returncode,
        "timed_out": timed_out,
        "stdout_private_id": stdout_id,
        "stderr_private_id": stderr_id,
        "stdout_byte_size": len(stdout),
        "stderr_byte_size": len(stderr),
        "stdout_sha256": sha256(stdout),
        "stderr_sha256": sha256(stderr),
        "safe_stderr_category": categorize_stderr(stderr),
        "output_format": definition["output_format"],
        "json_object_found": contains_json_object(parsed_stdout),
        "usage_accounting_available": bool(usage.get("input_total_available")),
        "usage": usage,
        "server_tool_use": server_tool_use(parsed_stdout),
    }


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
    if errors:
        terminal = "STRUCTURED_OUTPUT_DIAGNOSTIC_INCOMPLETE"
    elif any(probe["returncode"] == 0 and probe["json_object_found"] for probe in probes):
        terminal = "STRUCTURED_OUTPUT_INVOCATION_DEFECT_FOUND"
    elif any(probe["returncode"] == 0 for probe in probes):
        terminal = "STRUCTURED_OUTPUT_SCHEMA_ENFORCEMENT_UNSUPPORTED"
    else:
        terminal = "STRUCTURED_OUTPUT_UNSUPPORTED_OR_UNRELIABLE"
    return {
        "schema": "SPIRA_DEEPSEEK_STRUCTURED_OUTPUT_DIAGNOSTIC_RESULTS_V1",
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
            "schema": "SPIRA_DEEPSEEK_STRUCTURED_OUTPUT_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    probe_lines = "\n".join(
        f"- {probe['name']}: rc={probe['returncode']} json={probe['json_object_found']} stderr={probe['safe_stderr_category']}"
        for probe in results.get("probes", [])
    )
    return f"""# DeepSeek Structured Output Diagnostic Report

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

## Boundary

```text
No benchmark cases were sent.
No readiness, primary, holdout, or carryover sessions were started.
Raw stdout/stderr stayed outside the repository.
```
"""


def record_private_raw(private_root: Path, raw_manifest: list[dict[str, Any]], name: str, data: bytes, classification: str) -> str:
    raw_id = str(uuid.uuid4())
    path = private_root / f"{raw_id}-{name}"
    path.write_bytes(data)
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


def parse_stdout(data: bytes, output_format: str) -> Any:
    text = data.decode("utf-8", errors="replace")
    if output_format == "stream-json":
        events = []
        for line in text.splitlines():
            try:
                events.append(json.loads(line))
            except Exception:
                continue
        return events
    try:
        return json.loads(text)
    except Exception:
        return text


def contains_json_object(value: Any) -> bool:
    if isinstance(value, Mapping):
        return True
    if isinstance(value, list):
        return any(contains_json_object(item) for item in value)
    if isinstance(value, str):
        return bool(re.search(r"\{[^{}]*probe_status[^{}]*\}", value))
    return False


def categorize_stderr(stderr: bytes) -> str:
    text = stderr.decode("utf-8", errors="replace")
    lowered = text.lower()
    if not text.strip():
        return "EMPTY"
    if "error:" in lowered and "option" in lowered:
        return "CLI_OPTION_ERROR"
    if "json" in lowered and "schema" in lowered:
        return "JSON_SCHEMA_ERROR"
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
    cache_creation = first_int(usage, "cache_creation_input_tokens", "cacheCreationInputTokens")
    cache_read = first_int(usage, "cache_read_input_tokens", "cacheReadInputTokens")
    total = None
    if input_tokens is not None:
        total = input_tokens + (cache_creation or 0) + (cache_read or 0)
    return {
        "input_total_available": total is not None,
        "input_tokens": input_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_input_tokens": total,
    }


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
