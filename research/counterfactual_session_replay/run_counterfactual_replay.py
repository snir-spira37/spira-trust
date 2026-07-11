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


SCHEMA = "SPIRA_COUNTERFACTUAL_REPLAY_V1"
ALLOCATION_METHOD = "PROPORTIONAL_TO_MODEL_VISIBLE_UTF8_BYTES"
FINAL_STATUS_NO_JUSTIFICATION = "NO_JUSTIFICATION_FOR_BROAD_ORCHESTRATOR_PILOT"
FINAL_STATUS_INVALID = "REPLAY_INVALID"

CONTENT_KEYS = {
    "content",
    "text",
    "thinking",
    "message",
    "stdout",
    "stderr",
    "output",
    "encrypted_content",
    "base_instructions",
    "summary",
    "last_agent_message",
}


@dataclass
class Event:
    event_id: str
    sequence_index: int
    record_index: int
    payload_type: str
    source_tool: str
    category: str
    safe_path_class: str
    safe_command_class: str
    tool_answerability_class: str
    answerability_reason: str
    raw_visible_bytes: int
    raw_output_sha256: str
    classification_confidence: str
    usage_record_id: str | None = None
    allocated_fresh_tokens: float = 0.0
    first_visible_model_call: int | None = None
    last_visible_model_call: int | None = None
    reuse_count: int = 0
    reuse_confidence: str = "NOT_EVALUATED"
    termination_reason: str = "NOT_EVALUATED"


@dataclass
class Usage:
    sequence_index: int
    usage_record_id: str
    fresh_input_tokens: int
    cached_input_tokens: int
    output_tokens: int

    @property
    def total_input_tokens(self) -> int:
        return self.fresh_input_tokens + self.cached_input_tokens


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the locked SPIRA counterfactual replay on one recorded session.")
    parser.add_argument("--session-jsonl", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--session-id", default="program_completion_stable_codex")
    parser.add_argument("--project-class", default="SPIRA_EVIDENCE_TOOLING")
    args = parser.parse_args()

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    session_sha256 = file_sha256(args.session_jsonl)
    events, usage, compactions, parse_errors, duplicate_usage = parse_codex_session(args.session_id, args.session_jsonl)
    allocate_usage(events, usage)
    assign_reuse(events, usage, compactions)

    results = build_results(
        session_id=args.session_id,
        project_class=args.project_class,
        session_sha256=session_sha256,
        source_bytes=args.session_jsonl.stat().st_size,
        events=events,
        usage=usage,
        compactions=compactions,
        parse_errors=parse_errors,
        duplicate_usage=duplicate_usage,
    )
    write_outputs(output_dir, results, events, usage, compactions)
    write_sha256s(output_dir)
    print(json.dumps(results["summary"], indent=2, ensure_ascii=False))
    return 0


def parse_codex_session(session_id: str, path: Path) -> tuple[list[Event], list[Usage], list[dict[str, Any]], int, int]:
    events: list[Event] = []
    usage: list[Usage] = []
    compactions: list[dict[str, Any]] = []
    parse_errors = 0
    duplicate_usage = 0
    seen_usage_hashes: set[str] = set()
    tool_contexts: dict[str, dict[str, str]] = {}

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for record_index, line in enumerate(handle):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                continue
            payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
            payload_type = str(payload.get("type") or record.get("type") or "unknown")
            call_id = str(payload.get("call_id") or "")
            if payload_type in {"function_call", "custom_tool_call"} and call_id:
                tool_contexts[call_id] = invocation_context(payload)
            if payload_type in {"function_call_output", "custom_tool_call_output"} and call_id in tool_contexts:
                payload = {**payload, "_tool_context": tool_contexts[call_id]}
            info = payload.get("info") if isinstance(payload.get("info"), dict) else {}
            last_usage = info.get("last_token_usage") if isinstance(info.get("last_token_usage"), dict) else None
            if last_usage:
                usage_hash = stable_hash(last_usage)
                if usage_hash in seen_usage_hashes:
                    duplicate_usage += 1
                else:
                    seen_usage_hashes.add(usage_hash)
                    input_tokens = int_value(last_usage.get("input_tokens"))
                    cached = int_value(last_usage.get("cached_input_tokens"))
                    usage.append(
                        Usage(
                            sequence_index=record_index * 100 + 10,
                            usage_record_id=f"usage-{record_index}",
                            fresh_input_tokens=max(0, input_tokens - cached),
                            cached_input_tokens=cached,
                            output_tokens=int_value(last_usage.get("output_tokens")),
                        )
                    )

            event = make_event(session_id, record_index, payload_type, payload)
            if event is not None:
                events.append(event)
            if payload_type in {"compacted", "context_compacted"}:
                compactions.append(
                    {
                        "boundary_id": f"compaction-{record_index}",
                        "sequence_index": record_index * 100 + 20,
                        "record_index": record_index,
                        "payload_type": payload_type,
                        "termination_reason": "EXPLICIT_COMPACTION",
                    }
                )
    return events, usage, compactions, parse_errors, duplicate_usage


def make_event(session_id: str, record_index: int, payload_type: str, payload: dict[str, Any]) -> Event | None:
    visible_value: Any = None
    category = "OTHER"
    tool_context = payload.get("_tool_context") if isinstance(payload.get("_tool_context"), dict) else {}
    source_tool = str(payload.get("name") or tool_context.get("source_tool") or "")
    safe_path = str(tool_context.get("safe_path_class") or "none")
    safe_command = str(tool_context.get("safe_command_class") or "none")

    if payload_type == "agent_message" and payload.get("last_agent_message") is not None:
        visible_value = payload.get("last_agent_message")
        category = "REASONING_OR_INSTRUCTIONS"
    elif payload_type == "user_message" and payload.get("text_elements") is not None:
        visible_value = payload.get("text_elements")
        category = "USER_INSTRUCTION"
    elif payload_type == "patch_apply_end" and payload.get("changes") is not None:
        visible_value = payload.get("changes")
        category = "CODE_WRITE"
    elif payload_type in {"compacted", "context_compacted"}:
        visible_value = metadata_projection(payload)
        category = "CONTEXT_COMPACTION"
    elif payload.get("stdout") is not None or payload.get("stderr") is not None:
        visible_value = {"stdout": payload.get("stdout"), "stderr": payload.get("stderr")}
        safe_command = classify_command(str(payload.get("command") or ""))
        safe_path = classify_path(str(payload.get("path") or payload.get("file") or ""))
        category = category_from_command_and_path(safe_command, safe_path)
    elif payload_type in {"function_call_output", "custom_tool_call_output"} and payload.get("output") is not None:
        visible_value = payload.get("output")
        category = category_from_command_and_path(safe_command, safe_path)
    elif payload_type in {"function_call", "custom_tool_call"}:
        visible_value = invocation_metadata_projection(payload)
        category = "TOOL_INVOCATION"
    elif payload.get("content") is not None:
        visible_value = payload.get("content")
        category = "REASONING_OR_INSTRUCTIONS"
    elif payload.get("message") is not None:
        visible_value = payload.get("message")
        category = "REASONING_OR_INSTRUCTIONS"
    else:
        return None

    visible_bytes = utf8_len(visible_value)
    if visible_bytes <= 0:
        return None
    tool_class, reason = answerability_for(category, safe_path, safe_command)
    event_id = f"{session_id}-event-{record_index}"
    return Event(
        event_id=event_id,
        sequence_index=record_index * 100 + 20,
        record_index=record_index,
        payload_type=payload_type,
        source_tool=safe_tool_name(source_tool),
        category=category,
        safe_path_class=safe_path,
        safe_command_class=safe_command,
        tool_answerability_class=tool_class,
        answerability_reason=reason,
        raw_visible_bytes=visible_bytes,
        raw_output_sha256=stable_hash(visible_value),
        classification_confidence="HIGH",
    )


def answerability_for(category: str, safe_path: str, safe_command: str) -> tuple[str, str]:
    if category == "EVIDENCE_READ" or safe_path == "evidence":
        return "EXACT_EXISTING_TOOL", "SPIRA evidence query could be answered by existing SPIRA commands if frozen state is available"
    if category in {"GIT_OUTPUT", "TEST_OUTPUT", "STATE_DISCOVERY", "FILE_READ_OUTPUT", "SEARCH_OUTPUT", "PYTHON_OUTPUT", "BUILD_OUTPUT"}:
        return "BOUNDED_SUMMARY", "compact deterministic contract appears possible, but no measured adapter was run in this replay"
    return "NOT_TOOL_ANSWERABLE", "outside currently measured deterministic artifact-evidence replacements"


def allocate_usage(events: list[Event], usage_records: list[Usage]) -> None:
    sorted_events = sorted(events, key=lambda event: event.sequence_index)
    previous_usage_sequence = -1
    call_index = 0
    for usage_row in sorted(usage_records, key=lambda row: row.sequence_index):
        pending = [
            event
            for event in sorted_events
            if previous_usage_sequence < event.sequence_index < usage_row.sequence_index
        ]
        total_visible = sum(event.raw_visible_bytes for event in pending)
        if total_visible > 0:
            for event in pending:
                event.usage_record_id = usage_row.usage_record_id
                event.first_visible_model_call = call_index
                event.allocated_fresh_tokens += usage_row.fresh_input_tokens * (event.raw_visible_bytes / total_visible)
        previous_usage_sequence = usage_row.sequence_index
        call_index += 1


def assign_reuse(events: list[Event], usage_records: list[Usage], compactions: list[dict[str, Any]]) -> None:
    usage_sorted = sorted(usage_records, key=lambda row: row.sequence_index)
    compaction_sequences = sorted(int(row["sequence_index"]) for row in compactions)
    for event in events:
        if event.first_visible_model_call is None:
            event.reuse_confidence = "NOT_EVALUATED"
            event.termination_reason = "UNALLOCATED"
            continue
        terminating_sequence = None
        termination_reason = "SESSION_END"
        for sequence in compaction_sequences:
            if sequence > event.sequence_index:
                terminating_sequence = sequence
                termination_reason = "EXPLICIT_COMPACTION"
                break
        visible_call_indexes = [
            index
            for index, usage_row in enumerate(usage_sorted)
            if usage_row.sequence_index > event.sequence_index
            and (terminating_sequence is None or usage_row.sequence_index < terminating_sequence)
        ]
        if visible_call_indexes:
            event.last_visible_model_call = max(visible_call_indexes)
            event.reuse_count = max(0, len(visible_call_indexes) - 1)
        else:
            event.last_visible_model_call = event.first_visible_model_call
            event.reuse_count = 0
        event.reuse_confidence = "MEDIUM"
        event.termination_reason = termination_reason


def build_results(
    session_id: str,
    project_class: str,
    session_sha256: str,
    source_bytes: int,
    events: list[Event],
    usage: list[Usage],
    compactions: list[dict[str, Any]],
    parse_errors: int,
    duplicate_usage: int,
) -> dict[str, Any]:
    actual_fresh = sum(row.fresh_input_tokens for row in usage)
    actual_cached = sum(row.cached_input_tokens for row in usage)
    actual_output = sum(row.output_tokens for row in usage)
    actual_total = actual_fresh + actual_cached
    allocated_fresh = sum(event.allocated_fresh_tokens for event in events)
    coverage = pct(allocated_fresh, actual_fresh)
    classified_events = [event for event in events if event.tool_answerability_class]
    classification_coverage = pct(len(classified_events), len(events))
    exact_tool_events = [
        event for event in events if event.tool_answerability_class == "EXACT_EXISTING_TOOL"
    ]
    measured_replacements: list[dict[str, Any]] = []

    lower = scenario_result("lower_bound", actual_total, actual_fresh, actual_cached, [])
    realistic = scenario_result("realistic_bound", actual_total, actual_fresh, actual_cached, [])
    upper = scenario_result("upper_research_bound", actual_total, actual_fresh, actual_cached, [])

    invalid_reasons: list[str] = []
    if parse_errors > 0:
        invalid_reasons.append("parse errors > 0")
    if coverage < 85:
        invalid_reasons.append("event allocation coverage < 85%")
    if classification_coverage < 85:
        invalid_reasons.append("tool-answerability classification coverage < 85%")
    if exact_tool_events and not measured_replacements:
        invalid_reasons.append("EXACT_EXISTING_TOOL events found but no measured replacements were produced")

    valid = not invalid_reasons
    final_status = FINAL_STATUS_INVALID
    if valid:
        if lower["counterfactual_total_input_reduction_pct"] < 10:
            final_status = FINAL_STATUS_NO_JUSTIFICATION
        elif realistic["counterfactual_total_input_reduction_pct"] < 20:
            final_status = "WEAK_SESSION_WIDE_OPPORTUNITY"
        else:
            final_status = "INDETERMINATE_MODELED_UPPER_BOUND_ONLY"

    counters = {
        "category_counts": Counter(event.category for event in events),
        "tool_answerability_counts": Counter(event.tool_answerability_class for event in events),
        "payload_type_counts": Counter(event.payload_type for event in events),
        "safe_command_class_counts": Counter(event.safe_command_class for event in events),
        "safe_path_class_counts": Counter(event.safe_path_class for event in events),
    }

    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "summary": {
            "schema": SCHEMA,
            "session_id": session_id,
            "project_class": project_class,
            "session_sha256": session_sha256,
            "source_bytes": source_bytes,
            "final_status": final_status,
            "replay_valid": valid,
            "invalid_reasons": invalid_reasons,
            "actual_total_input_tokens": actual_total,
            "actual_fresh_input_tokens": actual_fresh,
            "actual_cached_input_tokens": actual_cached,
            "actual_output_tokens": actual_output,
            "fresh_share_pct": pct(actual_fresh, actual_total),
            "cached_share_pct": pct(actual_cached, actual_total),
            "event_count": len(events),
            "usage_record_count": len(usage),
            "duplicate_usage_records_collapsed": duplicate_usage,
            "parse_error_count": parse_errors,
            "compaction_boundary_count": len(compactions),
            "allocation_method": ALLOCATION_METHOD,
            "allocated_fresh_tokens": round(allocated_fresh, 3),
            "allocation_coverage_pct": coverage,
            "tool_answerability_classification_coverage_pct": classification_coverage,
            "replacement_measurement_count": len(measured_replacements),
            "lower_bound": lower,
            "realistic_bound": realistic,
            "upper_research_bound": upper,
        },
        "counters": {key: dict(value) for key, value in counters.items()},
        "replacement_measurements": measured_replacements,
        "compactions": compactions,
        "not_claimed": [
            "This is a counterfactual replay, not a live A/B experiment.",
            "No orchestrator build is authorized by this replay unless thresholds justify it.",
            "Provider usage is actual; event attribution is modeled.",
            "No raw transcript content, source code, tool output, raw commands, or raw paths are persisted.",
            "Cost-weighted savings are NOT_EVALUATED.",
            "Class C modeled summaries are not counted in lower or realistic bounds.",
        ],
    }


def scenario_result(name: str, actual_total: int, actual_fresh: int, actual_cached: int, included_events: list[Event]) -> dict[str, Any]:
    # V1 conservative replay includes no replacement without measured output and sufficiency.
    total_saving = 0.0
    fresh_saving = 0.0
    cached_saving = 0.0
    return {
        "scenario": name,
        "included_event_count": len(included_events),
        "immediate_fresh_saving_tokens": round(fresh_saving, 3),
        "propagated_cached_prefix_saving_tokens": round(cached_saving, 3),
        "total_token_volume_saving_tokens": round(total_saving, 3),
        "counterfactual_total_input_reduction_pct": pct(total_saving, actual_total),
        "counterfactual_fresh_input_reduction_pct": pct(fresh_saving, actual_fresh),
        "counterfactual_cached_prefix_reduction_pct": pct(cached_saving, actual_cached),
        "cost_weighted_reduction_pct": "NOT_EVALUATED",
    }


def write_outputs(output_dir: Path, results: dict[str, Any], events: list[Event], usage: list[Usage], compactions: list[dict[str, Any]]) -> None:
    (output_dir / "counterfactual_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "counterfactual_results.md").write_text(results_markdown(results), encoding="utf-8")
    (output_dir / "counterfactual_replay_manifest.json").write_text(json.dumps(manifest_json(results), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "tool_answerability_rules.json").write_text(json.dumps(tool_rules_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "replacement_measurements.json").write_text(json.dumps(results["replacement_measurements"], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_event_csv(output_dir / "event_classification.csv", events)
    write_sufficiency_csv(output_dir / "sufficiency_audit.csv")
    write_compaction_csv(output_dir / "compaction_boundaries.csv", compactions)
    write_reuse_csv(output_dir / "reuse_horizon.csv", events)
    (output_dir / "not_claimed.md").write_text(not_claimed_markdown(results), encoding="utf-8")


def results_markdown(results: dict[str, Any]) -> str:
    summary = results["summary"]
    lines = [
        "# Counterfactual Session Replay Results",
        "",
        "```text",
        f"final_status: {summary['final_status']}",
        f"replay_valid: {summary['replay_valid']}",
        f"actual_total_input_tokens: {summary['actual_total_input_tokens']}",
        f"actual_fresh_input_tokens: {summary['actual_fresh_input_tokens']}",
        f"actual_cached_input_tokens: {summary['actual_cached_input_tokens']}",
        f"fresh_share_pct: {summary['fresh_share_pct']}",
        f"cached_share_pct: {summary['cached_share_pct']}",
        f"allocation_coverage_pct: {summary['allocation_coverage_pct']}",
        f"tool_answerability_classification_coverage_pct: {summary['tool_answerability_classification_coverage_pct']}",
        f"replacement_measurement_count: {summary['replacement_measurement_count']}",
        "```",
        "",
        "## Scenario Results",
        "",
    ]
    for key in ["lower_bound", "realistic_bound", "upper_research_bound"]:
        scenario = summary[key]
        lines.extend(
            [
                f"### {scenario['scenario']}",
                "",
                "```text",
                f"included_event_count: {scenario['included_event_count']}",
                f"total_token_volume_saving_tokens: {scenario['total_token_volume_saving_tokens']}",
                f"counterfactual_total_input_reduction_pct: {scenario['counterfactual_total_input_reduction_pct']}",
                f"counterfactual_fresh_input_reduction_pct: {scenario['counterfactual_fresh_input_reduction_pct']}",
                f"counterfactual_cached_prefix_reduction_pct: {scenario['counterfactual_cached_prefix_reduction_pct']}",
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "No measured Class A or Class B replacement passed the locked replay gates in this conservative run. "
            "The lower and realistic bounds therefore remain 0%. Under the locked thresholds, this does not justify a broad orchestrator pilot.",
            "",
            "This does not change SPIRA Trust's current product scope or artifact-evidence claims.",
            "",
        ]
    )
    return "\n".join(lines)


def manifest_json(results: dict[str, Any]) -> dict[str, Any]:
    summary = results["summary"]
    return {
        "schema": "SPIRA_COUNTERFACTUAL_REPLAY_MANIFEST_V1",
        "created_at": results["created_at"],
        "session_id": summary["session_id"],
        "project_class": summary["project_class"],
        "selection_reason": "preselected longest validated program-completion session",
        "session_sha256": summary["session_sha256"],
        "source_bytes": summary["source_bytes"],
        "methodology": "research/counterfactual_session_replay_methodology.md",
        "privacy": "raw path omitted; transcript content not persisted",
    }


def tool_rules_json() -> dict[str, Any]:
    return {
        "schema": "SPIRA_COUNTERFACTUAL_TOOL_ANSWERABILITY_RULES_V1",
        "locked_for_run": True,
        "classes": {
            "EXACT_EXISTING_TOOL": "only existing deterministic tools with measured compact output",
            "EXACT_EXISTING_ADAPTER": "only existing deterministic adapters with measured compact output",
            "BOUNDED_SUMMARY": "modeled only; excluded from lower and realistic bounds",
            "NOT_TOOL_ANSWERABLE": "not counted as replaceable",
        },
        "v1_conservative_policy": [
            "No new adapter is implemented for this replay.",
            "No compact size is invented for lower or realistic bounds.",
            "No event is counted without measured replacement output and sufficiency.",
        ],
    }


def write_event_csv(path: Path, events: list[Event]) -> None:
    fields = [
        "event_id",
        "record_index",
        "payload_type",
        "source_tool",
        "category",
        "safe_path_class",
        "safe_command_class",
        "raw_visible_bytes",
        "raw_output_sha256",
        "allocated_fresh_tokens",
        "usage_record_id",
        "tool_answerability_class",
        "answerability_reason",
        "classification_confidence",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for event in events:
            writer.writerow({field: getattr(event, field) if field != "allocated_fresh_tokens" else round(event.allocated_fresh_tokens, 3) for field in fields})


def write_sufficiency_csv(path: Path) -> None:
    fields = [
        "event_id",
        "tool_answerability_class",
        "replacement_measurement_status",
        "sufficiency_confidence",
        "next_action_preserved",
        "included_in_lower",
        "included_in_realistic",
        "included_in_upper",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()


def write_compaction_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = ["boundary_id", "record_index", "payload_type", "termination_reason"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def write_reuse_csv(path: Path, events: list[Event]) -> None:
    fields = [
        "event_id",
        "first_visible_model_call",
        "last_visible_model_call",
        "reuse_count",
        "termination_reason",
        "reuse_confidence",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for event in events:
            writer.writerow({field: getattr(event, field) for field in fields})


def not_claimed_markdown(results: dict[str, Any]) -> str:
    return "# Not Claimed\n\n" + "\n".join(f"- {item}" for item in results["not_claimed"]) + "\n"


def write_sha256s(output_dir: Path) -> None:
    rows = []
    for path in sorted(output_dir.iterdir()):
        if path.name == "SHA256SUMS.txt" or not path.is_file():
            continue
        rows.append(f"{file_sha256(path)}  {path.name}")
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")


def metadata_projection(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in CONTENT_KEYS and isinstance(value, (str, int, float, bool, type(None)))
    }


def invocation_context(payload: dict[str, Any]) -> dict[str, str]:
    source_tool = safe_tool_name(str(payload.get("name") or ""))
    args = payload.get("arguments")
    if args is None:
        args = payload.get("input")
    args_value = parse_possible_json(args)
    command = extract_text_field(args_value, "command")
    path_value = (
        extract_text_field(args_value, "path")
        or extract_text_field(args_value, "file")
        or extract_text_field(args_value, "workdir")
    )
    return {
        "source_tool": source_tool,
        "safe_command_class": classify_command(command),
        "safe_path_class": classify_path(path_value),
    }


def invocation_metadata_projection(payload: dict[str, Any]) -> dict[str, Any]:
    context = invocation_context(payload)
    return {
        "type": payload.get("type"),
        "source_tool": context["source_tool"],
        "safe_command_class": context["safe_command_class"],
        "safe_path_class": context["safe_path_class"],
    }


def parse_possible_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def extract_text_field(value: Any, key: str) -> str:
    if isinstance(value, dict):
        found = value.get(key)
        return str(found) if found is not None else ""
    return ""


def category_from_command_and_path(command_class: str, path_class: str) -> str:
    if path_class == "evidence":
        return "EVIDENCE_READ"
    if command_class == "git":
        return "GIT_OUTPUT"
    if command_class == "test":
        return "TEST_OUTPUT"
    if command_class == "file_read":
        return "FILE_READ_OUTPUT"
    if command_class == "search":
        return "SEARCH_OUTPUT"
    if command_class == "python":
        return "PYTHON_OUTPUT"
    if command_class == "package_build":
        return "BUILD_OUTPUT"
    if command_class == "network_fetch":
        return "NETWORK_FETCH_OUTPUT"
    if command_class == "state_discovery":
        return "STATE_DISCOVERY"
    return "OTHER"


def classify_path(path_value: str) -> str:
    lowered = path_value.lower()
    if any(token in lowered for token in ["agent_summary", "spira-decision", "graph_report", "bill_of_materials", "evidence_pack", "sbom"]):
        return "evidence"
    if any(token in lowered for token in ["/source/", "\\source\\", "/src/", "\\src\\", "/tests/", "\\tests\\"]):
        return "code"
    return "other_path" if path_value else "none"


def classify_command(command: str) -> str:
    lowered = command.lower().strip()
    if lowered.startswith("git "):
        return "git"
    if any(token in lowered for token in ["pytest", "py_compile", "unittest", "tox", "nox"]):
        return "test"
    if lowered.startswith("python ") or lowered.startswith("py ") or "| python" in lowered:
        return "python"
    if lowered.startswith("get-content") or lowered.startswith("type ") or lowered.startswith("gc "):
        return "file_read"
    if lowered.startswith("rg ") or " rg " in lowered or "select-string" in lowered:
        return "search"
    if any(token in lowered for token in ["pip ", "build", "twine"]):
        return "package_build"
    if any(token in lowered for token in ["invoke-webrequest", "invoke-restmethod", "curl "]):
        return "network_fetch"
    if any(token in lowered for token in ["get-childitem", " dir ", " ls "]):
        return "state_discovery"
    return "other_command" if command else "none"


def safe_tool_name(value: str) -> str:
    if not value:
        return ""
    lowered = value.lower()
    if "shell_command" in lowered:
        return "shell_command"
    if "apply_patch" in lowered:
        return "apply_patch"
    if lowered in {"powershell", "bash", "read", "write", "edit", "glob", "grep"}:
        return value
    if "web" in lowered or "search" in lowered:
        return "search_or_web_tool"
    return "other_tool"


def utf8_len(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (dict, list)):
        return len(json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8"))
    return len(str(value).encode("utf-8"))


def int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def pct(numerator: float, denominator: float) -> float:
    return round((numerator / denominator) * 100.0, 3) if denominator else 0.0


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
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
