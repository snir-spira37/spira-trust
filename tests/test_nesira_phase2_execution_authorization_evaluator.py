from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_execution_authorization_evaluator as evaluator


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "spira_core" / "nesira_phase2_execution_authorization_evaluator.py"


def test_01_all_machine_checks_pass_no_human_go_is_not_authorized():
    artifact = evaluator.evaluate_execution_authorization(_context(), None, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_MISSING" in artifact["blocking_reasons"]
    _assert_floor_and_not_performed(artifact)


def test_02_agent_created_human_go_is_not_authorized():
    human_go = _human_go(origin="agent")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_SELF_AUTHORIZED_BY_AGENT" in artifact["blocking_reasons"]


def test_03_runner_created_human_go_is_not_authorized():
    human_go = _human_go(origin="runner")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_SELF_AUTHORIZED_BY_RUNNER" in artifact["blocking_reasons"]


def test_04_ci_success_as_human_go_is_not_authorized():
    human_go = _human_go(origin="ci")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_SELF_AUTHORIZED_BY_CI" in artifact["blocking_reasons"]


def test_05_human_go_signed_by_undeclared_root_is_not_authorized():
    human_go = _human_go(approver_root_id="approver-root-other")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_ROOT_UNDECLARED" in artifact["blocking_reasons"]


def test_06_missing_human_go_root_is_not_evaluated():
    human_go = _human_go(declared_approver_roots=[])

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "HUMAN_GO_ROOT_MISSING" in artifact["not_evaluated_reasons"]


def test_07_expired_human_go_with_trusted_clock_is_not_authorized():
    human_go = _human_go(time_window_status="expired")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_EXPIRED" in artifact["blocking_reasons"]


def test_08_clock_missing_is_not_evaluated():
    human_go = _human_go(clock_trusted=False)

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "CLOCK_MISSING_OR_UNTRUSTED" in artifact["not_evaluated_reasons"]


def test_09_revocation_unknown_is_not_evaluated():
    human_go = _human_go(revocation_status="unknown")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "REVOCATION_UNKNOWN_OR_STALE" in artifact["not_evaluated_reasons"]


def test_10_dry_run_digest_mismatch_is_not_authorized():
    human_go = _human_go(dry_run_artifact_digest="sha256:different-dry-run")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "DRY_RUN_ARTIFACT_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_11_action_authority_digest_mismatch_is_not_authorized():
    human_go = _human_go(action_authority_digest="sha256:different-authority")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "ACTION_AUTHORITY_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_12_subject_context_mismatch_is_not_authorized():
    human_go = _human_go(authorized_subject_context_digest="sha256:different-subject")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "SUBJECT_CONTEXT_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_13_runner_intended_context_differs_from_approved_context_is_not_authorized():
    human_go = _human_go(authorized_runner_intended_context_digest="sha256:different-runner-input")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "RUNNER_INTENDED_CONTEXT_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_14_prepared_bundle_matches_but_runner_input_differs_is_not_authorized():
    verifier = _verifier(
        compared_prepared_bundle_only=True,
        runner_intended_context_digest="sha256:different-runner-input",
    )

    artifact = evaluator.evaluate_execution_authorization(_context(), _human_go(), verifier)

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "TRUSTED_VERIFIER_COMPARED_PREPARED_BUNDLE_ONLY" in artifact["blocking_reasons"]
    assert "TRUSTED_VERIFIER_RUNNER_CONTEXT_MISMATCH" in artifact["blocking_reasons"]


def test_15_opaque_hash_without_human_readable_text_is_not_authorized():
    human_go = _human_go(human_acknowledgement_text="")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "OPAQUE_HASH_WITHOUT_HUMAN_READABLE_TEXT" in artifact["blocking_reasons"]


def test_16_acknowledgement_text_digest_mismatch_is_not_authorized():
    human_go = _human_go(presented_human_acknowledgement_text_digest="sha256:different-text")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_ACKNOWLEDGEMENT_TEXT_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_17_nonce_replay_is_not_authorized():
    human_go = _human_go(nonce_status="replayed")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "NONCE_REPLAY" in artifact["blocking_reasons"]


def test_18_nonce_registry_unavailable_is_not_evaluated():
    human_go = _human_go(nonce_registry_status="unavailable")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "NONCE_REGISTRY_NOT_EVALUATED" in artifact["not_evaluated_reasons"]


def test_19_approver_operator_collapse_without_policy_is_not_authorized():
    human_go = _human_go(operator_identity_ref="human:approver-1", role_coalescing_allowed=False)

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "APPROVER_OPERATOR_COLLAPSE_WITHOUT_POLICY" in artifact["blocking_reasons"]


def test_20_rollback_or_abort_missing_is_not_authorized():
    human_go = _human_go(rollback_or_abort_ref_digest="")

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "ROLLBACK_OR_ABORT_BINDING_MISSING" in artifact["blocking_reasons"]


def test_21_action_class_not_allowlisted_is_not_authorized():
    context = _context(allowed_action_classes=["different-action"])

    artifact = evaluator.evaluate_execution_authorization(context, _human_go(), _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "ACTION_CLASS_NOT_ALLOWLISTED" in artifact["blocking_reasons"]


def test_23_missing_action_allowlists_are_not_evaluated():
    context = _context()
    del context["allowed_action_classes"]
    human_go = _human_go()
    del human_go["approver_allowed_action_classes"]

    artifact = evaluator.evaluate_execution_authorization(context, human_go, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "ACTION_CLASS_ALLOWLIST_MISSING" in artifact["not_evaluated_reasons"]
    assert "APPROVER_ACTION_CLASS_ALLOWLIST_MISSING" in artifact["not_evaluated_reasons"]
    _assert_floor_and_not_performed(artifact)


def test_22_all_authorization_evidence_sufficient_still_does_not_perform_action():
    artifact = evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_SUFFICIENT
    assert artifact["action_not_performed"] is True
    assert artifact["blocking_reasons"] == []
    assert artifact["not_evaluated_reasons"] == []
    _assert_floor_and_not_performed(artifact)
    assert "EA-META-03" in artifact["assumptions"]
    for assumption in {
        "EA-HUMAN-TEXT-01",
        "EA-HUMAN-TEXT-02",
        "EA-NONCE-01",
        "EA-MISAPPLICATION-01",
        "EA-MISAPPLICATION-02",
        "EA-ROLE-01",
        "EA-ROLLBACK-01",
    }:
        assert assumption in artifact["assumptions"]


def test_all_paths_carry_floor_and_action_not_performed():
    artifacts = [
        evaluator.evaluate_execution_authorization(_context(), None, _verifier()),
        evaluator.evaluate_execution_authorization(_context(), _human_go(origin="agent"), _verifier()),
        evaluator.evaluate_execution_authorization(_context(), _human_go(clock_trusted=False), _verifier()),
        evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier()),
        evaluator.evaluate_execution_authorization({}, _human_go(), None),
    ]

    for artifact in artifacts:
        _assert_floor_and_not_performed(artifact)


def test_output_contains_no_executable_key():
    artifacts = [
        evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier()),
        evaluator.evaluate_execution_authorization(_context(), _human_go(origin="runner"), _verifier()),
        evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier(origin="runner")),
    ]

    for artifact in artifacts:
        assert _forbidden_output_hits(artifact) == []


def test_malformed_or_action_looking_inputs_fail_closed():
    human_go = _human_go()
    human_go["command"] = "do not run"
    verifier = _verifier()
    verifier["network_targets"] = ["example.invalid"]

    artifact = evaluator.evaluate_execution_authorization(_context(), human_go, verifier)

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "HUMAN_GO_ACTION_LOOKING" in artifact["blocking_reasons"]
    assert "TRUSTED_VERIFIER_ACTION_LOOKING" in artifact["blocking_reasons"]


def test_static_source_scan_finds_no_side_effect_imports_or_calls():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    forbidden_import_roots = {
        "http",
        "os",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "tempfile",
        "urllib",
    }
    forbidden_calls = {
        "open",
        "os.getenv",
        "os.popen",
        "os.remove",
        "os.system",
        "Path.write_bytes",
        "Path.write_text",
    }
    imported = set()
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in forbidden_calls:
                calls.append(name)

    assert imported.isdisjoint(forbidden_import_roots)
    assert calls == []


def test_two_run_equality():
    first = evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier())
    second = evaluator.evaluate_execution_authorization(_context(), _human_go(), _verifier())

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_public_wheel_does_not_expose_execution_authorization_evaluator(tmp_path):
    import subprocess
    import sys
    import zipfile

    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert "spira_core/nesira_phase2_execution_authorization_evaluator.py" not in names
    assert "execution-authorization evaluator" not in metadata.lower()


def _assert_floor_and_not_performed(artifact: dict[str, Any]) -> None:
    assert artifact["action_not_performed"] is True
    assert set(evaluator.ASSUMPTION_FLOOR).issubset(set(artifact["assumptions"]))
    assert "EA-TCB-03" in artifact["assumptions"]


def _forbidden_output_hits(value: Any) -> list[str]:
    hits: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if str(key).lower() in evaluator.FORBIDDEN_EXECUTABLE_KEYS:
                    hits.append(str(key))
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(hits)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _context(**overrides: Any) -> dict[str, Any]:
    context = {
        "action_id": "action:review-only-1",
        "action_class": "review-only-transition",
        "subject_context_digest": "sha256:subject",
        "environment_context_digest": "sha256:environment",
        "target_scope_digest": "sha256:target",
        "expected_side_effects_digest": "sha256:side-effects",
        "rollback_or_abort_ref_digest": "sha256:rollback",
        "evidence_bundle_digest": "sha256:evidence",
        "combined_verdict_digest": "sha256:combined",
        "action_authority_digest": "sha256:action-authority",
        "dry_run_artifact_digest": "sha256:dry-run",
        "runner_intended_context_digest": "sha256:runner-input",
        "allowed_action_classes": ["review-only-transition"],
    }
    context.update(overrides)
    return context


def _human_go(**overrides: Any) -> dict[str, Any]:
    human_go = {
        "human_go_id": "human-go:1",
        "origin": "external_human",
        "approval_method": "signed",
        "approval_decision": "allow",
        "approver_root_id": "approver-root-main",
        "approver_root_version": "1",
        "declared_approver_roots": ["approver-root-main"],
        "approver_identity_ref": "human:approver-1",
        "operator_identity_ref": "human:operator-1",
        "role_coalescing_allowed": False,
        "approver_allowed_action_classes": ["review-only-transition"],
        "clock_trusted": True,
        "time_window_status": "valid",
        "revocation_status": "not_revoked",
        "nonce_or_one_time_use_id": "nonce:1",
        "nonce_status": "unused",
        "nonce_registry_status": "available",
        "human_acknowledgement_text": "Approve review-only-transition for subject digest sha256:subject.",
        "human_acknowledgement_text_digest": "sha256:human-text",
        "presented_human_acknowledgement_text_digest": "sha256:human-text",
        "authorized_action_id": "action:review-only-1",
        "authorized_action_class": "review-only-transition",
        "authorized_subject_context_digest": "sha256:subject",
        "authorized_environment_context_digest": "sha256:environment",
        "authorized_target_scope_digest": "sha256:target",
        "expected_side_effects_digest": "sha256:side-effects",
        "rollback_or_abort_ref_digest": "sha256:rollback",
        "evidence_bundle_digest": "sha256:evidence",
        "combined_verdict_digest": "sha256:combined",
        "action_authority_digest": "sha256:action-authority",
        "dry_run_artifact_digest": "sha256:dry-run",
        "authorized_runner_intended_context_digest": "sha256:runner-input",
    }
    human_go.update(overrides)
    return human_go


def _verifier(**overrides: Any) -> dict[str, Any]:
    verifier = {
        "trusted_verifier_ref": "verifier-main@1",
        "origin": "trusted_verifier",
        "independent": True,
        "compared_runner_intended_context": True,
        "compared_prepared_bundle_only": False,
        "runner_intended_context_digest": "sha256:runner-input",
    }
    verifier.update(overrides)
    return verifier
