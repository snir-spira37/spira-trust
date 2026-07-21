from __future__ import annotations

from typing import Any, Mapping


SELECTED_CLASS = "AUDIT_RECORD_APPEND_ONLY"

VERDICT_SUFFICIENT = "AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE"
VERDICT_NOT_AUTHORIZED = "AUDIT_APPEND_NOT_AUTHORIZED"
VERDICT_NOT_EVALUATED = "AUDIT_APPEND_NOT_EVALUATED"

ACTION_NOT_PERFORMED = "ACTION_NOT_PERFORMED"
EFFECT_STATUS_UNKNOWN = "EFFECT_STATUS_UNKNOWN"
EFFECT_STATUS_NOT_ATTEMPTED = "NOT_ATTEMPTED"

ASSUMPTION_FLOOR = (
    "EA-HUMAN-01",
    "EA-TCB-01",
    "EA-TCB-03",
    "EA-CLOCK-01",
    "EA-META-01",
    "EA-META-02",
)

PERMANENTLY_NON_RECLASSIFIABLE = {
    "AUTOMATIC_REMEDIATOR",
    "LIVE_ISOLATION_RUNNER",
    "SECRET_EXFILTRATION_PRONE_ACTION",
    "SELF_MODIFYING_RUNNER",
    "SEVERANCE_EXECUTOR",
}

INELIGIBLE_CLASSES = PERMANENTLY_NON_RECLASSIFIABLE | {
    "ARBITRARY_COMMAND_EXECUTOR",
    "ARBITRARY_NETWORK_TARGET",
    "ARBITRARY_PATH_DELETE",
    "ARBITRARY_PATH_WRITE",
    "GENERIC_FILESYSTEM_MUTATOR",
    "GENERIC_NETWORK_CLIENT",
    "GENERIC_PYTHON_MODULE_RUNNER",
    "GENERIC_SCRIPT_RUNNER",
    "GENERIC_SHELL_COMMAND",
    "GENERIC_SUBPROCESS",
    "UNBOUNDED_CLEANUP_ACTION",
}

FORBIDDEN_KEYS = {
    "append_performed",
    "append_succeeded",
    "audit_written",
    "automatic_remediation",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "credential",
    "cwd",
    "delete_paths",
    "environment_dump",
    "environment_variables",
    "execution_approved",
    "file_handle",
    "filesystem_snapshot",
    "network_targets",
    "password",
    "powershell",
    "private_key",
    "python -m",
    "resolved_path",
    "runbook",
    "safe_to_execute",
    "script",
    "secret",
    "severance_authorized",
    "shell",
    "sink_path",
    "subprocess_args",
    "token",
    "write_paths",
}

FORBIDDEN_PATH_KEYS = {
    "absolute_path",
    "caller_path",
    "filesystem_path",
    "relative_path",
    "repository_path",
    "sink_path",
    "user_path",
}

FORBIDDEN_NETWORK_KEYS = {
    "endpoint",
    "host",
    "network_channel",
    "network_target",
    "network_targets",
    "url",
}

ZERO_BUDGET_FIELDS = (
    "temporary_files",
    "lock_files",
    "cache_writes",
    "checkpoint_writes",
    "post_effect_verification_writes",
    "network_sends",
    "cleanup_effects",
)

CONTEXT_BINDINGS = (
    ("subject_context_digest", "subject_context_digest", "SUBJECT_CONTEXT_DIGEST_MISMATCH"),
    ("environment_context_digest", "environment_context_digest", "ENVIRONMENT_CONTEXT_DIGEST_MISMATCH"),
    ("target_scope_digest", "target_scope_digest", "TARGET_SCOPE_DIGEST_MISMATCH"),
    ("combined_verdict_digest", "combined_verdict_digest", "COMBINED_VERDICT_DIGEST_MISMATCH"),
    ("action_authority_digest", "action_authority_digest", "ACTION_AUTHORITY_DIGEST_MISMATCH"),
    ("dry_run_artifact_digest", "dry_run_artifact_digest", "DRY_RUN_ARTIFACT_DIGEST_MISMATCH"),
    (
        "execution_authorization_digest",
        "execution_authorization_digest",
        "EXECUTION_AUTHORIZATION_DIGEST_MISMATCH",
    ),
    ("human_go_digest", "human_go_digest", "HUMAN_GO_DIGEST_MISMATCH"),
    ("side_effect_budget_digest", "side_effect_budget_digest", "SIDE_EFFECT_BUDGET_DIGEST_MISMATCH"),
    ("rollback_or_abort_ref_digest", "rollback_or_abort_ref_digest", "ROLLBACK_OR_ABORT_DIGEST_MISMATCH"),
)


def evaluate_audit_append_model(
    expected_context: Mapping[str, Any],
    audit_append_evidence: Mapping[str, Any] | None,
    trusted_verifier_evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    not_evaluated_reasons: list[str] = []
    evidence_refs: list[str] = []
    roots: list[str] = []
    assumptions = set(ASSUMPTION_FLOOR)
    effect_status = EFFECT_STATUS_NOT_ATTEMPTED

    context = expected_context if isinstance(expected_context, Mapping) else {}
    if not isinstance(expected_context, Mapping) or not _expected_context_complete(context):
        not_evaluated_reasons.append("EXPECTED_CONTEXT_MALFORMED_OR_INCOMPLETE")

    if audit_append_evidence is None:
        not_evaluated_reasons.append("AUDIT_APPEND_EVIDENCE_MISSING")
    elif not isinstance(audit_append_evidence, Mapping):
        not_evaluated_reasons.append("AUDIT_APPEND_EVIDENCE_MALFORMED")
    else:
        evidence_refs.append("audit_append_evidence")
        _evaluate_audit_append_evidence(
            audit_append_evidence,
            context,
            blocking_reasons,
            not_evaluated_reasons,
            roots,
        )
        effect_status = _effect_status(audit_append_evidence)
        if effect_status == EFFECT_STATUS_UNKNOWN:
            not_evaluated_reasons.append("APPEND_STATUS_UNKNOWN")
        elif effect_status != EFFECT_STATUS_NOT_ATTEMPTED:
            blocking_reasons.append("APPEND_STATUS_CLAIMS_EFFECT")

    _evaluate_trusted_verifier(
        trusted_verifier_evidence,
        context,
        audit_append_evidence,
        blocking_reasons,
        not_evaluated_reasons,
        evidence_refs,
    )

    if blocking_reasons:
        verdict = VERDICT_NOT_AUTHORIZED
    elif not_evaluated_reasons:
        verdict = VERDICT_NOT_EVALUATED
    else:
        verdict = VERDICT_SUFFICIENT

    return {
        "schema_id": "SPIRA_NESIRA_PHASE2_AUDIT_APPEND_EVALUATOR_RESULT",
        "schema_version": "1.0",
        "verdict": verdict,
        "action_not_performed": True,
        "selected_class": SELECTED_CLASS,
        "side_effect_budget_status": {
            "effect_status": effect_status,
            "primary_effect": "APPEND_ONE_BOUNDED_RECORD",
            "effect_count": _int_or_empty(_mapping_get(audit_append_evidence, "effect_count")),
            "total_effect_count": _int_or_empty(_mapping_get(audit_append_evidence, "total_effect_count")),
            "retry_count": _int_or_empty(_mapping_get(audit_append_evidence, "retry_count")),
        },
        "assumptions": sorted(assumptions),
        "conditional_on_roots": sorted(dict.fromkeys(roots)),
        "trusted_verifier_ref": _ref(trusted_verifier_evidence, "trusted_verifier_ref"),
        "human_go_ref": _ref(audit_append_evidence, "human_go_ref"),
        "precondition_breakdown": {
            "audit_append_evidence": _status(audit_append_evidence),
            "trusted_verifier": _status(trusted_verifier_evidence),
            "sink_truth_claim": "NOT_CLAIMED",
            "append_truth_claim": "NOT_CLAIMED",
            "runner_truth_claim": "NOT_CLAIMED_EA_TCB_03_ASSUMED",
        },
        "blocking_reasons": sorted(dict.fromkeys(blocking_reasons)),
        "not_evaluated_reasons": sorted(dict.fromkeys(not_evaluated_reasons)),
        "evidence_refs": sorted(dict.fromkeys(evidence_refs)),
    }


def _evaluate_audit_append_evidence(
    evidence: Mapping[str, Any],
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    roots: list[str],
) -> None:
    if _contains_key(evidence, FORBIDDEN_KEYS):
        blocking_reasons.append("AUDIT_APPEND_ACTION_LOOKING")
    if _contains_key(evidence, FORBIDDEN_PATH_KEYS):
        blocking_reasons.append("AUDIT_APPEND_ARBITRARY_PATH_INPUT")
    if _contains_key(evidence, FORBIDDEN_NETWORK_KEYS):
        blocking_reasons.append("AUDIT_APPEND_NETWORK_TARGET_SUPPLIED")

    action_class = _string(evidence.get("action_class"))
    if not action_class:
        not_evaluated_reasons.append("AUDIT_APPEND_ACTION_CLASS_MISSING")
    elif action_class in INELIGIBLE_CLASSES:
        blocking_reasons.append("AUDIT_APPEND_CLASS_INELIGIBLE")
    elif action_class != SELECTED_CLASS:
        blocking_reasons.append("AUDIT_APPEND_CLASS_NOT_SELECTED")

    if _contains_traversal_marker(evidence):
        blocking_reasons.append("AUDIT_APPEND_PATH_TRAVERSAL")

    _evaluate_sink_root(evidence, not_evaluated_reasons, blocking_reasons, roots)
    _evaluate_budget(evidence, not_evaluated_reasons, blocking_reasons)
    _evaluate_payload(evidence, not_evaluated_reasons, blocking_reasons)
    _evaluate_bindings(evidence, expected_context, not_evaluated_reasons, blocking_reasons)
    _evaluate_human_text(evidence, not_evaluated_reasons)


def _evaluate_sink_root(
    evidence: Mapping[str, Any],
    not_evaluated_reasons: list[str],
    blocking_reasons: list[str],
    roots: list[str],
) -> None:
    root_id = _string(evidence.get("audit_sink_root_id"))
    declared_roots = _string_list(evidence.get("declared_audit_sink_roots"))
    if not root_id or not declared_roots:
        not_evaluated_reasons.append("AUDIT_SINK_ROOT_MISSING")
    elif root_id not in declared_roots:
        blocking_reasons.append("AUDIT_SINK_ROOT_UNDECLARED")
    else:
        roots.append(f"{root_id}@{_string(evidence.get('audit_sink_root_version')) or 'unversioned'}")

    root_shape = _lower(evidence.get("audit_sink_root_shape"))
    if root_shape in {"cwd", "repository_root", "user_path", "environment_variable", "system_log", "network_endpoint"}:
        blocking_reasons.append("AUDIT_SINK_ROOT_FORBIDDEN_DEFAULT")
    elif root_shape and root_shape != "declared_append_only_sink":
        not_evaluated_reasons.append("AUDIT_SINK_ROOT_SHAPE_NOT_EVALUATED")


def _evaluate_budget(
    evidence: Mapping[str, Any],
    not_evaluated_reasons: list[str],
    blocking_reasons: list[str],
) -> None:
    if _string(evidence.get("effect_shape")) != "APPEND_ONE_BOUNDED_RECORD":
        blocking_reasons.append("AUDIT_APPEND_EFFECT_SHAPE_NOT_AUTHORIZED")

    effect_count = _int(evidence.get("effect_count"))
    total_count = _int(evidence.get("total_effect_count"))
    retry_count = _int(evidence.get("retry_count"))
    if effect_count is None:
        not_evaluated_reasons.append("AUDIT_APPEND_EFFECT_COUNT_MISSING")
    elif effect_count != 1:
        blocking_reasons.append("AUDIT_APPEND_EFFECT_COUNT_NOT_AUTHORIZED")
    if total_count is None:
        not_evaluated_reasons.append("AUDIT_APPEND_TOTAL_EFFECT_COUNT_MISSING")
    elif total_count > 1:
        blocking_reasons.append("AUDIT_APPEND_TOTAL_EFFECT_COUNT_EXCEEDS_CEILING")
    elif total_count != 1:
        not_evaluated_reasons.append("AUDIT_APPEND_TOTAL_EFFECT_COUNT_NOT_EVALUATED")
    if retry_count is None:
        not_evaluated_reasons.append("AUDIT_APPEND_RETRY_COUNT_MISSING")
    elif retry_count > 0:
        blocking_reasons.append("AUDIT_APPEND_RETRY_NOT_AUTHORIZED")
    elif retry_count != 0:
        not_evaluated_reasons.append("AUDIT_APPEND_RETRY_COUNT_NOT_EVALUATED")

    supporting = evidence.get("supporting_effects")
    if supporting not in (None, [], "none"):
        blocking_reasons.append("AUDIT_APPEND_SUPPORTING_EFFECTS_NOT_AUTHORIZED")
    for field in ZERO_BUDGET_FIELDS:
        value = _int(evidence.get(field, 0))
        if value is None:
            not_evaluated_reasons.append(f"{field.upper()}_NOT_EVALUATED")
        elif value != 0:
            blocking_reasons.append(f"{field.upper()}_NOT_AUTHORIZED")


def _evaluate_payload(
    evidence: Mapping[str, Any],
    not_evaluated_reasons: list[str],
    blocking_reasons: list[str],
) -> None:
    payload = evidence.get("audit_record_payload")
    if not isinstance(payload, Mapping):
        not_evaluated_reasons.append("AUDIT_RECORD_PAYLOAD_MALFORMED_OR_MISSING")
        return
    if _contains_key(payload, FORBIDDEN_KEYS | FORBIDDEN_NETWORK_KEYS | FORBIDDEN_PATH_KEYS):
        blocking_reasons.append("AUDIT_RECORD_PAYLOAD_FORBIDDEN_FIELD")

    schema_id = _string(evidence.get("audit_schema_id"))
    payload_schema_id = _string(payload.get("schema_id"))
    if not schema_id or not payload_schema_id:
        not_evaluated_reasons.append("AUDIT_SCHEMA_MISSING")
    elif schema_id != payload_schema_id:
        blocking_reasons.append("AUDIT_SCHEMA_MISMATCH")

    idempotency = _string(evidence.get("idempotency_key"))
    payload_idempotency = _string(payload.get("idempotency_key"))
    if not idempotency or not payload_idempotency:
        not_evaluated_reasons.append("IDEMPOTENCY_KEY_MISSING")
    elif idempotency != payload_idempotency:
        blocking_reasons.append("IDEMPOTENCY_KEY_MISMATCH")

    marker = _string(payload.get("result_marker"))
    if marker and marker not in {
        ACTION_NOT_PERFORMED,
        "AUDIT_APPEND_CONSIDERED_FOR_FUTURE_RUNNER_GATE",
        VERDICT_NOT_AUTHORIZED,
        VERDICT_NOT_EVALUATED,
    }:
        blocking_reasons.append("AUDIT_RECORD_RESULT_MARKER_NOT_AUTHORIZED")


def _evaluate_bindings(
    evidence: Mapping[str, Any],
    expected_context: Mapping[str, Any],
    not_evaluated_reasons: list[str],
    blocking_reasons: list[str],
) -> None:
    for evidence_key, context_key, reason in CONTEXT_BINDINGS:
        actual = _string(evidence.get(evidence_key))
        expected = _string(expected_context.get(context_key))
        if not actual or not expected:
            not_evaluated_reasons.append(f"{reason}_NOT_EVALUATED")
        elif actual != expected:
            blocking_reasons.append(reason)

    if not _string(evidence.get("rollback_or_abort_ref_digest")):
        not_evaluated_reasons.append("ROLLBACK_OR_ABORT_REFERENCE_MISSING")


def _evaluate_human_text(evidence: Mapping[str, Any], not_evaluated_reasons: list[str]) -> None:
    text = _lower(evidence.get("human_acknowledgement_text"))
    digest = _string(evidence.get("human_acknowledgement_text_digest"))
    presented_digest = _string(evidence.get("presented_human_acknowledgement_text_digest"))
    required_fragments = (
        "one non-secret audit record",
        "declared audit sink",
        "no command",
        "no target mutation",
        "no network send",
        "no additional write",
    )
    if not text or any(fragment not in text for fragment in required_fragments):
        not_evaluated_reasons.append("HUMAN_READABLE_SIDE_EFFECT_ACKNOWLEDGEMENT_MISSING")
    if not digest or not presented_digest or digest != presented_digest:
        not_evaluated_reasons.append("HUMAN_ACKNOWLEDGEMENT_TEXT_DIGEST_NOT_EVALUATED")


def _evaluate_trusted_verifier(
    trusted_verifier_evidence: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    audit_append_evidence: Mapping[str, Any] | None,
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    evidence_refs: list[str],
) -> None:
    if trusted_verifier_evidence is None:
        not_evaluated_reasons.append("TRUSTED_VERIFIER_MISSING")
        return
    if not isinstance(trusted_verifier_evidence, Mapping):
        not_evaluated_reasons.append("TRUSTED_VERIFIER_MALFORMED")
        return
    evidence_refs.append("trusted_verifier")
    if _contains_key(trusted_verifier_evidence, FORBIDDEN_KEYS | FORBIDDEN_PATH_KEYS | FORBIDDEN_NETWORK_KEYS):
        blocking_reasons.append("TRUSTED_VERIFIER_ACTION_LOOKING")

    origin = _lower(trusted_verifier_evidence.get("origin"))
    if origin in {"agent", "runner", "target"}:
        blocking_reasons.append(f"TRUSTED_VERIFIER_NOT_INDEPENDENT_{origin.upper()}")
    elif origin not in {"trusted_verifier", "external_verifier"}:
        not_evaluated_reasons.append("TRUSTED_VERIFIER_ORIGIN_NOT_EVALUATED")

    if trusted_verifier_evidence.get("independent") is not True:
        blocking_reasons.append("TRUSTED_VERIFIER_NOT_INDEPENDENT")
    if trusted_verifier_evidence.get("compared_runner_intended_budget") is not True:
        blocking_reasons.append("TRUSTED_VERIFIER_DID_NOT_COMPARE_RUNNER_INTENDED_BUDGET")
    if trusted_verifier_evidence.get("compared_prepared_bundle_only") is True:
        blocking_reasons.append("TRUSTED_VERIFIER_COMPARED_PREPARED_BUNDLE_ONLY")

    _compare_verifier_field(
        trusted_verifier_evidence,
        audit_append_evidence,
        expected_context,
        "runner_intended_side_effect_budget_digest",
        "side_effect_budget_digest",
        "TRUSTED_VERIFIER_SIDE_EFFECT_BUDGET_DIGEST_MISMATCH",
        blocking_reasons,
        not_evaluated_reasons,
    )
    _compare_verifier_field(
        trusted_verifier_evidence,
        audit_append_evidence,
        expected_context,
        "runner_intended_target_scope_digest",
        "target_scope_digest",
        "TRUSTED_VERIFIER_TARGET_SCOPE_DIGEST_MISMATCH",
        blocking_reasons,
        not_evaluated_reasons,
    )


def _compare_verifier_field(
    verifier: Mapping[str, Any],
    evidence: Mapping[str, Any] | None,
    context: Mapping[str, Any],
    verifier_key: str,
    model_key: str,
    reason: str,
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
) -> None:
    actual = _string(verifier.get(verifier_key))
    expected = _string(_mapping_get(evidence, model_key)) or _string(context.get(model_key))
    if not actual or not expected:
        not_evaluated_reasons.append(f"{reason}_NOT_EVALUATED")
    elif actual != expected:
        blocking_reasons.append(reason)


def _expected_context_complete(expected_context: Mapping[str, Any]) -> bool:
    required = (
        "action_id",
        "action_class",
        "subject_context_digest",
        "environment_context_digest",
        "target_scope_digest",
        "combined_verdict_digest",
        "action_authority_digest",
        "dry_run_artifact_digest",
        "execution_authorization_digest",
        "human_go_digest",
        "side_effect_budget_digest",
        "rollback_or_abort_ref_digest",
    )
    return all(_string(expected_context.get(key)) for key in required)


def _contains_key(value: Any, forbidden: set[str]) -> bool:
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, item in current.items():
                if str(key).lower() in forbidden:
                    return True
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _contains_traversal_marker(value: Any) -> bool:
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
        elif isinstance(current, str) and ".." in current:
            return True
    return False


def _effect_status(evidence: Mapping[str, Any]) -> str:
    status = _string(evidence.get("append_status")) or EFFECT_STATUS_NOT_ATTEMPTED
    if status == EFFECT_STATUS_UNKNOWN:
        return EFFECT_STATUS_UNKNOWN
    return status


def _mapping_get(value: Mapping[str, Any] | None, key: str) -> Any:
    if not isinstance(value, Mapping):
        return None
    return value.get(key)


def _status(value: Mapping[str, Any] | None) -> str:
    if value is None:
        return "MISSING"
    return "PRESENT" if isinstance(value, Mapping) else "MALFORMED"


def _ref(value: Mapping[str, Any] | None, key: str) -> str:
    if not isinstance(value, Mapping):
        return ""
    return _string(value.get(key))


def _int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _int_or_empty(value: Any) -> int | str:
    parsed = _int(value)
    return parsed if parsed is not None else ""


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _lower(value: Any) -> str:
    return _string(value).lower()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
