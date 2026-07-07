from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


class AdapterBoundaryError(ValueError):
    pass


@dataclass(frozen=True)
class TelemetryDecisionPayload:
    decision_payload: dict[str, Any]
    source_fixture: dict[str, Any]
    adapter_basis: dict[str, Any]


class Telemetry021ToDecision015Adapter:
    """Adapter for the bounded 021 fixture subset inside the unified core."""

    required_rules = {
        "raw_pass_through_forbidden",
        "cpu_or_temp_to_risk_and_load_by_normalize_no_health_claim",
        "coherence_neutral_design_constant_not_021_derived",
    }
    enrichment_rules = (
        "v2_load_remains_cpu_or_temp_stress",
        "v2_risk_is_surprise_stress_not_temperature_duplicate",
        "v2_coherence_is_declared_surprise_health_heuristic",
        "v2_no_vit_or_action_semantic_mapping",
    )
    surprise_only_rules = (
        "surprise_only_risk_is_surprise_stress",
        "surprise_only_coherence_is_surprise_health",
        "surprise_only_load_is_neutral_constant_not_021_derived",
        "surprise_only_action_vit_mode_are_context_only",
    )
    surprise_only_neutral_load = 0.5

    def __init__(self, workspace_root: str | Path | None = None) -> None:
        self.workspace_root = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
        self.fixture_path = self.workspace_root / "outputs/runtime_sandbox/SPIRA_WORKBENCH_REPLAY_PANEL_001/stone021_adapted_fixtures.json"
        self.raw_021_path = self.workspace_root / "outputs/runtime_sandbox/STONE_021_OPEN_RAW_CLASSIFICATION_001/raw_extract/isaac_data/rishimo_log.jsonl"

    def load_fixture(self, fixture_index: int = 0) -> dict[str, Any]:
        data = json.loads(self.fixture_path.read_text(encoding="utf-8"))
        fixtures = data.get("fixtures") or []
        if not fixtures:
            raise AdapterBoundaryError("Stone 021 fixture set is empty")
        if fixture_index < 0 or fixture_index >= len(fixtures):
            raise AdapterBoundaryError(f"fixture_index out of range: {fixture_index}")
        return dict(fixtures[fixture_index])

    def adapt(self, *, fixture_index: int = 0, raw_telemetry: Mapping[str, Any] | None = None) -> TelemetryDecisionPayload:
        if raw_telemetry is not None:
            raise AdapterBoundaryError("raw 021 telemetry pass-through is forbidden; use bounded adapted fixtures")
        fixture = self.load_fixture(fixture_index)
        self._validate_fixture_boundary(fixture)
        enriched_metrics = self._enriched_metrics(fixture)
        decision_payload = {
            "requested_action": fixture["requested_action"],
            "current_metrics": enriched_metrics,
            "options": dict(fixture["options"]),
        }
        return TelemetryDecisionPayload(
            decision_payload=decision_payload,
            source_fixture=fixture,
            adapter_basis={
                "adapter": "Telemetry021ToDecision015Adapter",
                "fixture_index": fixture_index,
                "fixture_path": self.fixture_path.as_posix(),
                "semantic_rules": list(fixture.get("adapter_trace", {}).get("semantic_rules", [])),
                "enrichment_rules": list(self.enrichment_rules),
                "original_fixture_metrics": dict(fixture.get("current_metrics", {})),
                "decision_payload_metrics": enriched_metrics,
                "blocked_fields_not_used": list(fixture.get("source_context", {}).get("blocked_fields_not_used", [])),
                "not_claimed": list(fixture.get("adapter_trace", {}).get("not_claimed", []))
                + [
                    "enriched metrics are adapter heuristics, not calibrated telemetry risk",
                    "coherence is derived from surprise health only in this v2 adapter layer",
                    "vit and 021 action labels remain blocked from decision semantics",
                ],
            },
        )

    def adapt_surprise_only(self, *, context_index: int = 0) -> TelemetryDecisionPayload:
        record = self.load_surprise_only_record(context_index)
        surprise = self._metric01(record.get("surprise_value"), "surprise_value")
        decision_payload = {
            "requested_action": "observe_021_surprise_context",
            "current_metrics": {
                "coherence": round(1.0 - surprise, 6),
                "load": self.surprise_only_neutral_load,
                "risk": round(surprise, 6),
            },
            "options": {"mode": "normal", "force_override": False},
        }
        return TelemetryDecisionPayload(
            decision_payload=decision_payload,
            source_fixture=record,
            adapter_basis={
                "adapter": "Telemetry021ToDecision015Adapter.surprise_only_context",
                "context_index": context_index,
                "raw_line_index": record.get("raw_line_index"),
                "fixture_path": self.raw_021_path.as_posix(),
                "semantic_rules": list(self.surprise_only_rules),
                "original_record": dict(record.get("source_record", {})),
                "decision_payload_metrics": dict(decision_payload["current_metrics"]),
                "blocked_fields_not_used": ["vit", "action_as_015_action", "mode_as_015_mode", "missing_load_as_021_load"],
                "not_claimed": [
                    "surprise-only context records do not contain cpu/load inputs",
                    "load is a neutral adapter constant, not a Stone 021 measurement",
                    "does not map vit/action/mode into Stone 015 semantics",
                    "does not claim calibrated telemetry risk",
                ],
            },
        )

    def load_surprise_only_record(self, context_index: int = 0) -> dict[str, Any]:
        if context_index < 0:
            raise AdapterBoundaryError(f"context_index out of range: {context_index}")
        seen = 0
        with self.raw_021_path.open("r", encoding="utf-8") as handle:
            for line_index, line in enumerate(handle):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not self._is_surprise_only_record(record):
                    continue
                if seen == context_index:
                    surprise = self._extract_surprise(record)
                    return {
                        "raw_line_index": line_index,
                        "context_index": context_index,
                        "surprise_value": surprise,
                        "source_record": record,
                    }
                seen += 1
        raise AdapterBoundaryError(f"surprise-only context_index out of range: {context_index}")

    def _enriched_metrics(self, fixture: Mapping[str, Any]) -> dict[str, float]:
        metrics = fixture.get("current_metrics")
        context = fixture.get("source_context")
        if not isinstance(metrics, Mapping) or not isinstance(context, Mapping):
            raise AdapterBoundaryError("fixture missing metrics or source_context")
        load = self._metric01(metrics.get("load"), "load")
        surprise = self._metric01(context.get("surprise_value"), "source_context.surprise_value")
        return {
            "coherence": round(1.0 - surprise, 6),
            "load": round(load, 6),
            "risk": round(surprise, 6),
        }

    def _metric01(self, value: Any, label: str) -> float:
        if not isinstance(value, (int, float)):
            raise AdapterBoundaryError(f"fixture metric is not numeric: {label}")
        number = float(value)
        if number < 0 or number > 1:
            raise AdapterBoundaryError(f"fixture metric outside 0..1: {label}")
        return number

    def _validate_fixture_boundary(self, fixture: Mapping[str, Any]) -> None:
        trace = fixture.get("adapter_trace")
        if not isinstance(trace, Mapping):
            raise AdapterBoundaryError("fixture is missing adapter_trace")
        rules = set(trace.get("semantic_rules") or [])
        missing = sorted(self.required_rules - rules)
        if missing:
            raise AdapterBoundaryError("fixture missing required semantic rules: " + ", ".join(missing))
        context = fixture.get("source_context")
        if not isinstance(context, Mapping):
            raise AdapterBoundaryError("fixture is missing source_context")
        blocked = set(context.get("blocked_fields_not_used") or [])
        if "vit" not in blocked or "action_as_015_action" not in blocked:
            raise AdapterBoundaryError("fixture does not preserve blocked vit/action boundaries")
        metrics = fixture.get("current_metrics")
        if not isinstance(metrics, Mapping):
            raise AdapterBoundaryError("fixture missing current_metrics")
        for key in ("coherence", "load", "risk"):
            self._metric01(metrics.get(key), key)
        self._metric01(context.get("surprise_value"), "source_context.surprise_value")

    def _extract_surprise(self, record: Mapping[str, Any]) -> float:
        value = record.get("surprise", record.get("sur"))
        return self._metric01(value, "record.surprise/sur")

    def _is_surprise_only_record(self, record: Mapping[str, Any]) -> bool:
        if "surprise" not in record and "sur" not in record:
            return False
        return not isinstance(record.get("inputs"), Mapping)

    def raw_record_family_summary(self) -> dict[str, Any]:
        shape_counts: Counter[str] = Counter()
        input_keys: Counter[str] = Counter()
        decision_mappable = 0
        context_only = 0
        surprise_only_context_probe_records = 0
        total = 0
        with self.raw_021_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                total += 1
                record = json.loads(line)
                shape_counts[",".join(sorted(record.keys()))] += 1
                inputs = record.get("inputs")
                if isinstance(inputs, Mapping):
                    input_keys.update(str(key) for key in inputs.keys())
                has_surprise = "surprise" in record or "sur" in record
                has_inputs = isinstance(inputs, Mapping)
                has_cpu = has_inputs and ("cpu_temp" in inputs or "cpu" in inputs)
                if has_cpu and has_surprise:
                    decision_mappable += 1
                elif has_surprise:
                    context_only += 1
                    if self._is_surprise_only_record(record):
                        surprise_only_context_probe_records += 1
        return {
            "verdict": "STONE_021_FULL_RECORD_FAMILY_SUMMARY_READY",
            "total_records": total,
            "decision_adapter_records": decision_mappable,
            "context_only_records": context_only,
            "surprise_only_context_probe_records": surprise_only_context_probe_records,
            "expanded_signal_candidate_records": decision_mappable + surprise_only_context_probe_records,
            "shape_counts": dict(shape_counts.most_common()),
            "input_key_counts": dict(input_keys.most_common()),
            "not_claimed": [
                "does not claim context-only records drive Stone 015 decisions",
                "surprise-only context probes use neutral load, not 021 load telemetry",
                "does not claim universal 021-to-015 mapping",
                "does not map vit to coherence",
                "does not map 021 actions to 015 actions",
            ],
        }
