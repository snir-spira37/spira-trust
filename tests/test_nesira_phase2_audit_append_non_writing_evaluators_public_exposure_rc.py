from __future__ import annotations

import json
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.4"
EXECUTION_EVALUATOR = "spira_core/nesira_phase2_execution_authorization_evaluator.py"
AUDIT_APPEND_EVALUATOR = "spira_core/nesira_phase2_audit_append_evaluator.py"
AUDIT_APPEND_RUNNER = "spira_core/nesira_phase2_audit_append_runner.py"
AUDIT_APPEND_PROVIDER = "spira_core/nesira_phase2_audit_append_provider.py"


def test_public_wheel_contains_non_writing_evaluators_only(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    names, metadata, entry_points = _wheel_payload(wheel_path)

    assert wheel_path.name == f"spira_trust-{VERSION}-py3-none-any.whl"
    assert f"Version: {VERSION}" in metadata
    assert EXECUTION_EVALUATOR in names
    assert AUDIT_APPEND_EVALUATOR in names
    assert AUDIT_APPEND_RUNNER not in names
    assert AUDIT_APPEND_PROVIDER not in names
    assert all(not name.startswith("tests/") for name in names)
    assert all(not name.startswith("research/") for name in names)
    assert all(not name.startswith("tools/") for name in names)
    assert all("_harness.py" not in name for name in names)
    assert "spira-trust = spira_core.trust_cli:main" in entry_points
    assert "spira = spira_core.trust_cli:main" in entry_points
    assert "audit" not in entry_points.lower()
    assert "append" not in entry_points.lower()
    assert "provider" not in metadata.lower()
    assert "execution approved" not in metadata.lower()


def test_installed_wheel_execution_authorization_evaluator_is_non_writing(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    python = _install_wheel_in_venv(tmp_path, wheel_path)

    code = r"""
import json
from spira_core import nesira_phase2_execution_authorization_evaluator as evaluator

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
verifier = {
    "trusted_verifier_ref": "verifier-main@1",
    "origin": "trusted_verifier",
    "independent": True,
    "compared_runner_intended_context": True,
    "compared_prepared_bundle_only": False,
    "runner_intended_context_digest": "sha256:runner-input",
}
artifact = evaluator.evaluate_execution_authorization(context, human_go, verifier)
print(json.dumps(artifact, sort_keys=True))
"""
    result = subprocess.run([python, "-c", code], text=True, capture_output=True, check=True)
    artifact = json.loads(result.stdout)

    assert artifact["verdict"] == "EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE"
    assert artifact["action_not_performed"] is True
    assert "EA-TCB-03" in artifact["assumptions"]
    assert _forbidden_output_hits(artifact) == []


def test_installed_wheel_audit_append_evaluator_is_non_writing(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    python = _install_wheel_in_venv(tmp_path, wheel_path)

    code = r"""
import json
from spira_core import nesira_phase2_audit_append_evaluator as evaluator

payload = {
    "schema_id": "audit-record-v1",
    "schema_version": "1",
    "record_id": "audit-record:1",
    "action_id": "action:audit-append-1",
    "action_class": evaluator.SELECTED_CLASS,
    "subject_context_digest": "sha256:subject",
    "environment_context_digest": "sha256:environment",
    "target_scope_digest": "sha256:target",
    "combined_verdict_digest": "sha256:combined",
    "action_authority_digest": "sha256:action-authority",
    "dry_run_artifact_digest": "sha256:dry-run",
    "execution_authorization_digest": "sha256:execution-authorization",
    "human_go_digest": "sha256:human-go",
    "side_effect_budget_digest": "sha256:budget",
    "result_marker": evaluator.ACTION_NOT_PERFORMED,
    "assumptions_carried": list(evaluator.ASSUMPTION_FLOOR),
    "created_at": "2026-07-21T00:00:00Z",
    "idempotency_key": "idem:1",
}
context = {
    "action_id": "action:audit-append-1",
    "action_class": evaluator.SELECTED_CLASS,
    "subject_context_digest": "sha256:subject",
    "environment_context_digest": "sha256:environment",
    "target_scope_digest": "sha256:target",
    "combined_verdict_digest": "sha256:combined",
    "action_authority_digest": "sha256:action-authority",
    "dry_run_artifact_digest": "sha256:dry-run",
    "execution_authorization_digest": "sha256:execution-authorization",
    "human_go_digest": "sha256:human-go",
    "side_effect_budget_digest": "sha256:budget",
    "rollback_or_abort_ref_digest": "sha256:rollback",
}
evidence = {
    "action_id": "action:audit-append-1",
    "action_class": evaluator.SELECTED_CLASS,
    "effect_shape": "APPEND_ONE_BOUNDED_RECORD",
    "effect_count": 1,
    "total_effect_count": 1,
    "retry_count": 0,
    "supporting_effects": [],
    "temporary_files": 0,
    "lock_files": 0,
    "cache_writes": 0,
    "checkpoint_writes": 0,
    "post_effect_verification_writes": 0,
    "network_sends": 0,
    "cleanup_effects": 0,
    "append_status": evaluator.EFFECT_STATUS_NOT_ATTEMPTED,
    "audit_sink_root_id": "audit-sink-root-main",
    "audit_sink_root_version": "1",
    "audit_sink_root_shape": "declared_append_only_sink",
    "declared_audit_sink_roots": ["audit-sink-root-main"],
    "audit_schema_id": "audit-record-v1",
    "audit_record_payload": payload,
    "idempotency_key": "idem:1",
    "subject_context_digest": "sha256:subject",
    "environment_context_digest": "sha256:environment",
    "target_scope_digest": "sha256:target",
    "combined_verdict_digest": "sha256:combined",
    "action_authority_digest": "sha256:action-authority",
    "dry_run_artifact_digest": "sha256:dry-run",
    "execution_authorization_digest": "sha256:execution-authorization",
    "human_go_digest": "sha256:human-go",
    "human_go_ref": "human-go:1",
    "side_effect_budget_digest": "sha256:budget",
    "rollback_or_abort_ref_digest": "sha256:rollback",
    "human_acknowledgement_text": (
        "One non-secret audit record may be appended to the declared audit sink. "
        "No command, no target mutation, no network send, no remediation, no severance, "
        "no retry, and no additional write is authorized by this approval."
    ),
    "human_acknowledgement_text_digest": "sha256:human-text",
    "presented_human_acknowledgement_text_digest": "sha256:human-text",
}
verifier = {
    "trusted_verifier_ref": "verifier-main@1",
    "origin": "trusted_verifier",
    "independent": True,
    "compared_runner_intended_budget": True,
    "compared_prepared_bundle_only": False,
    "runner_intended_side_effect_budget_digest": "sha256:budget",
    "runner_intended_target_scope_digest": "sha256:target",
}
artifact = evaluator.evaluate_audit_append_model(context, evidence, verifier)
print(json.dumps(artifact, sort_keys=True))
"""
    result = subprocess.run([python, "-c", code], text=True, capture_output=True, check=True)
    artifact = json.loads(result.stdout)

    assert artifact["verdict"] == "AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE"
    assert artifact["action_not_performed"] is True
    assert artifact["precondition_breakdown"]["append_truth_claim"] == "NOT_CLAIMED"
    assert artifact["precondition_breakdown"]["sink_truth_claim"] == "NOT_CLAIMED"
    assert "EA-TCB-03" in artifact["assumptions"]
    assert _forbidden_output_hits(artifact) == []


def test_public_exposure_rc_preserves_dependency_and_entry_point_posture():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == VERSION
    assert pyproject["project"]["dependencies"] == []
    assert pyproject["project"]["optional-dependencies"] == {
        "nesira-assessment": ["cryptography==49.0.0"],
    }
    assert pyproject["project"]["scripts"] == {
        "spira-trust": "spira_core.trust_cli:main",
        "spira": "spira_core.trust_cli:main",
    }
    allowlist = pyproject["tool"]["spira"]["public-wheel"]["package_allowlist"]
    assert "spira_core.nesira_phase2_execution_authorization_evaluator" in allowlist
    assert "spira_core.nesira_phase2_audit_append_evaluator" in allowlist
    assert "spira_core.nesira_phase2_audit_append_runner" not in allowlist
    assert "spira_core.nesira_phase2_audit_append_provider" not in allowlist


def _build_public_wheel(tmp_path: Path) -> Path:
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.splitlines()[0])


def _wheel_payload(wheel_path: Path) -> tuple[list[str], str, str]:
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
        metadata = zf.read(metadata_name).decode("utf-8")
        entry_points = zf.read(entry_points_name).decode("utf-8")
    return names, metadata, entry_points


def _install_wheel_in_venv(tmp_path: Path, wheel_path: Path) -> str:
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, text=True, capture_output=True)
    python = venv / "Scripts" / "python.exe"
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return str(python)


def _forbidden_output_hits(value: Any) -> list[str]:
    forbidden = {
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
        "path",
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
    hits: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if str(key).lower() in forbidden:
                    hits.append(str(key))
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(hits)
