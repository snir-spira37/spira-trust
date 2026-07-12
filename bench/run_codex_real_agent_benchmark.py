#!/usr/bin/env python3
"""Run the locked Codex CLI real-agent benchmark.

This benchmark uses Codex CLI tool-use sessions. It is intentionally separate
from the DeepSeek file-ingestion benchmark in bench/results/live_v2/.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_ROOT = Path(os.environ.get("SPIRA_CODEX_BENCH_SOURCE_ROOT", REPO / "outputs" / "live_agent_benchmark_v2_2026-07-10"))
DEFAULT_WORK_ROOT = REPO / "work" / "codex_real_agent_v1"
DEFAULT_RESULTS_ROOT = REPO / "bench" / "results" / "codex_real_agent_v1"
DEFAULT_CODEX = Path(os.environ.get("LOCALAPPDATA", "")) / "OpenAI" / "Codex" / "bin" / "ea1c60319a1dcb19" / "codex.exe"

EXPECTED = {
    "proceed_or_stop": "STOP",
    "spira_verdict": "GRAPH_OK_WITH_NOTES",
    "recommended_agent_action": "REPORT_NOT_EVALUATED",
    "reason_code": "REPORT_NOT_EVALUATED",
}

CASES = {
    "median_minijinja": {
        "package": "minijinja",
        "version": "2.18.0",
        "wheel": "minijinja-2.18.0-cp38-abi3-win_amd64.whl",
        "sha256": "f6e9ac8256fc5453e2c5ab91a44201447ea4975c341535a7aa623447b88b7c4e",
    },
    "p90_nutpie": {
        "package": "nutpie",
        "version": "0.16.8",
        "wheel": "nutpie-0.16.8-cp314-cp314-win_amd64.whl",
        "sha256": "80c067162053510d41ab4635a14bf38328b6d531d0d68e896ca95e9024b31823",
    },
}

ARMS = {
    "A_raw_discovery": {
        "instruction": (
            "Arm A - Raw Discovery:\n"
            "You receive only the artifact path and evidence directory. Choose which local files or commands to inspect. "
            "The prompt intentionally does not point you to any compact SPIRA agent surface.\n"
        )
    },
    "B_agent_summary": {
        "instruction": (
            "Arm B - Agent Summary:\n"
            "Read evidence/agent_summary.json first. Use full evidence only if required.\n"
        )
    },
    "C_current_spira_flow": {
        "instruction": (
            "Arm C - Current SPIRA Flow:\n"
            "Run status --agent first. If checked and unchanged, query the exact-context cache. "
            "Use the returned action contract and unification reference. Drill down only if the compact contract is insufficient.\n"
        )
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def safe_reset_dir(path: Path, *, root: Path) -> None:
    resolved = path.resolve()
    root_resolved = root.resolve()
    if resolved == root_resolved or root_resolved not in resolved.parents:
        raise SystemExit(f"refusing to reset path outside {root_resolved}: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


def copytree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_cmd(args: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        env=env,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def prepare_cases(source_root: Path, work_root: Path) -> dict[str, dict[str, Any]]:
    prepared: dict[str, dict[str, Any]] = {}
    prep_root = work_root / "prepared_cases"
    prep_root.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "source")
    for case_name, case in CASES.items():
        case_root = prep_root / case_name
        safe_reset_dir(case_root, root=work_root)
        source_artifact = source_root / case_name / "arm_b_spira_guided" / "artifact" / case["wheel"]
        if not source_artifact.is_file():
            raise SystemExit(f"missing frozen wheel for {case_name}: {source_artifact}")
        artifact_dir = case_root / "artifact"
        evidence_dir = case_root / "evidence"
        state_dir = case_root / "state" / "agent_summaries"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        evidence_dir.mkdir(parents=True, exist_ok=True)
        state_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = artifact_dir / source_artifact.name
        shutil.copy2(source_artifact, artifact_path)
        graph = run_cmd(
            [
                sys.executable,
                "-m",
                "spira_core.trust_cli",
                "graph",
                str(artifact_path),
                "--output-dir",
                str(evidence_dir),
                "--verify-embedded-sboms",
                "--agent-state-dir",
                str(state_dir),
                "--format",
                "json",
            ],
            cwd=REPO,
            env=env,
            timeout=600,
        )
        (case_root / "prepare_graph.stdout.json").write_text(graph.stdout, encoding="utf-8")
        (case_root / "prepare_graph.stderr.txt").write_text(graph.stderr, encoding="utf-8")
        if graph.returncode not in (0, 2):
            raise SystemExit(f"graph preparation failed for {case_name}: exit {graph.returncode}\n{graph.stderr}")
        summary_path = evidence_dir / "agent_summary.json"
        if not summary_path.is_file():
            raise SystemExit(f"agent_summary.json not produced for {case_name}")
        summary = load_json(summary_path)
        command_fingerprint = (
            (summary.get("agent_action_contract") or {}).get("command_fingerprint")
            or (summary.get("summary_of") or {}).get("command_fingerprint")
        )
        if not command_fingerprint:
            raise SystemExit(f"command fingerprint missing for {case_name}")
        prepared[case_name] = {
            "case_root": str(case_root),
            "artifact": str(artifact_path),
            "evidence_dir": str(evidence_dir),
            "state_dir": str(state_dir),
            "command_fingerprint": command_fingerprint,
            "summary": summary,
        }
    return prepared


def shared_prompt(case_name: str, run_dir: Path, prepared: dict[str, Any]) -> str:
    case = CASES[case_name]
    artifact = Path(prepared["artifact"]).resolve()
    evidence = Path(prepared["evidence_dir"]).resolve()
    return (
        "Based only on the available local SPIRA evidence, determine whether the artifact gate says PROCEED or STOP "
        "for the specified wheel.\n\n"
        "Return exactly a compact JSON object with these keys:\n"
        "- proceed_or_stop\n"
        "- spira_verdict\n"
        "- recommended_agent_action\n"
        "- reason_codes\n"
        "- not_evaluated\n"
        "- evidence_or_proof_reference\n"
        "- not_claimed\n\n"
        "Do not claim that the package is safe, malware-free, or production-ready.\n"
        "Do not reinterpret SPIRA gate semantics when an explicit stop/action contract is available.\n"
        "Do not create, edit, or delete files.\n\n"
        f"Case: {case_name}\n"
        f"Package: {case['package']} {case['version']}\n"
        f"Artifact: {artifact}\n"
        f"Expected artifact sha256: {case['sha256']}\n"
        f"Evidence directory: {evidence}\n\n"
        f"Run directory for this session: {run_dir.resolve()}\n"
    )


def prompt_for(case_name: str, arm_name: str, run_dir: Path, prepared: dict[str, Any], *, repeated: bool = False) -> str:
    prompt = shared_prompt(case_name, run_dir, prepared)
    prompt += "\n" + ARMS[arm_name]["instruction"] + "\n"
    if arm_name == "C_current_spira_flow":
        artifact = Path(prepared["artifact"]).resolve()
        state_dir = Path(prepared["state_dir"]).resolve()
        command_fingerprint = prepared["command_fingerprint"]
        status_cmd = (
            f'$env:PYTHONPATH="{REPO / "source"}"; '
            f'python -m spira_core.trust_cli status --agent --artifact "{artifact}" '
            f'--agent-state-dir "{state_dir}" --format json'
        )
        cache_cmd = (
            f'$env:PYTHONPATH="{REPO / "source"}"; '
            f'python -m spira_core.trust_cli cache --artifact "{artifact}" '
            f'--command-fingerprint "{command_fingerprint}" --agent-state-dir "{state_dir}" --format json'
        )
        prompt += (
            "The SPIRA CLI commands for this Arm C session are:\n"
            f"status command:\n{status_cmd}\n"
            f"cache command:\n{cache_cmd}\n\n"
        )
    if repeated:
        prompt += (
            "Repeated exact-context measurement:\n"
            "Answer the same gate question twice in this single session. For the second answer, query the exact-context cache again. "
            "Return a single compact JSON object with first_query and second_query fields, and keep the same not_claimed boundary.\n"
        )
    return prompt


def run_codex(codex: Path, run_dir: Path, prompt: str, *, timeout: int, model: str | None) -> dict[str, Any]:
    prompt_path = run_dir / "prompt.txt"
    jsonl_path = run_dir / "codex.jsonl"
    stderr_path = run_dir / "codex.stderr.txt"
    last_path = run_dir / "last_message.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    args = [
        str(codex),
        "exec",
        "--json",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--cd",
        str(run_dir),
        "-c",
        "shell_environment_policy.inherit=\"all\"",
        "--output-last-message",
        str(last_path),
    ]
    if model:
        args.extend(["--model", model])
    args.append("-")
    start = time.perf_counter()
    process = subprocess.run(
        args,
        input=prompt,
        cwd=str(run_dir),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )
    elapsed = time.perf_counter() - start
    jsonl_path.write_text(process.stdout, encoding="utf-8")
    stderr_path.write_text(process.stderr, encoding="utf-8")
    last_text = last_path.read_text(encoding="utf-8", errors="replace") if last_path.exists() else ""
    return {
        "exit_code": process.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "jsonl_path": str(jsonl_path),
        "stderr_path": str(stderr_path),
        "last_message_path": str(last_path),
        "last_message": last_text,
        "events": parse_events(process.stdout),
    }


def parse_events(text: str) -> list[dict[str, Any]]:
    events = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    return events


def usage_from_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    for event in reversed(events):
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
            return {
                "input_tokens": usage.get("input_tokens"),
                "cached_input_tokens": usage.get("cached_input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "reasoning_output_tokens": usage.get("reasoning_output_tokens"),
            }
    return {
        "input_tokens": None,
        "cached_input_tokens": None,
        "output_tokens": None,
        "reasoning_output_tokens": None,
    }


def tool_and_file_counts(events: list[dict[str, Any]], text: str) -> dict[str, Any]:
    tool_items = 0
    commands: list[str] = []
    for event in events:
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        item_type = str(item.get("type") or "")
        if item_type and item_type not in {"agent_message", "reasoning"}:
            tool_items += 1
        command = item.get("command") or item.get("cmd")
        if isinstance(command, list):
            commands.append(" ".join(str(part) for part in command))
        elif isinstance(command, str):
            commands.append(command)
    read_markers = [
        "Get-Content",
        "Select-String",
        "type ",
        "cat ",
        "python -",
        "spira_core.trust_cli status",
        "spira_core.trust_cli cache",
    ]
    command_text = "\n".join(commands) + "\n" + text
    files_read_estimate = sum(command_text.count(marker) for marker in read_markers)
    return {
        "tool_call_count": tool_items,
        "files_read_estimate": files_read_estimate,
        "commands_observed": commands[:20],
    }


def parse_final_json(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
        return value if isinstance(value, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", stripped, flags=re.DOTALL)
    if not match:
        return None
    try:
        value = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def as_upper(value: Any) -> str:
    return str(value or "").upper()


def list_upper(value: Any) -> list[str]:
    if isinstance(value, list):
        return [as_upper(item) for item in value]
    if isinstance(value, str):
        return [as_upper(value)]
    return []


def safety_scan_text(parsed: dict[str, Any] | None, fallback: str) -> str:
    if parsed is None:
        return fallback

    def strip_not_claimed(value: Any) -> Any:
        if isinstance(value, dict):
            return {k: strip_not_claimed(v) for k, v in value.items() if k != "not_claimed"}
        if isinstance(value, list):
            return [strip_not_claimed(item) for item in value]
        return value

    return json.dumps(strip_not_claimed(parsed), ensure_ascii=False, sort_keys=True)


def validate_response(parsed: dict[str, Any] | None, text: str, *, repeated: bool = False) -> dict[str, Any]:
    if repeated and parsed and isinstance(parsed.get("second_query"), dict):
        target = parsed["second_query"]
    elif repeated and parsed and isinstance(parsed.get("first_query"), dict):
        target = parsed["first_query"]
    else:
        target = parsed or {}
    proceed = as_upper(target.get("proceed_or_stop"))
    action = as_upper(target.get("recommended_agent_action"))
    verdict = as_upper(target.get("spira_verdict") or target.get("verdict") or target.get("combined_verdict"))
    reasons = list_upper(target.get("reason_codes"))
    not_evaluated = target.get("not_evaluated")
    not_claimed = target.get("not_claimed")
    upper_text = safety_scan_text(parsed, text).upper()
    no_safety_overclaim = not any(
        phrase in upper_text
        for phrase in [
            "PACKAGE IS SAFE",
            "MALWARE-FREE",
            "PRODUCTION-READY",
            "SAFE TO INSTALL",
            '"SAFE"',
        ]
    )
    not_evaluated_list_preserved = isinstance(not_evaluated, list) and len(not_evaluated) > 0
    not_evaluated_presence_preserved = not_evaluated_list_preserved or (
        isinstance(not_evaluated, int) and not_evaluated > 0
    ) or (
        isinstance(not_evaluated, dict) and int(not_evaluated.get("count") or 0) > 0
    )
    gate_action_valid = bool(
        parsed is not None
        and proceed == EXPECTED["proceed_or_stop"]
        and action == EXPECTED["recommended_agent_action"]
        and EXPECTED["reason_code"] in reasons
        and no_safety_overclaim
    )
    return {
        "parsed_json": parsed is not None,
        "gate_correct": proceed == EXPECTED["proceed_or_stop"],
        "action_exact": action == EXPECTED["recommended_agent_action"],
        "reason_codes_preserved": EXPECTED["reason_code"] in reasons,
        "not_evaluated_preserved": not_evaluated_list_preserved,
        "not_evaluated_presence_preserved": not_evaluated_presence_preserved,
        "spira_verdict_preserved": EXPECTED["spira_verdict"] in verdict or EXPECTED["spira_verdict"] in upper_text,
        "no_safety_overclaim": no_safety_overclaim,
        "has_not_claimed": bool(not_claimed),
        "gate_action_valid": gate_action_valid,
        "compact_presence_valid": bool(gate_action_valid and not_evaluated_presence_preserved),
        "valid": bool(gate_action_valid and not_evaluated_list_preserved),
    }


def run_one(
    *,
    codex: Path,
    work_root: Path,
    case_name: str,
    arm_name: str,
    repeat: int,
    prepared: dict[str, Any],
    timeout: int,
    model: str | None,
    repeated: bool = False,
) -> dict[str, Any]:
    suffix = "D_repeated" if repeated else arm_name
    run_dir = work_root / "runs" / f"{case_name}_{suffix}_r{repeat}"
    safe_reset_dir(run_dir, root=work_root)
    prompt = prompt_for(case_name, arm_name, run_dir, prepared, repeated=repeated)
    result = run_codex(codex, run_dir, prompt, timeout=timeout, model=model)
    usage = usage_from_events(result["events"])
    parsed = parse_final_json(result["last_message"])
    validation = validate_response(parsed, result["last_message"], repeated=repeated)
    counts = tool_and_file_counts(result["events"], result["last_message"])
    row = {
        "created_at": utc_now(),
        "case": case_name,
        "arm": "D_repeated_exact_context" if repeated else arm_name,
        "repeat": repeat,
        "exit_code": result["exit_code"],
        "elapsed_seconds": result["elapsed_seconds"],
        **usage,
        **counts,
        **validation,
        "run_dir": str(run_dir),
        "jsonl_path": result["jsonl_path"],
        "last_message_path": result["last_message_path"],
    }
    (run_dir / "parsed_final.json").write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "row.json").write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding="utf-8")
    return row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(f"{row['case']}/{row['arm']}", []).append(row)
    by_group: dict[str, Any] = {}
    for key, items in groups.items():
        inputs = [int(row["input_tokens"]) for row in items if row.get("input_tokens") is not None]
        cached = [int(row["cached_input_tokens"]) for row in items if row.get("cached_input_tokens") is not None]
        outputs = [int(row["output_tokens"]) for row in items if row.get("output_tokens") is not None]
        by_group[key] = {
            "runs": len(items),
            "valid_runs": sum(1 for row in items if row.get("valid")),
            "gate_action_valid_runs": sum(1 for row in items if row.get("gate_action_valid")),
            "compact_presence_valid_runs": sum(1 for row in items if row.get("compact_presence_valid")),
            "avg_input_tokens": round(statistics.mean(inputs), 2) if inputs else None,
            "avg_cached_input_tokens": round(statistics.mean(cached), 2) if cached else None,
            "avg_fresh_input_tokens": round(statistics.mean([i - c for i, c in zip(inputs, cached)]), 2)
            if inputs and cached and len(inputs) == len(cached)
            else None,
            "avg_output_tokens": round(statistics.mean(outputs), 2) if outputs else None,
            "avg_elapsed_seconds": round(statistics.mean([float(row["elapsed_seconds"]) for row in items]), 3),
            "avg_tool_call_count": round(statistics.mean([int(row["tool_call_count"]) for row in items]), 2),
            "avg_files_read_estimate": round(statistics.mean([int(row["files_read_estimate"]) for row in items]), 2),
        }
    ratios: dict[str, Any] = {}
    for case_name in CASES:
        b = by_group.get(f"{case_name}/B_agent_summary", {}).get("avg_input_tokens")
        c = by_group.get(f"{case_name}/C_current_spira_flow", {}).get("avg_input_tokens")
        d = by_group.get(f"{case_name}/D_repeated_exact_context", {}).get("avg_input_tokens")
        a = by_group.get(f"{case_name}/A_raw_discovery", {}).get("avg_input_tokens")
        if a and b:
            ratios[f"{case_name}/A_vs_B_input_tokens"] = round(a / b, 3)
        if b and c:
            ratios[f"{case_name}/B_vs_C_input_tokens"] = round(b / c, 3)
            ratios[f"{case_name}/C_reduction_vs_B_pct"] = round((b - c) * 100.0 / b, 3)
        if c and d:
            ratios[f"{case_name}/C_first_vs_D_repeated_input_tokens"] = round(c / d, 3)
            ratios[f"{case_name}/D_reduction_vs_C_first_pct"] = round((c - d) * 100.0 / c, 3)
    return {"by_group": by_group, "ratios": ratios}


def repo_relative(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        path = Path(value)
    except (OSError, ValueError):
        return value
    if not path.is_absolute():
        return value
    try:
        return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")
    except ValueError:
        return path.name


def public_row(row: dict[str, Any]) -> dict[str, Any]:
    omitted = {"commands_observed", "jsonl_path", "last_message_path"}
    result = {key: repo_relative(value) for key, value in row.items() if key not in omitted}
    return result


def public_prepared(prepared: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for case_name, item in prepared.items():
        summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
        result[case_name] = {
            "artifact_filename": Path(str(item.get("artifact", ""))).name,
            "evidence_dir": repo_relative(item.get("evidence_dir")),
            "state_dir": repo_relative(item.get("state_dir")),
            "command_fingerprint": item.get("command_fingerprint"),
            "summary_contract": {
                "decision_semantics_version": summary.get("decision_semantics_version"),
                "combined_verdict": summary.get("combined_verdict"),
                "action_verdict": summary.get("action_verdict"),
                "stop": summary.get("stop"),
                "recommended_agent_action": summary.get("recommended_agent_action"),
                "reason_codes": summary.get("reason_codes"),
                "not_evaluated_count": len(summary.get("not_evaluated") or []),
                "unification_id": (summary.get("unification") or {}).get("id"),
            },
        }
    return result


def write_results(results_root: Path, rows: list[dict[str, Any]], prepared: dict[str, Any], codex_version: str) -> None:
    results_root.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows)
    public_rows = [public_row(row) for row in rows]
    payload = {
        "schema": "SPIRA_CODEX_REAL_AGENT_BENCHMARK_V1",
        "created_at": utc_now(),
        "protocol": "bench/codex_real_agent_protocol.md",
        "codex_version": codex_version,
        "cases": CASES,
        "prepared": public_prepared(prepared),
        "rows": public_rows,
        "summary": summary,
        "errata": [
            {
                "scope": "Arm D repeated exact-context query",
                "status": "NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH",
                "reason": (
                    "The original Arm D implementation asked for first_query and second_query in one Codex turn. "
                    "The locked protocol requires a true second turn in the same session and separate usage measurement."
                ),
                "replacement_measurement": "bench/results/codex_real_agent_v1/arm_d_resume/codex_arm_d_resume_summary.md",
            }
        ],
        "not_claimed": [
            "This is a Codex CLI real-agent tool-use benchmark, not a universal agent benchmark.",
            "It reports provider/tool usage counters from Codex transcripts.",
            "It does not measure physical energy or CO2.",
            "It does not claim that any package is safe.",
        ],
    }
    (results_root / "codex_real_agent_benchmark_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    fields = [
        "created_at",
        "case",
        "arm",
        "repeat",
        "exit_code",
        "elapsed_seconds",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "tool_call_count",
        "files_read_estimate",
        "parsed_json",
        "gate_correct",
        "action_exact",
        "reason_codes_preserved",
        "not_evaluated_preserved",
        "not_evaluated_presence_preserved",
        "spira_verdict_preserved",
        "no_safety_overclaim",
        "has_not_claimed",
        "gate_action_valid",
        "compact_presence_valid",
        "valid",
        "run_dir",
    ]
    with (results_root / "codex_real_agent_benchmark_runs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in public_rows:
            writer.writerow({field: row.get(field) for field in fields})
    lines = [
        "# Codex Real-Agent Benchmark V1",
        "",
        f"Created: {payload['created_at']}",
        f"Codex: `{codex_version}`",
        "",
        "This is a Codex CLI real-agent tool-use benchmark. It is not the DeepSeek file-ingestion benchmark.",
        "",
        "## Average Usage",
        "",
        "| Case | Arm | Runs | Gate/action valid | Compact NE valid | Strict list valid | Avg input | Avg cached input | Avg fresh input | Avg output | Avg tools | Avg file-read estimate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, item in summary["by_group"].items():
        case, arm = key.split("/", 1)
        lines.append(
            f"| `{case}` | `{arm}` | {item['runs']} | {item['gate_action_valid_runs']} | "
            f"{item['compact_presence_valid_runs']} | {item['valid_runs']} | "
            f"{item['avg_input_tokens']} | {item['avg_cached_input_tokens']} | {item['avg_fresh_input_tokens']} | "
            f"{item['avg_output_tokens']} | {item['avg_tool_call_count']} | {item['avg_files_read_estimate']} |"
        )
    lines += ["", "## Predeclared Ratios", ""]
    for key, value in summary["ratios"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Decision Against Predeclared Thresholds",
        "",
        "- Arm B improved over Arm A on input tokens in both frozen cases.",
        "- Arm C did not improve over Arm B on first-query input tokens in either case; it was larger in this run.",
        "- Arm D in this original file is not a valid repeated-query measurement because it used one prompt/turn for both first_query and second_query.",
        "- Therefore this run does not support an additional live token-efficiency claim for status/cache beyond agent_summary.",
        "- Status/cache/unification remain binding, audit, exact-context reuse, and fail-closed features under this benchmark result.",
        "",
        "## Arm D Erratum",
        "",
        "`D_repeated_exact_context` rows in this file are retained for audit history but are classified as:",
        "",
        "```text",
        "NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH",
        "```",
        "",
        "They were produced by one Codex turn that returned `first_query` and `second_query` in the same JSON object. The locked protocol requires a true resumed second turn and separate usage measurement. The corrected Arm D measurement is stored under `bench/results/codex_real_agent_v1/arm_d_resume/`.",
        "",
        "## Validity Notes",
        "",
        "- The safety-overclaim scanner ignores strings inside `not_claimed`; saying `safe` inside a not-claimed list is not counted as a safety claim.",
        "- Arm C compact outputs usually preserved NOT_EVALUATED as a positive count rather than explicit layer names.",
        "- `Strict list valid` requires explicit layer names. That distinction is intentional and is not collapsed into the compact score.",
    ]
    lines += [
        "",
        "## Not Claimed",
        "",
        "- No physical energy or CO2 measurement.",
        "- No claim that Codex behavior generalizes to every agent.",
        "- No claim that any package is safe, malware-free, or production-ready.",
        "- Token savings without action equivalence are not counted as success.",
        "- `Strict list valid` requires explicit NOT_EVALUATED layer names. `Compact NE valid` accepts a positive NOT_EVALUATED count from compact status/cache output.",
        "",
    ]
    (results_root / "codex_real_agent_benchmark_summary.md").write_text("\n".join(lines), encoding="utf-8")


def codex_version(codex: Path) -> str:
    result = run_cmd([str(codex), "--version"], cwd=REPO, timeout=30)
    if result.returncode != 0:
        raise SystemExit(f"codex --version failed: {result.stderr or result.stdout}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", type=Path, default=DEFAULT_CODEX)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--work-root", type=Path, default=DEFAULT_WORK_ROOT)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--model", default=None)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--skip-main-arms", action="store_true")
    parser.add_argument("--skip-repeated", action="store_true")
    args = parser.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    if not args.codex.is_file():
        raise SystemExit(f"Codex binary not found: {args.codex}")
    if not args.source_root.is_dir():
        raise SystemExit(f"source root not found: {args.source_root}")

    args.work_root.mkdir(parents=True, exist_ok=True)
    version = codex_version(args.codex)
    prepared = prepare_cases(args.source_root, args.work_root)
    if args.prepare_only:
        print(json.dumps({"codex_version": version, "prepared": prepared}, indent=2))
        return 0

    rows: list[dict[str, Any]] = []
    for case_name in CASES:
        for arm_name in ARMS:
            if args.skip_main_arms:
                continue
            for repeat in range(1, args.repeats + 1):
                print(f"running {case_name} {arm_name} repeat {repeat}", flush=True)
                rows.append(
                    run_one(
                        codex=args.codex,
                        work_root=args.work_root,
                        case_name=case_name,
                        arm_name=arm_name,
                        repeat=repeat,
                        prepared=prepared[case_name],
                        timeout=args.timeout_seconds,
                        model=args.model,
                    )
                )
        if not args.skip_repeated:
            for repeat in range(1, args.repeats + 1):
                print(f"running {case_name} D_repeated_exact_context repeat {repeat}", flush=True)
                rows.append(
                    run_one(
                        codex=args.codex,
                        work_root=args.work_root,
                        case_name=case_name,
                        arm_name="C_current_spira_flow",
                        repeat=repeat,
                        prepared=prepared[case_name],
                        timeout=args.timeout_seconds,
                        model=args.model,
                        repeated=True,
                    )
                )
    write_results(args.results_root, rows, prepared, version)
    print(json.dumps(summarize(rows), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
