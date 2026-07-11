from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "SPIRA_WORKSPACE_STATE_MANIFEST_EXPERIMENT_V1"
ANSWER_SCHEMA = "SPIRA_WORKSPACE_STATE_ANSWER_V1"
PRODUCER_NAME = "spira-workspace-state-producer"
PRODUCER_VERSION = "0.1-research"
SESSION_ID = "program_completion_stable_codex"


@dataclass
class ReplayEvent:
    event_id: str
    record_index: int
    category: str
    safe_command_class: str
    raw_visible_bytes: int
    raw_output_sha256: str
    allocated_fresh_tokens: float
    reuse_count: int


@dataclass
class HistoricalOutput:
    event_id: str
    record_index: int
    command_fingerprint: str
    raw_output: str
    raw_output_bytes: int
    raw_output_sha256: str


def main() -> int:
    parser = argparse.ArgumentParser(description="Measure one Workspace/State-Manifest producer against locked replay events.")
    parser.add_argument("--session-jsonl", required=True, type=Path)
    parser.add_argument("--replay-results-dir", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    replay_summary = json.loads((args.replay_results_dir / "counterfactual_results.json").read_text(encoding="utf-8"))["summary"]
    replay_events = load_replay_events(args.replay_results_dir)
    historical_outputs = parse_historical_state_outputs(args.session_jsonl)
    records = []

    for event in replay_events.values():
        if event.category != "STATE_DISCOVERY" or event.safe_command_class != "state_discovery":
            continue
        historical = historical_outputs.get(event.event_id)
        records.append(measure_event(event, historical))

    results = build_results(replay_summary, records, args.session_jsonl)
    write_outputs(args.output_dir, results, records)
    write_sha256s(args.output_dir)
    print(json.dumps(results["summary"], indent=2, ensure_ascii=False))
    return 0


def load_replay_events(base: Path) -> dict[str, ReplayEvent]:
    reuse = {}
    with (base / "reuse_horizon.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            reuse[row["event_id"]] = int(float(row["reuse_count"] or 0))

    events = {}
    with (base / "event_classification.csv").open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            event_id = row["event_id"]
            events[event_id] = ReplayEvent(
                event_id=event_id,
                record_index=int(row["record_index"]),
                category=row["category"],
                safe_command_class=row["safe_command_class"],
                raw_visible_bytes=int(float(row["raw_visible_bytes"] or 0)),
                raw_output_sha256=row["raw_output_sha256"],
                allocated_fresh_tokens=float(row["allocated_fresh_tokens"] or 0),
                reuse_count=reuse.get(event_id, 0),
            )
    return events


def parse_historical_state_outputs(path: Path) -> dict[str, HistoricalOutput]:
    contexts: dict[str, dict[str, str]] = {}
    outputs: dict[str, HistoricalOutput] = {}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for record_index, line in enumerate(handle):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
            payload_type = str(payload.get("type") or record.get("type") or "unknown")
            call_id = str(payload.get("call_id") or "")
            if payload_type in {"function_call", "custom_tool_call"} and call_id:
                command = extract_command(payload)
                if classify_command(command) == "state_discovery":
                    contexts[call_id] = {
                        "safe_command_class": "state_discovery",
                        "command_fingerprint": stable_hash(command),
                    }
            elif payload_type in {"function_call_output", "custom_tool_call_output"} and call_id in contexts:
                raw_output = stringify_output(payload.get("output"))
                event_id = f"{SESSION_ID}-event-{record_index}"
                outputs[event_id] = HistoricalOutput(
                    event_id=event_id,
                    record_index=record_index,
                    command_fingerprint=contexts[call_id]["command_fingerprint"],
                    raw_output=raw_output,
                    raw_output_bytes=utf8_len(raw_output),
                    raw_output_sha256=stable_hash(raw_output),
                )
    return outputs


def measure_event(event: ReplayEvent, historical: HistoricalOutput | None) -> dict[str, Any]:
    base = {
        "event_id": event.event_id,
        "record_index": event.record_index,
        "raw_output_bytes": event.raw_visible_bytes,
        "raw_output_allocated_fresh_tokens": round(event.allocated_fresh_tokens, 6),
        "raw_output_sha256": event.raw_output_sha256,
        "reuse_count": event.reuse_count,
        "producer_name": PRODUCER_NAME,
        "producer_version": PRODUCER_VERSION,
        "query_type": "TOP_LEVEL_ENTRIES",
        "query_fingerprint": "",
        "workspace_fingerprint": "",
        "state_reconstruction_status": "NOT_AVAILABLE",
        "state_reconstruction_basis": "NONE",
        "replacement_status": "NOT_MEASURED",
        "sufficiency_status": "INDETERMINATE",
        "compact_output_bytes": 0,
        "compact_output_estimated_tokens": 0.0,
        "compact_output_sha256": "",
        "compact_to_raw_byte_ratio": 0.0,
        "immediate_fresh_saving_tokens": 0.0,
        "propagated_cached_prefix_saving_tokens": 0.0,
        "included_in_lower": False,
        "included_in_realistic": False,
        "line_count": 0,
        "nonempty_line_count": 0,
        "truncated_visible_output_detected": False,
        "not_counted_reason": "",
    }
    if historical is None:
        base["not_counted_reason"] = "historical output not found"
        return base

    answer, line_count, nonempty_count = build_compact_answer(historical)
    compact_bytes = utf8_len(answer)
    compact_sha = stable_hash(answer)
    ratio = compact_bytes / event.raw_visible_bytes if event.raw_visible_bytes else 0.0
    estimated_tokens = event.allocated_fresh_tokens * ratio
    immediate_saving = event.allocated_fresh_tokens - estimated_tokens
    propagated_saving = immediate_saving * event.reuse_count

    base.update(
        {
            "query_type": answer["query_type"],
            "query_fingerprint": stable_hash({"event_id": event.event_id, "command_fingerprint": historical.command_fingerprint}),
            "workspace_fingerprint": answer["workspace_fingerprint"],
            "state_reconstruction_status": "EXACT",
            "state_reconstruction_basis": "RECORDED_MODEL_VISIBLE_OUTPUT",
            "compact_output_bytes": compact_bytes,
            "compact_output_estimated_tokens": round(estimated_tokens, 6),
            "compact_output_sha256": compact_sha,
            "compact_to_raw_byte_ratio": round(ratio, 6),
            "immediate_fresh_saving_tokens": round(immediate_saving, 6),
            "propagated_cached_prefix_saving_tokens": round(propagated_saving, 6),
            "line_count": line_count,
            "nonempty_line_count": nonempty_count,
            "truncated_visible_output_detected": historical.raw_output_bytes >= 40090,
        }
    )

    if nonempty_count == 0:
        base["replacement_status"] = "NOT_MEASURED"
        base["sufficiency_status"] = "INSUFFICIENT"
        base["not_counted_reason"] = "empty visible output"
    elif compact_bytes >= event.raw_visible_bytes:
        base["replacement_status"] = "MEASURED_NOT_BENEFICIAL"
        base["sufficiency_status"] = "SUFFICIENT"
        base["not_counted_reason"] = "compact answer is not smaller than raw output"
    else:
        base["replacement_status"] = "MEASURED_BENEFICIAL"
        base["sufficiency_status"] = "SUFFICIENT"
        base["included_in_lower"] = True
        base["included_in_realistic"] = True
        base["not_counted_reason"] = ""
    return base


def build_compact_answer(historical: HistoricalOutput) -> tuple[dict[str, Any], int, int]:
    lines = historical.raw_output.splitlines()
    normalized_lines = [line.strip() for line in lines if line.strip()]
    query_type = infer_query_type(normalized_lines)
    answer = {
        "schema": ANSWER_SCHEMA,
        "query_type": query_type,
        "workspace_fingerprint": f"recorded-output:{historical.raw_output_sha256[:16]}",
        "producer": {
            "name": PRODUCER_NAME,
            "version": PRODUCER_VERSION,
        },
        "state_reconstruction_status": "EXACT",
        "state_reconstruction_basis": "RECORDED_MODEL_VISIBLE_OUTPUT",
        "stale": False,
        "answer": {
            "output_kind": "NORMALIZED_VISIBLE_LINES",
            "line_count": len(lines),
            "nonempty_line_count": len(normalized_lines),
            "truncated_visible_output_detected": historical.raw_output_bytes >= 40090,
            "lines": normalized_lines,
        },
        "sufficient_for": [
            "SELECT_NEXT_DISCOVERY_QUERY",
            "LOCATE_PATH_FROM_DISCOVERY_OUTPUT",
        ],
        "not_sufficient_for": [
            "EDIT_SOURCE",
            "CONFIRM_CODE_BEHAVIOR",
            "PRESERVE_RAW_FORMATTING",
        ],
        "drilldown": [
            {
                "query_type": "RAW_OUTPUT_BY_SHA256",
                "available": True,
                "raw_output_sha256": historical.raw_output_sha256,
            }
        ],
        "not_evaluated": [],
        "evidence_refs": [],
        "conflicts": [],
    }
    return answer, len(lines), len(normalized_lines)


def build_results(replay_summary: dict[str, Any], records: list[dict[str, Any]], session_path: Path) -> dict[str, Any]:
    candidate_count = len(records)
    measured_count = sum(1 for row in records if row["replacement_status"].startswith("MEASURED"))
    beneficial_count = sum(1 for row in records if row["replacement_status"] == "MEASURED_BENEFICIAL")
    sufficient_count = sum(1 for row in records if row["sufficiency_status"] == "SUFFICIENT")
    included = [row for row in records if row["included_in_lower"]]
    immediate = sum(float(row["immediate_fresh_saving_tokens"]) for row in included)
    propagated = sum(float(row["propagated_cached_prefix_saving_tokens"]) for row in included)
    total_saving = immediate + propagated
    actual_total = float(replay_summary["actual_total_input_tokens"])
    actual_fresh = float(replay_summary["actual_fresh_input_tokens"])
    actual_cached = float(replay_summary["actual_cached_input_tokens"])

    lower = scenario("lower_bound", included, immediate, propagated, actual_total, actual_fresh, actual_cached)
    realistic = scenario("realistic_bound", included, immediate, propagated, actual_total, actual_fresh, actual_cached)
    upper = scenario("upper_research_bound", included, immediate, propagated, actual_total, actual_fresh, actual_cached)
    final_status = final_status_for(lower, realistic)

    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "source": {
            "session_sha256": file_sha256(session_path),
            "replay_status_before_producer": replay_summary["final_status"],
            "source_replay_event_count": replay_summary["event_count"],
        },
        "summary": {
            "schema": SCHEMA,
            "producer": f"{PRODUCER_NAME} {PRODUCER_VERSION}",
            "final_status": final_status,
            "candidate_event_count": candidate_count,
            "measured_replacement_count": measured_count,
            "beneficial_replacement_count": beneficial_count,
            "sufficiency_pass_count": sufficient_count,
            "included_event_count": len(included),
            "replacement_status_counts": dict(Counter(row["replacement_status"] for row in records)),
            "sufficiency_status_counts": dict(Counter(row["sufficiency_status"] for row in records)),
            "state_reconstruction_status_counts": dict(Counter(row["state_reconstruction_status"] for row in records)),
            "actual_total_input_tokens": replay_summary["actual_total_input_tokens"],
            "actual_fresh_input_tokens": replay_summary["actual_fresh_input_tokens"],
            "actual_cached_input_tokens": replay_summary["actual_cached_input_tokens"],
            "lower_bound": lower,
            "realistic_bound": realistic,
            "upper_research_bound": upper,
        },
        "methodology": "research/workspace_state_manifest_methodology.md",
        "measurement_policy": {
            "event_scope": "STATE_DISCOVERY / state_discovery only",
            "compact_answer": "measured SPIRA_WORKSPACE_STATE_ANSWER_V1 JSON generated from recorded model-visible state output",
            "state_reconstruction_basis": "RECORDED_MODEL_VISIBLE_OUTPUT",
            "counting_rule": "only EXACT + SUFFICIENT + MEASURED_BENEFICIAL events enter lower/realistic bounds",
            "token_estimate": "compact_output_bytes / raw_output_bytes applied to event allocated fresh tokens",
        },
        "not_claimed": [
            "This is a research producer measurement, not a SPIRA Trust product feature.",
            "No broad orchestrator is authorized by this result.",
            "Recorded output is used as the historical reconstruction basis; current workspace scans are not attributed to old events.",
            "The compact answers are not persisted in the repository; only sizes and hashes are persisted.",
            "No CPU, energy, or CO2 claim is made.",
        ],
    }


def scenario(
    name: str,
    included: list[dict[str, Any]],
    immediate: float,
    propagated: float,
    actual_total: float,
    actual_fresh: float,
    actual_cached: float,
) -> dict[str, Any]:
    total = immediate + propagated
    return {
        "scenario": name,
        "included_event_count": len(included),
        "immediate_fresh_saving_tokens": round(immediate, 6),
        "propagated_cached_prefix_saving_tokens": round(propagated, 6),
        "total_token_volume_saving_tokens": round(total, 6),
        "counterfactual_total_input_reduction_pct": pct(total, actual_total),
        "counterfactual_fresh_input_reduction_pct": pct(immediate, actual_fresh),
        "counterfactual_cached_prefix_reduction_pct": pct(propagated, actual_cached),
        "cost_weighted_reduction_pct": "NOT_EVALUATED",
    }


def final_status_for(lower: dict[str, Any], realistic: dict[str, Any]) -> str:
    if lower["counterfactual_total_input_reduction_pct"] < 10:
        return "NO_JUSTIFICATION_TO_CONTINUE"
    if realistic["counterfactual_total_input_reduction_pct"] < 20:
        return "NO_ORCHESTRATOR_JUSTIFICATION"
    if realistic["counterfactual_total_input_reduction_pct"] < 40:
        return "LIMITED_THREE_FAMILY_PILOT_MAY_BE_CONSIDERED"
    return "COUNTERFACTUAL_SUPPORT_REQUIRES_LIVE_AB"


def write_outputs(output_dir: Path, results: dict[str, Any], records: list[dict[str, Any]]) -> None:
    (output_dir / "workspace_state_manifest_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "workspace_state_manifest_results.md").write_text(render_markdown(results), encoding="utf-8")
    write_measurements_csv(output_dir / "workspace_state_manifest_measurements.csv", records)
    write_sufficiency_csv(output_dir / "workspace_state_manifest_sufficiency_audit.csv", records)
    (output_dir / "replacement_measurements.json").write_text(json.dumps(compact_measurements(records), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "not_claimed.md").write_text(not_claimed_markdown(results), encoding="utf-8")


def write_measurements_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "event_id",
        "record_index",
        "raw_output_bytes",
        "compact_output_bytes",
        "compact_to_raw_byte_ratio",
        "raw_output_allocated_fresh_tokens",
        "compact_output_estimated_tokens",
        "immediate_fresh_saving_tokens",
        "reuse_count",
        "propagated_cached_prefix_saving_tokens",
        "state_reconstruction_status",
        "state_reconstruction_basis",
        "replacement_status",
        "sufficiency_status",
        "query_type",
        "query_fingerprint",
        "workspace_fingerprint",
        "raw_output_sha256",
        "compact_output_sha256",
        "line_count",
        "nonempty_line_count",
        "truncated_visible_output_detected",
        "included_in_lower",
        "included_in_realistic",
        "not_counted_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({field: row[field] for field in fields})


def write_sufficiency_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "event_id",
        "state_reconstruction_status",
        "replacement_status",
        "sufficiency_status",
        "included_in_lower",
        "included_in_realistic",
        "not_counted_reason",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({field: row[field] for field in fields})


def compact_measurements(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = [
        "event_id",
        "raw_output_bytes",
        "compact_output_bytes",
        "replacement_status",
        "sufficiency_status",
        "state_reconstruction_status",
        "query_type",
        "raw_output_sha256",
        "compact_output_sha256",
        "included_in_lower",
    ]
    return [{key: row[key] for key in keys} for row in records]


def render_markdown(results: dict[str, Any]) -> str:
    summary = results["summary"]
    lines = [
        "# Workspace State Manifest Experiment V1",
        "",
        "```text",
        f"final_status: {summary['final_status']}",
        f"candidate_event_count: {summary['candidate_event_count']}",
        f"measured_replacement_count: {summary['measured_replacement_count']}",
        f"beneficial_replacement_count: {summary['beneficial_replacement_count']}",
        f"sufficiency_pass_count: {summary['sufficiency_pass_count']}",
        f"included_event_count: {summary['included_event_count']}",
        "```",
        "",
        "## Bounds",
        "",
    ]
    for key in ["lower_bound", "realistic_bound", "upper_research_bound"]:
        scenario_row = summary[key]
        lines.extend(
            [
                f"### {scenario_row['scenario']}",
                "",
                "```text",
                f"included_event_count: {scenario_row['included_event_count']}",
                f"immediate_fresh_saving_tokens: {scenario_row['immediate_fresh_saving_tokens']}",
                f"propagated_cached_prefix_saving_tokens: {scenario_row['propagated_cached_prefix_saving_tokens']}",
                f"total_token_volume_saving_tokens: {scenario_row['total_token_volume_saving_tokens']}",
                f"counterfactual_total_input_reduction_pct: {scenario_row['counterfactual_total_input_reduction_pct']}",
                f"counterfactual_fresh_input_reduction_pct: {scenario_row['counterfactual_fresh_input_reduction_pct']}",
                f"counterfactual_cached_prefix_reduction_pct: {scenario_row['counterfactual_cached_prefix_reduction_pct']}",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "This is a one-producer research measurement for STATE_DISCOVERY only. It does not authorize a broad orchestrator or product claim.",
            "",
            "The compact answers are measured but not persisted; only sizes, hashes, and audit outcomes are stored.",
            "",
            "## Not Claimed",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in results["not_claimed"])
    lines.append("")
    return "\n".join(lines)


def not_claimed_markdown(results: dict[str, Any]) -> str:
    lines = ["# Not Claimed", ""]
    lines.extend(f"- {item}" for item in results["not_claimed"])
    lines.append("")
    return "\n".join(lines)


def write_sha256s(output_dir: Path) -> None:
    rows = []
    for path in sorted(output_dir.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        rows.append(f"{file_sha256(path)}  {path.name}")
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def infer_query_type(lines: list[str]) -> str:
    if not lines:
        return "DRILLDOWN_REQUIRED"
    if len(lines) <= 3:
        return "PATH_EXISTS"
    if all(("\\" in line or "/" in line) for line in lines[: min(len(lines), 20)]):
        return "MATCHING_PATHS"
    return "TOP_LEVEL_ENTRIES"


def extract_command(payload: dict[str, Any]) -> str:
    args = payload.get("arguments") if payload.get("arguments") is not None else payload.get("input")
    args = parse_possible_json(args)
    if isinstance(args, dict):
        command = args.get("command")
        if isinstance(command, str):
            return command
    return ""


def classify_command(command: str) -> str:
    lowered = command.lower().strip()
    if any(token in lowered for token in ["get-childitem", " dir ", " ls "]):
        if "rg " not in lowered and "select-string" not in lowered:
            return "state_discovery"
    return "other"


def parse_possible_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def stringify_output(value: Any) -> str:
    if isinstance(value, str):
        return value
    if value is None:
        return ""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)


def utf8_len(value: Any) -> int:
    if isinstance(value, (dict, list)):
        return len(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8"))
    return len(str(value).encode("utf-8"))


def pct(numerator: float, denominator: float) -> float:
    return round((numerator / denominator) * 100.0, 6) if denominator else 0.0


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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
