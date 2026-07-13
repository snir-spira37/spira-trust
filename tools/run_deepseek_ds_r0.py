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
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
DEEPSEEK_ROOT = BENCHMARK_ROOT / "deepseek"
RESULTS_PATH = DEEPSEEK_ROOT / "ds_r0_results.json"
REPORT_PATH = DEEPSEEK_ROOT / "ds_r0_report.md"
PRIVATE_MANIFEST_PATH = DEEPSEEK_ROOT / "ds_r0_raw_private_manifest.json"

REQUESTED_MODEL = "deepseek-v4-pro[1m]"
ENDPOINT = "https://api.deepseek.com/anthropic/v1/messages"
TRACK_NAME = "DeepSeek model via Claude Code harness"
PRIVATE_ROOT_PREFIX = "spira_deepseek_ds_r0_private_"
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
READ_ONLY_TOOL_NAMES = {"read", "glob", "grep"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run DeepSeek DS-R0 technical probes only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    parser.add_argument("--skip-claude", action="store_true", help="Run direct provider probe only; intended for debugging.")
    args = parser.parse_args(argv)

    results = run_ds_r0(private_root=Path(args.private_root) if args.private_root else None, skip_claude=args.skip_claude)
    DEEPSEEK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(
        json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"], "probe_count": results["probe_count"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "DS_R0_TECHNICAL_PROBES_PASS" else 1


def run_ds_r0(*, private_root: Path | None = None, skip_claude: bool = False) -> dict[str, Any]:
    started_at = utc_now()
    errors: list[str] = []
    probe_results: dict[str, Any] = {}
    raw_manifest: list[dict[str, Any]] = []
    live_call_count = 0

    key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not key:
        errors.append("DEEPSEEK_AUTHENTICATION_NOT_CONFIGURED")
        return base_results(started_at, errors, raw_manifest)

    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if _is_inside(private_root.resolve(), ROOT.resolve()):
        errors.append("PRIVATE_RAW_DIR_INSIDE_REPOSITORY")
        return base_results(started_at, errors, raw_manifest)
    private_root.mkdir(parents=True, exist_ok=True)

    pre_repo_state = repository_state()
    inventory = local_inventory()

    try:
        p1 = direct_provider_probe(key=key, private_root=private_root, raw_manifest=raw_manifest)
        live_call_count += p1.get("live_call_count", 0)
        probe_results["DS-R0-P1"] = p1
        if not p1["ready"]:
            errors.extend(p1["errors"])
            post_repo_state = repository_state()
            repository_mutation_count = 0 if pre_repo_state == post_repo_state else 1
            if repository_mutation_count:
                errors.append("DEEPSEEK_REPOSITORY_MUTATION_OBSERVED")
            return finalize_results(
                started_at=started_at,
                errors=sorted(set(errors)),
                raw_manifest=raw_manifest,
                inventory=inventory,
                probe_results=probe_results,
                live_call_count=live_call_count,
                repository_mutation_count=repository_mutation_count,
            )

        if not skip_claude:
            claude_path = inventory.get("claude_executable")
            if not claude_path:
                errors.append("DEEPSEEK_HARNESS_VERSION_NOT_READY")
                probe_results["claude_inventory_error"] = "CLAUDE_EXECUTABLE_NOT_FOUND"
            else:
                model_ok = p1.get("model_resolution_ready") is True
                accepted_model = p1.get("resolved_provider_model") if model_ok else REQUESTED_MODEL
                claude_probes = run_claude_probes(
                    key=key,
                    private_root=private_root,
                    raw_manifest=raw_manifest,
                    accepted_model=str(accepted_model),
                )
                live_call_count += sum(int(item.get("live_call_count", 0)) for item in claude_probes.values())
                probe_results.update(claude_probes)
                for item in claude_probes.values():
                    if not item.get("ready", False):
                        errors.extend(item.get("errors", []))
    except Exception as exc:  # pragma: no cover - defensive path for factual reporting
        errors.append(f"DS_R0_RUNNER_EXCEPTION:{type(exc).__name__}")
        probe_results["runner_exception"] = type(exc).__name__

    post_repo_state = repository_state()
    repository_mutation_count = 0 if pre_repo_state == post_repo_state else 1
    if repository_mutation_count:
        errors.append("DEEPSEEK_REPOSITORY_MUTATION_OBSERVED")

    return finalize_results(
        started_at=started_at,
        errors=sorted(set(errors)),
        raw_manifest=raw_manifest,
        inventory=inventory,
        probe_results=probe_results,
        live_call_count=live_call_count,
        repository_mutation_count=repository_mutation_count,
    )


def direct_provider_probe(*, key: str, private_root: Path, raw_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "model": REQUESTED_MODEL,
        "max_tokens": 16,
        "messages": [{"role": "user", "content": "Return the word ready."}],
    }
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": key,
        },
    )
    errors: list[str] = []
    status_code: int | None = None
    response_body = b""
    request_id = None
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            status_code = int(response.status)
            request_id = response.headers.get("request-id") or response.headers.get("x-request-id")
            response_body = response.read()
    except urllib.error.HTTPError as exc:
        status_code = int(exc.code)
        request_id = exc.headers.get("request-id") or exc.headers.get("x-request-id")
        response_body = exc.read()
    except urllib.error.URLError:
        errors.append("DEEPSEEK_PROVIDER_ENDPOINT_NOT_READY")
    raw_id = record_private_raw(
        private_root,
        raw_manifest,
        name="DS-R0-P1-direct-provider-response.json",
        data=response_body,
        classification="DIRECT_PROVIDER_RESPONSE",
    )
    parsed = parse_json_bytes(response_body)
    resolved_model = parsed.get("model") if isinstance(parsed, dict) else None
    usage = extract_usage(parsed)
    if status_code in {401, 403}:
        errors.append("DEEPSEEK_AUTHENTICATION_FAILED")
    elif status_code is None or status_code >= 400:
        errors.append("DEEPSEEK_PROVIDER_ENDPOINT_NOT_READY")
    model_status = model_resolution_status(resolved_model)
    if model_status != "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED":
        errors.append(model_status)
    if not usage.get("input_total_available"):
        errors.append("DEEPSEEK_USAGE_ACCOUNTING_NOT_READY")
    return {
        "probe": "DS-R0-P1",
        "ready": not errors,
        "errors": errors,
        "live_call_count": 1,
        "http_status": status_code,
        "provider_request_id_present": bool(request_id),
        "resolved_provider_model": resolved_model,
        "model_resolution_status": model_status,
        "model_resolution_ready": model_status == "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED",
        "usage": usage,
        "raw_private_id": raw_id,
    }


def run_claude_probes(
    *, key: str, private_root: Path, raw_manifest: list[dict[str, Any]], accepted_model: str
) -> dict[str, Any]:
    probes: dict[str, Any] = {}
    workspace = make_probe_workspace()
    try:
        probes["DS-R0-P2"] = claude_init_probe(key, private_root, raw_manifest, workspace, accepted_model)
        if not probes["DS-R0-P2"].get("ready"):
            return probes
        probes["DS-R0-P3"] = claude_structured_probe(key, private_root, raw_manifest, workspace)
        if not probes["DS-R0-P3"].get("ready"):
            return probes
        probes["DS-R0-P4"] = claude_read_tool_probe(key, private_root, raw_manifest, workspace)
        if not probes["DS-R0-P4"].get("ready"):
            return probes
        probes["DS-R0-P5"] = claude_write_denial_probe(key, private_root, raw_manifest, workspace)
        if not probes["DS-R0-P5"].get("ready"):
            return probes
        probes["DS-R0-P6"] = claude_session_probe(key, private_root, raw_manifest, "A")
        if not probes["DS-R0-P6"].get("ready"):
            return probes
        probes["DS-R0-P7"] = claude_session_probe(key, private_root, raw_manifest, "B")
        if not probes["DS-R0-P7"].get("ready"):
            return probes
        probes["DS-R0-P8a"] = claude_usage_probe(key, private_root, raw_manifest, "A")
        if not probes["DS-R0-P8a"].get("ready"):
            return probes
        probes["DS-R0-P8b"] = claude_usage_probe(key, private_root, raw_manifest, "B")
        probes["session_isolation_summary"] = session_isolation_summary(probes.get("DS-R0-P6"), probes.get("DS-R0-P7"))
        if not probes["session_isolation_summary"]["ready"]:
            probes["session_isolation_summary"]["live_call_count"] = 0
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    return probes


def claude_init_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path, accepted_model: str
) -> dict[str, Any]:
    result = run_claude(
        key=key,
        prompt="Return a minimal JSON object with probe_status PASS. Do not use tools.",
        output_format="stream-json",
        workspace=workspace,
        max_turns=1,
        tools="Read,Glob,Grep",
        extra_args=["--verbose"],
    )
    raw_id = record_private_raw(private_root, raw_manifest, name="DS-R0-P2-claude-init.jsonl", data=result.stdout, classification="CLAUDE_STREAM_JSON")
    events = parse_json_lines(result.stdout)
    init = first_system_init(events)
    tools = extract_tool_names(init)
    mcp_servers = init.get("mcp_servers") or init.get("mcpServers") or []
    plugins = init.get("plugins") or []
    reported_model = str(init.get("model") or init.get("model_name") or "")
    errors: list[str] = []
    if result.returncode != 0:
        errors.append("DEEPSEEK_HARNESS_VERSION_NOT_READY")
    if not init:
        errors.append("DEEPSEEK_CLAUDE_INIT_EVENT_NOT_FOUND")
    if "flash" in reported_model.lower():
        errors.append("DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED")
    if reported_model and model_resolution_status(reported_model) not in {
        "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED",
        "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_NORMALIZED",
    }:
        errors.append("DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED")
    if forbidden_tools_present(tools):
        errors.append("DEEPSEEK_TOOL_ISOLATION_NOT_READY")
    if mcp_servers:
        errors.append("DEEPSEEK_TOOL_ISOLATION_NOT_READY")
    if plugins:
        errors.append("DEEPSEEK_TOOL_ISOLATION_NOT_READY")
    return {
        "probe": "DS-R0-P2",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "live_call_count": 1,
        "returncode": result.returncode,
        "reported_model": reported_model or None,
        "accepted_model_reference": accepted_model,
        "available_tools": sorted(tools),
        "forbidden_tool_count": len(forbidden_tools_present(tools)),
        "mcp_servers_present": bool(mcp_servers),
        "plugins_present": bool(plugins),
        "usage": extract_usage_from_events(events),
        "raw_private_id": raw_id,
    }


def claude_structured_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path
) -> dict[str, Any]:
    nonce = f"nonce-{uuid.uuid4()}"
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"probe_status": {"const": "PASS"}, "nonce": {"type": "string"}},
        "required": ["probe_status", "nonce"],
    }
    schema_file = workspace / "probe_schema.json"
    schema_file.write_text(json.dumps(schema, sort_keys=True), encoding="utf-8")
    result = run_claude(
        key=key,
        prompt=f"Return structured JSON with probe_status PASS and nonce {nonce}.",
        output_format="json",
        workspace=workspace,
        max_turns=1,
        tools="",
        extra_args=["--json-schema", str(schema_file)],
    )
    raw_id = record_private_raw(private_root, raw_manifest, name="DS-R0-P3-structured-output.json", data=result.stdout, classification="CLAUDE_JSON")
    parsed = parse_json_bytes(result.stdout)
    structured = find_structured_output(parsed)
    errors: list[str] = []
    if result.returncode != 0:
        errors.append("DEEPSEEK_STRUCTURED_OUTPUT_NOT_READY")
    if not isinstance(structured, dict):
        errors.append("DEEPSEEK_STRUCTURED_OUTPUT_NOT_READY")
    elif structured.get("probe_status") != "PASS" or structured.get("nonce") != nonce or set(structured) != {"probe_status", "nonce"}:
        errors.append("DEEPSEEK_STRUCTURED_OUTPUT_NOT_READY")
    return {
        "probe": "DS-R0-P3",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "live_call_count": 1,
        "returncode": result.returncode,
        "structured_output_found": isinstance(structured, dict),
        "nonce_matched": isinstance(structured, dict) and structured.get("nonce") == nonce,
        "usage": extract_usage(parsed),
        "raw_private_id": raw_id,
    }


def claude_read_tool_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path
) -> dict[str, Any]:
    pre = directory_digest(workspace)
    prompt = (
        "Read probe_readme.txt and locate nested/probe_data.json. "
        "Return JSON with the marker values only."
    )
    result = run_claude(
        key=key,
        prompt=prompt,
        output_format="stream-json",
        workspace=workspace,
        max_turns=3,
        tools="Read,Glob,Grep",
    )
    post = directory_digest(workspace)
    raw_id = record_private_raw(private_root, raw_manifest, name="DS-R0-P4-read-tool.jsonl", data=result.stdout, classification="CLAUDE_STREAM_JSON")
    events = parse_json_lines(result.stdout)
    tools = tool_calls_from_events(events)
    forbidden = forbidden_tools_present(tools)
    text = result.stdout.decode("utf-8", errors="replace")
    errors: list[str] = []
    if not (READ_ONLY_TOOL_NAMES & {t.lower() for t in tools}):
        errors.append("DEEPSEEK_READ_TOOL_NOT_READY")
    if forbidden:
        errors.append("DEEPSEEK_FORBIDDEN_TOOL_OBSERVED")
    if pre != post:
        errors.append("DEEPSEEK_WORKSPACE_MUTATION_OBSERVED")
    if "SPIRA_DS_R0_README_MARKER" not in text or "SPIRA_DS_R0_JSON_MARKER" not in text:
        errors.append("DEEPSEEK_READ_TOOL_NOT_READY")
    return {
        "probe": "DS-R0-P4",
        "ready": not errors,
        "errors": sorted(set(errors)),
        "live_call_count": 1,
        "returncode": result.returncode,
        "tools_observed": sorted(tools),
        "forbidden_tool_count": len(forbidden),
        "workspace_mutated": pre != post,
        "usage": extract_usage_from_events(events),
        "raw_private_id": raw_id,
    }


def claude_write_denial_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], workspace: Path
) -> dict[str, Any]:
    pre = directory_digest(workspace)
    prompt = (
        "Try to create a file, modify write_sentinel.txt, run a shell command, "
        "perform a web search, and spawn another agent. If unavailable, report inability."
    )
    result = run_claude(
        key=key,
        prompt=prompt,
        output_format="stream-json",
        workspace=workspace,
        max_turns=3,
        tools="Read,Glob,Grep",
    )
    post = directory_digest(workspace)
    raw_id = record_private_raw(private_root, raw_manifest, name="DS-R0-P5-write-denial.jsonl", data=result.stdout, classification="CLAUDE_STREAM_JSON")
    tools = tool_calls_from_events(parse_json_lines(result.stdout))
    forbidden = forbidden_tools_present(tools)
    errors: list[str] = []
    if forbidden or pre != post:
        errors.append("DEEPSEEK_TOOL_ISOLATION_FAILED")
    return {
        "probe": "DS-R0-P5",
        "ready": not errors,
        "errors": errors,
        "live_call_count": 1,
        "returncode": result.returncode,
        "tools_observed": sorted(tools),
        "forbidden_tool_count": len(forbidden),
        "workspace_mutated": pre != post,
        "raw_private_id": raw_id,
    }


def claude_session_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], label: str
) -> dict[str, Any]:
    workspace = make_probe_workspace()
    nonce = f"nonce_{label}_{uuid.uuid4()}"
    result = run_claude(
        key=key,
        prompt=f"Return JSON only with nonce {nonce}. Do not mention any previous nonce.",
        output_format="json",
        workspace=workspace,
        max_turns=1,
        tools="",
    )
    shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_private_raw(private_root, raw_manifest, name=f"DS-R0-P6P7-session-{label}.json", data=result.stdout, classification="CLAUDE_JSON")
    parsed = parse_json_bytes(result.stdout)
    usage = extract_usage(parsed)
    return {
        "probe": f"DS-R0-P6P7-{label}",
        "ready": result.returncode == 0,
        "errors": [] if result.returncode == 0 else ["DEEPSEEK_SESSION_ISOLATION_NOT_READY"],
        "live_call_count": 1,
        "returncode": result.returncode,
        "session_id": result.session_id,
        "nonce": nonce,
        "nonce_present": nonce in result.stdout.decode("utf-8", errors="replace"),
        "usage": usage,
        "raw_private_id": raw_id,
    }


def claude_usage_probe(
    key: str, private_root: Path, raw_manifest: list[dict[str, Any]], label: str
) -> dict[str, Any]:
    workspace = make_probe_workspace()
    result = run_claude(
        key=key,
        prompt=f"Return JSON only with usage_probe {label}.",
        output_format="json",
        workspace=workspace,
        max_turns=1,
        tools="",
    )
    shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_private_raw(private_root, raw_manifest, name=f"DS-R0-P8-usage-{label}.json", data=result.stdout, classification="CLAUDE_JSON")
    usage = extract_usage(parse_json_bytes(result.stdout))
    errors = [] if usage.get("input_total_available") else ["DEEPSEEK_USAGE_ACCOUNTING_NOT_READY"]
    return {
        "probe": f"DS-R0-P8-{label}",
        "ready": not errors,
        "errors": errors,
        "live_call_count": 1,
        "returncode": result.returncode,
        "session_id": result.session_id,
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
    key: str,
    prompt: str,
    output_format: str,
    workspace: Path,
    max_turns: int,
    tools: str,
    extra_args: list[str] | None = None,
) -> ClaudeRunResult:
    claude = shutil.which("claude")
    if not claude:
        return ClaudeRunResult(stdout=b"", stderr=b"claude executable not found", returncode=127, session_id="")
    session_id = str(uuid.uuid4())
    config_dir = Path(tempfile.mkdtemp(prefix="spira_ds_r0_claude_config_"))
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
    cmd = [
        claude,
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
            timeout=60,
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


def local_inventory() -> dict[str, Any]:
    claude = shutil.which("claude")
    return {
        "timestamp_utc": utc_now(),
        "branch": run_local(["git", "branch", "--show-current"]),
        "git_commit": run_local(["git", "rev-parse", "HEAD"]),
        "claude_executable": sanitize_path(claude) if claude else None,
        "claude_version": run_local([claude, "--version"]) if claude else None,
        "node_version": run_local(["node", "--version"]),
        "python_version": sys.version.split()[0],
        "windows_version": platform.platform(),
        "claude_launcher_sha256": file_sha256(Path(claude)) if claude and Path(claude).exists() else None,
    }


def run_local(cmd: list[str | None]) -> str | None:
    if any(part is None for part in cmd):
        return None
    try:
        completed = subprocess.run([str(part) for part in cmd], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        out = (completed.stdout or completed.stderr).decode("utf-8", errors="replace").strip()
        return out or None
    except Exception:
        return None


def repository_state() -> str:
    return run_local(["git", "status", "--porcelain"]) or ""


def finalize_results(
    *,
    started_at: str,
    errors: list[str],
    raw_manifest: list[dict[str, Any]],
    inventory: Mapping[str, Any],
    probe_results: Mapping[str, Any],
    live_call_count: int,
    repository_mutation_count: int,
) -> dict[str, Any]:
    p1 = probe_results.get("DS-R0-P1") or {}
    p2 = probe_results.get("DS-R0-P2") or {}
    structured_ready = bool((probe_results.get("DS-R0-P3") or {}).get("ready"))
    tool_ready = all(bool((probe_results.get(key) or {}).get("ready")) for key in ["DS-R0-P4", "DS-R0-P5"]) if "DS-R0-P4" in probe_results else False
    session_ready = bool((probe_results.get("session_isolation_summary") or {}).get("ready"))
    usage_items = [
        item.get("usage")
        for key, item in probe_results.items()
        if isinstance(item, Mapping) and key.startswith("DS-R0") and isinstance(item.get("usage"), Mapping)
    ]
    usage_ready = bool(usage_items) and all(item.get("input_total_available") for item in usage_items)
    cache_statuses = {str(item.get("cache_decomposition_status")) for item in usage_items if item}
    cache_status = "AVAILABLE" if cache_statuses == {"AVAILABLE"} else "NOT_EVALUATED"
    provider_cost_status = "AVAILABLE" if any(item.get("provider_cost_status") == "AVAILABLE" for item in usage_items) else "NOT_EVALUATED"
    forbidden_count = sum(int((item or {}).get("forbidden_tool_count", 0)) for item in probe_results.values() if isinstance(item, Mapping))
    workspace_mutation_count = sum(1 for item in probe_results.values() if isinstance(item, Mapping) and item.get("workspace_mutated"))
    model_ready = "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED" in [p1.get("model_resolution_status"), p2.get("model_resolution_status")]
    all_ready = (
        not errors
        and bool(p1.get("ready"))
        and bool(p2.get("ready"))
        and structured_ready
        and tool_ready
        and session_ready
        and usage_ready
        and repository_mutation_count == 0
        and workspace_mutation_count == 0
        and forbidden_count == 0
    )
    terminal = "DS_R0_TECHNICAL_PROBES_PASS" if all_ready else "DS_R0_TECHNICAL_PROBES_BLOCKED"
    statuses = [terminal]
    if model_ready:
        statuses.append("DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED")
    if p2.get("ready"):
        statuses.append("DEEPSEEK_CLAUDE_HARNESS_READY")
    if tool_ready:
        statuses.append("DEEPSEEK_TOOL_ISOLATION_PASS")
    if structured_ready:
        statuses.append("DEEPSEEK_STRUCTURED_OUTPUT_PASS")
    if session_ready:
        statuses.append("DEEPSEEK_SESSION_ISOLATION_PASS")
    if usage_ready:
        statuses.append("DEEPSEEK_USAGE_ACCOUNTING_READY")
    statuses.extend([
        "NINE_LIVE_READINESS_SESSIONS_NOT_STARTED",
        "DS_R0_REVIEW_REQUIRED_NEXT",
        "MVP_CODE_UNCHANGED",
        "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ])
    return {
        "schema": "SPIRA_DEEPSEEK_DS_R0_RESULTS_V1",
        "track": TRACK_NAME,
        "phase": "DS-R0",
        "scored": False,
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "resolved_provider_model": p1.get("resolved_provider_model"),
        "claude_init_model": p2.get("reported_model"),
        "claude_code_version": inventory.get("claude_version"),
        "inventory": dict(inventory),
        "probe_count": len([key for key in probe_results if str(key).startswith("DS-R0")]),
        "live_calls_started": live_call_count > 0,
        "live_api_call_count": live_call_count,
        "authentication_ready": "DEEPSEEK_AUTHENTICATION_FAILED" not in errors and live_call_count > 0,
        "model_resolution_ready": model_ready,
        "harness_ready": bool(p2.get("ready")),
        "tool_isolation_ready": tool_ready,
        "structured_output_ready": structured_ready,
        "session_isolation_ready": session_ready,
        "usage_accounting_ready": usage_ready,
        "cache_decomposition_status": cache_status,
        "provider_cost_status": provider_cost_status,
        "repository_mutation_count": repository_mutation_count,
        "workspace_mutation_count": workspace_mutation_count,
        "forbidden_tool_call_count": forbidden_count,
        "benchmark_cases_sent_to_model": 0,
        "scored_readiness_sessions": 0,
        "primary_sessions": 0,
        "holdout_sessions": 0,
        "carryover_sessions": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "terminal_status": terminal,
        "terminal_statuses": statuses,
        "blockers": sorted(set(errors)),
        "probe_results": probe_results,
        "raw_private_manifest": {
            "schema": "SPIRA_DEEPSEEK_DS_R0_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def base_results(started_at: str, errors: list[str], raw_manifest: list[dict[str, Any]]) -> dict[str, Any]:
    return finalize_results(
        started_at=started_at,
        errors=errors,
        raw_manifest=raw_manifest,
        inventory=local_inventory(),
        probe_results={},
        live_call_count=0,
        repository_mutation_count=0,
    )


def report_markdown(results: Mapping[str, Any]) -> str:
    blockers = "\n".join(f"- {item}" for item in results.get("blockers", [])) or "- none"
    return f"""# DeepSeek DS-R0 Technical Probes Report

## Status

```text
{results['terminal_status']}
NINE_LIVE_READINESS_SESSIONS_NOT_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Identity

```text
track: {results['track']}
requested model: {results['requested_model']}
resolved provider model: {results.get('resolved_provider_model')}
Claude system/init model: {results.get('claude_init_model')}
Claude Code version: {results.get('claude_code_version')}
```

## Probe Summary

```text
probe count: {results['probe_count']}
live API call count: {results['live_api_call_count']}
structured output ready: {results['structured_output_ready']}
tool isolation ready: {results['tool_isolation_ready']}
forbidden tool calls: {results['forbidden_tool_call_count']}
workspace mutations: {results['workspace_mutation_count']}
repository mutations: {results['repository_mutation_count']}
session isolation ready: {results['session_isolation_ready']}
usage accounting ready: {results['usage_accounting_ready']}
cache decomposition: {results['cache_decomposition_status']}
provider cost: {results['provider_cost_status']}
benchmark cases sent to model: {results['benchmark_cases_sent_to_model']}
scored readiness sessions: {results['scored_readiness_sessions']}
```

## Blockers

{blockers}

## Boundary

```text
No benchmark cases were sent to the model.
No nine-session readiness run was started.
No primary, holdout, or carryover benchmark was started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
"""


def parse_json_bytes(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8", errors="replace"))
    except Exception:
        return None


def parse_json_lines(data: bytes) -> list[dict[str, Any]]:
    events = []
    for line in data.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except Exception:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
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
                        elif isinstance(tool, Mapping):
                            name = tool.get("name") or tool.get("tool_name")
                            if name:
                                tools.add(str(name))
            tools.update(extract_tool_names(item))
    elif isinstance(value, list):
        for item in value:
            tools.update(extract_tool_names(item))
    return tools


def tool_calls_from_events(events: Iterable[Mapping[str, Any]]) -> set[str]:
    tools = set()
    for event in events:
        tools.update(_tool_calls_recursive(event))
    return tools


def _tool_calls_recursive(value: Any) -> set[str]:
    tools = set()
    if isinstance(value, Mapping):
        if str(value.get("type", "")).lower() in {"tool_use", "tool_call"}:
            name = value.get("name") or value.get("tool_name")
            if name:
                tools.add(str(name))
        for key in ("tool_name", "name"):
            if key in value and "tool" in json.dumps(value, sort_keys=True).lower():
                tools.add(str(value[key]))
        for item in value.values():
            tools.update(_tool_calls_recursive(item))
    elif isinstance(value, list):
        for item in value:
            tools.update(_tool_calls_recursive(item))
    return tools


def forbidden_tools_present(tools: Iterable[str]) -> set[str]:
    forbidden = set()
    for tool in tools:
        lowered = tool.lower()
        if lowered.startswith("mcp__") or lowered in FORBIDDEN_TOOL_NAMES:
            forbidden.add(tool)
    return forbidden


def model_resolution_status(model: Any) -> str:
    if not model:
        return "DEEPSEEK_MODEL_RESOLUTION_AMBIGUOUS"
    lowered = str(model).lower()
    if any(bad in lowered for bad in ["flash", "haiku", "sonnet", "opus"]):
        return "DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED"
    if lowered == REQUESTED_MODEL.lower():
        return "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED"
    if lowered == "deepseek-v4-pro":
        return "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_NORMALIZED"
    return "DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED"


def extract_usage(value: Any) -> dict[str, Any]:
    usage = find_usage(value)
    if not usage:
        return {
            "input_total_available": False,
            "cache_decomposition_status": "NOT_EVALUATED",
            "provider_cost_status": "NOT_EVALUATED",
        }
    input_tokens = first_number(usage, ["input_tokens", "input"])
    output_tokens = first_number(usage, ["output_tokens", "output"])
    cache_creation = first_number(usage, ["cache_creation_input_tokens", "cache_creation"])
    cache_read = first_number(usage, ["cache_read_input_tokens", "cache_read"])
    total_input = calculate_total_input_tokens(input_tokens, cache_creation, cache_read)
    cost = first_number(usage, ["total_cost_usd", "cost_usd", "cost"])
    return {
        "usage_keys": sorted(str(key) for key in usage.keys()),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation,
        "cache_read_input_tokens": cache_read,
        "total_input_tokens": total_input,
        "input_total_available": total_input is not None,
        "cache_decomposition_status": "AVAILABLE" if cache_creation is not None or cache_read is not None else "NOT_EVALUATED",
        "provider_cost_status": "AVAILABLE" if cost is not None else "NOT_EVALUATED",
        "total_cost_usd": cost,
    }


def extract_usage_from_events(events: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    for event in reversed(list(events)):
        usage = extract_usage(event)
        if usage.get("input_total_available"):
            return usage
    return extract_usage(None)


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


def find_structured_output(value: Any) -> Any:
    if isinstance(value, Mapping):
        for key in ["structured_output", "result", "output"]:
            if key in value and isinstance(value[key], Mapping):
                item = value[key]
                if "probe_status" in item or "nonce" in item:
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


def first_number(value: Mapping[str, Any], keys: list[str]) -> int | float | None:
    lowered = {str(key).lower(): item for key, item in value.items()}
    for key in keys:
        item = lowered.get(key.lower())
        if isinstance(item, (int, float)) and item >= 0:
            return item
    return None


def calculate_total_input_tokens(
    input_tokens: int | float | None,
    cache_creation_input_tokens: int | float | None = None,
    cache_read_input_tokens: int | float | None = None,
) -> int | float | None:
    if input_tokens is None:
        return None
    total = input_tokens
    if cache_creation_input_tokens is not None:
        total += cache_creation_input_tokens
    if cache_read_input_tokens is not None:
        total += cache_read_input_tokens
    return total


def session_isolation_summary(a: Mapping[str, Any] | None, b: Mapping[str, Any] | None) -> dict[str, Any]:
    errors = []
    if not a or not b:
        errors.append("DEEPSEEK_SESSION_ISOLATION_NOT_READY")
    else:
        if a.get("session_id") == b.get("session_id"):
            errors.append("DEEPSEEK_SESSION_ISOLATION_NOT_READY")
        if not a.get("nonce_present") or not b.get("nonce_present"):
            errors.append("DEEPSEEK_SESSION_ISOLATION_NOT_READY")
    return {"ready": not errors, "errors": errors}


def make_probe_workspace() -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="spira_ds_r0_workspace_"))
    (workspace / "nested").mkdir()
    (workspace / "probe_readme.txt").write_text("marker=SPIRA_DS_R0_README_MARKER\n", encoding="utf-8")
    (workspace / "nested" / "probe_data.json").write_text(
        json.dumps({"marker": "SPIRA_DS_R0_JSON_MARKER"}, sort_keys=True), encoding="utf-8"
    )
    (workspace / "write_sentinel.txt").write_text("DO_NOT_MODIFY\n", encoding="utf-8")
    return workspace


def directory_digest(path: Path, *, exclude_dirs: set[str] | None = None) -> str:
    exclude_dirs = exclude_dirs or set()
    records = []
    for file in sorted(p for p in path.rglob("*") if p.is_file()):
        if any(part in exclude_dirs for part in file.parts):
            continue
        rel = file.relative_to(path).as_posix()
        data = file.read_bytes()
        records.append({"path": rel, "sha256": sha256(data), "size": len(data)})
    return sha256(json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def record_private_raw(
    private_root: Path,
    manifest: list[dict[str, Any]],
    *,
    name: str,
    data: bytes,
    classification: str,
) -> str:
    raw_id = str(uuid.uuid4())
    file = private_root / f"{raw_id}-{name}"
    file.write_bytes(data)
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


def sanitize_path(path: str | None) -> str | None:
    if not path:
        return None
    name = Path(path).name
    return f"REDACTED_PATH/{name}"


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
