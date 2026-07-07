from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contract import (
    COHERENCE_WARN_THRESHOLD,
    DECISION_BLOCK,
    GuardrailResponse,
    LOAD_WARN_THRESHOLD,
    REASON_BLOCK_HIGH_RISK,
    REASON_BLOCK_INTERNAL_ERROR,
    REASON_BLOCK_MALFORMED_INPUT,
    REASON_BLOCK_UNSUPPORTED_MODE,
    REQUIRED_METRICS,
    RISK_BLOCK_THRESHOLD,
    SOURCE_CONTRACT_GUARD,
    SOURCE_EXCEPTION_GUARD,
    SOURCE_STONE_015,
    SUPPORTED_MODES,
)
from .core import core_decide


ZERO_HASH = "0" * 64


class Decision015LedgerError(RuntimeError):
    pass


def _default_output_dir() -> Path:
    return Path.cwd() / ".spira_core" / "decision015"


def _paths(output_dir: str | Path | None) -> tuple[Path, Path]:
    root = Path(output_dir) if output_dir is not None else _default_output_dir()
    root.mkdir(parents=True, exist_ok=True)
    return root / "logs.jsonl", root / "decision_ledger.jsonl"


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _last_entry_hash(path: Path) -> str:
    if not path.is_file():
        return ZERO_HASH
    last_line = ""
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                last_line = line
    if not last_line:
        return ZERO_HASH
    try:
        entry = json.loads(last_line)
    except json.JSONDecodeError as exc:
        raise Decision015LedgerError("ledger_tail_unreadable") from exc
    entry_hash = entry.get("entry_hash")
    if not isinstance(entry_hash, str) or len(entry_hash) != 64:
        raise Decision015LedgerError("ledger_tail_hash_missing")
    return entry_hash


def _append_ledger_entry(path: Path, request: Any, response: dict) -> dict:
    prev_hash = _last_entry_hash(path)
    sequence = 1
    if path.is_file():
        with path.open("r", encoding="utf-8") as handle:
            sequence = sum(1 for line in handle if line.strip()) + 1
    entry = {
        "sequence": sequence,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "request_sha256": _sha_bytes(_canonical_bytes(request)),
        "response_sha256": _sha_bytes(_canonical_bytes(response)),
        "decision": response.get("decision"),
        "reason_code": response.get("reason_code"),
        "decision_source": response.get("decision_source"),
        "runtime_ms": response.get("runtime_ms"),
        "prev_entry_hash": prev_hash,
    }
    entry["entry_hash"] = _sha_bytes(_canonical_bytes(entry))
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
    return entry


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _base_response(
    *,
    decision: str,
    reason_code: str,
    decision_source: str,
    started: float,
    coherence_state: float | None = None,
    raw_015_result: dict | None = None,
) -> GuardrailResponse:
    return GuardrailResponse(
        decision=decision,
        coherence_state=coherence_state,
        reason_code=reason_code,
        decision_source=decision_source,
        raw_015_result=raw_015_result,
        runtime_ms=round((time.perf_counter() - started) * 1000, 3),
    )


def _validate_request(request: Any) -> str | None:
    if not isinstance(request, dict):
        return REASON_BLOCK_MALFORMED_INPUT
    if not isinstance(request.get("requested_action"), str) or not request["requested_action"].strip():
        return REASON_BLOCK_MALFORMED_INPUT
    metrics = request.get("current_metrics")
    if not isinstance(metrics, dict) or not metrics:
        return REASON_BLOCK_MALFORMED_INPUT
    for key in REQUIRED_METRICS:
        if key not in metrics or not _is_number(metrics[key]):
            return REASON_BLOCK_MALFORMED_INPUT
    options = request.get("options")
    if not isinstance(options, dict):
        return REASON_BLOCK_MALFORMED_INPUT
    if not isinstance(options.get("force_override"), bool):
        return REASON_BLOCK_MALFORMED_INPUT
    mode = options.get("mode")
    if not isinstance(mode, str):
        return REASON_BLOCK_MALFORMED_INPUT
    if mode not in SUPPORTED_MODES:
        return REASON_BLOCK_UNSUPPORTED_MODE
    return None


def _append_log(path: Path, request: Any, response: GuardrailResponse) -> None:
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "request": request,
        "response": response.to_dict(),
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")


def decide_request(request: Any, *, output_dir: str | Path | None = None) -> dict:
    log_path, ledger_path = _paths(output_dir)
    started = time.perf_counter()
    try:
        validation_error = _validate_request(request)
        if validation_error == REASON_BLOCK_MALFORMED_INPUT:
            response = _base_response(
                decision=DECISION_BLOCK,
                reason_code=REASON_BLOCK_MALFORMED_INPUT,
                decision_source=SOURCE_CONTRACT_GUARD,
                started=started,
            )
        elif validation_error == REASON_BLOCK_UNSUPPORTED_MODE:
            response = _base_response(
                decision=DECISION_BLOCK,
                reason_code=REASON_BLOCK_UNSUPPORTED_MODE,
                decision_source=SOURCE_CONTRACT_GUARD,
                started=started,
            )
        elif float(request["current_metrics"]["risk"]) >= RISK_BLOCK_THRESHOLD:
            response = _base_response(
                decision=DECISION_BLOCK,
                reason_code=REASON_BLOCK_HIGH_RISK,
                decision_source=SOURCE_CONTRACT_GUARD,
                started=started,
            )
        elif float(request["current_metrics"]["coherence"]) < COHERENCE_WARN_THRESHOLD:
            response = _base_response(
                decision="WARN",
                reason_code="WARN_LOW_COHERENCE",
                decision_source=SOURCE_CONTRACT_GUARD,
                started=started,
                coherence_state=float(request["current_metrics"]["coherence"]),
            )
        elif float(request["current_metrics"]["load"]) >= LOAD_WARN_THRESHOLD:
            response = _base_response(
                decision="WARN",
                reason_code="WARN_HIGH_LOAD",
                decision_source=SOURCE_CONTRACT_GUARD,
                started=started,
                coherence_state=float(request["current_metrics"]["coherence"]),
            )
        else:
            decision, reason_code, coherence_state, raw = core_decide(request)
            response = _base_response(
                decision=decision,
                reason_code=reason_code,
                decision_source=SOURCE_STONE_015,
                started=started,
                coherence_state=coherence_state,
                raw_015_result=raw,
            )
    except Exception as exc:
        response = _base_response(
            decision=DECISION_BLOCK,
            reason_code=REASON_BLOCK_INTERNAL_ERROR,
            decision_source=SOURCE_EXCEPTION_GUARD,
            started=started,
            raw_015_result={"error_type": type(exc).__name__, "error": str(exc)},
        )
    try:
        _append_ledger_entry(ledger_path, request, response.to_dict())
    except Decision015LedgerError as exc:
        response = _base_response(
            decision=DECISION_BLOCK,
            reason_code=REASON_BLOCK_INTERNAL_ERROR,
            decision_source=SOURCE_EXCEPTION_GUARD,
            started=started,
            raw_015_result={"error_type": type(exc).__name__, "error": str(exc)},
        )
    _append_log(log_path, request, response)
    return response.to_dict()


def reset_log(*, output_dir: str | Path | None = None) -> None:
    log_path, ledger_path = _paths(output_dir)
    log_path.write_text("", encoding="utf-8", newline="\n")
    ledger_path.write_text("", encoding="utf-8", newline="\n")
