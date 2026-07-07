from __future__ import annotations

from typing import Any

from spira_core.vendored_stone015 import load_bridge_classes

from .contract import (
    DEFAULT_015_OPTIONS,
    DECISION_ALLOW,
    DECISION_WARN,
    REASON_ALLOW_OK,
    REASON_WARN_HIGH_LOAD,
    REASON_WARN_LOW_COHERENCE,
    SOURCE_STONE_015,
    mode_to_actions,
)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _to_stone_015_health_metrics(metrics: dict) -> dict:
    """Translate MVP risk/load semantics into Stone 015 health-like metrics."""
    coherence = _clamp01(metrics["coherence"])
    load = _clamp01(metrics["load"])
    risk = _clamp01(metrics["risk"])
    load_health = _clamp01(1.0 - load)
    risk_health = _clamp01(1.0 - risk)
    return {
        "coherence": coherence,
        "load_health": load_health,
        "risk_health": risk_health,
        "signal_health": coherence,
        "saturation_health": load_health,
        "error_health": risk_health,
    }


def call_stone_015(request: dict) -> dict:
    """Call real vendored Stone 015. This function does not substitute a fake decision."""
    bridge_cls, config_cls = load_bridge_classes()
    bridge = bridge_cls(config_cls(db_path=":memory:", auto_checkpoint=False, enable_trace=False))
    metrics = dict(request["current_metrics"])
    stone_015_metrics = _to_stone_015_health_metrics(metrics)
    mode = request.get("options", {}).get("mode", "normal")
    requested_action = str(request["requested_action"])
    decision = bridge.decide(
        {"requested_action": requested_action, "mode": mode},
        list(DEFAULT_015_OPTIONS),
        actions=mode_to_actions(mode, requested_action),
        metrics=stone_015_metrics,
    )
    coherence = float(bridge.get_coherence())
    return {
        "decision": decision,
        "coherence": coherence,
        "input_metrics": metrics,
        "stone_015_metrics": stone_015_metrics,
        "mode": mode,
        "requested_action": requested_action,
        "metric_adapter": "mvp_risk_load_to_stone_015_health_metrics",
        "vendored_stone_015_verified": True,
    }


def classify_stone_015_result(raw_015_result: dict[str, Any]) -> tuple[str, str, float | None]:
    decision = str(raw_015_result.get("decision", "")).strip().lower()
    coherence = raw_015_result.get("coherence")
    coherence_state = float(coherence) if coherence is not None else None
    metrics = raw_015_result.get("input_metrics") or {}
    load = float(metrics.get("load", 0.0))

    if decision in {"accurate", "safe", "contract", "wait"}:
        return DECISION_WARN, REASON_WARN_LOW_COHERENCE, coherence_state
    if coherence_state is not None and coherence_state < 0.5:
        return DECISION_WARN, REASON_WARN_LOW_COHERENCE, coherence_state
    if load >= 0.75:
        return DECISION_WARN, REASON_WARN_HIGH_LOAD, coherence_state
    return DECISION_ALLOW, REASON_ALLOW_OK, coherence_state


def core_decide(request: dict) -> tuple[str, str, float | None, dict]:
    raw = call_stone_015(request)
    decision, reason_code, coherence_state = classify_stone_015_result(raw)
    raw["decision_source"] = SOURCE_STONE_015
    return decision, reason_code, coherence_state, raw
