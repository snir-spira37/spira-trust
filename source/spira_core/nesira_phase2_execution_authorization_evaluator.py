from __future__ import annotations

from typing import Any, Mapping


VERDICT_SUFFICIENT = "EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE"
VERDICT_NOT_AUTHORIZED = "EXECUTION_NOT_AUTHORIZED"
VERDICT_NOT_EVALUATED = "EXECUTION_AUTHORIZATION_NOT_EVALUATED"

ACTION_NOT_PERFORMED = "ACTION_NOT_PERFORMED"

ASSUMPTION_FLOOR = (
    "EA-HUMAN-01",
    "EA-TCB-01",
    "EA-TCB-03",
    "EA-CLOCK-01",
    "EA-META-01",
    "EA-META-02",
)

FORBIDDEN_EXECUTABLE_KEYS = {
    "automatic_remediation",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "cwd",
    "environment_variables",
    "execution_approved",
    "network_targets",
    "powershell",
    "python -m",
    "runbook",
    "safe_to_execute",
    "script",
    "severance_authorized",
    "shell",
    "subprocess_args",
    "write_paths",
}

FORBIDDEN_GO_ORIGINS = {
    "agent",
    "assessment",
    "ci",
    "combined_verdict",
    "dry_run",
    "runner",
    "target",
}

FORBIDDEN_VERIFIER_ORIGINS = {
    "agent",
    "runner",
    "target",
}

CONTEXT_BINDINGS = (
    ("authorized_action_id", "action_id", "ACTION_ID_MISMATCH"),
    ("authorized_action_class", "action_class", "ACTION_CLASS_MISMATCH"),
    ("authorized_subject_context_digest", "subject_context_digest", "SUBJECT_CONTEXT_DIGEST_MISMATCH"),
    ("authorized_environment_context_digest", "environment_context_digest", "ENVIRONMENT_CONTEXT_DIGEST_MISMATCH"),
    ("authorized_target_scope_digest", "target_scope_digest", "TARGET_SCOPE_DIGEST_MISMATCH"),
    ("expected_side_effects_digest", "expected_side_effects_digest", "EXPECTED_SIDE_EFFECTS_DIGEST_MISMATCH"),
    ("rollback_or_abort_ref_digest", "rollback_or_abort_ref_digest", "ROLLBACK_OR_ABORT_DIGEST_MISMATCH"),
    ("evidence_bundle_digest", "evidence_bundle_digest", "EVIDENCE_BUNDLE_DIGEST_MISMATCH"),
    ("combined_verdict_digest", "combined_verdict_digest", "COMBINED_VERDICT_DIGEST_MISMATCH"),
    ("action_authority_digest", "action_authority_digest", "ACTION_AUTHORITY_DIGEST_MISMATCH"),
    ("dry_run_artifact_digest", "dry_run_artifact_digest", "DRY_RUN_ARTIFACT_DIGEST_MISMATCH"),
    (
        "authorized_runner_intended_context_digest",
        "runner_intended_context_digest",
        "RUNNER_INTENDED_CONTEXT_DIGEST_MISMATCH",
    ),
)


def evaluate_execution_authorization(
    expected_context: Mapping[str, Any],
    human_go: Mapping[str, Any] | None,
    trusted_verifier_evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Evaluate authorization consistency without performing any action."""

    blocking_reasons: list[str] = []
    not_evaluated_reasons: list[str] = []
    evidence_refs: list[str] = []
    roots: list[str] = []
    assumptions = set(ASSUMPTION_FLOOR)

    context = expected_context if isinstance(expected_context, Mapping) else {}
    if not isinstance(expected_context, Mapping) or not _expected_context_complete(context):
        blocking_reasons.append("EXPECTED_CONTEXT_MALFORMED_OR_INCOMPLETE")

    _evaluate_human_go(human_go, context, blocking_reasons, not_evaluated_reasons, assumptions, evidence_refs, roots)
    _evaluate_trusted_verifier(
        trusted_verifier_evidence,
        context,
        blocking_reasons,
        not_evaluated_reasons,
        assumptions,
        evidence_refs,
    )

    if blocking_reasons:
        verdict = VERDICT_NOT_AUTHORIZED
    elif not_evaluated_reasons:
        verdict = VERDICT_NOT_EVALUATED
    else:
        verdict = VERDICT_SUFFICIENT
        assumptions.add("EA-META-03")

    return {
        "schema_id": "SPIRA_NESIRA_PHASE2_EXECUTION_AUTHORIZATION_EVALUATOR_RESULT",
        "schema_version": "1.0",
        "verdict": verdict,
        "action_not_performed": True,
        "assumptions": sorted(assumptions),
        "conditional_on_roots": sorted(dict.fromkeys(roots)),
        "trusted_verifier_ref": _ref(trusted_verifier_evidence, "trusted_verifier_ref"),
        "human_go_ref": _ref(human_go, "human_go_id"),
        "precondition_breakdown": {
            "human_go": _human_go_status(human_go),
            "trusted_verifier": _trusted_verifier_status(trusted_verifier_evidence),
            "runner_truth_claim": "NOT_CLAIMED_EA_TCB_03_ASSUMED",
        },
        "blocking_reasons": sorted(dict.fromkeys(blocking_reasons)),
        "not_evaluated_reasons": sorted(dict.fromkeys(not_evaluated_reasons)),
        "evidence_refs": sorted(dict.fromkeys(evidence_refs)),
    }


def _evaluate_human_go(
    human_go: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
    evidence_refs: list[str],
    roots: list[str],
) -> None:
    if human_go is None:
        blocking_reasons.append("HUMAN_GO_MISSING")
        return
    if not isinstance(human_go, Mapping):
        not_evaluated_reasons.append("HUMAN_GO_MALFORMED")
        return
    evidence_refs.append("human_go")
    _add_human_go_assumptions(human_go, assumptions)
    if _contains_forbidden_key(human_go):
        blocking_reasons.append("HUMAN_GO_ACTION_LOOKING")
        return

    origin = _lower(human_go.get("origin"))
    if origin in FORBIDDEN_GO_ORIGINS:
        blocking_reasons.append(f"HUMAN_GO_SELF_AUTHORIZED_BY_{origin.upper()}")
    elif origin not in {"external_human", "change_control"}:
        not_evaluated_reasons.append("HUMAN_GO_ORIGIN_NOT_EVALUATED")

    root_id = _string(human_go.get("approver_root_id"))
    declared_roots = _string_list(human_go.get("declared_approver_roots"))
    if not declared_roots:
        not_evaluated_reasons.append("HUMAN_GO_ROOT_MISSING")
    elif root_id not in declared_roots:
        blocking_reasons.append("HUMAN_GO_ROOT_UNDECLARED")
    else:
        roots.append(f"{root_id}@{_string(human_go.get('approver_root_version')) or 'unversioned'}")

    decision = _lower(human_go.get("approval_decision"))
    if decision == "deny":
        blocking_reasons.append("HUMAN_GO_EXPLICIT_DENY")
    elif decision != "allow":
        not_evaluated_reasons.append("HUMAN_GO_DECISION_NOT_EVALUATED")

    _evaluate_action_scope(human_go, expected_context, blocking_reasons)
    _evaluate_clock_and_revocation(human_go, blocking_reasons, not_evaluated_reasons, assumptions)
    _evaluate_roles(human_go, blocking_reasons, assumptions)
    _evaluate_context_bindings(human_go, expected_context, blocking_reasons, not_evaluated_reasons, assumptions)
    _evaluate_human_text(human_go, blocking_reasons, assumptions)
    _evaluate_nonce(human_go, blocking_reasons, not_evaluated_reasons, assumptions)


def _evaluate_trusted_verifier(
    trusted_verifier_evidence: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
    evidence_refs: list[str],
) -> None:
    if trusted_verifier_evidence is None:
        not_evaluated_reasons.append("TRUSTED_VERIFIER_MISSING")
        return
    if not isinstance(trusted_verifier_evidence, Mapping):
        not_evaluated_reasons.append("TRUSTED_VERIFIER_MALFORMED")
        return
    evidence_refs.append("trusted_verifier")
    assumptions.update({"EA-TCB-02", "EA-MISAPPLICATION-02"})
    if _contains_forbidden_key(trusted_verifier_evidence):
        blocking_reasons.append("TRUSTED_VERIFIER_ACTION_LOOKING")
        return

    origin = _lower(trusted_verifier_evidence.get("origin"))
    if origin in FORBIDDEN_VERIFIER_ORIGINS:
        blocking_reasons.append(f"TRUSTED_VERIFIER_NOT_INDEPENDENT_{origin.upper()}")
    elif origin not in {"trusted_verifier", "external_verifier"}:
        not_evaluated_reasons.append("TRUSTED_VERIFIER_ORIGIN_NOT_EVALUATED")

    if trusted_verifier_evidence.get("independent") is not True:
        blocking_reasons.append("TRUSTED_VERIFIER_NOT_INDEPENDENT")
    if trusted_verifier_evidence.get("compared_runner_intended_context") is not True:
        blocking_reasons.append("TRUSTED_VERIFIER_DID_NOT_COMPARE_RUNNER_INTENDED_CONTEXT")
    if trusted_verifier_evidence.get("compared_prepared_bundle_only") is True:
        blocking_reasons.append("TRUSTED_VERIFIER_COMPARED_PREPARED_BUNDLE_ONLY")

    observed = _string(trusted_verifier_evidence.get("runner_intended_context_digest"))
    expected = _string(expected_context.get("runner_intended_context_digest"))
    if not observed:
        not_evaluated_reasons.append("TRUSTED_VERIFIER_RUNNER_CONTEXT_MISSING")
    elif observed != expected:
        blocking_reasons.append("TRUSTED_VERIFIER_RUNNER_CONTEXT_MISMATCH")


def _evaluate_action_scope(
    human_go: Mapping[str, Any],
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
) -> None:
    action_class = _string(expected_context.get("action_class"))
    allowlist = _string_list(expected_context.get("allowed_action_classes"))
    if action_class and allowlist and action_class not in allowlist:
        blocking_reasons.append("ACTION_CLASS_NOT_ALLOWLISTED")

    approver_allowlist = _string_list(human_go.get("approver_allowed_action_classes"))
    if action_class and approver_allowlist and action_class not in approver_allowlist:
        blocking_reasons.append("APPROVER_NOT_ALLOWED_FOR_ACTION_CLASS")


def _evaluate_clock_and_revocation(
    human_go: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
) -> None:
    if human_go.get("clock_trusted") is not True:
        not_evaluated_reasons.append("CLOCK_MISSING_OR_UNTRUSTED")
        return

    if _lower(human_go.get("time_window_status")) == "expired":
        blocking_reasons.append("HUMAN_GO_EXPIRED")
    elif _lower(human_go.get("time_window_status")) != "valid":
        not_evaluated_reasons.append("HUMAN_GO_TIME_WINDOW_NOT_EVALUATED")

    revocation_status = _lower(human_go.get("revocation_status"))
    if revocation_status:
        assumptions.add("EA-REVOKE-01")
    if revocation_status == "revoked":
        blocking_reasons.append("HUMAN_GO_REVOKED")
    elif revocation_status in {"unknown", "stale"}:
        assumptions.add("EA-REVOKE-02")
        not_evaluated_reasons.append("REVOCATION_UNKNOWN_OR_STALE")
    elif revocation_status != "not_revoked":
        not_evaluated_reasons.append("REVOCATION_NOT_EVALUATED")


def _evaluate_roles(
    human_go: Mapping[str, Any],
    blocking_reasons: list[str],
    assumptions: set[str],
) -> None:
    assumptions.add("EA-ROLE-01")
    approver = _string(human_go.get("approver_identity_ref"))
    operator = _string(human_go.get("operator_identity_ref"))
    if approver and operator and approver == operator:
        assumptions.add("EA-ROLE-02")
        if human_go.get("role_coalescing_allowed") is not True:
            blocking_reasons.append("APPROVER_OPERATOR_COLLAPSE_WITHOUT_POLICY")


def _evaluate_context_bindings(
    human_go: Mapping[str, Any],
    expected_context: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
) -> None:
    assumptions.update({"EA-CONTEXT-01", "EA-CONTEXT-02", "EA-MISAPPLICATION-01"})
    for human_key, context_key, reason in CONTEXT_BINDINGS:
        expected = _string(expected_context.get(context_key))
        actual = _string(human_go.get(human_key))
        if not expected or not actual:
            not_evaluated_reasons.append(f"{reason}_NOT_EVALUATED")
        elif actual != expected:
            blocking_reasons.append(reason)

    if not _string(human_go.get("rollback_or_abort_ref_digest")):
        assumptions.add("EA-ROLLBACK-01")
        blocking_reasons.append("ROLLBACK_OR_ABORT_BINDING_MISSING")
    elif _string(human_go.get("rollback_or_abort_ref_digest")):
        assumptions.add("EA-ROLLBACK-01")


def _evaluate_human_text(
    human_go: Mapping[str, Any],
    blocking_reasons: list[str],
    assumptions: set[str],
) -> None:
    assumptions.update({"EA-HUMAN-TEXT-01", "EA-HUMAN-TEXT-02"})
    text = _string(human_go.get("human_acknowledgement_text"))
    digest = _string(human_go.get("human_acknowledgement_text_digest"))
    presented_digest = _string(human_go.get("presented_human_acknowledgement_text_digest"))
    if not text:
        blocking_reasons.append("OPAQUE_HASH_WITHOUT_HUMAN_READABLE_TEXT")
    if not digest or not presented_digest or digest != presented_digest:
        blocking_reasons.append("HUMAN_ACKNOWLEDGEMENT_TEXT_DIGEST_MISMATCH")


def _evaluate_nonce(
    human_go: Mapping[str, Any],
    blocking_reasons: list[str],
    not_evaluated_reasons: list[str],
    assumptions: set[str],
) -> None:
    assumptions.add("EA-NONCE-01")
    nonce = _string(human_go.get("nonce_or_one_time_use_id"))
    nonce_status = _lower(human_go.get("nonce_status"))
    registry_status = _lower(human_go.get("nonce_registry_status"))
    if registry_status:
        assumptions.add("EA-NONCE-02")
    if registry_status in {"unavailable", "unknown", "stale"}:
        not_evaluated_reasons.append("NONCE_REGISTRY_NOT_EVALUATED")
        return
    if not nonce:
        blocking_reasons.append("NONCE_MISSING")
    elif nonce_status in {"replayed", "used"}:
        blocking_reasons.append("NONCE_REPLAY")
    elif nonce_status != "unused":
        not_evaluated_reasons.append("NONCE_NOT_EVALUATED")


def _add_human_go_assumptions(human_go: Mapping[str, Any], assumptions: set[str]) -> None:
    assumptions.add("EA-HUMAN-02")
    method = _lower(human_go.get("approval_method"))
    if method in {"signed", "approval_system", "change_control"}:
        assumptions.update({"EA-SIGN-01", "EA-SIGN-02"})


def _expected_context_complete(expected_context: Mapping[str, Any]) -> bool:
    required = (
        "action_id",
        "action_class",
        "subject_context_digest",
        "environment_context_digest",
        "target_scope_digest",
        "expected_side_effects_digest",
        "rollback_or_abort_ref_digest",
        "evidence_bundle_digest",
        "combined_verdict_digest",
        "action_authority_digest",
        "dry_run_artifact_digest",
        "runner_intended_context_digest",
    )
    return all(_string(expected_context.get(key)) for key in required)


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


def _human_go_status(human_go: Mapping[str, Any] | None) -> str:
    if human_go is None:
        return "MISSING"
    return "PRESENT" if isinstance(human_go, Mapping) else "MALFORMED"


def _trusted_verifier_status(trusted_verifier_evidence: Mapping[str, Any] | None) -> str:
    if trusted_verifier_evidence is None:
        return "MISSING"
    return "PRESENT" if isinstance(trusted_verifier_evidence, Mapping) else "MALFORMED"


def _ref(value: Mapping[str, Any] | None, key: str) -> str:
    if not isinstance(value, Mapping):
        return ""
    return _string(value.get(key))


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _lower(value: Any) -> str:
    return _string(value).lower()


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str)]
