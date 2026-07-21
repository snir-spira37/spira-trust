from __future__ import annotations

import ast
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_audit_append_evaluator as evaluator


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "spira_core" / "nesira_phase2_audit_append_evaluator.py"


def test_01_strongest_valid_path_is_sufficient_for_future_gate_and_not_performed():
    artifact = evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_SUFFICIENT
    assert artifact["action_not_performed"] is True
    assert artifact["blocking_reasons"] == []
    assert artifact["not_evaluated_reasons"] == []
    _assert_floor_and_not_performed(artifact)


def test_02_missing_audit_sink_root_is_not_evaluated():
    evidence = _evidence(audit_sink_root_id="", declared_audit_sink_roots=[])

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "AUDIT_SINK_ROOT_MISSING" in artifact["not_evaluated_reasons"]


def test_03_user_supplied_absolute_path_is_not_authorized():
    evidence = _evidence(absolute_path="C:/tmp/audit.log")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_ARBITRARY_PATH_INPUT" in artifact["blocking_reasons"]


def test_04_path_traversal_is_not_authorized():
    evidence = _evidence(audit_record_payload={**_payload(), "relative_name": "../audit.log"})

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_PATH_TRAVERSAL" in artifact["blocking_reasons"]


def test_05_network_target_supplied_is_not_authorized():
    evidence = _evidence(network_target="https://example.invalid/audit")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_NETWORK_TARGET_SUPPLIED" in artifact["blocking_reasons"]


def test_06_command_field_in_payload_is_not_authorized():
    evidence = _evidence(audit_record_payload={**_payload(), "command": "do not run"})

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_RECORD_PAYLOAD_FORBIDDEN_FIELD" in artifact["blocking_reasons"]


def test_07_secret_bearing_payload_is_not_authorized():
    evidence = _evidence(audit_record_payload={**_payload(), "token": "secret-token"})

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_RECORD_PAYLOAD_FORBIDDEN_FIELD" in artifact["blocking_reasons"]


def test_08_total_effect_count_two_is_not_authorized():
    evidence = _evidence(total_effect_count=2)

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_TOTAL_EFFECT_COUNT_EXCEEDS_CEILING" in artifact["blocking_reasons"]


def test_09_retry_count_one_is_not_authorized():
    evidence = _evidence(retry_count=1)

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_RETRY_NOT_AUTHORIZED" in artifact["blocking_reasons"]


def test_10_missing_idempotency_key_is_not_evaluated():
    evidence = _evidence(idempotency_key="", audit_record_payload={**_payload(), "idempotency_key": ""})

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "IDEMPOTENCY_KEY_MISSING" in artifact["not_evaluated_reasons"]


def test_11_missing_human_readable_side_effect_acknowledgement_is_not_evaluated():
    evidence = _evidence(human_acknowledgement_text="sha256:opaque")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "HUMAN_READABLE_SIDE_EFFECT_ACKNOWLEDGEMENT_MISSING" in artifact["not_evaluated_reasons"]


def test_12_human_go_digest_binds_different_side_effect_budget_is_not_authorized():
    evidence = _evidence(side_effect_budget_digest="sha256:different-budget")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "SIDE_EFFECT_BUDGET_DIGEST_MISMATCH" in artifact["blocking_reasons"]


def test_13_trusted_verifier_compares_prepared_bundle_only_is_not_authorized():
    verifier = _verifier(compared_prepared_bundle_only=True)

    artifact = evaluator.evaluate_audit_append_model(_context(), _evidence(), verifier)

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "TRUSTED_VERIFIER_COMPARED_PREPARED_BUNDLE_ONLY" in artifact["blocking_reasons"]


def test_14_rollback_or_abort_reference_missing_is_not_evaluated():
    context = _context(rollback_or_abort_ref_digest="")
    evidence = _evidence(rollback_or_abort_ref_digest="")

    artifact = evaluator.evaluate_audit_append_model(context, evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert "ROLLBACK_OR_ABORT_REFERENCE_MISSING" in artifact["not_evaluated_reasons"]


def test_15_append_status_unknown_is_unknown_and_has_no_follow_on_action():
    evidence = _evidence(append_status=evaluator.EFFECT_STATUS_UNKNOWN)

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_EVALUATED
    assert artifact["side_effect_budget_status"]["effect_status"] == evaluator.EFFECT_STATUS_UNKNOWN
    assert "APPEND_STATUS_UNKNOWN" in artifact["not_evaluated_reasons"]
    assert artifact["action_not_performed"] is True


def test_16_strongest_verdict_still_performs_no_append_without_runner_gate():
    artifact = evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_SUFFICIENT
    assert artifact["action_not_performed"] is True
    assert artifact["precondition_breakdown"]["append_truth_claim"] == "NOT_CLAIMED"
    assert artifact["precondition_breakdown"]["sink_truth_claim"] == "NOT_CLAIMED"


def test_class_not_selected_is_not_authorized():
    evidence = _evidence(action_class="LOCAL_STATUS_MARKER_CREATE_ONLY")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_CLASS_NOT_SELECTED" in artifact["blocking_reasons"]


def test_permanently_non_reclassifiable_class_is_not_authorized():
    evidence = _evidence(action_class="SEVERANCE_EXECUTOR")

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_CLASS_INELIGIBLE" in artifact["blocking_reasons"]


def test_supporting_write_is_not_authorized():
    evidence = _evidence(cache_writes=1)

    artifact = evaluator.evaluate_audit_append_model(_context(), evidence, _verifier())

    assert artifact["verdict"] == evaluator.VERDICT_NOT_AUTHORIZED
    assert "CACHE_WRITES_NOT_AUTHORIZED" in artifact["blocking_reasons"]


def test_all_outputs_carry_floor_and_action_not_performed():
    artifacts = [
        evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier()),
        evaluator.evaluate_audit_append_model(_context(), None, _verifier()),
        evaluator.evaluate_audit_append_model(_context(), _evidence(retry_count=1), _verifier()),
        evaluator.evaluate_audit_append_model(_context(), _evidence(), None),
        evaluator.evaluate_audit_append_model({}, _evidence(), _verifier()),
    ]

    for artifact in artifacts:
        _assert_floor_and_not_performed(artifact)


def test_output_contains_no_executable_or_append_truth_key():
    artifact = evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier())

    assert _forbidden_output_hits(artifact) == []


def test_static_source_scan_finds_no_side_effect_imports_or_calls():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    forbidden_import_roots = {
        "glob",
        "http",
        "io",
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
        "io.open",
        "os.getenv",
        "os.popen",
        "os.remove",
        "os.system",
        "Path.exists",
        "Path.is_file",
        "Path.read_bytes",
        "Path.read_text",
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
    first = evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier())
    second = evaluator.evaluate_audit_append_model(_context(), _evidence(), _verifier())

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_public_wheel_does_not_expose_audit_append_evaluator(tmp_path):
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

    assert "spira_core/nesira_phase2_audit_append_evaluator.py" not in names
    assert "audit append evaluator" not in metadata.lower()


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
                if str(key).lower() in evaluator.FORBIDDEN_KEYS:
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
    context.update(overrides)
    return context


def _evidence(**overrides: Any) -> dict[str, Any]:
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
        "audit_record_payload": _payload(),
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
    evidence.update(overrides)
    return evidence


def _payload(**overrides: Any) -> dict[str, Any]:
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
    payload.update(overrides)
    return payload


def _verifier(**overrides: Any) -> dict[str, Any]:
    verifier = {
        "trusted_verifier_ref": "verifier-main@1",
        "origin": "trusted_verifier",
        "independent": True,
        "compared_runner_intended_budget": True,
        "compared_prepared_bundle_only": False,
        "runner_intended_side_effect_budget_digest": "sha256:budget",
        "runner_intended_target_scope_digest": "sha256:target",
    }
    verifier.update(overrides)
    return verifier
