from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .bridge import SpiraBridge, SpiraBridgeConfig, VesselIntent

DEFAULT_PHASE_CAPS = {
    "healthy_warmup": 25,
    "healthy_growth": 50,
    "soft_degradation": 50,
    "incident_1": 40,
    "recovery_1": 60,
    "healthy_window": 75,
    "incident_2": 65,
    "recovery_2": 85,
    "final_healthy": 100,
}


@dataclass
class OrchestratorConfig:
    db_path: str = "spira_memory.db"
    random_seed: int = 42
    phase_caps: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_PHASE_CAPS))
    max_fast_streak_above_50: int = 2
    max_fast_streak_above_75: int = 1
    sleep_seconds: float = 0.0
    restart_at_step: int = 50


@dataclass
class OrchestratorState:
    rollout_percent: int = 0
    paused: bool = False
    history: List[Dict[str, Any]] = field(default_factory=list)
    restart_done: bool = False
    consecutive_fast: int = 0


class RolloutOrchestrator:
    def __init__(self, bridge: SpiraBridge, session_id: str, config: Optional[OrchestratorConfig] = None):
        self.bridge = bridge
        self.session_id = session_id
        self.config = config or OrchestratorConfig()
        self.state = OrchestratorState()
        self._rng = random.Random(self.config.random_seed)

    def phase_of(self, step: int) -> str:
        if 0 <= step <= 14:
            return "healthy_warmup"
        if 15 <= step <= 24:
            return "healthy_growth"
        if 25 <= step <= 34:
            return "soft_degradation"
        if 35 <= step <= 44:
            return "incident_1"
        if 45 <= step <= 59:
            return "recovery_1"
        if 60 <= step <= 69:
            return "healthy_window"
        if 70 <= step <= 79:
            return "incident_2"
        if 80 <= step <= 89:
            return "recovery_2"
        return "final_healthy"

    def generate_metrics(self, step: int, rollout_percent: int) -> Tuple[str, Dict[str, float]]:
        phase = self.phase_of(step)
        m = {
            "coherence": 0.96,
            "signal": 0.90,
            "latency_health": 0.93,
            "error_health": 0.95,
            "saturation_health": 0.91,
        }
        pressure = min(rollout_percent / 100.0, 1.0)
        m["latency_health"] -= 0.10 * pressure
        m["saturation_health"] -= 0.14 * pressure
        m["coherence"] -= 0.04 * pressure

        if phase == "healthy_warmup":
            pass
        elif phase == "healthy_growth":
            m["signal"] += 0.02
            m["coherence"] += 0.01
        elif phase == "soft_degradation":
            m["coherence"] -= 0.10
            m["signal"] -= 0.08
            m["latency_health"] -= 0.12
            m["error_health"] -= 0.08
            m["saturation_health"] -= 0.10
        elif phase == "incident_1":
            m["coherence"] -= 0.28
            m["signal"] -= 0.24
            m["latency_health"] -= 0.36
            m["error_health"] -= 0.40
            m["saturation_health"] -= 0.24
        elif phase == "recovery_1":
            m["coherence"] -= 0.08
            m["signal"] -= 0.06
            m["latency_health"] -= 0.10
            m["error_health"] -= 0.08
            m["saturation_health"] -= 0.08
        elif phase == "healthy_window":
            m["coherence"] += 0.01
            m["signal"] += 0.02
        elif phase == "incident_2":
            wobble = 0.04 * __import__("math").sin(step)
            m["coherence"] -= 0.24 + wobble
            m["signal"] -= 0.20
            m["latency_health"] -= 0.30
            m["error_health"] -= 0.34
            m["saturation_health"] -= 0.22
        elif phase == "recovery_2":
            m["coherence"] -= 0.06
            m["signal"] -= 0.04
            m["latency_health"] -= 0.08
            m["error_health"] -= 0.06
            m["saturation_health"] -= 0.06
        elif phase == "final_healthy":
            m["coherence"] += 0.015
            m["signal"] += 0.025

        for key in list(m):
            m[key] += self._rng.uniform(-0.012, 0.012)
            m[key] = max(0.0, min(1.0, round(m[key], 4)))
        return phase, m

    def choose_intent(self, metrics: Dict[str, float]) -> str:
        if metrics["error_health"] < 0.55 or metrics["latency_health"] < 0.55:
            return "filter"
        if metrics["coherence"] < 0.78:
            return "heal"
        if metrics["signal"] > 0.88 and metrics["coherence"] > 0.90:
            return "expand"
        return "balance"

    def choose_payload(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        rollout_percent = self.state.rollout_percent
        if metrics["error_health"] < 0.55 or metrics["latency_health"] < 0.55:
            actions = ["contain", "analyze"]
            options = ["safe", "accurate"]
        elif metrics["coherence"] < 0.78:
            actions = ["repair", "stabilize"]
            options = ["safe", "accurate", "fast"]
        elif rollout_percent < 25:
            actions = ["expand", "observe"]
            options = ["safe", "fast", "accurate"]
        elif rollout_percent < 60:
            actions = ["observe", "stabilize"]
            options = ["safe", "accurate", "fast"]
        else:
            actions = ["observe", "finalize"]
            options = ["safe", "accurate", "fast"]
        return {"actions": actions, "options": options, "metrics": metrics}

    def _phase_cap(self, phase: str) -> int:
        return int(self.config.phase_caps.get(phase, 100))

    def _fast_delta(self, rollout_percent: int) -> int:
        if rollout_percent < 10:
            return 10
        if rollout_percent < 25:
            return 15
        if rollout_percent < 40:
            return 10
        if rollout_percent < 60:
            return 10
        if rollout_percent < 80:
            return 5
        return 2

    def _safe_delta(self, rollout_percent: int) -> int:
        if rollout_percent < 20:
            return 5
        if rollout_percent < 50:
            return 10
        if rollout_percent < 80:
            return 5
        return 2

    def apply_decision(self, decision: str, metrics: Dict[str, float], phase: str) -> str:
        rp = self.state.rollout_percent
        phase_cap = self._phase_cap(phase)
        severe = metrics["error_health"] < 0.55 or metrics["latency_health"] < 0.55

        if decision == "fast":
            self.state.consecutive_fast += 1
            delta = self._fast_delta(rp)
            throttle_reasons: List[str] = []
            if rp >= 50 and self.state.consecutive_fast > self.config.max_fast_streak_above_50:
                delta = min(delta, 5)
                throttle_reasons.append("fast_streak_above_50")
            if rp >= 75 and self.state.consecutive_fast > self.config.max_fast_streak_above_75:
                delta = min(delta, 2)
                throttle_reasons.append("fast_streak_above_75")
            target = min(100, phase_cap, rp + delta)
            if target == rp:
                self.state.paused = False
                if rp >= phase_cap:
                    return f"maintain rollout at {rp}% (phase cap {phase_cap}% reached)"
                return f"maintain full rollout at {rp}%"
            self.state.rollout_percent = target
            self.state.paused = False
            if throttle_reasons:
                return f"throttled fast rollout {rp}% -> {target}% ({','.join(throttle_reasons)})"
            return f"expand rollout {rp}% -> {target}%"

        self.state.consecutive_fast = 0
        if decision == "safe":
            delta = self._safe_delta(rp)
            target = min(100, phase_cap, rp + delta)
            self.state.paused = False
            if target == rp:
                if rp >= phase_cap:
                    return f"maintain rollout at {rp}% (phase cap {phase_cap}% reached)"
                return f"maintain full rollout at {rp}%"
            self.state.rollout_percent = target
            return f"controlled rollout {rp}% -> {target}%"

        if decision == "accurate":
            self.state.paused = True
            if severe:
                cut = 10 if rp >= 40 else 5
                target = max(0, rp - cut)
                self.state.rollout_percent = target
                return f"hold/analyze and reduce rollout {rp}% -> {target}%"
            return f"hold rollout at {rp}% for deeper observation"

        self.state.paused = True
        return f"unknown decision={decision}"

    def step(self, step: int) -> Dict[str, Any]:
        phase, metrics = self.generate_metrics(step, self.state.rollout_percent)
        intent = self.choose_intent(metrics)
        intent_coherence = self.bridge.execute_intent(VesselIntent(intent), session_id=self.session_id)
        payload = self.choose_payload(metrics)
        decision = self.bridge.decide(
            context={"phase": phase, "step": step},
            options=payload["options"],
            session_id=self.session_id,
            actions=payload["actions"],
            metrics=payload["metrics"],
        )
        decision_coherence = self.bridge.peek_coherence(session_id=self.session_id)
        action_text = self.apply_decision(decision, metrics, phase)
        row = {
            "step": step,
            "ts": time.time(),
            "phase": phase,
            "intent": intent,
            "decision": decision,
            "intent_coherence": float(intent_coherence),
            "decision_coherence": float(decision_coherence),
            "rollout_percent": int(self.state.rollout_percent),
            "paused": bool(self.state.paused),
            "orchestrator_action": action_text,
            **metrics,
        }
        self.state.history.append(row)
        return row


def run_rollout_stress_test(
    *,
    steps: int = 100,
    session_id: str = "spira_orchestrator_demo",
    config: Optional[OrchestratorConfig] = None,
) -> Dict[str, Any]:
    cfg = config or OrchestratorConfig()
    bridge_cfg = SpiraBridgeConfig(db_path=cfg.db_path)
    bridge = SpiraBridge(bridge_cfg)
    try:
        bridge.create_session(
            session_id,
            {
                "domain": "100_step_rollout_stress_test",
                "service": "spira-api",
                "goal": "long-horizon orchestration test on guardrails v2.3",
            },
        )
        orch = RolloutOrchestrator(bridge=bridge, session_id=session_id, config=cfg)
        for step in range(steps):
            orch.step(step)
            if step == cfg.restart_at_step and not orch.state.restart_done:
                bridge.close()
                bridge = SpiraBridge(SpiraBridgeConfig(db_path=cfg.db_path))
                orch.bridge = bridge
                orch.state.restart_done = True
            if cfg.sleep_seconds > 0:
                time.sleep(cfg.sleep_seconds)

        history = orch.state.history
        decisions = {"safe": 0, "fast": 0, "accurate": 0}
        phase_decisions: Dict[str, Dict[str, int]] = {}
        for row in history:
            decisions[row["decision"]] = decisions.get(row["decision"], 0) + 1
            phase_bucket = phase_decisions.setdefault(row["phase"], {"accurate": 0, "fast": 0, "safe": 0})
            phase_bucket[row["decision"]] = phase_bucket.get(row["decision"], 0) + 1

        decision_coherences = [float(row["decision_coherence"]) for row in history]
        result = {
            "session_id": session_id,
            "history": history,
            "decision_counts": decisions,
            "phase_decisions": phase_decisions,
            "final_state": {
                "final_rollout_percent": orch.state.rollout_percent,
                "paused": orch.state.paused,
                "history_len": len(history),
                "min_coherence": round(min(decision_coherences), 4),
                "max_coherence": round(max(decision_coherences), 4),
                "avg_coherence": round(sum(decision_coherences) / len(decision_coherences), 4),
                "restart_done": orch.state.restart_done,
            },
        }
        return result
    finally:
        try:
            bridge.close()
        except Exception:
            pass
