from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


DRY_RUN_VERDICT_SATISFIED = "DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION"
DRY_RUN_VERDICT_BLOCKED = "DRY_RUN_BLOCKED"
DRY_RUN_VERDICT_NOT_EVALUATED = "DRY_RUN_NOT_EVALUATED"

ACTION_AUTHORITY_SUFFICIENT = "ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION"
ACTION_NOT_AUTHORIZED = "ACTION_NOT_AUTHORIZED"
ACTION_NOT_EVALUATED = "ACTION_NOT_EVALUATED"

NESIRA_VERDICT_SUFFICIENT = "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
NESIRA_VERDICT_INSUFFICIENT = "TRUST_INSUFFICIENT"
NESIRA_VERDICT_NOT_EVALUATED = "TRUST_NOT_EVALUATED"

ACTION_NOT_PERFORMED = "ACTION_NOT_PERFORMED"
DRY_RUN_ONLY_NOT_EXECUTION = "DRY_RUN_ONLY_NOT_EXECUTION"
SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED = "SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED"
NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION = "NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION"
ACTION_AUTHORITY_NOT_EXECUTION = "ACTION_AUTHORITY_NOT_EXECUTION"

MANDATORY_MARKERS = (
    ACTION_NOT_PERFORMED,
    DRY_RUN_ONLY_NOT_EXECUTION,
    SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED,
    NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION,
    ACTION_AUTHORITY_NOT_EXECUTION,
)

FORBIDDEN_EXECUTABLE_KEYS = {
    "apply",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "cwd",
    "environment_variables",
    "execute",
    "network_targets",
    "powershell",
    "python -m",
    "remediate",
    "runbook",
    "script",
    "sever",
    "shell",
    "subprocess_args",
    "write_paths",
}


def evaluate_dry_run(
    expected_context: Mapping[str, Any],
    combined_verdict: Mapping[str, Any],
    nesira_assessment: Mapping[str, Any] | None,
    action_authority_result: Mapping[str, Any] | None,
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    not_evaluated_reasons: list[str] = []
    evidence_refs: list[str] = []
    assumptions = set()
    context = expected_context if isinstance(expected_context, Mapping) else {}

    if not isinstance(expected_context, Mapping) or not _expected_context_complete(context):
        blocking_reasons.append("EXPECTED_CONTEXT_MALFORMED_OR_INCOMPLETE")

    if not isinstance(combined_verdict, Mapping):
        not_evaluated_reasons.append("COMBINED_VERDICT_MALFORMED")
    else:
        _evaluate_combined(combined_verdict, blocking_reasons, not_evaluated_reasons, evidence_refs)

    _evaluate_nesira(nesira_assessment, blocking_reasons, not_evaluated_reasons, assumptions, evidence_refs)
    _evaluate_action_authority(
        action_authority_result,
        context,
        blocking_reasons,
        not_evaluated_reasons,
        assumptions,
        evidence_refs,
    )

    if blocking_reasons:
        verdict = DRY_RUN_VERDICT_BLOCKED
    elif not_evaluated_reasons:
        verdict = DRY_RUN_VERDICT_NOT_EVALUATED
    else:
        verdict = DRY_RUN_VERDICT_SATISFIED

    return _artifact(
        verdict=verdict,
        expected_context=context,
        blocking_reasons=blocking_reasons,
        not_evaluated_reasons=not_evaluated_reasons,
        assumptions=assumptions,
        evidence_refs=evidence_refs,
        rollback_or_abort_ref_present=_rollback_present(action_authority_result),
    )


def _evaluate_combined(
    combined_verdict: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> None:
    winning_status = str(combined_verdict.get("winning_status") or "")
    verdict = str(combined_verdict.get("combined_verdict") or "")
    evidence_refs.append("combined_verdict")
    if winning_status == "BLOCK" or verdict == "GRAPH_BLOCK":
        blocking_reasons.append("COMBINED_VERDICT_BLOCK")
    if winning_status in {"WARN", "NOTE"}:
        blocking_reasons.append("COMBINED_VERDICT_NOT_CLEAN")
    if "nesira_phase2_assessment" in _string_list(combined_verdict.get("not_evaluated_layers")):
        not_evaluated_reasons.append("NESIRA_LAYER_NOT_EVALUATED_IN_COMBINED_VERDICT")


def _evaluate_nesira(
    nesira_assessment: Mapping[str, Any] | None,
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
    evidence_refs: list[str],
) -> None:
    if nesira_assessment is None:
        not_evaluated_reasons.append("NESIRA_ASSESSMENT_MISSING")
        return
    if not isinstance(nesira_assessment, Mapping):
        not_evaluated_reasons.append("NESIRA_ASSESSMENT_MALFORMED")
        return
    evidence_refs.append("nesira_assessment")
    if _contains_forbidden_key(nesira_assessment):
        blocking_reasons.append("NESIRA_ASSESSMENT_ACTION_LOOKING")
        return
    verdict = nesira_assessment.get("verdict")
    for item in _string_list(nesira_assessment.get("assumptions")):
        assumptions.add(item)
    if verdict == NESIRA_VERDICT_INSUFFICIENT:
        blocking_reasons.append("NESIRA_TRUST_INSUFFICIENT")
    elif verdict == NESIRA_VERDICT_NOT_EVALUATED:
        not_evaluated_reasons.append("NESIRA_TRUST_NOT_EVALUATED")
    elif verdict == NESIRA_VERDICT_SUFFICIENT:
        if _isolation_present(nesira_assessment) and "PT-ISOLATION-01" not in assumptions:
            blocking_reasons.append("NESIRA_ISOLATION_CAVEAT_MISSING")
    else:
        not_evaluated_reasons.append("NESIRA_ASSESSMENT_MALFORMED")


def _evaluate_action_authority(
    action_authority_result: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
    evidence_refs: list[str],
) -> None:
    if action_authority_result is None:
        blocking_reasons.append("ACTION_AUTHORITY_MISSING")
        return
    if not isinstance(action_authority_result, Mapping):
        not_evaluated_reasons.append("ACTION_AUTHORITY_MALFORMED")
        return
    evidence_refs.append("action_authority")
    if _contains_forbidden_key(action_authority_result):
        blocking_reasons.append("ACTION_AUTHORITY_ACTION_LOOKING")
        return
    verdict = action_authority_result.get("verdict")
    for item in _string_list(action_authority_result.get("assumptions")):
        assumptions.add(item)
    if verdict == ACTION_NOT_AUTHORIZED:
        blocking_reasons.append("ACTION_NOT_AUTHORIZED")
        return
    if verdict == ACTION_NOT_EVALUATED:
        not_evaluated_reasons.append("ACTION_AUTHORITY_NOT_EVALUATED")
        return
    if verdict != ACTION_AUTHORITY_SUFFICIENT:
        not_evaluated_reasons.append("ACTION_AUTHORITY_MALFORMED")
        return
    if not _authority_matches_context(action_authority_result, expected_context):
        blocking_reasons.append("ACTION_AUTHORITY_CONTEXT_MISMATCH")
    if not _rollback_present(action_authority_result):
        blocking_reasons.append("ACTION_AUTHORITY_ROLLBACK_OR_ABORT_MISSING")


def _artifact(
    *,
    verdict: str,
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
    evidence_refs: list[str],
    rollback_or_abort_ref_present: bool,
) -> dict[str, Any]:
    return {
        "schema_id": "SPIRA_NESIRA_PHASE2_DRY_RUN_ARTIFACT",
        "schema_version": "1.0",
        "dry_run_id": _context_digest(expected_context),
        "dry_run_verdict": verdict,
        "action_not_performed": True,
        "execution_authorization_required": True,
        "markers": list(MANDATORY_MARKERS),
        "expected_context_digest": _context_digest(expected_context),
        "precondition_summary": _summary(verdict),
        "blocking_reasons": sorted(dict.fromkeys(blocking_reasons)),
        "not_evaluated_reasons": sorted(dict.fromkeys(not_evaluated_reasons)),
        "assumptions_carried": sorted(assumptions),
        "rollback_or_abort_ref_present": rollback_or_abort_ref_present,
        "evidence_refs": sorted(dict.fromkeys(evidence_refs)),
    }


def _summary(verdict: str) -> str:
    if verdict == DRY_RUN_VERDICT_SATISFIED:
        return "preconditions satisfied for later human review; action not performed"
    if verdict == DRY_RUN_VERDICT_BLOCKED:
        return "dry-run blocked; action not performed"
    return "dry-run not evaluated because evidence was unavailable; action not performed"


def _expected_context_complete(expected_context: Mapping[str, Any]) -> bool:
    required = (
        "action_class",
        "subject_context",
        "environment_context",
        "action_authority_root_id",
    )
    return all(expected_context.get(key) not in (None, "") for key in required)


def _authority_matches_context(action_authority_result: Mapping[str, Any], expected_context: Mapping[str, Any]) -> bool:
    return (
        action_authority_result.get("authorized_action_class") == expected_context.get("action_class")
        and action_authority_result.get("authorized_subject_context") == expected_context.get("subject_context")
        and action_authority_result.get("authorized_environment_context") == expected_context.get("environment_context")
        and action_authority_result.get("action_authority_root_id") == expected_context.get("action_authority_root_id")
    )


def _rollback_present(action_authority_result: Mapping[str, Any] | None) -> bool:
    return isinstance(action_authority_result, Mapping) and bool(action_authority_result.get("rollback_or_abort_ref"))


def _isolation_present(nesira_assessment: Mapping[str, Any]) -> bool:
    sub_assessments = nesira_assessment.get("sub_assessments")
    if isinstance(sub_assessments, Mapping) and "isolation" in sub_assessments:
        return True
    breakdown = nesira_assessment.get("per_domain_breakdown")
    return isinstance(breakdown, Mapping) and "isolation" in breakdown


def _contains_forbidden_key(value: Any) -> bool:
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, item in current.items():
                if str(key).lower() in FORBIDDEN_EXECUTABLE_KEYS:
                    return True
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _context_digest(expected_context: Mapping[str, Any]) -> str:
    payload = {
        "action_authority_root_id": str(expected_context.get("action_authority_root_id") or ""),
        "action_class": str(expected_context.get("action_class") or ""),
        "environment_context": str(expected_context.get("environment_context") or ""),
        "subject_context": str(expected_context.get("subject_context") or ""),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()
