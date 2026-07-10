from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Mapping

from .combined_verdict import DECISION_SEMANTICS_VERSION


CACHE_SCHEMA = "SPIRA_AGENT_VERDICT_CACHE_V1"
CACHE_SCHEMA_VERSION = "1.0"


def build_agent_verdict_cache(
    artifact_path: str | Path,
    *,
    command_fingerprint: str,
    policy_sha256: str | None = None,
    decision_semantics_version: str | None = None,
    tool_version: str | None = None,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(artifact_path)
    if not path.is_file() or path.suffix != ".whl":
        return _miss(
            artifact={"filename": path.name, "sha256": None},
            reason_code="ARTIFACT_NOT_FOUND",
            expected=_expected_context(
                command_fingerprint=command_fingerprint,
                policy_sha256=policy_sha256,
                decision_semantics_version=decision_semantics_version,
                tool_version=tool_version,
            ),
            summary_count=0,
        )

    artifact = {"filename": path.name, "sha256": sha256(path.read_bytes()).hexdigest()}
    expected = _expected_context(
        command_fingerprint=command_fingerprint,
        policy_sha256=policy_sha256,
        decision_semantics_version=decision_semantics_version,
        tool_version=tool_version,
    )
    summaries = _load_summaries(Path(state_dir) if state_dir else Path.cwd() / ".spira" / "agent_summaries")
    artifact_matches = _summaries_for_sha(summaries, str(artifact["sha256"]))
    if not artifact_matches:
        filename_matches = _summaries_for_filename(summaries, str(artifact["filename"]))
        if filename_matches:
            return _miss(
                artifact=artifact,
                reason_code="ARTIFACT_CHANGED_SINCE_CHECK",
                expected=expected,
                summary_count=len(filename_matches),
                context_match=False,
            )
        return _miss(
            artifact=artifact,
            reason_code="ARTIFACT_NOT_CHECKED",
            expected=expected,
            summary_count=0,
            context_match=False,
        )

    available_contexts = {_context_key(_summary_context(summary)) for summary in artifact_matches}
    matching = [summary for summary in artifact_matches if _summary_context(summary) == expected]
    if not matching:
        context_ambiguous = len(available_contexts) > 1
        return _miss(
            artifact=artifact,
            reason_code="CONTEXT_AMBIGUOUS" if context_ambiguous else "CONTEXT_MISMATCH",
            expected=expected,
            summary_count=len(artifact_matches),
            context_match=False,
            context_ambiguous=context_ambiguous,
            available_context_count=len(available_contexts),
        )

    result_keys = {_action_result_key(summary) for summary in matching}
    if len(result_keys) > 1:
        return _miss(
            artifact=artifact,
            reason_code="EXACT_CONTEXT_RESULT_CONFLICT",
            expected=expected,
            summary_count=len(matching),
            context_match=True,
            result_conflict=True,
            available_result_count=len(result_keys),
        )

    selected = _latest_summary(matching)
    contract = selected.get("agent_action_contract") if isinstance(selected.get("agent_action_contract"), Mapping) else selected
    approval = selected.get("approval") if isinstance(selected.get("approval"), Mapping) else {}
    return {
        "schema": CACHE_SCHEMA,
        "schema_version": CACHE_SCHEMA_VERSION,
        "created_at": _utc(),
        "cache_hit": True,
        "match_scope": "full_evidence_context",
        "context_match": True,
        "context_ambiguous": False,
        "result_conflict": False,
        "filename": artifact["filename"],
        "artifact_sha256": artifact["sha256"],
        "policy_sha256": expected["policy_sha256"],
        "command_fingerprint": expected["command_fingerprint"],
        "decision_semantics_version": expected["decision_semantics_version"],
        "tool_version": expected["tool_version"],
        "stop": contract.get("stop"),
        "recommended_agent_action": contract.get("recommended_agent_action"),
        "reason_codes": list(contract.get("reason_codes") or selected.get("reason_codes") or []),
        "summary_path": selected.get("_loaded_from"),
        "summary_count": len(matching),
        "evidence": contract.get("evidence"),
        "approved": bool(approval.get("approved", False)),
        "approval_source": approval.get("approval_source", "unverified"),
        "scope": "cache_exact_context",
    }


def format_agent_verdict_cache(result: Mapping[str, Any]) -> str:
    lines = [
        "SPIRA Agent Verdict Cache",
        "=========================",
        f"Cache hit: {result.get('cache_hit')}",
        f"Context match: {result.get('context_match')}",
        f"Artifact: {result.get('filename')}",
        f"Stop: {result.get('stop')}",
        f"Action: {result.get('recommended_agent_action')}",
    ]
    if result.get("reason_codes"):
        lines.append(f"Reason codes: {', '.join(result.get('reason_codes') or [])}")
    if result.get("summary_path"):
        lines.append(f"Summary: {result.get('summary_path')}")
    return "\n".join(lines) + "\n"


def _miss(
    *,
    artifact: Mapping[str, Any],
    reason_code: str,
    expected: Mapping[str, Any],
    summary_count: int,
    context_match: bool | None = None,
    context_ambiguous: bool = False,
    result_conflict: bool = False,
    available_context_count: int | None = None,
    available_result_count: int | None = None,
) -> dict[str, Any]:
    result = {
        "schema": CACHE_SCHEMA,
        "schema_version": CACHE_SCHEMA_VERSION,
        "created_at": _utc(),
        "cache_hit": False,
        "match_scope": "full_evidence_context",
        "context_match": context_match,
        "context_ambiguous": context_ambiguous,
        "result_conflict": result_conflict,
        "filename": artifact.get("filename"),
        "artifact_sha256": artifact.get("sha256"),
        "policy_sha256": expected["policy_sha256"],
        "command_fingerprint": expected["command_fingerprint"],
        "decision_semantics_version": expected["decision_semantics_version"],
        "tool_version": expected["tool_version"],
        "stop": True,
        "recommended_agent_action": "RERUN_REQUIRED",
        "reason_codes": [reason_code],
        "summary_path": None,
        "summary_count": summary_count,
        "evidence": None,
        "approved": False,
        "approval_source": "unverified",
        "scope": "cache_exact_context",
    }
    if available_context_count is not None:
        result["available_context_count"] = available_context_count
    if available_result_count is not None:
        result["available_result_count"] = available_result_count
    return result


def _expected_context(
    *,
    command_fingerprint: str,
    policy_sha256: str | None,
    decision_semantics_version: str | None,
    tool_version: str | None,
) -> dict[str, Any]:
    return {
        "command_fingerprint": command_fingerprint,
        "policy_sha256": policy_sha256,
        "decision_semantics_version": decision_semantics_version or DECISION_SEMANTICS_VERSION,
        "tool_version": tool_version or _tool_version(),
    }


def _summary_context(summary: Mapping[str, Any]) -> dict[str, Any]:
    contract = summary.get("agent_action_contract") if isinstance(summary.get("agent_action_contract"), Mapping) else {}
    summary_of = summary.get("summary_of") if isinstance(summary.get("summary_of"), Mapping) else {}
    return {
        "command_fingerprint": str(contract.get("command_fingerprint") or summary_of.get("command_fingerprint") or ""),
        "policy_sha256": contract.get("policy_sha256") or summary_of.get("policy_sha256"),
        "decision_semantics_version": str(contract.get("decision_semantics_version") or summary.get("decision_semantics_version") or summary_of.get("decision_semantics_version") or ""),
        "tool_version": str(summary_of.get("tool_version") or ""),
    }


def _context_key(context: Mapping[str, Any]) -> str:
    return json.dumps(context, sort_keys=True, separators=(",", ":"))


def _action_result_key(summary: Mapping[str, Any]) -> str:
    contract = summary.get("agent_action_contract") if isinstance(summary.get("agent_action_contract"), Mapping) else summary
    payload = {
        "graph_verdict": contract.get("graph_verdict") or summary.get("verdict"),
        "combined_verdict": contract.get("combined_verdict") or summary.get("combined_verdict"),
        "action_verdict": contract.get("action_verdict") or summary.get("action_verdict"),
        "stop": contract.get("stop") if "stop" in contract else summary.get("stop"),
        "stop_source": contract.get("stop_source") or summary.get("stop_source"),
        "recommended_agent_action": contract.get("recommended_agent_action") or summary.get("recommended_agent_action"),
        "reason_codes": list(contract.get("reason_codes") or summary.get("reason_codes") or []),
        "not_evaluated": list(contract.get("not_evaluated") or summary.get("not_evaluated") or []),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _summaries_for_sha(summaries: list[dict[str, Any]], sha_value: str) -> list[dict[str, Any]]:
    return [
        summary
        for summary in summaries
        for artifact in summary.get("artifacts", []) or []
        if str(artifact.get("sha256")) == sha_value
    ]


def _summaries_for_filename(summaries: list[dict[str, Any]], filename: str) -> list[dict[str, Any]]:
    return [
        summary
        for summary in summaries
        for artifact in summary.get("artifacts", []) or []
        if str(artifact.get("filename")) == filename
    ]


def _latest_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(summaries, key=lambda item: (str(item.get("created_at") or ""), str(item.get("_loaded_from") or "")))[-1]


def _load_summaries(state_dir: Path) -> list[dict[str, Any]]:
    if not state_dir.is_dir():
        return []
    summaries = []
    for path in sorted(state_dir.glob("*.agent_summary.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("schema") != "SPIRA_AGENT_SUMMARY_V1":
            continue
        data["_loaded_from"] = str(path.resolve())
        summaries.append(data)
    return summaries


def _tool_version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        return "source-tree"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
