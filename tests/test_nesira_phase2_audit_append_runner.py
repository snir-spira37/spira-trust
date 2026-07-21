from __future__ import annotations

import ast
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_audit_append_runner as runner


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "spira_core" / "nesira_phase2_audit_append_runner.py"


def test_01_positive_path_calls_append_once_and_reports_applied():
    capability = _capability()

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_APPLIED
    assert artifact["effect_status"] == runner.EFFECT_STATUS_APPLIED
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 1
    assert set(runner.APPLIED_ASSUMPTIONS).issubset(set(artifact["assumptions"]))
    assert "CAP-TCB-01" in artifact["assumptions"]
    assert capability["call_count"] == 1
    assert capability["calls"] == [(_payload(), "idem:1")]


def test_02_missing_audit_append_artifact_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(_context(), None, _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "AUDIT_APPEND_ARTIFACT_MISSING" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_03_missing_execution_authorization_artifact_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(_context(), _audit_append(), None, capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "EXECUTION_AUTHORIZATION_ARTIFACT_MISSING" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_04_missing_capability_does_not_call_append():
    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), None)

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "APPEND_CAPABILITY_MISSING" in artifact["not_evaluated_reasons"]
    assert artifact["effect_count_attempted"] == 0


def test_05_audit_append_not_satisfied_does_not_call_append():
    capability = _capability()
    audit_append = _audit_append(verdict="AUDIT_APPEND_NOT_AUTHORIZED")

    artifact = runner.run_audit_append(_context(), audit_append, _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_EVALUATOR_NOT_SATISFIED" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_06_execution_authorization_not_satisfied_does_not_call_append():
    capability = _capability()
    execution_authorization = _execution_authorization(verdict="EXECUTION_NOT_AUTHORIZED")

    artifact = runner.run_audit_append(_context(), _audit_append(), execution_authorization, capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "EXECUTION_AUTHORIZATION_NOT_SATISFIED" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_07_action_class_mismatch_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(action_class="LOCAL_STATUS_MARKER_CREATE_ONLY"),
        _audit_append(),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "RUNNER_ACTION_CLASS_NOT_AUTHORIZED" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_08_payload_missing_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(audit_record_payload=None),
        _audit_append(),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "AUDIT_RECORD_PAYLOAD_MISSING" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_09_idempotency_missing_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(idempotency_key=""),
        _audit_append(),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "IDEMPOTENCY_KEY_MISSING" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_10_audit_sink_ref_missing_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(audit_sink_root_ref=""),
        _audit_append(),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "AUDIT_SINK_ROOT_REF_MISSING" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_11_payload_action_looking_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(audit_record_payload={**_payload(), "command": "do not run"}),
        _audit_append(),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_RECORD_PAYLOAD_ACTION_LOOKING" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_12_audit_append_artifact_action_looking_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(),
        _audit_append(command_line="do not run"),
        _execution_authorization(),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "AUDIT_APPEND_ARTIFACT_ACTION_LOOKING" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_13_execution_authorization_action_looking_does_not_call_append():
    capability = _capability()

    artifact = runner.run_audit_append(
        _context(),
        _audit_append(),
        _execution_authorization(runbook="do not run"),
        capability,
    )

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "EXECUTION_AUTHORIZATION_ARTIFACT_ACTION_LOOKING" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_14_capability_exposes_probe_or_path_operation_does_not_call_append():
    capability = _capability(stat="probe")

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_EXPOSES_FORBIDDEN_OPERATION" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_15_capability_method_missing_does_not_call_append():
    capability = _capability()
    del capability["append_one"]

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "APPEND_CAPABILITY_METHOD_MISSING" in artifact["not_evaluated_reasons"]
    assert capability["call_count"] == 0


def test_16_capability_ref_mismatch_does_not_call_append():
    capability = _capability(append_capability_ref="capability:other")

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_REF_MISMATCH" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_17_capability_digest_missing_does_not_call_append():
    capability = _capability(append_capability_root_digest="")

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_EVALUATED
    assert "APPEND_CAPABILITY_ROOT_DIGEST_NOT_EVALUATED" in artifact["not_evaluated_reasons"]
    _assert_no_call(artifact, capability)


def test_18_capability_digest_mismatch_does_not_call_append():
    capability = _capability(append_capability_root_digest="sha256:substituted")

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_ROOT_DIGEST_MISMATCH" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_19_human_go_approved_digest_mismatch_does_not_call_append():
    capability = _capability()
    context = _context(human_go_authorized_append_capability_root_digest="sha256:other")

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_ROOT_DIGEST_MISMATCH" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_20_trusted_verifier_approved_digest_mismatch_does_not_call_append():
    capability = _capability()
    context = _context(trusted_verifier_approved_append_capability_root_digest="sha256:other")

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_ROOT_DIGEST_MISMATCH" in artifact["blocking_reasons"]
    _assert_no_call(artifact, capability)


def test_21_append_response_unknown_is_not_success_and_called_once():
    capability = _capability(response={"effect_status": runner.EFFECT_STATUS_UNKNOWN})

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_status"] == runner.EFFECT_STATUS_UNKNOWN
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 0
    assert capability["call_count"] == 1


def test_22_append_exception_is_unknown_and_no_fallback_write():
    capability = _capability(raises=True)

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 0
    assert capability["call_count"] == 1
    assert "APPEND_CAPABILITY_STATUS_UNKNOWN" in artifact["not_evaluated_reasons"]


def test_23_output_contains_no_executable_or_path_fields():
    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), _capability())

    assert _forbidden_output_hits(artifact) == []


def test_24_static_source_scan_finds_no_ambient_execution_or_probe_primitives():
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
        "exists",
        "is_file",
        "stat",
        "read",
        "read_text",
        "read_bytes",
        "iterdir",
        "glob",
        "resolve",
        "absolute",
        "samefile",
        "os.system",
        "os.popen",
        "subprocess.run",
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


def test_all_negative_cases_make_zero_append_calls():
    cases = [
        (_context(), None, _execution_authorization(), _capability()),
        (_context(), _audit_append(), None, _capability()),
        (_context(), _audit_append(verdict="AUDIT_APPEND_NOT_EVALUATED"), _execution_authorization(), _capability()),
        (_context(), _audit_append(), _execution_authorization(verdict="EXECUTION_NOT_AUTHORIZED"), _capability()),
        (_context(action_class="LOCAL_STATUS_MARKER_CREATE_ONLY"), _audit_append(), _execution_authorization(), _capability()),
        (_context(audit_record_payload=None), _audit_append(), _execution_authorization(), _capability()),
        (_context(idempotency_key=""), _audit_append(), _execution_authorization(), _capability()),
        (_context(audit_sink_root_ref=""), _audit_append(), _execution_authorization(), _capability()),
        (_context(audit_record_payload={**_payload(), "script": "no"}), _audit_append(), _execution_authorization(), _capability()),
        (_context(), _audit_append(command="no"), _execution_authorization(), _capability()),
        (_context(), _audit_append(), _execution_authorization(command="no"), _capability()),
        (_context(), _audit_append(), _execution_authorization(), _capability(open="no")),
        (_context(), _audit_append(), _execution_authorization(), _capability(append_capability_ref="other")),
        (_context(), _audit_append(), _execution_authorization(), _capability(append_capability_root_digest="sha256:other")),
    ]

    for context, audit_append, execution_authorization, capability in cases:
        artifact = runner.run_audit_append(context, audit_append, execution_authorization, capability)
        assert artifact["verdict"] in {runner.VERDICT_NOT_AUTHORIZED, runner.VERDICT_NOT_EVALUATED}
        if capability is not None:
            assert capability["call_count"] == 0
        assert artifact["effect_count_attempted"] == 0
        assert artifact["effect_count_applied"] == 0


def test_append_capability_called_at_most_once_even_when_response_is_malformed():
    capability = _capability(response={"effect_status": "MALFORMED"})

    artifact = runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert capability["call_count"] == 1
    assert artifact["effect_count_applied"] == 0


def test_floor_assumptions_always_carried():
    artifacts = [
        runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), _capability()),
        runner.run_audit_append(_context(), None, _execution_authorization(), _capability()),
        runner.run_audit_append(_context(), _audit_append(), None, _capability()),
        runner.run_audit_append(_context(), _audit_append(), _execution_authorization(), _capability(raises=True)),
    ]

    for artifact in artifacts:
        assert set(runner.ASSUMPTION_FLOOR).issubset(set(artifact["assumptions"]))
        assert "EA-TCB-03" in artifact["assumptions"]


def test_two_run_equality_for_negative_case():
    first = runner.run_audit_append(_context(), None, _execution_authorization(), _capability())
    second = runner.run_audit_append(_context(), None, _execution_authorization(), _capability())

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_public_wheel_does_not_expose_audit_append_runner(tmp_path):
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

    assert "spira_core/nesira_phase2_audit_append_runner.py" not in names
    assert "audit append runner" not in metadata.lower()


def _assert_no_call(artifact: dict[str, Any], capability: dict[str, Any]) -> None:
    assert capability["call_count"] == 0
    assert artifact["effect_count_attempted"] == 0
    assert artifact["effect_count_applied"] == 0
    assert artifact["effect_status"] == runner.EFFECT_STATUS_NOT_ATTEMPTED


def _forbidden_output_hits(value: Any) -> list[str]:
    hits: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if str(key).lower() in runner.FORBIDDEN_ARTIFACT_KEYS or str(key).lower() in runner.FORBIDDEN_CAPABILITY_KEYS:
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
        "action_class": runner.SELECTED_CLASS,
        "audit_record_payload": _payload(),
        "idempotency_key": "idem:1",
        "audit_sink_root_ref": "audit-sink-root-main@1",
        "append_capability_ref": "append-capability:main",
        "append_capability_root_digest": "sha256:capability-root",
        "human_go_authorized_append_capability_root_digest": "sha256:capability-root",
        "trusted_verifier_approved_append_capability_root_digest": "sha256:capability-root",
    }
    context.update(overrides)
    return context


def _audit_append(**overrides: Any) -> dict[str, Any]:
    artifact = {
        "schema_id": "SPIRA_NESIRA_PHASE2_AUDIT_APPEND_EVALUATOR_RESULT",
        "schema_version": "1.0",
        "verdict": runner.AUDIT_APPEND_EVALUATOR_VERDICT_REQUIRED,
        "action_not_performed": True,
        "assumptions": list(runner.ASSUMPTION_FLOOR),
    }
    artifact.update(overrides)
    return artifact


def _execution_authorization(**overrides: Any) -> dict[str, Any]:
    artifact = {
        "schema_id": "SPIRA_NESIRA_PHASE2_EXECUTION_AUTHORIZATION_EVALUATOR_RESULT",
        "schema_version": "1.0",
        "verdict": runner.EXECUTION_AUTHORIZATION_VERDICT_REQUIRED,
        "action_not_performed": True,
        "assumptions": list(runner.ASSUMPTION_FLOOR),
    }
    artifact.update(overrides)
    return artifact


def _capability(**overrides: Any) -> dict[str, Any]:
    calls: list[tuple[Any, str]] = []
    capability: dict[str, Any] = {}

    def append_one(record_payload: Any, idempotency_key: str) -> dict[str, Any]:
        capability["call_count"] += 1
        calls.append((record_payload, idempotency_key))
        if capability["raises"]:
            raise RuntimeError("append status unavailable")
        return capability["response"]

    capability.update({
        "append_capability_ref": "append-capability:main",
        "append_capability_root_digest": "sha256:capability-root",
        "append_one": append_one,
        "call_count": 0,
        "calls": calls,
        "response": {"effect_status": runner.EFFECT_STATUS_APPLIED},
        "raises": False,
    })
    capability.update(overrides)
    return capability


def _payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "schema_id": "audit-record-v1",
        "schema_version": "1",
        "record_id": "audit-record:1",
        "action_id": "action:audit-append-1",
        "action_class": runner.SELECTED_CLASS,
        "result_marker": "AUDIT_APPEND_REQUESTED_BY_AUTHORIZED_RUNNER",
    }
    payload.update(overrides)
    return payload
