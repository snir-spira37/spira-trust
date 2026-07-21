from __future__ import annotations

import ast
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_audit_append_provider as provider
from spira_core import nesira_phase2_audit_append_runner as runner


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "spira_core" / "nesira_phase2_audit_append_provider.py"


def test_01_descriptor_digest_is_deterministic(tmp_path):
    first = provider.canonical_descriptor(_sink_binding(tmp_path))
    second = provider.canonical_descriptor(_sink_binding(tmp_path))

    assert provider.descriptor_digest(first) == provider.descriptor_digest(second)


def test_02_descriptor_digest_mismatch_prevents_runner_injection(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))
    context = _runner_context(tmp_path, capability, append_capability_root_digest="sha256:other")

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert "APPEND_CAPABILITY_ROOT_DIGEST_MISMATCH" in artifact["blocking_reasons"]
    assert _sink_text(tmp_path) == ""


def test_03_runner_facing_provider_object_exposes_only_allowed_keys(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))

    assert set(capability) == provider.RUNNER_FACING_KEYS


def test_04_positive_path_calls_provider_once_and_writes_one_record(tmp_path):
    capability = provider.make_declared_audit_append_capability(
        _sink_binding(tmp_path, native_idempotency_enforced=True)
    )
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_APPLIED
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 1
    assert set(provider.CAPABILITY_PROVIDER_ASSUMPTION_FLOOR).issubset(set(artifact["assumptions"]))
    assert "CAP-TCB-01" in artifact["assumptions"]
    lines = _sink_lines(tmp_path)
    assert len(lines) == 1
    assert json.loads(lines[0]) == _payload()


def test_05_repeated_idempotency_key_does_not_create_duplicate_record(tmp_path):
    capability = provider.make_declared_audit_append_capability(
        _sink_binding(tmp_path, native_idempotency_enforced=True)
    )
    context = _runner_context(tmp_path, capability)

    first = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)
    second = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert first["verdict"] == runner.VERDICT_APPLIED
    assert second["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert second["effect_count_applied"] == 0
    assert len(_sink_lines(tmp_path)) == 1


def test_05b_without_native_durable_idempotency_provider_reports_unknown_and_writes_zero(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_05c_cross_instance_repeated_key_without_native_idempotency_writes_zero_records(tmp_path):
    first_capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))
    second_capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))

    first = runner.run_audit_append(
        _runner_context(tmp_path, first_capability),
        _audit_append(),
        _execution_authorization(),
        first_capability,
    )
    second = runner.run_audit_append(
        _runner_context(tmp_path, second_capability),
        _audit_append(),
        _execution_authorization(),
        second_capability,
    )

    assert first["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert second["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert _sink_text(tmp_path) == ""


def test_06_oversized_record_is_rejected_before_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path, max_record_size=10))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_07_secret_bearing_record_is_rejected_before_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))
    context = _runner_context(tmp_path, capability, audit_record_payload={**_payload(), "token": "secret"})

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_attempted"] == 1
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_08_command_or_path_payload_is_rejected_before_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path))
    context = _runner_context(tmp_path, capability, audit_record_payload={**_payload(), "runbook": "do not run"})

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_NOT_AUTHORIZED
    assert artifact["effect_count_attempted"] == 0
    assert _sink_text(tmp_path) == ""


def test_09_provider_status_unknown_maps_to_no_success(tmp_path):
    capability = provider.make_declared_audit_append_capability(
        _sink_binding(tmp_path, max_record_size=1, native_idempotency_enforced=True)
    )
    response = capability["append_one"](_payload(), "idem:1")

    assert response["effect_status"] == provider.APPEND_NOT_AUTHORIZED
    assert response["assumptions"] == []
    assert _sink_text(tmp_path) == ""


def test_10_missing_sink_binding_prevents_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path, _private_sink_target=""))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_11_undeclared_sink_binding_prevents_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path, declared_sink_binding=False))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_12_retry_request_prevents_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path, retry_count=1))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_13_fallback_sink_request_prevents_append(tmp_path):
    capability = provider.make_declared_audit_append_capability(_sink_binding(tmp_path, supporting_effects=["fallback_sink"]))
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert _sink_text(tmp_path) == ""


def test_14_no_parent_directory_creation(tmp_path):
    missing_parent_sink = tmp_path / "missing" / "audit.jsonl"
    capability = provider.make_declared_audit_append_capability(
        _sink_binding(tmp_path, _private_sink_target=str(missing_parent_sink))
    )
    context = _runner_context(tmp_path, capability)

    artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)

    assert artifact["verdict"] == runner.VERDICT_STATUS_UNKNOWN
    assert artifact["effect_count_applied"] == 0
    assert not missing_parent_sink.parent.exists()


def test_15_negative_cases_produce_zero_records(tmp_path):
    cases = [
        _sink_binding(tmp_path, _private_sink_target=""),
        _sink_binding(tmp_path, declared_sink_binding=False),
        _sink_binding(tmp_path, retry_count=1),
        _sink_binding(tmp_path, supporting_effects=["fallback_sink"]),
        _sink_binding(tmp_path, authorized_action_class="LOCAL_STATUS_MARKER_CREATE_ONLY"),
        _sink_binding(tmp_path, effect_shape="WRITE_RECORD"),
    ]

    for item in cases:
        capability = provider.make_declared_audit_append_capability(item)
        context = _runner_context(tmp_path, capability)
        artifact = runner.run_audit_append(context, _audit_append(), _execution_authorization(), capability)
        assert artifact["effect_count_applied"] == 0

    assert _sink_text(tmp_path) == ""


def test_16_provider_applied_response_carries_cap_assumptions(tmp_path):
    capability = provider.make_declared_audit_append_capability(
        _sink_binding(tmp_path, native_idempotency_enforced=True)
    )
    response = capability["append_one"](_payload(), "idem:1")

    assert response["effect_status"] == provider.APPEND_APPLIED
    assert set(provider.CAPABILITY_PROVIDER_ASSUMPTION_FLOOR).issubset(set(response["assumptions"]))
    assert "CAP-TCB-01" in response["assumptions"]


def test_17_provider_source_scan_has_only_append_open_write_filesystem_calls():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    forbidden_import_roots = {
        "glob",
        "http",
        "os",
        "pathlib",
        "requests",
        "shutil",
        "socket",
        "subprocess",
        "urllib",
    }
    forbidden_calls = {
        "delete",
        "exists",
        "glob",
        "is_file",
        "iterdir",
        "makedirs",
        "mkdir",
        "move",
        "read",
        "read_bytes",
        "read_text",
        "remove",
        "rename",
        "replace",
        "resolve",
        "rmtree",
        "samefile",
        "stat",
    }
    imported = set()
    calls = []
    open_modes = []
    write_calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in forbidden_calls:
                calls.append(name)
            if name == "open":
                open_modes.append(_literal_arg(node, 1))
            if name.endswith(".write"):
                write_calls.append(name)

    assert imported.isdisjoint(forbidden_import_roots)
    assert calls == []
    assert open_modes == ["a"]
    assert write_calls == ["sink.write"]


def test_18_public_wheel_does_not_expose_provider(tmp_path):
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

    assert "spira_core/nesira_phase2_audit_append_provider.py" not in names
    assert "audit append provider" not in metadata.lower()


def test_19_no_cli_exposure_for_provider():
    source = (ROOT / "tools" / "build_spira_trust_public.py").read_text(encoding="utf-8")

    assert "nesira_phase2_audit_append_provider.py" not in source


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _literal_arg(node: ast.Call, index: int) -> Any:
    if len(node.args) <= index:
        return None
    value = node.args[index]
    return value.value if isinstance(value, ast.Constant) else None


def _runner_context(tmp_path: Path, capability: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    digest = capability["append_capability_root_digest"]
    context = {
        "action_id": "action:audit-provider-1",
        "action_class": runner.SELECTED_CLASS,
        "audit_record_payload": _payload(),
        "idempotency_key": "idem:1",
        "audit_sink_root_ref": "audit-sink-root-main@1",
        "append_capability_ref": capability["append_capability_ref"],
        "append_capability_root_digest": digest,
        "human_go_authorized_append_capability_root_digest": digest,
        "trusted_verifier_approved_append_capability_root_digest": digest,
    }
    context.update(overrides)
    _ensure_sink(tmp_path)
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


def _sink_binding(tmp_path: Path, **overrides: Any) -> dict[str, Any]:
    binding = {
        "provider_id": "audit-append-provider-main",
        "provider_class": provider.PROVIDER_CLASS,
        "provider_contract_version": "1",
        "audit_sink_root_id": "audit-sink-root-main",
        "audit_sink_root_version": "1",
        "sink_binding_digest": "sha256:sink-binding",
        "append_only_policy_id": "append-only-policy-main",
        "append_only_policy_digest": "sha256:append-only-policy",
        "idempotency_namespace": "idempotency:test",
        "record_schema_id": "audit-record-v1",
        "record_schema_version": "1",
        "max_record_size": 4096,
        "authorized_action_class": provider.ACTION_CLASS,
        "effect_shape": provider.EFFECT_SHAPE,
        "effect_count": 1,
        "total_effect_count": 1,
        "retry_count": 0,
        "supporting_effects": [],
        "declared_sink_binding": True,
        "append_capability_ref": "append-capability:main",
        "_private_sink_target": str(_sink_file(tmp_path)),
    }
    binding.update(overrides)
    return binding


def _payload(**overrides: Any) -> dict[str, Any]:
    payload = {
        "schema_id": "audit-record-v1",
        "schema_version": "1",
        "record_id": "audit-record:1",
        "action_id": "action:audit-provider-1",
        "action_class": runner.SELECTED_CLASS,
        "result_marker": "AUDIT_APPEND_REQUESTED_BY_AUTHORIZED_RUNNER",
        "idempotency_key": "idem:1",
    }
    payload.update(overrides)
    return payload


def _sink_file(tmp_path: Path) -> Path:
    return tmp_path / "audit.jsonl"


def _ensure_sink(tmp_path: Path) -> None:
    _sink_file(tmp_path).touch()


def _sink_text(tmp_path: Path) -> str:
    path = _sink_file(tmp_path)
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _sink_lines(tmp_path: Path) -> list[str]:
    text = _sink_text(tmp_path)
    return [line for line in text.splitlines() if line]
