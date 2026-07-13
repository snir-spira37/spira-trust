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
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
TRACK_ROOT = ROOT / "research" / "multi_agent_benchmark" / "claude_native"
RESULTS_PATH = TRACK_ROOT / "claude_native_auth_remediation_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_auth_remediation_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_auth_remediation_raw_private_manifest.json"

REQUESTED_MODEL = "haiku"
PRIVATE_ROOT_PREFIX = "spira_claude_native_auth_private_"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Claude native auth remediation smoke only.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    args = parser.parse_args(argv)
    results = run_auth_smoke(private_root=Path(args.private_root) if args.private_root else None)
    TRACK_ROOT.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    PRIVATE_MANIFEST_PATH.write_text(json.dumps(results["raw_private_manifest"], sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"terminal_status": results["terminal_status"]}, sort_keys=True))
    return 0 if results["terminal_status"] == "CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED" else 1


def run_auth_smoke(*, private_root: Path | None = None) -> dict[str, Any]:
    started_at = utc_now()
    raw_manifest: list[dict[str, Any]] = []
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if _is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize(started_at, {}, raw_manifest, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"], None)
    private_root.mkdir(parents=True, exist_ok=True)

    inventory = local_inventory()
    if not inventory.get("claude_executable"):
        return finalize(started_at, inventory, raw_manifest, ["CLAUDE_EXECUTABLE_NOT_FOUND"], None)

    workspace = Path(tempfile.mkdtemp(prefix="spira_claude_native_auth_workspace_"))
    try:
        result = run_claude(workspace)
    finally:
        shutil.rmtree(workspace, ignore_errors=True)
    raw_id = record_raw_pair(private_root, raw_manifest, "claude-native-auth-smoke", result)
    parsed = parse_json(result.stdout)
    errors: list[str] = []
    if auth_error_observed(result, parsed):
        errors.append("CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY")
    elif result.returncode != 0:
        errors.append("CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_FAILED")
    usage = extract_usage(parsed)
    if auth_error_observed(result, parsed):
        usage = {"input_total_available": False, "status": "NOT_EVALUATED_DUE_TO_AUTH"}
    if result.returncode == 0 and not usage.get("input_total_available"):
        errors.append("CLAUDE_NATIVE_USAGE_ACCOUNTING_SMOKE_NOT_AVAILABLE")
    return finalize(started_at, inventory, raw_manifest, errors, {
        "returncode": result.returncode,
        "raw_private_id": raw_id,
        "auth_error_observed": auth_error_observed(result, parsed),
        "usage": usage,
        "reported_model": reported_model(parsed),
        "stdout_byte_size": len(result.stdout),
        "stderr_byte_size": len(result.stderr),
        "stdout_sha256": sha256(result.stdout),
        "stderr_sha256": sha256(result.stderr),
    })


class ClaudeRunResult:
    def __init__(self, *, stdout: bytes, stderr: bytes, returncode: int, session_id: str) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.session_id = session_id


def run_claude(workspace: Path) -> ClaudeRunResult:
    session_id = str(uuid.uuid4())
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
        "",
        "--disallowedTools",
        "Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*",
        "--strict-mcp-config",
        "--no-chrome",
        "--disable-slash-commands",
        "--max-turns",
        "1",
        "Return JSON only with auth_smoke PASS.",
    ]
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
        return ClaudeRunResult(stdout=completed.stdout, stderr=completed.stderr, returncode=completed.returncode, session_id=session_id)
    except subprocess.TimeoutExpired as exc:
        return ClaudeRunResult(stdout=exc.stdout or b"", stderr=exc.stderr or b"timeout", returncode=124, session_id=session_id)


def finalize(
    started_at: str,
    inventory: Mapping[str, Any],
    raw_manifest: list[dict[str, Any]],
    errors: list[str],
    smoke: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not errors and smoke and smoke.get("returncode") == 0:
        terminal = "CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED"
    elif "CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY" in errors:
        terminal = "CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY"
    elif "CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_FAILED" in errors:
        terminal = "CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_FAILED"
    else:
        terminal = "CLAUDE_NATIVE_AUTH_REMEDIATION_INCOMPLETE"
    return {
        "schema": "SPIRA_CLAUDE_NATIVE_AUTH_REMEDIATION_RESULTS_V1",
        "terminal_status": terminal,
        "terminal_statuses": [
            terminal,
            "NO_BENCHMARK_CASES_SENT",
            "NO_READINESS_SESSIONS_STARTED",
            "CLAUDE_NATIVE_C0_RERUN_NOT_AUTHORIZED",
            "EFFICIENCY_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
        ],
        "started_at_utc": started_at,
        "completed_at_utc": utc_now(),
        "requested_model": REQUESTED_MODEL,
        "inventory": dict(inventory),
        "blockers": sorted(set(errors)),
        "smoke": dict(smoke or {}),
        "benchmark_cases_sent_to_model": 0,
        "readiness_sessions_started": 0,
        "primary_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "raw_private_manifest": {
            "schema": "SPIRA_CLAUDE_NATIVE_AUTH_REMEDIATION_RAW_PRIVATE_MANIFEST_V1",
            "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
            "raw_file_count": len(raw_manifest),
            "raw_files": raw_manifest,
        },
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    blockers = "\n".join(f"- {item}" for item in results.get("blockers", [])) or "- none"
    smoke = results.get("smoke", {})
    return f"""# Claude Native Authentication Remediation Report

## Status

```text
{results['terminal_status']}
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
CLAUDE_NATIVE_C0_RERUN_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Identity

```text
requested model: {results['requested_model']}
Claude Code version: {results.get('inventory', {}).get('claude_version')}
Claude Code binary sha256: {results.get('inventory', {}).get('claude_launcher_sha256')}
reported model: {smoke.get('reported_model')}
```

## Smoke

```text
returncode: {smoke.get('returncode')}
auth error observed: {smoke.get('auth_error_observed')}
usage accounting available: {smoke.get('usage', {}).get('input_total_available')}
benchmark cases sent: {results['benchmark_cases_sent_to_model']}
readiness sessions: {results['readiness_sessions_started']}
```

## Blockers

{blockers}
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
        "python_version": sys.version.split()[0],
        "windows_version": platform.platform(),
    }


def resolve_claude() -> str:
    return resolve_claude_or_none() or "claude"


def resolve_claude_or_none() -> str | None:
    link = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Links" / "claude.exe"
    if link.exists():
        return str(link)
    found = shutil.which("claude")
    if found:
        return found
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    matches = list(local.glob("Anthropic.ClaudeCode_*/*claude.exe")) if local.exists() else []
    return str(matches[0]) if matches else None


def record_raw_pair(private_root: Path, manifest: list[dict[str, Any]], name: str, result: ClaudeRunResult) -> str:
    stdout_id = record_private_raw(private_root, manifest, f"{name}-stdout.raw", result.stdout, "CLAUDE_NATIVE_AUTH_STDOUT")
    record_private_raw(private_root, manifest, f"{name}-stderr.raw", result.stderr, "CLAUDE_NATIVE_AUTH_STDERR")
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


def auth_error_observed(result: ClaudeRunResult, parsed: Any) -> bool:
    text = result.stdout.decode("utf-8", errors="replace") + "\n" + result.stderr.decode("utf-8", errors="replace")
    if "not logged in" in text.lower() or "please run /login" in text.lower():
        return True
    if isinstance(parsed, Mapping):
        return "not logged in" in str(parsed.get("result") or "").lower()
    return False


def reported_model(value: Any) -> str | None:
    if isinstance(value, Mapping):
        for key in ["model", "model_name"]:
            if value.get(key):
                return str(value[key])
        for item in value.values():
            found = reported_model(item)
            if found:
                return found
    elif isinstance(value, list):
        for item in value:
            found = reported_model(item)
            if found:
                return found
    return None


def extract_usage(value: Any) -> dict[str, Any]:
    usage = find_usage(value)
    if not usage:
        return {"input_total_available": False}
    input_tokens = first_number(usage, ["input_tokens", "input"])
    return {"input_total_available": input_tokens is not None, "input_tokens": input_tokens}


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


def parse_json(data: bytes) -> Any:
    try:
        return json.loads(data.decode("utf-8", errors="replace"))
    except Exception:
        return None


def run_local(cmd: list[str | None]) -> str | None:
    if any(part is None for part in cmd):
        return None
    try:
        completed = subprocess.run([str(part) for part in cmd], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        out = (completed.stdout or completed.stderr).decode("utf-8", errors="replace").strip()
        return out or None
    except Exception:
        return None


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
