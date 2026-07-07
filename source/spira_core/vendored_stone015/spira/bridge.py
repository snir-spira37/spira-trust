from __future__ import annotations

import logging
import textwrap
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from .parser import parse_script
from .runtime import RuntimeConfig, SpiraRuntime
from .storage import SpiraMemoryDB

logger = logging.getLogger(__name__)


class SpiraMode(Enum):
    DECISION = "decision"
    CIRCUIT_BREAKER = "circuit_breaker"
    ANOMALY_DETECTOR = "anomaly_detector"
    WORKFLOW_ORCHESTRATOR = "workflow_orchestrator"
    CONTEXT_ENRICHER = "context_enricher"


class VesselIntent(Enum):
    EXPAND = "expand"
    CONTRACT = "contract"
    BALANCE = "balance"
    HEAL = "heal"
    FILTER = "filter"


@dataclass
class SpiraBridgeConfig:
    mode: SpiraMode = SpiraMode.DECISION
    db_path: str = "spira_memory.db"
    auto_checkpoint: bool = True
    checkpoint_interval_seconds: int = 60
    coherence_threshold: float = 0.35
    fast_track_min_coherence: float = 0.78
    safe_only_below_coherence: float = 0.62
    incident_metric_floor: float = 0.65
    trend_window: int = 4
    max_decline_for_fast: float = 0.12
    cooldown_decisions_after_incident: int = 3
    healthy_observations_to_unlock_fast_after_incident: int = 2
    recovery_fast_unlock_internal_floor: float = 0.78
    recovery_fast_unlock_metric_floor: float = 0.85
    healthy_metrics_floor_for_conflict_tolerance: float = 0.88
    worst_metric_floor_for_conflict_tolerance: float = 0.80
    max_llm_calls_per_session: int = 10
    max_quantum_ops_per_session: int = 50
    enable_trace: bool = False
    world_name: str = "production"
    partzuf_name: str = "integration"
    vessel_name: str = "bridge"
    script_timeout: float = 30.0
    llm_timeout: float = 20.0
    on_shevira: Optional[Callable[[float, Dict[str, Any]], None]] = None
    on_tikkun: Optional[Callable[[float, Dict[str, Any]], None]] = None
    on_measure: Optional[Callable[[str, Any], None]] = None


@dataclass
class SpiraSession:
    session_id: str
    created_at: float
    last_activity: float
    variables: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    decisions: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)


class SpiraBridge:
    """Bridge integration layer for using Spira as a decision engine and more."""

    def __init__(self, config: Optional[SpiraBridgeConfig] = None):
        self.config = config or SpiraBridgeConfig()
        self._lock = threading.RLock()
        self._runtime: Optional[SpiraRuntime] = None
        self._session_store = SpiraMemoryDB(self.config.db_path)
        self._sessions: Dict[str, SpiraSession] = {}
        self._session_runtimes: Dict[str, SpiraRuntime] = {}
        self._last_checkpoint = time.time()
        self._stats = {
            "total_decisions": 0,
            "total_anomalies": 0,
            "total_circuit_breaks": 0,
            "total_tikkun_calls": 0,
            "avg_coherence": 0.0,
            "coherence_samples": 0,
        }
        self._init_runtime()

    def _init_runtime(self) -> None:
        runtime_cfg = RuntimeConfig(
            echo_logs=self.config.enable_trace,
            trace=self.config.enable_trace,
            continue_on_error=True,
            max_errors=50,
            auto_checkpoint_label="bridge_checkpoint" if self.config.auto_checkpoint else None,
            profile=False,
            log_batch_size=50,
            max_loop_iters=1000,
            max_logs=None,
        )
        self._runtime = SpiraRuntime(db_path=self.config.db_path, config=runtime_cfg)
        self._disable_runtime_db_logging(self._runtime)
        self._initialize_runtime_state(self._runtime)

    def _disable_runtime_db_logging(self, runtime: SpiraRuntime) -> None:
        try:
            runtime.db._logging_enabled = False
        except Exception:
            logger.exception("Failed to disable runtime DB logging")

    def _persist_session_runtime(self, session_id: str) -> None:
        if session_id not in self._sessions or session_id not in self._session_runtimes:
            return
        session = self._sessions[session_id]
        rt = self._session_runtimes[session_id]
        try:
            self._session_store.save_bridge_session(
                session_id,
                session.context,
                session.created_at,
                session.last_activity,
                status="active",
                state=rt.serialize_state(),
            )
        except Exception:
            logger.exception("Failed to persist session runtime", extra={"session_id": session_id})

    def _restore_persisted_session_runtime(self, session_id: str, row: Dict[str, Any]) -> SpiraRuntime:
        runtime_cfg = RuntimeConfig(
            echo_logs=self.config.enable_trace,
            trace=self.config.enable_trace,
            continue_on_error=True,
            max_errors=50,
            auto_checkpoint_label=None,
            profile=False,
            log_batch_size=50,
            max_loop_iters=1000,
            max_logs=None,
        )
        rt = SpiraRuntime(db_path=self.config.db_path, config=runtime_cfg)
        self._disable_runtime_db_logging(rt)
        state = row.get("state")
        if state:
            rt.restore_state(state)
        else:
            self._initialize_runtime_state(rt)
        return rt

    def _ensure_runtime(self) -> SpiraRuntime:
        if self._runtime is None:
            self._init_runtime()
        return self._runtime

    def _initialize_runtime_state(self, runtime: SpiraRuntime) -> None:
        init_script = textwrap.dedent(
            f"""
            world create {self.config.world_name} flow=1.0
            world use {self.config.world_name}
            partzuf create {self.config.partzuf_name} mode=balanced
            partzuf use {self.config.partzuf_name}
            vessel create {self.config.vessel_name} capacity=1.0 screen=1.0
            vessel use {self.config.vessel_name}
            """
        ).strip()
        try:
            nodes = parse_script(init_script)
            runtime.execute(nodes)
        except Exception:
            logger.exception("Failed to initialize runtime state")

    def _hydrate_session_from_row(self, row: Dict[str, Any]) -> SpiraSession:
        session = SpiraSession(
            session_id=row["session_id"],
            created_at=row["created_at"],
            last_activity=row["last_activity"],
            context=row.get("context") or {},
        )
        self._sessions[session.session_id] = session
        return session

    def _load_persisted_session(self, session_id: str) -> Optional[SpiraSession]:
        row = self._session_store.get_bridge_session(session_id)
        if row is None:
            return None
        session = self._sessions.get(session_id)
        if session is None:
            session = self._hydrate_session_from_row(row)
        return session

    def _get_runtime(self, session_id: Optional[str] = None) -> SpiraRuntime:
        if session_id is None:
            return self._ensure_runtime()
        with self._lock:
            if session_id not in self._session_runtimes:
                row = self._session_store.get_bridge_session(session_id)
                if not row:
                    raise ValueError(f"unknown session: {session_id}")
                if session_id not in self._sessions:
                    self._hydrate_session_from_row(row)
                self._session_runtimes[session_id] = self._restore_persisted_session_runtime(session_id, row)
            self._sessions[session_id].last_activity = time.time()
            try:
                self._session_store.touch_bridge_session(session_id, self._sessions[session_id].last_activity)
            except Exception:
                logger.exception("Failed to touch session activity", extra={"session_id": session_id})
            return self._session_runtimes[session_id]

    def _update_stats(self, coherence: float) -> None:
        with self._lock:
            total = self._stats["coherence_samples"] * self._stats["avg_coherence"]
            self._stats["coherence_samples"] += 1
            self._stats["avg_coherence"] = (total + coherence) / self._stats["coherence_samples"]

    def _maybe_checkpoint(self) -> None:
        if not self.config.auto_checkpoint:
            return
        if time.time() - self._last_checkpoint > self.config.checkpoint_interval_seconds:
            rt = self._ensure_runtime()
            try:
                rt.checkpoint("bridge_auto")
                self._last_checkpoint = time.time()
            except Exception:
                logger.exception("Bridge auto-checkpoint failed")

    def _handle_shevira(self, coherence: float, context: Dict[str, Any]) -> None:
        self._stats["total_circuit_breaks"] += 1
        if self.config.on_shevira:
            try:
                self.config.on_shevira(coherence, context)
            except Exception:
                logger.exception("on_shevira callback failed")

    def session_exists(self, session_id: str) -> bool:
        with self._lock:
            if session_id in self._sessions:
                return True
            return self._session_store.get_bridge_session(session_id) is not None

    def get_session(self, session_id: str) -> Optional[SpiraSession]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                session = self._load_persisted_session(session_id)
            if session is None:
                return None
            session.last_activity = time.time()
            try:
                self._session_store.touch_bridge_session(session_id, session.last_activity)
            except Exception:
                logger.exception("Failed to touch session during get_session", extra={"session_id": session_id})
            return session

    def get_active_session_count(self) -> int:
        return self._session_store.count_bridge_sessions()

    def _compute_coherence(self, session_id: Optional[str] = None, *, update_stats: bool = True) -> float:
        rt = self._get_runtime(session_id)
        rt.recompute_state()
        coherence = rt.s.coherence
        if session_id is None and update_stats:
            self._update_stats(coherence)
        return coherence

    def get_coherence(self, session_id: Optional[str] = None) -> float:
        return self._compute_coherence(session_id=session_id, update_stats=True)

    def peek_coherence(self, session_id: Optional[str] = None) -> float:
        return self._compute_coherence(session_id=session_id, update_stats=False)

    def get_vessel_state(self, session_id: Optional[str] = None) -> Dict[str, float]:
        rt = self._get_runtime(session_id)
        v = rt.vessel()
        rt.recompute_state()
        return {
            "or_level": v.or_level,
            "capacity": v.capacity,
            "screen_strength": v.screen_strength,
            "coherence": rt.s.coherence,
            "noise": rt.s.noise,
            "shevira": rt.s.shevira_flag,
        }

    def execute_intent(
        self,
        intent: VesselIntent,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> float:
        rt = self._get_runtime(session_id)
        policy = self._policy_state(rt)
        if intent == VesselIntent.EXPAND:
            rt.masach("soft")
            rt.draw_or(0.1)
        elif intent == VesselIntent.CONTRACT:
            rt.tzimtzum("medium")
        elif intent == VesselIntent.HEAL:
            rt.tikkun()
            self._stats["total_tikkun_calls"] += 1
        elif intent == VesselIntent.FILTER:
            rt.masach("strict")
        elif intent == VesselIntent.BALANCE:
            rt.masach("truth")
        rt.recompute_state()
        current = float(rt.s.coherence)
        target = self._intent_target_coherence(intent, current, policy)
        coherence = self._sync_runtime_coherence(rt, target)
        policy["last_intent"] = intent.value
        if intent == VesselIntent.HEAL and self.config.on_tikkun:
            try:
                self.config.on_tikkun(coherence, context or {})
            except Exception:
                logger.exception("on_tikkun callback failed")
        if rt.s.shevira_flag:
            self._handle_shevira(coherence, context or {})
        if session_id is not None:
            self._persist_session_runtime(session_id)
        self._maybe_checkpoint()
        return coherence

    def _policy_state(self, rt: SpiraRuntime) -> Dict[str, Any]:
        state = rt.s.memory.setdefault(
            "decision_policy",
            {
                "history": [],
                "cooldown_remaining": 0,
                "last_incident_at": None,
                "last_decision": None,
                "recovery_unlock_remaining": 0,
                "last_intent": None,
                "healthy_observation_count": 0,
                "healthy_streak": 0,
                "recent_metrics": [],
                "current_effective_score": 1.0,
                "current_metric_anchor": 1.0,
            },
        )
        state.setdefault("history", [])
        state.setdefault("cooldown_remaining", 0)
        state.setdefault("last_incident_at", None)
        state.setdefault("last_decision", None)
        state.setdefault("recovery_unlock_remaining", 0)
        state.setdefault("last_intent", None)
        state.setdefault("healthy_observation_count", 0)
        state.setdefault("healthy_streak", 0)
        state.setdefault("recent_metrics", [])
        state.setdefault("current_effective_score", rt.s.coherence)
        state.setdefault("current_metric_anchor", rt.s.coherence)
        return state

    def _clip01(self, value: float) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return 0.0

    def _clean_options(self, options: Optional[List[str]]) -> List[str]:
        opts = [str(opt).strip() for opt in (options or []) if str(opt).strip()]
        return opts or ["expand", "wait", "contract"]

    def _metric_summary(self, metrics: Optional[Dict[str, float]]) -> Tuple[Optional[float], Optional[float], float, bool]:
        if not metrics:
            return None, None, 0.0, False
        clipped = {str(k): self._clip01(v) for k, v in metrics.items()}
        values = list(clipped.values())
        avg_metric = sum(values) / len(values) if values else None
        metric_coherence = clipped.get("coherence")
        worst_metric = min(values) if values else 0.0
        has_incident = bool(values) and worst_metric < self.config.incident_metric_floor
        return avg_metric, metric_coherence, worst_metric, has_incident

    def _trend_summary(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        recent = history[-max(2, self.config.trend_window):]
        if len(recent) < 2:
            return {"delta": 0.0, "declining": False, "decline_streak": 0}
        scores = [float(item.get("effective_score", item.get("internal_coherence", 0.0))) for item in recent]
        delta = scores[-1] - scores[0]
        decline_streak = 0
        for prev, cur in zip(scores[-2::-1], scores[:0:-1]):
            if cur < prev:
                decline_streak += 1
            else:
                break
        return {
            "delta": delta,
            "declining": delta < 0,
            "decline_streak": decline_streak,
        }

    def _prefer_option(self, candidates: List[str], primary: List[str], fallback: List[str]) -> str:
        for preferred in primary:
            if preferred in candidates:
                return preferred
        for preferred in fallback:
            if preferred in candidates:
                return preferred
        return candidates[0]

    def _metric_anchor(self, avg_metric: Optional[float], metric_coherence: Optional[float], worst_metric: float) -> Optional[float]:
        weighted: List[Tuple[float, float]] = []
        if metric_coherence is not None:
            weighted.append((0.50, metric_coherence))
        if avg_metric is not None:
            weighted.append((0.30, avg_metric))
        if worst_metric:
            weighted.append((0.20, worst_metric))
        if not weighted:
            return None
        total_weight = sum(weight for weight, _ in weighted)
        return sum(weight * value for weight, value in weighted) / total_weight

    def _qualifies_healthy_observation(
        self,
        *,
        coherence_value: float,
        avg_metric: Optional[float],
        metric_coherence: Optional[float],
        worst_metric: float,
        metric_incident: bool,
    ) -> bool:
        if metric_incident:
            return False
        if coherence_value < self.config.recovery_fast_unlock_internal_floor:
            return False
        if metric_coherence is not None and metric_coherence < self.config.recovery_fast_unlock_metric_floor:
            return False
        if avg_metric is not None and avg_metric < self.config.recovery_fast_unlock_metric_floor:
            return False
        if worst_metric and worst_metric < max(self.config.incident_metric_floor, self.config.recovery_fast_unlock_metric_floor - 0.08):
            return False
        return True

    def _project_unlock_fast_for_current_step(
        self,
        *,
        policy: Dict[str, Any],
        internal_coherence: float,
        avg_metric: Optional[float],
        metric_coherence: Optional[float],
        worst_metric: float,
        metric_incident: bool,
        cooldown_remaining: int,
    ) -> bool:
        if cooldown_remaining > 0:
            return False
        streak = int(policy.get("healthy_streak", 0))
        current_healthy = self._qualifies_healthy_observation(
            coherence_value=internal_coherence,
            avg_metric=avg_metric,
            metric_coherence=metric_coherence,
            worst_metric=worst_metric,
            metric_incident=metric_incident,
        )
        projected = streak + (1 if current_healthy else 0)
        return projected >= int(self.config.healthy_observations_to_unlock_fast_after_incident)

    def _sync_runtime_coherence(self, rt: SpiraRuntime, target: float) -> float:
        rt.recompute_state()
        derived = float(rt.s.derived_coherence)
        clamped = self._clip01(target)
        delta = clamped - derived
        if delta >= 0.0:
            rt.s.manual_coherence_bonus = min(0.25, delta)
            rt.s.manual_coherence_penalty = 0.0
        else:
            rt.s.manual_coherence_bonus = 0.0
            rt.s.manual_coherence_penalty = min(1.0, -delta)
        rt.recompute_state()
        return float(rt.s.coherence)

    def _intent_target_coherence(self, intent: VesselIntent, current: float, policy: Dict[str, Any]) -> float:
        cooldown = int(policy.get("cooldown_remaining", 0))
        recovery = int(policy.get("recovery_unlock_remaining", 0))
        target = current
        if intent == VesselIntent.EXPAND:
            target -= 0.02 if current >= self.config.fast_track_min_coherence else 0.04
        elif intent == VesselIntent.CONTRACT:
            target += 0.02 if current < 0.9 else 0.0
        elif intent == VesselIntent.FILTER:
            target += 0.015 if current < 0.9 else 0.0
        elif intent == VesselIntent.BALANCE:
            target += 0.01 if current < 0.92 else 0.0
        elif intent == VesselIntent.HEAL:
            target += 0.08 if current < 0.9 else 0.03
            if cooldown > 0:
                target += 0.01
            if recovery > 0:
                target += 0.01
        return self._clip01(target)

    def _update_runtime_from_decision(
        self,
        rt: SpiraRuntime,
        *,
        policy: Dict[str, Any],
        decision: str,
        internal_coherence: float,
        metric_anchor: Optional[float],
        metric_incident: bool,
        worst_metric: float,
        trend: Dict[str, Any],
        cooldown_remaining: int,
        recovery_unlock_remaining: int,
        healthy_for_unlock: bool,
        action_list: List[str],
        effective_score: float,
    ) -> float:
        anchor = metric_anchor if metric_anchor is not None else internal_coherence
        target = (0.60 * internal_coherence) + (0.40 * anchor)

        if decision == "fast":
            target -= 0.03
            if effective_score >= 0.93 and cooldown_remaining == 0 and recovery_unlock_remaining == 0:
                target += 0.01
        elif decision == "accurate":
            target -= 0.01
        elif decision == "safe":
            target += 0.01 if anchor >= 0.80 else -0.01

        if metric_incident:
            target -= 0.08
        if worst_metric and worst_metric < self.config.incident_metric_floor:
            target -= min(0.08, (self.config.incident_metric_floor - worst_metric) * 0.18)

        if trend.get("declining"):
            target -= min(0.06, abs(float(trend.get("delta", 0.0))) * 0.25 + float(trend.get("decline_streak", 0)) * 0.01)

        if cooldown_remaining > 0:
            target -= 0.03
        if recovery_unlock_remaining > 0:
            target -= 0.01

        repair_bias = len({"repair", "recover", "stabilize", "observe"}.intersection(action_list))
        if repair_bias and not metric_incident and anchor >= self.config.safe_only_below_coherence:
            target += min(0.05, 0.015 * repair_bias)
        if healthy_for_unlock:
            target += 0.02

        updated = self._sync_runtime_coherence(rt, target)
        policy["current_effective_score"] = effective_score
        policy["current_metric_anchor"] = anchor
        return updated

    def _apply_decision_guardrails(
        self,
        opts: List[str],
        *,
        internal_coherence: float,
        avg_metric: Optional[float],
        metric_coherence: Optional[float],
        trend: Dict[str, Any],
        cooldown_remaining: int,
        recovery_unlock_remaining: int,
        recovery_unlock_ready_now: bool,
    ) -> Tuple[List[str], List[str]]:
        allowed = list(opts)
        reasons: List[str] = []

        if cooldown_remaining > 0 and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("cooldown_active")

        if recovery_unlock_remaining > 0 and not recovery_unlock_ready_now and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("recovery_warmup_active")

        if internal_coherence < self.config.fast_track_min_coherence and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("internal_coherence_below_fast_floor")

        if metric_coherence is not None and metric_coherence < self.config.fast_track_min_coherence and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("metric_coherence_below_fast_floor")

        if trend.get("declining") and abs(float(trend.get("delta", 0.0))) >= self.config.max_decline_for_fast and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("negative_trend_blocks_fast")

        if avg_metric is not None and avg_metric < self.config.safe_only_below_coherence and "fast" in allowed:
            allowed = [opt for opt in allowed if opt != "fast"]
            reasons.append("average_metric_health_low")

        if not allowed:
            allowed = [opts[0]]
        return allowed, reasons

    def decide(
        self,
        context: Dict[str, Any],
        options: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        *,
        actions: Optional[List[str]] = None,
        metrics: Optional[Dict[str, float]] = None,
    ) -> Any:
        rt = self._get_runtime(session_id)
        internal_coherence = self.get_coherence(session_id=session_id)
        opts = self._clean_options(options)

        action_list = [str(item).strip() for item in (actions or []) if str(item).strip()]
        metric_map = {str(k): float(v) for k, v in (metrics or {}).items()}
        avg_metric, metric_coherence, worst_metric, metric_incident = self._metric_summary(metric_map)
        effective_score_parts = [internal_coherence]
        if avg_metric is not None:
            effective_score_parts.append(avg_metric)
        if metric_coherence is not None:
            effective_score_parts.append(metric_coherence)
        effective_score = sum(effective_score_parts) / len(effective_score_parts)

        policy = self._policy_state(rt)
        trend = self._trend_summary(policy["history"])
        incident_by_state = internal_coherence < self.config.safe_only_below_coherence
        incident_by_metric_coherence = metric_coherence is not None and metric_coherence < self.config.safe_only_below_coherence

        if metric_incident or incident_by_state or incident_by_metric_coherence:
            policy["cooldown_remaining"] = max(
                int(policy.get("cooldown_remaining", 0)),
                int(self.config.cooldown_decisions_after_incident),
            )
            policy["recovery_unlock_remaining"] = max(
                int(policy.get("recovery_unlock_remaining", 0)),
                int(self.config.healthy_observations_to_unlock_fast_after_incident),
            )
            policy["last_incident_at"] = time.time()

        risk_actions = {"recover", "repair", "contain", "analyze", "stabilize"}
        growth_actions = {"expand", "accelerate", "finalize", "resume", "observe"}
        risk_bias = len(risk_actions.intersection(action_list))
        growth_bias = len(growth_actions.intersection(action_list))
        conflicting_actions = risk_bias > 0 and growth_bias > 0

        cooldown_remaining = int(policy.get("cooldown_remaining", 0))
        recovery_unlock_remaining = int(policy.get("recovery_unlock_remaining", 0))
        healthy_metric_conflict_tolerance = (
            not metric_incident
            and internal_coherence >= self.config.healthy_metrics_floor_for_conflict_tolerance
            and (metric_coherence is None or metric_coherence >= self.config.healthy_metrics_floor_for_conflict_tolerance)
            and (avg_metric is None or avg_metric >= self.config.healthy_metrics_floor_for_conflict_tolerance)
            and worst_metric >= self.config.worst_metric_floor_for_conflict_tolerance
            and not trend.get("declining")
            and cooldown_remaining == 0
        )
        recovery_safe_override = (
            not metric_incident
            and avg_metric is not None
            and avg_metric >= 0.84
            and metric_coherence is not None
            and metric_coherence >= 0.70
            and worst_metric >= 0.70
            and internal_coherence >= 0.45
            and not trend.get("declining")
            and (
                recovery_unlock_remaining > 0
                or cooldown_remaining > 0
                or internal_coherence < self.config.fast_track_min_coherence
                or str(policy.get("last_intent", "")) in {"filter", "heal"}
            )
        )
        recovery_unlock_ready_now = self._project_unlock_fast_for_current_step(
            policy=policy,
            internal_coherence=internal_coherence,
            avg_metric=avg_metric,
            metric_coherence=metric_coherence,
            worst_metric=worst_metric,
            metric_incident=metric_incident,
            cooldown_remaining=cooldown_remaining,
        )
        recovery_safe_override = recovery_safe_override and not recovery_unlock_ready_now
        allowed, guardrail_reasons = self._apply_decision_guardrails(
            opts,
            internal_coherence=internal_coherence,
            avg_metric=avg_metric,
            metric_coherence=metric_coherence,
            trend=trend,
            cooldown_remaining=cooldown_remaining,
            recovery_unlock_remaining=recovery_unlock_remaining,
            recovery_unlock_ready_now=recovery_unlock_ready_now,
        )

        severe = (
            ((internal_coherence < self.config.safe_only_below_coherence) and not recovery_safe_override)
            or ((metric_coherence is not None and metric_coherence < self.config.safe_only_below_coherence) and not recovery_safe_override)
            or (avg_metric is not None and avg_metric < self.config.safe_only_below_coherence)
            or metric_incident
            or (risk_bias >= 2 and not healthy_metric_conflict_tolerance and not recovery_safe_override)
        )
        caution = (
            cooldown_remaining > 0
            or trend.get("declining")
            or (risk_bias > growth_bias and not healthy_metric_conflict_tolerance and not recovery_safe_override)
            or effective_score < self.config.fast_track_min_coherence
            or (conflicting_actions and healthy_metric_conflict_tolerance)
        )
        aggressive_ok = (
            not severe
            and not caution
            and effective_score >= 0.88
            and internal_coherence >= self.config.fast_track_min_coherence
            and (metric_coherence is None or metric_coherence >= self.config.fast_track_min_coherence)
            and growth_bias >= risk_bias
        )
        recovery_promotion_ok = (
            recovery_unlock_ready_now
            and not severe
            and cooldown_remaining == 0
            and internal_coherence >= self.config.recovery_fast_unlock_internal_floor
            and (metric_coherence is None or metric_coherence >= self.config.recovery_fast_unlock_metric_floor)
            and (avg_metric is None or avg_metric >= self.config.recovery_fast_unlock_metric_floor)
            and growth_bias >= risk_bias
        )

        if len(allowed) == 1:
            decision = allowed[0]
        elif healthy_metric_conflict_tolerance and conflicting_actions:
            decision = self._prefer_option(allowed, ["safe", "fast", "accurate"], [allowed[0]])
        elif recovery_safe_override:
            decision = self._prefer_option(allowed, ["safe", "accurate", "fast"], [allowed[0]])
        elif severe:
            decision = self._prefer_option(allowed, ["accurate", "safe"], ["contract", "wait", allowed[0]])
        elif aggressive_ok or recovery_promotion_ok:
            decision = self._prefer_option(allowed, ["fast", "safe", "accurate"], [allowed[0]])
        elif caution:
            decision = self._prefer_option(allowed, ["safe", "accurate"], ["wait", allowed[0]])
        elif effective_score >= 0.72:
            decision = self._prefer_option(allowed, ["safe", "fast", "accurate"], [allowed[0]])
        else:
            decision = self._prefer_option(allowed, ["accurate", "safe", "contract"], [allowed[0]])

        rt.s.memory["decision_context"] = {
            **dict(context),
            "actions": action_list,
            "metrics": metric_map,
            "allowed_options": list(allowed),
            "guardrails": list(guardrail_reasons),
            "effective_score": effective_score,
        }
        rt.s.last_result = decision
        self._stats["total_decisions"] += 1

        audit = {
            "ts": time.time(),
            "decision": decision,
            "internal_coherence": internal_coherence,
            "metric_coherence": metric_coherence,
            "avg_metric": avg_metric,
            "worst_metric": worst_metric,
            "effective_score": effective_score,
            "actions": action_list,
            "metrics": metric_map,
            "options": list(opts),
            "allowed_options": list(allowed),
            "guardrails": list(guardrail_reasons),
            "conflicting_actions": conflicting_actions,
            "healthy_metric_conflict_tolerance": healthy_metric_conflict_tolerance,
            "recovery_safe_override": recovery_safe_override,
            "cooldown_remaining_before": cooldown_remaining,
            "recovery_unlock_remaining_before": recovery_unlock_remaining,
            "trend": trend,
        }
        policy["history"].append(audit)
        policy["history"] = policy["history"][-25:]
        if policy.get("cooldown_remaining", 0) > 0:
            policy["cooldown_remaining"] = max(0, int(policy["cooldown_remaining"]) - 1)

        updated_coherence = self._update_runtime_from_decision(
            rt,
            policy=policy,
            decision=decision,
            internal_coherence=internal_coherence,
            metric_anchor=self._metric_anchor(avg_metric, metric_coherence, worst_metric),
            metric_incident=metric_incident,
            worst_metric=worst_metric,
            trend=trend,
            cooldown_remaining=cooldown_remaining,
            recovery_unlock_remaining=recovery_unlock_remaining,
            healthy_for_unlock=recovery_unlock_ready_now,
            action_list=action_list,
            effective_score=effective_score,
        )
        healthy_for_unlock = self._qualifies_healthy_observation(
            coherence_value=updated_coherence,
            avg_metric=avg_metric,
            metric_coherence=metric_coherence,
            worst_metric=worst_metric,
            metric_incident=metric_incident,
        )
        if healthy_for_unlock:
            policy["healthy_streak"] = int(policy.get("healthy_streak", 0)) + 1
            policy["healthy_observation_count"] = int(policy.get("healthy_observation_count", 0)) + 1
        else:
            policy["healthy_streak"] = 0
            if metric_incident:
                policy["healthy_observation_count"] = 0

        if policy.get("recovery_unlock_remaining", 0) > 0 and healthy_for_unlock:
            policy["recovery_unlock_remaining"] = max(0, int(policy["recovery_unlock_remaining"]) - 1)
        elif metric_incident:
            policy["recovery_unlock_remaining"] = max(
                int(policy.get("recovery_unlock_remaining", 0)),
                int(self.config.healthy_observations_to_unlock_fast_after_incident),
            )

        policy["recent_metrics"].append({
            "ts": audit["ts"],
            "metrics": metric_map,
            "effective_score": effective_score,
            "updated_coherence": updated_coherence,
            "healthy_streak": int(policy.get("healthy_streak", 0)),
        })
        policy["recent_metrics"] = policy["recent_metrics"][-10:]
        audit["updated_coherence"] = updated_coherence
        audit["healthy_streak_after"] = int(policy.get("healthy_streak", 0))
        audit["recovery_unlock_remaining_after"] = int(policy.get("recovery_unlock_remaining", 0))
        policy["last_decision"] = decision

        if session_id is not None:
            self._sessions[session_id].decisions.append(
                {
                    "ts": audit["ts"],
                    "decision": decision,
                    "coherence": updated_coherence,
                    "effective_score": effective_score,
                    "guardrails": list(guardrail_reasons),
                }
            )
        if self.config.on_measure:
            try:
                self.config.on_measure("decision", decision)
            except Exception:
                logger.exception("on_measure callback failed")
        if session_id is not None:
            self._persist_session_runtime(session_id)
        self._maybe_checkpoint()
        return decision

    def allow_request(
        self,
        request_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> bool:
        coherence = self.get_coherence(session_id=session_id)
        if coherence < self.config.coherence_threshold:
            self._handle_shevira(coherence, request_context or {})
            return False
        state = self.get_vessel_state(session_id=session_id)
        if state["or_level"] > state["capacity"] * 0.9 and coherence < 0.5:
            self._handle_shevira(coherence, request_context or {})
            return False
        return True

    def detect_anomaly(self, metric_values: Dict[str, float]) -> Dict[str, Any]:
        values = list(metric_values.values())
        if not values:
            return {
                "is_anomaly": False,
                "coherence": self.get_coherence(),
                "confidence": 0.0,
                "suggested_action": "none",
            }
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        coherence = max(0.0, min(1.0, 1.0 - min(1.0, variance)))
        is_anomaly = coherence < self.config.coherence_threshold
        if is_anomaly:
            self._stats["total_anomalies"] += 1
        return {
            "is_anomaly": is_anomaly,
            "coherence": coherence,
            "confidence": 1.0 - coherence if is_anomaly else coherence,
            "suggested_action": "tikkun" if is_anomaly else "none",
        }

    def orchestrate(
        self,
        current_state: Dict[str, Any],
        available_actions: List[str],
        session_id: Optional[str] = None,
    ) -> str:
        if not available_actions:
            return ""
        rt = self._get_runtime(session_id)
        rt.s.memory["workflow_state"] = dict(current_state)
        coherence = self.get_coherence(session_id=session_id)
        if len(available_actions) == 1:
            return available_actions[0]
        if coherence < self.config.coherence_threshold:
            return available_actions[0]
        rt.superpose("next_action", *available_actions)
        action = str(rt.measure("next_action"))
        if session_id is not None:
            self._persist_session_runtime(session_id)
        return action

    def enrich_context(self, raw_context: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        coherence = self.get_coherence(session_id=session_id)
        state = self.get_vessel_state(session_id=session_id)
        if state["shevira"]:
            intent = "heal"
        elif state["or_level"] > state["capacity"] * 0.8:
            intent = "contract"
        elif coherence > 0.8:
            intent = "expand"
        else:
            intent = "balance"
        enriched = dict(raw_context)
        enriched["spira"] = {
            "coherence": coherence,
            "vessel_or_level": state["or_level"],
            "vessel_capacity": state["capacity"],
            "vessel_screen": state["screen_strength"],
            "shevira_active": state["shevira"],
            "recommended_intent": intent,
            "is_healthy": coherence >= self.config.coherence_threshold,
        }
        return enriched

    def create_session(self, session_id: str, initial_context: Optional[Dict[str, Any]] = None) -> SpiraSession:
        with self._lock:
            if session_id in self._sessions:
                raise ValueError(f"Session {session_id} already exists")
            try:
                persisted = self._session_store.get_bridge_session(session_id)
            except Exception:
                logger.exception("Failed checking for existing persisted session", extra={"session_id": session_id})
                persisted = None
            if persisted is not None:
                raise ValueError(f"Session {session_id} already exists")
            session = SpiraSession(
                session_id=session_id,
                created_at=time.time(),
                last_activity=time.time(),
                context=initial_context or {},
            )
            runtime_cfg = RuntimeConfig(
                echo_logs=self.config.enable_trace,
                trace=self.config.enable_trace,
                continue_on_error=True,
                max_errors=50,
                auto_checkpoint_label=None,
                profile=False,
                log_batch_size=50,
                max_loop_iters=1000,
                max_logs=None,
            )
            rt = SpiraRuntime(db_path=self.config.db_path, config=runtime_cfg)
            self._disable_runtime_db_logging(rt)
            self._initialize_runtime_state(rt)
            self._session_runtimes[session_id] = rt
            self._sessions[session_id] = session
            self._persist_session_runtime(session_id)
            return session

    def close_session(self, session_id: str) -> bool:
        with self._lock:
            existed = self.session_exists(session_id)
            if not existed:
                return False
            if session_id in self._session_runtimes:
                try:
                    self._session_runtimes[session_id].close()
                except Exception:
                    logger.exception("Failed closing session runtime", extra={"session_id": session_id})
                del self._session_runtimes[session_id]
            if session_id in self._sessions:
                del self._sessions[session_id]
            try:
                self._session_store.delete_bridge_session(session_id)
            except Exception:
                logger.exception("Failed deleting persisted session", extra={"session_id": session_id})
                raise
            return True

    def list_sessions(self) -> List[Dict[str, Any]]:
        return self._session_store.list_bridge_session_summaries()

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "current_coherence": self.peek_coherence(),
            "active_sessions": self._session_store.count_bridge_sessions(),
            "loaded_sessions": len(self._sessions),
            "session_ids": self._session_store.list_bridge_session_ids(),
            "config": {
                "mode": self.config.mode.value,
                "coherence_threshold": self.config.coherence_threshold,
                "fast_track_min_coherence": self.config.fast_track_min_coherence,
                "safe_only_below_coherence": self.config.safe_only_below_coherence,
                "incident_metric_floor": self.config.incident_metric_floor,
                "trend_window": self.config.trend_window,
                "cooldown_decisions_after_incident": self.config.cooldown_decisions_after_incident,
                "healthy_observations_to_unlock_fast_after_incident": self.config.healthy_observations_to_unlock_fast_after_incident,
                "recovery_fast_unlock_internal_floor": self.config.recovery_fast_unlock_internal_floor,
                "recovery_fast_unlock_metric_floor": self.config.recovery_fast_unlock_metric_floor,
            },
        }

    def reset(self) -> None:
        with self._lock:
            if self._runtime:
                try:
                    self._runtime.close()
                except Exception:
                    logger.exception("Failed closing bridge runtime during reset")
            for sid, rt in list(self._session_runtimes.items()):
                try:
                    rt.close()
                except Exception:
                    logger.exception("Failed closing session runtime during reset", extra={"session_id": sid})
            self._runtime = None
            self._sessions.clear()
            self._session_runtimes.clear()
            self._stats = {
                "total_decisions": 0,
                "total_anomalies": 0,
                "total_circuit_breaks": 0,
                "total_tikkun_calls": 0,
                "avg_coherence": 0.0,
                "coherence_samples": 0,
            }
            self._init_runtime()

    def close(self) -> None:
        with self._lock:
            if self._runtime:
                try:
                    self._runtime.close()
                except Exception:
                    logger.exception("Failed closing bridge runtime")
            for sid, rt in list(self._session_runtimes.items()):
                try:
                    rt.close()
                except Exception:
                    logger.exception("Failed closing session runtime", extra={"session_id": sid})
            self._runtime = None
            self._sessions.clear()
            self._session_runtimes.clear()
            try:
                self._session_store.close()
            except Exception:
                logger.exception("Failed closing session store")


_default_bridge: Optional[SpiraBridge] = None


def get_bridge() -> SpiraBridge:
    global _default_bridge
    if _default_bridge is None:
        _default_bridge = SpiraBridge()
    return _default_bridge


def decide(
    context: Dict[str, Any],
    options: Optional[List[str]] = None,
    *,
    actions: Optional[List[str]] = None,
    metrics: Optional[Dict[str, float]] = None,
) -> Any:
    return get_bridge().decide(context, options, actions=actions, metrics=metrics)


def allow_request(context: Optional[Dict[str, Any]] = None) -> bool:
    return get_bridge().allow_request(context)


def detect_anomaly(metrics: Dict[str, float]) -> Dict[str, Any]:
    return get_bridge().detect_anomaly(metrics)


def enrich_context(context: Dict[str, Any]) -> Dict[str, Any]:
    return get_bridge().enrich_context(context)
