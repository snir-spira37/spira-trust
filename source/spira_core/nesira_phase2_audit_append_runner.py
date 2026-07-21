from __future__ import annotations

from typing import Any, Mapping


SELECTED_CLASS = "AUDIT_RECORD_APPEND_ONLY"

AUDIT_APPEND_EVALUATOR_VERDICT_REQUIRED = "AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE"
EXECUTION_AUTHORIZATION_VERDICT_REQUIRED = "EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE"

VERDICT_APPLIED = "AUDIT_APPEND_APPLIED"
VERDICT_NOT_AUTHORIZED = "AUDIT_APPEND_NOT_AUTHORIZED"
VERDICT_NOT_EVALUATED = "AUDIT_APPEND_NOT_EVALUATED"
VERDICT_STATUS_UNKNOWN = "AUDIT_APPEND_STATUS_UNKNOWN"

EFFECT_STATUS_NOT_ATTEMPTED = "NOT_ATTEMPTED"
EFFECT_STATUS_ATTEMPTED = "APPEND_ATTEMPTED"
EFFECT_STATUS_APPLIED = "APPEND_APPLIED"
EFFECT_STATUS_UNKNOWN = "APPEND_STATUS_UNKNOWN"

ASSUMPTION_FLOOR = (
    "EA-HUMAN-01",
    "EA-TCB-01",
    "EA-TCB-03",
    "EA-CLOCK-01",
    "EA-META-01",
    "EA-META-02",
)

APPLIED_ASSUMPTIONS = (
    "CAP-PROVIDER-01",
    "CAP-PROVIDER-02",
    "CAP-PROVIDER-03",
    "CAP-SINK-01",
    "CAP-SINK-02",
    "CAP-IDEMPOTENCY-01",
    "CAP-IDEMPOTENCY-02",
    "CAP-STATUS-01",
    "CAP-TCB-01",
)

FORBIDDEN_CAPABILITY_KEYS = {
    "absolute",
    "absolute_path",
    "command",
    "delete",
    "endpoint",
    "exists",
    "glob",
    "is_file",
    "iterdir",
    "list",
    "network_endpoint",
    "network_target",
    "open",
    "path",
    "read",
    "read_bytes",
    "read_text",
    "resolve",
    "samefile",
    "shell",
    "stat",
    "write",
}

FORBIDDEN_ARTIFACT_KEYS = {
    "automatic_remediation",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "cwd",
    "network_targets",
    "powershell",
    "python -m",
    "runbook",
    "safe_to_execute",
    "script",
    "severance_authorized",
    "shell",
    "sink_path",
    "subprocess_args",
    "write_paths",
}


def run_audit_append(
    expected_context: Mapping[str, Any],
    audit_append_artifact: Mapping[str, Any] | None,
    execution_authorization_artifact: Mapping[str, Any] | None,
    append_capability: Mapping[str, Any] | None,
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    not_evaluated_reasons: list[str] = []
    evidence_refs: list[str] = []
    roots: list[str] = []
    assumptions = set(ASSUMPTION_FLOOR)

    context = expected_context if isinstance(expected_context, Mapping) else {}
    if not isinstance(expected_context, Mapping) or not _expected_context_complete(context):
        not_evaluated_reasons.append("EXPECTED_CONTEXT_MALFORMED_OR_INCOMPLETE")

    _evaluate_context(context, blocking_reasons, not_evaluated_reasons, roots)
    _evaluate_audit_append_artifact(
        audit_append_artifact,
        blocking_reasons,
        not_evaluated_reasons,
        evidence_refs,
    )
    _evaluate_execution_authorization_artifact(
        execution_authorization_artifact,
        blocking_reasons,
        not_evaluated_reasons,
        evidence_refs,
    )
    append_fn = _evaluate_append_capability(
        append_capability,
        context,
        blocking_reasons,
        not_evaluated_reasons,
        evidence_refs,
    )

    if blocking_reasons:
        return _artifact(
            context,
            VERDICT_NOT_AUTHORIZED,
            EFFECT_STATUS_NOT_ATTEMPTED,
            0,
            0,
            assumptions,
            roots,
            blocking_reasons,
            not_evaluated_reasons,
            evidence_refs,
        )
    if not_evaluated_reasons or append_fn is None:
        return _artifact(
            context,
            VERDICT_NOT_EVALUATED,
            EFFECT_STATUS_NOT_ATTEMPTED,
            0,
            0,
            assumptions,
            roots,
            blocking_reasons,
            not_evaluated_reasons,
            evidence_refs,
        )

    try:
        response = append_fn(context.get("audit_record_payload"), _string(context.get("idempotency_key")))
    except Exception:
        return _artifact(
            context,
            VERDICT_STATUS_UNKNOWN,
            EFFECT_STATUS_UNKNOWN,
            1,
            0,
            assumptions,
            roots,
            blocking_reasons,
            ["APPEND_CAPABILITY_STATUS_UNKNOWN"],
            evidence_refs,
        )

    status = _append_response_status(response)
    if status == EFFECT_STATUS_APPLIED:
        assumptions.update(APPLIED_ASSUMPTIONS)
        return _artifact(
            context,
            VERDICT_APPLIED,
            EFFECT_STATUS_APPLIED,
            1,
            1,
            assumptions,
            roots,
            blocking_reasons,
            not_evaluated_reasons,
            evidence_refs,
        )

    return _artifact(
        context,
        VERDICT_STATUS_UNKNOWN,
        status,
        1,
        0,
        assumptions,
        roots,
        blocking_reasons,
        ["APPEND_CAPABILITY_STATUS_UNKNOWN"],
        evidence_refs,
    )


def _evaluate_context(
    context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    roots: list[str],
) -> None:
    if _string(context.get("action_class")) != SELECTED_CLASS:
        blocking_reasons.append("RUNNER_ACTION_CLASS_NOT_AUTHORIZED")

    payload = context.get("audit_record_payload")
    if not isinstance(payload, Mapping):
        not_evaluated_reasons.append("AUDIT_RECORD_PAYLOAD_MISSING")
    elif _contains_key(payload, FORBIDDEN_ARTIFACT_KEYS):
        blocking_reasons.append("AUDIT_RECORD_PAYLOAD_ACTION_LOOKING")

    if not _string(context.get("idempotency_key")):
        not_evaluated_reasons.append("IDEMPOTENCY_KEY_MISSING")

    root = _string(context.get("audit_sink_root_ref"))
    if not root:
        not_evaluated_reasons.append("AUDIT_SINK_ROOT_REF_MISSING")
    else:
        roots.append(root)

    if _contains_key(context, FORBIDDEN_ARTIFACT_KEYS):
        blocking_reasons.append("RUNNER_CONTEXT_ACTION_LOOKING")


def _evaluate_audit_append_artifact(
    artifact: Mapping[str, Any] | None,
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> None:
    if artifact is None:
        not_evaluated_reasons.append("AUDIT_APPEND_ARTIFACT_MISSING")
        return
    if not isinstance(artifact, Mapping):
        not_evaluated_reasons.append("AUDIT_APPEND_ARTIFACT_MALFORMED")
        return
    evidence_refs.append("audit_append_artifact")
    if _contains_key(artifact, FORBIDDEN_ARTIFACT_KEYS):
        blocking_reasons.append("AUDIT_APPEND_ARTIFACT_ACTION_LOOKING")
    if _string(artifact.get("verdict")) != AUDIT_APPEND_EVALUATOR_VERDICT_REQUIRED:
        blocking_reasons.append("AUDIT_APPEND_EVALUATOR_NOT_SATISFIED")
    if artifact.get("action_not_performed") is not True:
        blocking_reasons.append("AUDIT_APPEND_ARTIFACT_CLAIMS_EFFECT")


def _evaluate_execution_authorization_artifact(
    artifact: Mapping[str, Any] | None,
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> None:
    if artifact is None:
        not_evaluated_reasons.append("EXECUTION_AUTHORIZATION_ARTIFACT_MISSING")
        return
    if not isinstance(artifact, Mapping):
        not_evaluated_reasons.append("EXECUTION_AUTHORIZATION_ARTIFACT_MALFORMED")
        return
    evidence_refs.append("execution_authorization_artifact")
    if _contains_key(artifact, FORBIDDEN_ARTIFACT_KEYS):
        blocking_reasons.append("EXECUTION_AUTHORIZATION_ARTIFACT_ACTION_LOOKING")
    if _string(artifact.get("verdict")) != EXECUTION_AUTHORIZATION_VERDICT_REQUIRED:
        blocking_reasons.append("EXECUTION_AUTHORIZATION_NOT_SATISFIED")
    if artifact.get("action_not_performed") is not True:
        blocking_reasons.append("EXECUTION_AUTHORIZATION_ARTIFACT_CLAIMS_EFFECT")
    if "EA-TCB-03" not in _string_list(artifact.get("assumptions")):
        blocking_reasons.append("EXECUTION_AUTHORIZATION_MISSING_EA_TCB_03")


def _evaluate_append_capability(
    capability: Mapping[str, Any] | None,
    context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> Any:
    if capability is None:
        not_evaluated_reasons.append("APPEND_CAPABILITY_MISSING")
        return None
    if not isinstance(capability, Mapping):
        not_evaluated_reasons.append("APPEND_CAPABILITY_MALFORMED")
        return None
    evidence_refs.append("append_capability")
    if _contains_key(capability, FORBIDDEN_CAPABILITY_KEYS):
        blocking_reasons.append("APPEND_CAPABILITY_EXPOSES_FORBIDDEN_OPERATION")

    append_fn = capability.get("append_one")
    if not callable(append_fn):
        not_evaluated_reasons.append("APPEND_CAPABILITY_METHOD_MISSING")
        append_fn = None

    capability_ref = _string(capability.get("append_capability_ref"))
    expected_ref = _string(context.get("append_capability_ref"))
    if not capability_ref or not expected_ref:
        not_evaluated_reasons.append("APPEND_CAPABILITY_REF_NOT_EVALUATED")
    elif capability_ref != expected_ref:
        blocking_reasons.append("APPEND_CAPABILITY_REF_MISMATCH")

    runner_digest = _string(capability.get("append_capability_root_digest"))
    expected_digest = _string(context.get("append_capability_root_digest"))
    human_digest = _string(context.get("human_go_authorized_append_capability_root_digest"))
    verifier_digest = _string(context.get("trusted_verifier_approved_append_capability_root_digest"))
    if not runner_digest or not expected_digest or not human_digest or not verifier_digest:
        not_evaluated_reasons.append("APPEND_CAPABILITY_ROOT_DIGEST_NOT_EVALUATED")
    elif runner_digest != expected_digest or runner_digest != human_digest or runner_digest != verifier_digest:
        blocking_reasons.append("APPEND_CAPABILITY_ROOT_DIGEST_MISMATCH")

    return append_fn


def _artifact(
    context: Mapping[str, Any],
    verdict: str,
    effect_status: str,
    attempted: int,
    applied: int,
    assumptions: set[str],
    roots: list[str],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> dict[str, Any]:
    return {
        "schema_id": "SPIRA_NESIRA_PHASE2_AUDIT_APPEND_RUNNER_RESULT",
        "schema_version": "1.0",
        "action_class": SELECTED_CLASS,
        "action_id": _string(context.get("action_id")),
        "verdict": verdict,
        "effect_status": effect_status,
        "effect_count_attempted": attempted,
        "effect_count_applied": applied,
        "total_effect_count": attempted,
        "idempotency_key": _string(context.get("idempotency_key")),
        "audit_sink_root_ref": _string(context.get("audit_sink_root_ref")),
        "append_capability_ref": _string(context.get("append_capability_ref")),
        "assumptions": sorted(assumptions),
        "conditional_on_roots": sorted(dict.fromkeys(roots)),
        "precondition_breakdown": {
            "audit_append_artifact": "PRESENT" if attempted or not blocking_reasons else "CHECKED",
            "execution_authorization_artifact": "CHECKED",
            "append_capability": "CALLED_ONCE" if attempted else "NOT_CALLED",
            "capability_digest_binding": "CHECKED",
        },
        "blocking_reasons": sorted(dict.fromkeys(blocking_reasons)),
        "not_evaluated_reasons": sorted(dict.fromkeys(not_evaluated_reasons)),
        "evidence_refs": sorted(dict.fromkeys(evidence_refs)),
    }


def _append_response_status(response: Any) -> str:
    if not isinstance(response, Mapping):
        return EFFECT_STATUS_UNKNOWN
    status = _string(response.get("effect_status")) or _string(response.get("append_status"))
    if status == EFFECT_STATUS_APPLIED:
        return EFFECT_STATUS_APPLIED
    if status == EFFECT_STATUS_ATTEMPTED:
        return EFFECT_STATUS_UNKNOWN
    return EFFECT_STATUS_UNKNOWN


def _expected_context_complete(context: Mapping[str, Any]) -> bool:
    required = (
        "action_id",
        "action_class",
        "audit_record_payload",
        "idempotency_key",
        "audit_sink_root_ref",
        "append_capability_ref",
        "append_capability_root_digest",
        "human_go_authorized_append_capability_root_digest",
        "trusted_verifier_approved_append_capability_root_digest",
    )
    return all(context.get(key) for key in required)


def _contains_key(value: Any, forbidden: set[str]) -> bool:
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, item in current.items():
                if str(key).lower() in forbidden:
                    return True
                if key != "append_one":
                    stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
