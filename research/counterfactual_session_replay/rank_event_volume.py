from __future__ import annotations

import argparse
import csv
import hashlib
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "SPIRA_EVENT_VOLUME_RANKING_V1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Rank replay event classes by measured volume and context lifetime.")
    parser.add_argument("--replay-results-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    events = load_events(args.replay_results_dir)
    reuse = load_reuse(args.replay_results_dir)
    summary = json.loads((args.replay_results_dir / "counterfactual_results.json").read_text(encoding="utf-8"))["summary"]

    rankings = {
        "by_category": rank(events, reuse, ["category"]),
        "by_category_and_command": rank(events, reuse, ["category", "safe_command_class"]),
        "by_category_command_path": rank(events, reuse, ["category", "safe_command_class", "safe_path_class"]),
    }
    bounded = [row for row in rankings["by_category"] if row["tool_answerability_counts"].get("BOUNDED_SUMMARY", 0)]
    first_candidate = select_first_candidate(bounded)
    result = {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "source_replay": {
            "session_id": summary["session_id"],
            "session_sha256": summary["session_sha256"],
            "replay_final_status": summary["final_status"],
            "replay_valid": summary["replay_valid"],
            "event_count": summary["event_count"],
            "actual_fresh_input_tokens": summary["actual_fresh_input_tokens"],
            "actual_total_input_tokens": summary["actual_total_input_tokens"],
        },
        "measurement_rules": {
            "raw_visible_bytes": "measured UTF-8 byte size already persisted by the replay; raw content is not read from the transcript",
            "allocated_fresh_tokens": "modeled attribution from provider token usage using the locked replay allocation method",
            "context_exposure_byte_calls": "derived as raw_visible_bytes * (reuse_count + 1); this is not provider token usage",
            "bounded_summary": "candidate class only; no lower/realistic savings are counted without a measured producer output and sufficiency audit",
        },
        "rankings": rankings,
        "first_producer_candidate": first_candidate,
        "decision": {
            "status": "ONE_PRODUCER_MEASUREMENT_AUTHORIZED",
            "authorized_scope": first_candidate["producer_candidate"] if first_candidate else "NONE",
            "not_authorized": [
                "broad orchestrator",
                "multiple producers in parallel",
                "product claim",
                "lower/realistic savings claim before measured producer output",
            ],
        },
        "not_claimed": [
            "This ranking does not change the prior replay result.",
            "No new savings are claimed.",
            "Context exposure byte-calls are a derived ranking signal, not provider token billing.",
            "Producer selection is authorization for one measurement experiment only, not product build authorization.",
        ],
    }

    (args.output_dir / "event_volume_ranking_v1.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (args.output_dir / "event_volume_ranking_v1.md").write_text(render_markdown(result), encoding="utf-8")
    write_csv(args.output_dir / "event_volume_ranking_by_category.csv", rankings["by_category"])
    write_csv(args.output_dir / "event_volume_ranking_by_category_command.csv", rankings["by_category_and_command"])
    write_sha256s(args.output_dir)
    print(json.dumps(result["decision"], indent=2, ensure_ascii=False))
    return 0


def load_events(base: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with (base / "event_classification.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)
    return rows


def load_reuse(base: Path) -> dict[str, int]:
    reuse: dict[str, int] = {}
    with (base / "reuse_horizon.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            reuse[row["event_id"]] = int(float(row["reuse_count"] or 0))
    return reuse


def rank(events: list[dict[str, Any]], reuse: dict[str, int], keys: list[str]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        groups[tuple(event[key] for key in keys)].append(event)

    rows = []
    for group_key, items in groups.items():
        raw_bytes = [int(float(item["raw_visible_bytes"] or 0)) for item in items]
        fresh_tokens = [float(item["allocated_fresh_tokens"] or 0) for item in items]
        reuse_counts = [reuse.get(item["event_id"], 0) for item in items]
        exposure_bytes = [byte_count * (reuse_count + 1) for byte_count, reuse_count in zip(raw_bytes, reuse_counts)]
        exposure_tokens = [token_count * (reuse_count + 1) for token_count, reuse_count in zip(fresh_tokens, reuse_counts)]
        answerability = Counter(item["tool_answerability_class"] for item in items)
        rows.append(
            {
                "group": dict(zip(keys, group_key)),
                "event_count": len(items),
                "raw_visible_bytes_total": sum(raw_bytes),
                "allocated_fresh_tokens_total": round(sum(fresh_tokens), 3),
                "median_event_bytes": percentile(raw_bytes, 50),
                "p90_event_bytes": percentile(raw_bytes, 90),
                "median_reuse_count": percentile(reuse_counts, 50),
                "p90_reuse_count": percentile(reuse_counts, 90),
                "context_exposure_byte_calls_total": sum(exposure_bytes),
                "context_exposure_fresh_token_calls_total": round(sum(exposure_tokens), 3),
                "tool_answerability_counts": dict(answerability),
            }
        )
    rows.sort(key=lambda row: (row["context_exposure_byte_calls_total"], row["raw_visible_bytes_total"]), reverse=True)
    return rows


def select_first_candidate(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    # The first measurement should target a deterministic, queryable producer rather than
    # broad file-read/code-understanding replacement. Rank by observed persistence, then
    # prefer categories with mechanical semantics and clear drill-down.
    preference = {
        "TEST_OUTPUT": 100,
        "STATE_DISCOVERY": 95,
        "GIT_OUTPUT": 90,
        "BUILD_OUTPUT": 85,
        "SEARCH_OUTPUT": 70,
        "PYTHON_OUTPUT": 60,
        "FILE_READ_OUTPUT": 25,
    }

    def score(row: dict[str, Any]) -> tuple[float, int]:
        category = row["group"].get("category", "")
        return (float(row["context_exposure_byte_calls_total"]) * preference.get(category, 10), preference.get(category, 10))

    selected = max(rows, key=score)
    category = selected["group"]["category"]
    producer = {
        "TEST_OUTPUT": "Test/Error-Manifest",
        "STATE_DISCOVERY": "Workspace/State-Manifest",
        "GIT_OUTPUT": "Git/Change-Manifest",
        "BUILD_OUTPUT": "Build-Manifest",
        "SEARCH_OUTPUT": "Repo/Search-Manifest",
        "PYTHON_OUTPUT": "Script/Execution-Manifest",
        "FILE_READ_OUTPUT": "Repo-Manifest",
    }.get(category, "UNKNOWN")
    return {
        "producer_candidate": producer,
        "selected_category": category,
        "selection_reason": (
            "highest weighted candidate among BOUNDED_SUMMARY classes using measured context exposure "
            "and a deterministic-semantics preference; this authorizes one producer measurement only"
        ),
        "measured_row": selected,
    }


def percentile(values: list[int], pct: int) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = round(((pct / 100) * (len(ordered) - 1)))
    return int(ordered[index])


def render_markdown(result: dict[str, Any]) -> str:
    summary = result["source_replay"]
    candidate = result["first_producer_candidate"]
    lines = [
        "# Event Volume Ranking V1",
        "",
        "```text",
        f"source_session_id: {summary['session_id']}",
        f"source_replay_status: {summary['replay_final_status']}",
        f"source_replay_valid: {summary['replay_valid']}",
        f"event_count: {summary['event_count']}",
        f"actual_fresh_input_tokens: {summary['actual_fresh_input_tokens']}",
        "```",
        "",
        "## Decision",
        "",
        "```text",
        f"status: {result['decision']['status']}",
        f"authorized_scope: {result['decision']['authorized_scope']}",
        "```",
        "",
        "This does not authorize a broad orchestrator or multiple producers. It only selects one producer candidate for a measured output/sufficiency experiment.",
        "",
        "## Top Categories",
        "",
        "| rank | category | events | raw bytes | allocated fresh tokens | median bytes | p90 bytes | median reuse | p90 reuse | exposure byte-calls | answerability |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for index, row in enumerate(result["rankings"]["by_category"][:12], 1):
        group = row["group"]["category"]
        lines.append(
            f"| {index} | `{group}` | {row['event_count']} | {row['raw_visible_bytes_total']} | "
            f"{row['allocated_fresh_tokens_total']} | {row['median_event_bytes']} | {row['p90_event_bytes']} | "
            f"{row['median_reuse_count']} | {row['p90_reuse_count']} | {row['context_exposure_byte_calls_total']} | "
            f"`{json.dumps(row['tool_answerability_counts'], sort_keys=True)}` |"
        )
    if candidate:
        lines.extend(
            [
                "",
                "## First Producer Candidate",
                "",
                "```text",
                f"producer_candidate: {candidate['producer_candidate']}",
                f"selected_category: {candidate['selected_category']}",
                f"selection_reason: {candidate['selection_reason']}",
                "```",
            ]
        )
    lines.extend(
        [
            "",
            "## Not Claimed",
            "",
            "- No new savings are claimed.",
            "- Context exposure byte-calls are a ranking signal, not billing.",
            "- The previous replay result remains unchanged.",
            "- A producer must still generate measured output and pass sufficiency audit before any replay savings can be counted.",
            "",
        ]
    )
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "group",
        "event_count",
        "raw_visible_bytes_total",
        "allocated_fresh_tokens_total",
        "median_event_bytes",
        "p90_event_bytes",
        "median_reuse_count",
        "p90_reuse_count",
        "context_exposure_byte_calls_total",
        "context_exposure_fresh_token_calls_total",
        "tool_answerability_counts",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            serialized = row.copy()
            serialized["group"] = json.dumps(serialized["group"], sort_keys=True)
            serialized["tool_answerability_counts"] = json.dumps(serialized["tool_answerability_counts"], sort_keys=True)
            writer.writerow(serialized)


def write_sha256s(output_dir: Path) -> None:
    rows = []
    for path in sorted(output_dir.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        rows.append(f"{file_sha256(path)}  {path.name}")
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
