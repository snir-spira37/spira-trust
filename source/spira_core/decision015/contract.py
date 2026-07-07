from __future__ import annotations

from dataclasses import dataclass
from typing import Final


DECISION_ALLOW: Final = "ALLOW"
DECISION_WARN: Final = "WARN"
DECISION_BLOCK: Final = "BLOCK"

REASON_ALLOW_OK: Final = "ALLOW_OK"
REASON_WARN_LOW_COHERENCE: Final = "WARN_LOW_COHERENCE"
REASON_WARN_HIGH_LOAD: Final = "WARN_HIGH_LOAD"
REASON_BLOCK_HIGH_RISK: Final = "BLOCK_HIGH_RISK"
REASON_BLOCK_MALFORMED_INPUT: Final = "BLOCK_MALFORMED_INPUT"
REASON_BLOCK_UNSUPPORTED_MODE: Final = "BLOCK_UNSUPPORTED_MODE"
REASON_BLOCK_INTERNAL_ERROR: Final = "BLOCK_INTERNAL_ERROR"

SOURCE_CONTRACT_GUARD: Final = "mvp_contract_guard"
SOURCE_STONE_015: Final = "stone_015"
SOURCE_EXCEPTION_GUARD: Final = "exception_guard"

SUPPORTED_MODES: Final = ("safe", "normal", "fast")
REQUIRED_METRICS: Final = ("coherence", "load", "risk")

RISK_BLOCK_THRESHOLD: Final = 0.8
LOAD_WARN_THRESHOLD: Final = 0.75
COHERENCE_WARN_THRESHOLD: Final = 0.5

DEFAULT_015_OPTIONS: Final = ("safe", "fast", "accurate")


@dataclass(frozen=True)
class GuardrailResponse:
    decision: str
    coherence_state: float | None
    reason_code: str
    decision_source: str
    raw_015_result: dict | None
    runtime_ms: float

    def to_dict(self) -> dict:
        return {
            "decision": self.decision,
            "coherence_state": self.coherence_state,
            "reason_code": self.reason_code,
            "decision_source": self.decision_source,
            "raw_015_result": self.raw_015_result,
            "runtime_ms": self.runtime_ms,
        }


def mode_to_actions(mode: str, requested_action: str) -> list[str]:
    if mode == "safe":
        return ["stabilize", requested_action]
    if mode == "fast":
        return [requested_action, "accelerate"]
    return [requested_action]
