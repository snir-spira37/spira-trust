from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4


SPIRA_CORE_NOT_CLAIMED = (
    "runs a local non-production unified core",
    "does not claim production readiness",
    "does not call live IBM Quantum or external hardware",
    "does not claim all 33 Stone 2 systems execute as runtime processors",
    "does not claim all 21 stones are runtime processors",
    "does not claim direct stone-to-stone code connections",
    "does not widen the active runtime hot path beyond 002->021->015->001",
    "does not close E",
)

RUNTIME_HOT_PATH = ("002", "021", "015", "001")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def new_trace_id() -> str:
    return f"spira-core-{uuid4()}"
