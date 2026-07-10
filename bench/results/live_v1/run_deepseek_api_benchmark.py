#!/usr/bin/env python3
"""Run a small live token benchmark through the DeepSeek Chat API.

This is deliberately an API file-ingestion benchmark, not a full autonomous
agent benchmark: each run sends a fixed evidence bundle to the model and records
the provider-reported token usage.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_KEY_FILE = Path.home() / "Desktop" / "spira api deep.txt"
API_URL = "https://api.deepseek.com/chat/completions"

CASES = {
    "median_minijinja": {
        "dir": ROOT / "median_minijinja",
        "label": "median SBOM bytes case",
        "expected": {
            "proceed_or_stop": "STOP",
            "recommended_agent_action": "REPORT_NOT_EVALUATED",
            "combined_verdict": "GRAPH_OK_WITH_NOTES",
        },
    },
    "p90_nutpie": {
        "dir": ROOT / "p90_nutpie",
        "label": "p90 SBOM bytes case",
        "expected": {
            "proceed_or_stop": "STOP",
            "recommended_agent_action": "REPORT_NOT_EVALUATED",
            "combined_verdict": "GRAPH_OK_WITH_NOTES",
        },
    },
}

ARMS = {
    "a_full_evidence": {
        "description": "Broad SPIRA evidence without agent_summary.json",
        "files": [
            "spira-decision.json",
            "graph_report.json",
            "bill_of_materials.json",
            "graph_summary.txt",
            "input_manifest.json",
            "graph_evidence_manifest.json",
        ],
    },
    "a_decision_only": {
        "description": "Minimal legacy baseline: spira-decision.json only",
        "files": ["spira-decision.json"],
    },
    "b_agent_summary": {
        "description": "SPIRA agent_summary.json only",
        "files": ["agent_summary.json"],
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_api_key(path: Path) -> str:
    env_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if env_key:
        return env_key
    if not path.exists():
        raise SystemExit(f"API key file not found: {path}")
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    match = re.search(r"\bsk-[A-Za-z0-9_\-]{20,}\b", text)
    if match:
        return match.group(0)
    lines = [line.strip().strip('"').strip("'") for line in text.splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    if not lines:
        raise SystemExit(f"API key file is empty: {path}")
    return lines[0]


def load_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def compose_user_prompt(case_name: str, arm_name: str) -> tuple[str, list[dict[str, Any]]]:
    case = CASES[case_name]
    arm = ARMS[arm_name]
    evidence_dir = case["dir"] / ("arm_b_spira_guided" if arm_name == "b_agent_summary" else "arm_a_no_guidance") / "evidence"
    files_payload = []
    for name in arm["files"]:
        path = evidence_dir / name
        content = load_file(path)
        files_payload.append(
            {
                "path": str(path),
                "name": name,
                "bytes": path.stat().st_size,
                "content": content,
            }
        )

    prompt = (
        "Based only on the local SPIRA evidence files provided below, decide whether "
        "the artifact gate says PROCEED or STOP.\n\n"
        "Return only a compact JSON object with these keys: proceed_or_stop, verdict, "
        "combined_verdict, recommended_agent_action, blockers, warnings, "
        "not_evaluated, evidence_paths_used, short_reason.\n\n"
        "Important rules:\n"
        "- Do not claim the package is safe.\n"
        "- NOT_EVALUATED is not OK.\n"
        "- If the evidence says stop=true or REPORT_NOT_EVALUATED, answer STOP.\n"
        "- If a field is not present in the provided files, say null or [].\n\n"
        f"Case: {case_name} ({case['label']})\n"
        f"Arm: {arm_name} ({arm['description']})\n\n"
    )
    for file_payload in files_payload:
        prompt += (
            f"\n--- FILE: {file_payload['name']} "
            f"({file_payload['bytes']} bytes) ---\n"
            f"{file_payload['content']}\n"
        )
    return prompt, files_payload


def call_deepseek(api_key: str, model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    body = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a precise artifact-gate assistant. Answer only from "
                    "the provided evidence. Do not add security claims."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "thinking": {"type": "disabled"},
        "stream": False,
    }
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "spira-trust-live-token-benchmark/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek API HTTP {exc.code}: {detail[:1000]}") from exc


def response_text(response: dict[str, Any]) -> str:
    try:
        message = response["choices"][0]["message"]
        return message.get("content") or message.get("reasoning_content") or ""
    except Exception:
        return ""


def finish_reason(response: dict[str, Any]) -> Any:
    try:
        return response["choices"][0].get("finish_reason")
    except Exception:
        return None


def usage_from(response: dict[str, Any]) -> dict[str, Any]:
    usage = response.get("usage") or {}
    return {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "prompt_cache_hit_tokens": usage.get("prompt_cache_hit_tokens"),
        "prompt_cache_miss_tokens": usage.get("prompt_cache_miss_tokens"),
    }


def correctness_flags(text: str) -> dict[str, bool]:
    parsed = parse_json_response(text)
    proceed_or_stop = str(parsed.get("proceed_or_stop", "")).upper() if parsed else ""
    recommended = str(parsed.get("recommended_agent_action", "")).upper() if parsed else ""
    not_evaluated = parsed.get("not_evaluated") if parsed else None
    upper = text.upper()
    return {
        "parsed_json": parsed is not None,
        "gate_correct_stop": proceed_or_stop == "STOP",
        "action_exact_report_not_evaluated": recommended == "REPORT_NOT_EVALUATED",
        "has_not_evaluated": isinstance(not_evaluated, list) and len(not_evaluated) > 0,
        "mentions_stop": "STOP" in upper,
        "mentions_report_not_evaluated": "REPORT_NOT_EVALUATED" in upper,
        "mentions_graph_ok_with_notes": "GRAPH_OK_WITH_NOTES" in upper,
        "claims_safe": " SAFE" in upper or '"SAFE"' in upper or "IS SAFE" in upper,
    }


def parse_json_response(text: str) -> dict[str, Any] | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(f"{row['case']}/{row['arm']}", []).append(row)

    by_group: dict[str, Any] = {}
    for key, group_rows in groups.items():
        totals = [int(row["total_tokens"]) for row in group_rows if row.get("total_tokens") is not None]
        prompts = [int(row["prompt_tokens"]) for row in group_rows if row.get("prompt_tokens") is not None]
        completions = [int(row["completion_tokens"]) for row in group_rows if row.get("completion_tokens") is not None]
        by_group[key] = {
            "runs": len(group_rows),
            "prompt_tokens_avg": round(statistics.mean(prompts), 2) if prompts else None,
            "completion_tokens_avg": round(statistics.mean(completions), 2) if completions else None,
            "total_tokens_avg": round(statistics.mean(totals), 2) if totals else None,
            "correct_runs": sum(
                1
                for row in group_rows
                if row.get("gate_correct_stop")
                and row.get("has_not_evaluated")
                and row.get("mentions_graph_ok_with_notes")
                and not row.get("claims_safe")
            ),
            "exact_action_runs": sum(1 for row in group_rows if row.get("action_exact_report_not_evaluated")),
        }

    ratios: dict[str, Any] = {}
    for case_name in CASES:
        summary_key = f"{case_name}/b_agent_summary"
        summary_avg = by_group.get(summary_key, {}).get("prompt_tokens_avg")
        if not summary_avg:
            continue
        for arm in ("a_full_evidence", "a_decision_only"):
            key = f"{case_name}/{arm}"
            avg = by_group.get(key, {}).get("prompt_tokens_avg")
            if avg:
                ratios[f"{case_name}/{arm}_vs_b_agent_summary_prompt_tokens"] = round(avg / summary_avg, 2)
    return {"by_group": by_group, "ratios": ratios}


def write_outputs(rows: list[dict[str, Any]], responses: list[dict[str, Any]], model: str) -> None:
    out_json = ROOT / "deepseek_api_benchmark_results.json"
    out_csv = ROOT / "deepseek_api_benchmark_runs.csv"
    out_md = ROOT / "deepseek_api_benchmark_summary.md"

    summary = summarize(rows)
    payload = {
        "schema": "SPIRA_DEEPSEEK_API_FILE_INGESTION_BENCHMARK_V1",
        "created_at": utc_now(),
        "model": model,
        "api_url": API_URL,
        "not_claimed": [
            "This is an API file-ingestion benchmark, not a full autonomous agent tool-use benchmark.",
            "It measures provider-reported token usage for fixed evidence prompts.",
            "It does not measure physical energy, latency economics, or CO2.",
        ],
        "rows": rows,
        "summary": summary,
        "responses": responses,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    fieldnames = [
        "created_at",
        "case",
        "arm",
        "repeat",
        "input_bytes",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "prompt_cache_hit_tokens",
        "prompt_cache_miss_tokens",
        "mentions_stop",
        "mentions_report_not_evaluated",
        "mentions_graph_ok_with_notes",
        "claims_safe",
        "parsed_json",
        "gate_correct_stop",
        "action_exact_report_not_evaluated",
        "has_not_evaluated",
    ]
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name) for name in fieldnames})

    lines = [
        "# DeepSeek API Benchmark Summary",
        "",
        f"Created: {payload['created_at']}",
        f"Model: `{model}`",
        "",
        "This is an API file-ingestion benchmark, not a full autonomous agent tool-use benchmark.",
        "",
        "## Average Tokens",
        "",
        "| Case | Arm | Runs | Avg prompt | Avg completion | Avg total | Correct runs | Exact action runs |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for key, item in summary["by_group"].items():
        case, arm = key.split("/", 1)
        lines.append(
            f"| {case} | {arm} | {item['runs']} | {item['prompt_tokens_avg']} | "
            f"{item['completion_tokens_avg']} | {item['total_tokens_avg']} | "
            f"{item['correct_runs']} | {item['exact_action_runs']} |"
        )
    lines += ["", "## Prompt Token Ratios", ""]
    for key, value in summary["ratios"].items():
        lines.append(f"- `{key}`: {value}x")
    lines += [
        "",
        "## Not Claimed",
        "",
        "- No physical energy / CO2 measurement.",
        "- No full autonomous tool-use agent measurement.",
        "- Correctness means the parsed JSON answered STOP, preserved a non-empty not_evaluated list, preserved GRAPH_OK_WITH_NOTES, and did not claim safety.",
        "- `exact_action_runs` in the JSON summary separately counts responses that preserved `recommended_agent_action: REPORT_NOT_EVALUATED` exactly.",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--model", default="deepseek-v4-flash")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--smoke", action="store_true", help="Run one tiny API request and exit.")
    args = parser.parse_args()

    if args.repeats < 1 and not args.smoke:
        raise SystemExit("--repeats must be at least 1")

    api_key = read_api_key(args.key_file)

    if args.smoke:
        response = call_deepseek(api_key, args.model, "Reply with exactly: SPIRA_DEEPSEEK_OK", 50)
        usage = usage_from(response)
        text = response_text(response).strip()
        print(f"smoke_status=ok model={args.model} total_tokens={usage.get('total_tokens')} reply={text[:80]}")
        return 0

    rows: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    for case_name in CASES:
        for arm_name in ARMS:
            prompt, files_payload = compose_user_prompt(case_name, arm_name)
            input_bytes = sum(item["bytes"] for item in files_payload)
            for repeat in range(1, args.repeats + 1):
                print(f"running case={case_name} arm={arm_name} repeat={repeat} input_bytes={input_bytes}")
                response = call_deepseek(api_key, args.model, prompt, args.max_tokens)
                usage = usage_from(response)
                text = response_text(response)
                flags = correctness_flags(text)
                row = {
                    "created_at": utc_now(),
                    "case": case_name,
                    "arm": arm_name,
                    "repeat": repeat,
                    "input_bytes": input_bytes,
                    **usage,
                    **flags,
                }
                rows.append(row)
                responses.append(
                    {
                        "case": case_name,
                        "arm": arm_name,
                        "repeat": repeat,
                        "usage": usage,
                        "finish_reason": finish_reason(response),
                        "correctness_flags": flags,
                        "text": text,
                    }
                )
                write_outputs(rows, responses, args.model)
                time.sleep(args.sleep_seconds)

    write_outputs(rows, responses, args.model)
    print(f"wrote {ROOT / 'deepseek_api_benchmark_summary.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
