from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


PLAN_SCHEMA = "SPIRA_AGENT_RERUN_PLAN_V1"
PLAN_SCHEMA_VERSION = "1.0"

ACTION_RERUN_REQUIRED = "RERUN_REQUIRED"
ACTION_REUSE_PRIOR = "REUSE_PRIOR_ACTION"

REQUIRED_CONTEXT_FIELDS = [
    "artifact_sha256",
    "command_fingerprint",
    "policy_sha256",
    "decision_semantics_version",
    "tool_version",
    "strict_closure",
    "lockfile_sha256",
    "baseline_sha256",
    "wheelhouse_sha256",
    "target_environment_sha256",
    "verify_embedded_sboms",
    "attestation_sha256",
    "attestation_trust_root_sha256",
]

NON_EMPTY_FIELDS = [
    "artifact_sha256",
    "command_fingerprint",
    "decision_semantics_version",
    "tool_version",
]

FIELD_RULES = {
    "artifact_sha256": ("ARTIFACT_CHANGED", ["verification", "combined_decision", "agent_summary", "cache"]),
    "command_fingerprint": ("COMMAND_CONTEXT_CHANGED", ["verification", "combined_decision", "agent_summary", "cache"]),
    "policy_sha256": ("POLICY_CHANGED", ["policy_checks", "combined_decision", "agent_summary", "cache"]),
    "decision_semantics_version": ("DECISION_SEMANTICS_CHANGED", ["agent_action_contract", "cache"]),
    "tool_version": ("TOOL_VERSION_CHANGED", ["verification", "agent_action_contract", "cache"]),
    "strict_closure": ("STRICT_CLOSURE_CHANGED", ["graph_closure", "combined_decision", "cache"]),
    "lockfile_sha256": ("LOCKFILE_CHANGED", ["lockfile_cross_check", "combined_decision", "cache"]),
    "baseline_sha256": ("BASELINE_CHANGED", ["baseline_drift", "combined_decision", "cache"]),
    "wheelhouse_sha256": ("WHEELHOUSE_CHANGED", ["graph_closure", "combined_decision", "cache"]),
    "target_environment_sha256": ("TARGET_ENVIRONMENT_CHANGED", ["target_environment_checks", "combined_decision", "cache"]),
    "verify_embedded_sboms": ("SBOM_VERIFICATION_MODE_CHANGED", ["pep770_sbom_consistency", "combined_decision", "cache"]),
    "attestation_sha256": ("ATTESTATION_CONTEXT_CHANGED", ["pep740_offline_attestations", "combined_decision", "cache"]),
    "attestation_trust_root_sha256": ("ATTESTATION_CONTEXT_CHANGED", ["pep740_offline_attestations", "combined_decision", "cache"]),
}


def build_rerun_plan(
    current_context: Mapping[str, Any],
    previous_context: Mapping[str, Any],
) -> dict[str, Any]:
    current = _normalize_context(current_context)
    previous = _normalize_context(previous_context)
    reason_codes: list[str] = []
    rerun: list[str] = []

    validation_reasons = _validation_reasons(current, "current") + _validation_reasons(previous, "previous")
    reason_codes.extend(validation_reasons)
    if current.get("context_ambiguous") or previous.get("context_ambiguous"):
        reason_codes.append("CONTEXT_AMBIGUOUS")
        rerun.extend(["context_resolution", "cache"])
    if current.get("result_conflict") or previous.get("result_conflict"):
        reason_codes.append("EXACT_CONTEXT_RESULT_CONFLICT")
        rerun.extend(["state_audit", "cache"])

    if not validation_reasons:
        for field, (reason, steps) in FIELD_RULES.items():
            if current.get(field) != previous.get(field):
                reason_codes.append(reason)
                rerun.extend(steps)

    reason_codes = _canonical_list(reason_codes)
    rerun = _canonical_list(rerun)
    rerun_required = bool(reason_codes)
    return {
        "schema": PLAN_SCHEMA,
        "schema_version": PLAN_SCHEMA_VERSION,
        "created_at": _utc(),
        "rerun_required": rerun_required,
        "stop": rerun_required,
        "recommended_agent_action": ACTION_RERUN_REQUIRED if rerun_required else ACTION_REUSE_PRIOR,
        "rerun": rerun,
        "reuse": [] if rerun_required else ["prior_agent_action_contract"],
        "reason_codes": reason_codes,
        "current_context": current,
        "previous_context": previous,
        "not_claimed": [
            "rerun planner does not execute verification",
            "rerun planner is not human approval",
            "rerun planner is not a safety or malware claim",
            "reuse means context-equivalent prior action may be served by cache",
        ],
    }


def context_from_agent_summary(summary: Mapping[str, Any]) -> dict[str, Any]:
    contract = summary.get("agent_action_contract") if isinstance(summary.get("agent_action_contract"), Mapping) else {}
    summary_of = summary.get("summary_of") if isinstance(summary.get("summary_of"), Mapping) else {}
    return _normalize_context(
        {
            "artifact_sha256": contract.get("artifact_sha256"),
            "command_fingerprint": contract.get("command_fingerprint") or summary_of.get("command_fingerprint"),
            "policy_sha256": contract.get("policy_sha256") or summary_of.get("policy_sha256"),
            "decision_semantics_version": contract.get("decision_semantics_version") or summary.get("decision_semantics_version"),
            "tool_version": summary_of.get("tool_version") or ((summary.get("tool") or {}).get("version") if isinstance(summary.get("tool"), Mapping) else None),
            "strict_closure": summary_of.get("strict_closure"),
            "lockfile_sha256": summary_of.get("lockfile_sha256"),
            "baseline_sha256": summary_of.get("baseline_sha256"),
            "wheelhouse_sha256": summary_of.get("artifact_set_sha256"),
            "target_environment_sha256": summary_of.get("target_environment_sha256"),
            "verify_embedded_sboms": summary_of.get("verify_embedded_sboms"),
            "attestation_sha256": summary_of.get("attestation_sha256"),
            "attestation_trust_root_sha256": summary_of.get("attestation_trust_root_sha256"),
            "context_ambiguous": False,
            "result_conflict": False,
        }
    )


def load_context(path: str | Path) -> dict[str, Any]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": "UNSUPPORTED", "unsupported_context": True}
    if not isinstance(data, dict):
        return {"schema": "UNSUPPORTED", "unsupported_context": True}
    if data.get("schema") == "SPIRA_AGENT_SUMMARY_V1":
        return context_from_agent_summary(data)
    return _normalize_context(data)


def format_rerun_plan(plan: Mapping[str, Any]) -> str:
    lines = [
        "SPIRA Agent Rerun Plan",
        "=======================",
        f"Rerun required: {plan.get('rerun_required')}",
        f"Stop: {plan.get('stop')}",
        f"Action: {plan.get('recommended_agent_action')}",
    ]
    if plan.get("reason_codes"):
        lines.append(f"Reason codes: {', '.join(plan.get('reason_codes') or [])}")
    if plan.get("rerun"):
        lines.append(f"Rerun: {', '.join(plan.get('rerun') or [])}")
    if plan.get("reuse"):
        lines.append(f"Reuse: {', '.join(plan.get('reuse') or [])}")
    return "\n".join(lines) + "\n"


def _normalize_context(context: Mapping[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_CONTEXT_FIELDS if field not in context]
    normalized = {field: context.get(field) for field in REQUIRED_CONTEXT_FIELDS}
    normalized["missing_context_fields"] = missing
    normalized["context_ambiguous"] = bool(context.get("context_ambiguous", False))
    normalized["result_conflict"] = bool(context.get("result_conflict", False))
    normalized["unsupported_context"] = bool(context.get("unsupported_context", False))
    return normalized


def _validation_reasons(context: Mapping[str, Any], label: str) -> list[str]:
    reasons = []
    if context.get("unsupported_context"):
        reasons.append(f"{label.upper()}_UNSUPPORTED_CONTEXT")
    missing = list(context.get("missing_context_fields") or [])
    if missing:
        reasons.append(f"{label.upper()}_MISSING_CONTEXT_FIELDS")
    for field in NON_EMPTY_FIELDS:
        if context.get(field) in (None, ""):
            reasons.append(f"{label.upper()}_UNKNOWN_{field.upper()}")
    return reasons


def _canonical_list(values: list[str]) -> list[str]:
    return sorted({str(value) for value in values})


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
