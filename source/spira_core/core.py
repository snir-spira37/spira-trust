from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .adapters import Telemetry021ToDecision015Adapter
from .contracts import RUNTIME_HOT_PATH
from .decision015 import decide_request


def _decision015(
    workspace_root: Path,
    payload: Mapping[str, Any],
    *,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    # workspace_root is kept for the public internal signature; Stone 015 is now package-local.
    _ = workspace_root
    return decide_request(dict(payload), output_dir=output_dir)


def _controller_measurement(decision_response: Mapping[str, Any], decision_payload: Mapping[str, Any]) -> float:
    coherence = decision_response.get("coherence_state")
    if isinstance(coherence, (int, float)):
        return max(0.0, min(1.0, float(coherence)))
    metrics = decision_payload.get("current_metrics", {})
    fallback = metrics.get("coherence", 0.5) if isinstance(metrics, Mapping) else 0.5
    return max(0.0, min(1.0, float(fallback)))


def run_core(*, workspace_root: Path, fixture_index: int) -> dict[str, Any]:
    from .omega import run_omega_controller

    adapter = Telemetry021ToDecision015Adapter(workspace_root)
    adapted = adapter.adapt(fixture_index=fixture_index)
    decision = _decision015(
        workspace_root,
        adapted.decision_payload,
        output_dir=workspace_root / "outputs" / "spira_core_decision015_runs",
    )
    measured = _controller_measurement(decision, adapted.decision_payload)
    omega = run_omega_controller([measured])
    status = "PASS" if decision.get("decision") in {"ALLOW", "WARN", "BLOCK"} and omega.get("verdict") == "OMEGA_CONTROLLER_MECHANISM_READY" else "BLOCK"
    return {
        "phase": "CORE",
        "status": status,
        "purpose": "bounded execution through 002->021->015->001",
        "runtime_hot_path": list(RUNTIME_HOT_PATH),
        "fixture_index": fixture_index,
        "adapter": {
            "verdict": "ADAPTED_WITH_SEMANTIC_BOUNDARIES",
            "decision_payload": adapted.decision_payload,
            "basis": adapted.adapter_basis,
        },
        "decision": {
            "status": decision.get("decision"),
            "decision": decision.get("decision"),
            "reason_code": decision.get("reason_code"),
            "decision_source": decision.get("decision_source"),
            "coherence_state": decision.get("coherence_state"),
            "raw_response": decision,
        },
        "omega_control": {
            "status": omega.get("verdict"),
            "measurement_source": "decision.coherence_state fallback current_metrics.coherence",
            "measured_f": measured,
            "trace": omega.get("trace", []),
        },
    }
