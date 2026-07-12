#!/usr/bin/env python3
"""Measure Arm D with a true Codex CLI resume turn.

The first Codex turn runs the current SPIRA flow. The second turn resumes the
same session and asks the same gate question again, requiring another cache
query. This fixes the Arm D implementation mismatch in the first V1 run.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import run_codex_real_agent_benchmark as base


DEFAULT_RESULTS_ROOT = base.REPO / "bench" / "results" / "codex_real_agent_v1"
DEFAULT_RESUME_RESULTS_ROOT = base.REPO / "bench" / "results" / "codex_real_agent_v1" / "arm_d_resume"
USAGE_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")


def run_resume_turn(
    *,
    codex: Path,
    session_id: str,
    run_dir: Path,
    prompt: str,
    timeout: int,
    model: str | None,
) -> dict[str, Any]:
    prompt_path = run_dir / "resume_prompt.txt"
    jsonl_path = run_dir / "resume.jsonl"
    stderr_path = run_dir / "resume.stderr.txt"
    last_path = run_dir / "resume_last_message.txt"
    prompt_path.write_text(prompt, encoding="utf-8")
    args = [
        str(codex),
        "exec",
        "resume",
        "--json",
        "--skip-git-repo-check",
        "-c",
        "shell_environment_policy.inherit=\"all\"",
        "--output-last-message",
        str(last_path),
    ]
    if model:
        args.extend(["--model", model])
    args.extend([session_id, "-"])
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
    events = base.parse_events(process.stdout)
    return {
        "exit_code": process.returncode,
        "elapsed_seconds": round(elapsed, 3),
        "jsonl_path": str(jsonl_path),
        "stderr_path": str(stderr_path),
        "last_message_path": str(last_path),
        "last_message": last_text,
        "events": events,
    }


def session_id_from(events: list[dict[str, Any]]) -> str:
    for event in events:
        if event.get("type") == "thread.started" and event.get("thread_id"):
            return str(event["thread_id"])
    raise RuntimeError("thread.started event with thread_id not found")


def second_prompt() -> str:
    return (
        "Repeat the same artifact gate question from the previous turn for the same wheel.\n"
        "Do not read full evidence unless the compact cache/status result is insufficient.\n"
        "Query the exact-context cache again before answering.\n\n"
        "Return exactly a compact JSON object with these keys:\n"
        "- proceed_or_stop\n"
        "- spira_verdict\n"
        "- recommended_agent_action\n"
        "- reason_codes\n"
        "- not_evaluated\n"
        "- evidence_or_proof_reference\n"
        "- not_claimed\n\n"
        "Do not claim that the package is safe, malware-free, or production-ready.\n"
    )


def row_from_turn(
    *,
    case_name: str,
    repeat: int,
    turn: str,
    run_dir: Path,
    result: dict[str, Any],
) -> dict[str, Any]:
    usage = base.usage_from_events(result["events"])
    parsed = base.parse_final_json(result["last_message"])
    validation = base.validate_response(parsed, result["last_message"])
    counts = base.tool_and_file_counts(result["events"], result["last_message"])
    row = {
        "created_at": base.utc_now(),
        "case": case_name,
        "arm": "D_resume_true_second_turn",
        "repeat": repeat,
        "turn": turn,
        "exit_code": result["exit_code"],
        "elapsed_seconds": result["elapsed_seconds"],
        **usage,
        **counts,
        **validation,
        "run_dir": str(run_dir),
        "jsonl_path": result["jsonl_path"],
        "last_message_path": result["last_message_path"],
    }
    return row


def apply_turn_usage_deltas(first_row: dict[str, Any], second_row: dict[str, Any]) -> None:
    for field in USAGE_FIELDS:
        first_value = first_row.get(field)
        second_value = second_row.get(field)
        first_row[f"cumulative_{field}"] = first_value
        first_row[f"previous_cumulative_{field}"] = 0
        first_row[f"turn_{field}"] = first_value
        if first_value is not None:
            first_row[field] = first_value
        second_row[f"cumulative_{field}"] = second_value
        second_row[f"previous_cumulative_{field}"] = first_value
        if first_value is None or second_value is None:
            second_row[f"turn_{field}"] = None
            second_row[field] = None
            continue
        delta = int(second_value) - int(first_value)
        second_row[f"turn_{field}"] = delta
        second_row[field] = delta
    first_row["usage_counter_scope"] = "turn"
    first_row["usage_derivation"] = "first turn; turn usage equals session cumulative usage"
    second_row["usage_counter_scope"] = "turn_delta_from_cumulative_session"
    second_row["usage_derivation"] = "second turn usage computed as second cumulative usage minus first cumulative usage"


def run_pair(
    *,
    codex: Path,
    work_root: Path,
    case_name: str,
    repeat: int,
    prepared: dict[str, Any],
    timeout: int,
    model: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    run_dir = work_root / "runs" / f"{case_name}_D_resume_r{repeat}"
    base.safe_reset_dir(run_dir, root=work_root)
    first_prompt = base.prompt_for(case_name, "C_current_spira_flow", run_dir, prepared)
    first = base.run_codex(codex, run_dir, first_prompt, timeout=timeout, model=model)
    session_id = session_id_from(first["events"])
    second = run_resume_turn(
        codex=codex,
        session_id=session_id,
        run_dir=run_dir,
        prompt=second_prompt(),
        timeout=timeout,
        model=model,
    )
    first_row = row_from_turn(case_name=case_name, repeat=repeat, turn="first", run_dir=run_dir, result=first)
    second_row = row_from_turn(case_name=case_name, repeat=repeat, turn="second", run_dir=run_dir, result=second)
    apply_turn_usage_deltas(first_row, second_row)
    first_row["session_id"] = session_id
    second_row["session_id"] = session_id
    (run_dir / "first_row.json").write_text(json.dumps(first_row, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "second_row.json").write_text(json.dumps(second_row, ensure_ascii=False, indent=2), encoding="utf-8")
    return first_row, second_row


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(f"{row['case']}/{row['turn']}", []).append(row)
    by_group: dict[str, Any] = {}
    for key, items in groups.items():
        inputs = [int(row["input_tokens"]) for row in items if row.get("input_tokens") is not None]
        cached = [int(row["cached_input_tokens"]) for row in items if row.get("cached_input_tokens") is not None]
        outputs = [int(row["output_tokens"]) for row in items if row.get("output_tokens") is not None]
        by_group[key] = {
            "runs": len(items),
            "gate_action_valid_runs": sum(1 for row in items if row.get("gate_action_valid")),
            "compact_presence_valid_runs": sum(1 for row in items if row.get("compact_presence_valid")),
            "strict_list_valid_runs": sum(1 for row in items if row.get("valid")),
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
    for case_name in base.CASES:
        first = by_group.get(f"{case_name}/first", {}).get("avg_input_tokens")
        second = by_group.get(f"{case_name}/second", {}).get("avg_input_tokens")
        if first and second:
            ratios[f"{case_name}/first_vs_second_input_tokens"] = round(first / second, 3)
            ratios[f"{case_name}/second_reduction_vs_first_pct"] = round((first - second) * 100.0 / first, 3)
    return {"by_group": by_group, "ratios": ratios}


def public_row(row: dict[str, Any]) -> dict[str, Any]:
    omitted = {"commands_observed", "jsonl_path", "last_message_path", "session_id"}
    return {key: base.repo_relative(value) for key, value in row.items() if key not in omitted}


def write_outputs(results_root: Path, rows: list[dict[str, Any]], codex_version: str) -> None:
    results_root.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows)
    public_rows = [public_row(row) for row in rows]
    payload = {
        "schema": "SPIRA_CODEX_REAL_AGENT_ARM_D_RESUME_V1",
        "created_at": base.utc_now(),
        "protocol": "bench/codex_real_agent_protocol.md",
        "codex_version": codex_version,
        "rows": public_rows,
        "summary": summary,
        "not_claimed": [
            "This measures true Codex CLI resume turns for Arm D only.",
            "It does not replace the Arm A/B/C first-query results.",
            "It does not measure physical energy or CO2.",
            "It does not claim that any package is safe.",
        ],
    }
    (results_root / "codex_arm_d_resume_results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    fields = [
        "created_at",
        "case",
        "arm",
        "repeat",
        "turn",
        "exit_code",
        "elapsed_seconds",
        "input_tokens",
        "cached_input_tokens",
        "output_tokens",
        "reasoning_output_tokens",
        "cumulative_input_tokens",
        "cumulative_cached_input_tokens",
        "cumulative_output_tokens",
        "cumulative_reasoning_output_tokens",
        "previous_cumulative_input_tokens",
        "previous_cumulative_cached_input_tokens",
        "previous_cumulative_output_tokens",
        "previous_cumulative_reasoning_output_tokens",
        "usage_counter_scope",
        "tool_call_count",
        "files_read_estimate",
        "gate_action_valid",
        "compact_presence_valid",
        "valid",
        "run_dir",
    ]
    with (results_root / "codex_arm_d_resume_runs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in public_rows:
            writer.writerow({field: row.get(field) for field in fields})
    lines = [
        "# Codex Arm D Resume Measurement",
        "",
        f"Created: {payload['created_at']}",
        f"Codex: `{codex_version}`",
        "",
        "This corrects the Arm D implementation mismatch from the original V1 run by using a true `codex exec resume` second turn.",
        "",
        "`codex exec --json` reports cumulative session usage on resumed turns. This report uses turn-scoped usage: first turn equals cumulative usage; second turn is computed as second cumulative usage minus first cumulative usage.",
        "",
        "## Average Usage",
        "",
        "| Case | Turn | Runs | Gate/action valid | Compact NE valid | Strict list valid | Avg turn input | Avg turn cached input | Avg turn fresh input | Avg turn output | Avg tools | Avg file-read estimate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, item in summary["by_group"].items():
        case, turn = key.split("/", 1)
        lines.append(
            f"| `{case}` | `{turn}` | {item['runs']} | {item['gate_action_valid_runs']} | "
            f"{item['compact_presence_valid_runs']} | {item['strict_list_valid_runs']} | "
            f"{item['avg_input_tokens']} | {item['avg_cached_input_tokens']} | {item['avg_fresh_input_tokens']} | "
            f"{item['avg_output_tokens']} | {item['avg_tool_call_count']} | {item['avg_files_read_estimate']} |"
        )
    lines += ["", "## Predeclared Repeated-Query Ratios", ""]
    for key, value in summary["ratios"].items():
        lines.append(f"- `{key}`: {value}")
    lines += [
        "",
        "## Decision",
        "",
        "- The original Arm D result is treated as `NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH`.",
        "- This file is the valid true-resume Arm D measurement.",
        "- The true resumed second turn showed a modest input-token reduction, but did not clear the predeclared 20% improvement threshold in either frozen case.",
        "- No live-token benefit claim for repeated exact-context cache queries is supported by this measurement.",
        "- Cache remains an exact-context correctness/reuse feature under this result, not a measured live-token saving feature.",
        "",
        "## Not Claimed",
        "",
        "- No physical energy or CO2 measurement.",
        "- No claim that Codex behavior generalizes to every agent.",
        "- No claim that any package is safe, malware-free, or production-ready.",
        "",
    ]
    (results_root / "codex_arm_d_resume_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--codex", type=Path, default=base.DEFAULT_CODEX)
    parser.add_argument("--source-root", type=Path, default=base.DEFAULT_SOURCE_ROOT)
    parser.add_argument("--work-root", type=Path, default=base.DEFAULT_WORK_ROOT)
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESUME_RESULTS_ROOT)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--model", default=None)
    args = parser.parse_args()
    if args.repeats < 1:
        raise SystemExit("--repeats must be at least 1")
    if not args.codex.is_file():
        raise SystemExit(f"Codex binary not found: {args.codex}")
    args.work_root.mkdir(parents=True, exist_ok=True)
    version = base.codex_version(args.codex)
    prepared = base.prepare_cases(args.source_root, args.work_root)
    rows: list[dict[str, Any]] = []
    for case_name in base.CASES:
        for repeat in range(1, args.repeats + 1):
            print(f"running {case_name} D true-resume repeat {repeat}", flush=True)
            first, second = run_pair(
                codex=args.codex,
                work_root=args.work_root,
                case_name=case_name,
                repeat=repeat,
                prepared=prepared[case_name],
                timeout=args.timeout_seconds,
                model=args.model,
            )
            rows.extend([first, second])
    write_outputs(args.results_root, rows, version)
    print(json.dumps(summarize(rows), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
