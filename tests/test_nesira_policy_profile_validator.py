from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from spira_core import nesira_policy_profile_validator as validator


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "nesira_policy_profile"
SEVERANCE = FIXTURES / "severance"
ISOLATION = FIXTURES / "isolation"
EVIDENCE = ISOLATION / "evidence"
NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


EXPECTED_CONTEXT = {
    "subject_sha256": "a" * 64,
    "candidate_sha256": "b" * 64,
    "legacy_dependency_id": "legacy-db-primary",
    "operation": "severance-blocked",
    "environment_id": "prod-eu-1",
    "evidence_sha256": "c" * 64,
    "policy_id": "nesira-phase1-policy",
    "source_commit": "df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe",
    "state_version": "state-1",
}

ISOLATION_PROFILE = {
    "schema_version": "1.0",
    "profile_id": "legacy-isolation-profile-v1",
}

ISOLATION_CONTEXT = {
    "profile_id": "legacy-isolation-profile-v1",
    "environment_id": "prod-eu-1",
    "candidate_sha256": "b" * 64,
    "legacy_dependency_id": "legacy-db-primary",
}


def test_positive_fixtures_are_valid_but_never_proceed():
    positives = [
        _validate_severance("valid_severance_blocked", EXPECTED_CONTEXT),
        _validate_severance("valid_severance_review", {**EXPECTED_CONTEXT, "operation": "manual-review", "state_version": "state-2"}),
        _validate_severance(
            "valid_severance_cutover",
            {**EXPECTED_CONTEXT, "operation": "cutover-candidate", "state_version": "state-3"},
        ),
        _validate_isolation("valid_isolation_single_evidence"),
        _validate_isolation("valid_isolation_multi_evidence"),
        _validate_isolation("valid_isolation_control_probe"),
    ]

    assert len(positives) == 6
    assert [item["validation_status"] for item in positives] == ["VALID"] * 6
    assert {item["recommended_agent_action"] for item in positives} == {"REPORT_NOT_EVALUATED"}
    assert all(item["stop"] is True for item in positives)
    assert all("evaluated" not in item for item in positives)
    assert all(item["phase1_evaluation_completed"] is True for item in positives)
    assert all(item["not_evaluated"] for item in positives)


def test_severance_error_mapping_matches_v1_1_contract():
    malformed_json = validator.validate_severance_authorization_bytes(b"{", expected_context=EXPECTED_CONTEXT, now_utc=NOW)
    malformed_dsse = _validate_severance("malformed_dsse", EXPECTED_CONTEXT)
    payload_decode = _validate_severance("payload_decode_failure", EXPECTED_CONTEXT)
    schema_violation = _validate_severance("schema_violation", EXPECTED_CONTEXT)
    missing_context = _validate_severance("valid_severance_blocked", {"subject_sha256": "a" * 64})
    subject_mismatch = _validate_severance("valid_severance_blocked", {**EXPECTED_CONTEXT, "subject_sha256": "f" * 64})
    unsupported = _validate_severance("unsupported_schema_version", {**EXPECTED_CONTEXT, "operation": "manual-review", "state_version": "state-5"})
    expired = _validate_severance("expired_temporal_binding", {**EXPECTED_CONTEXT, "operation": "manual-review", "state_version": "state-6"})

    assert malformed_json["validation_status"] == "RERUN_REQUIRED"
    assert malformed_dsse["validation_status"] == "RERUN_REQUIRED"
    assert payload_decode["validation_status"] == "RERUN_REQUIRED"
    assert schema_violation["validation_status"] == "INVALID"
    assert missing_context["validation_status"] == "NOT_EVALUATED"
    assert subject_mismatch["validation_status"] == "RERUN_REQUIRED"
    assert unsupported["validation_status"] == "RERUN_REQUIRED"
    assert expired["validation_status"] == "RERUN_REQUIRED"
    _assert_global_invariants(
        [
            malformed_json,
            malformed_dsse,
            payload_decode,
            schema_violation,
            missing_context,
            subject_mismatch,
            unsupported,
            expired,
        ]
    )


def test_isolation_error_mapping_matches_v1_1_contract(tmp_path):
    malformed_json = validator.validate_legacy_isolation_result_bytes(
        b"{",
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )
    schema_violation_doc = _load_isolation("valid_isolation_single_evidence")
    del schema_violation_doc["candidate_sha256"]
    schema_violation = validator.validate_legacy_isolation_result(
        schema_violation_doc,
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )
    missing_context = validator.validate_legacy_isolation_result(
        _load_isolation("valid_isolation_single_evidence"),
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context={"profile_id": "legacy-isolation-profile-v1"},
    )
    context_mismatch = validator.validate_legacy_isolation_result(
        _load_isolation("valid_isolation_single_evidence"),
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context={**ISOLATION_CONTEXT, "environment_id": "staging"},
    )
    hash_mismatch = _validate_isolation("hash_mismatch")
    traversal = _validate_isolation("unsafe_traversal")
    absolute = _validate_isolation("absolute_path")
    missing_file = _validate_isolation("missing_evidence_file")
    unsupported = _validate_isolation("unsupported_schema_version")
    symlink_escape = _symlink_escape_result(tmp_path)
    directory_evidence = _directory_evidence_result(tmp_path)
    duplicate_evidence = _duplicate_evidence_result()

    assert malformed_json["validation_status"] == "RERUN_REQUIRED"
    assert schema_violation["validation_status"] == "INVALID"
    assert missing_context["validation_status"] == "NOT_EVALUATED"
    assert context_mismatch["validation_status"] == "RERUN_REQUIRED"
    assert hash_mismatch["validation_status"] == "INVALID"
    assert traversal["validation_status"] == "INVALID"
    assert absolute["validation_status"] == "INVALID"
    assert missing_file["validation_status"] == "NOT_EVALUATED"
    assert unsupported["validation_status"] == "RERUN_REQUIRED"
    assert symlink_escape["validation_status"] == "INVALID"
    assert directory_evidence["validation_status"] == "INVALID"
    assert duplicate_evidence["validation_status"] == "INVALID"
    assert directory_evidence["reason_codes"] == ["LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE"]
    assert duplicate_evidence["reason_codes"] == ["LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH"]
    _assert_global_invariants(
        [
            malformed_json,
            schema_violation,
            missing_context,
            context_mismatch,
            hash_mismatch,
            traversal,
            absolute,
            missing_file,
            unsupported,
            symlink_escape,
            directory_evidence,
            duplicate_evidence,
        ]
    )


def test_path_security_remediation_rejects_absolute_drive_relative_and_unc_paths():
    cases = {
        "/tmp/evidence.txt": "absolute evidence path",
        "/": "absolute evidence path",
        "/var/log/example": "absolute evidence path",
        "/tmp/../evidence.txt": "absolute evidence path",
        "C:tmp/evidence.txt": "drive-qualified evidence path",
        "C:": "drive-qualified evidence path",
        "D:folder/file": "drive-qualified evidence path",
        "c:tmp/evidence.txt": "drive-qualified evidence path",
        "C:tmp\\evidence.txt": "drive-qualified evidence path",
        "C:\\tmp\\evidence.txt": "drive-qualified evidence path",
        "C:/tmp/evidence.txt": "drive-qualified evidence path",
        "\\\\server\\share\\file": "absolute evidence path",
        "//server/share/file": "absolute evidence path",
        "..\\outside.txt": "traversal or empty path component",
        "safe/..\\outside.txt": "traversal or empty path component",
    }

    for path, reason in cases.items():
        report = _isolation_with_evidence(path, "e" * 64)

        assert report["validation_status"] == "INVALID", path
        assert report["reason_codes"] == ["LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH"], path
        assert report["blocking_items"] == ["unsafe evidence path"], path
        assert report["checks"][0]["details"]["reason"] == reason, path
        assert report["recommended_agent_action"] != "PROCEED"
        assert report["stop"] is True


def test_regular_file_requirement_does_not_return_tool_error_or_leak_local_path(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "adir").mkdir()
    doc = _load_isolation("valid_isolation_single_evidence")
    doc["evidence_manifest"] = [{"path": "adir", "sha256": validator.sha256_hex_bytes(b"")}]

    report = validator.validate_legacy_isolation_result(
        doc,
        profile=ISOLATION_PROFILE,
        evidence_root=root,
        current_context=ISOLATION_CONTEXT,
    )

    serialized = json.dumps(report, sort_keys=True)
    assert report["validation_status"] == "INVALID"
    assert report["reason_codes"] == ["LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE"]
    assert report["tool_errors"] == []
    assert str(tmp_path) not in serialized
    assert "Permission denied" not in serialized
    assert report["recommended_agent_action"] != "PROCEED"
    assert report["stop"] is True


def test_duplicate_canonical_evidence_paths_are_rejected_without_silent_deduplication():
    exact = _duplicate_evidence_result()
    dot_equivalent = _isolation_with_entries(
        [
            {"path": "evidence_a.txt", "sha256": _evidence_hash("evidence_a.txt")},
            {"path": "./evidence_a.txt", "sha256": _evidence_hash("evidence_a.txt")},
        ]
    )

    for report in (exact, dot_equivalent):
        assert report["validation_status"] == "INVALID"
        assert report["reason_codes"] == ["LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH"]
        assert report["recommended_agent_action"] != "PROCEED"
        assert report["stop"] is True


def test_mutation_pairs_do_not_preserve_valid_status():
    base_severance = _validate_severance("valid_severance_blocked", EXPECTED_CONTEXT)
    subject_mutation = _validate_severance("valid_severance_blocked", {**EXPECTED_CONTEXT, "subject_sha256": "f" * 64})
    candidate_mutation = _validate_severance("valid_severance_blocked", {**EXPECTED_CONTEXT, "candidate_sha256": "f" * 64})
    base_isolation = _validate_isolation("valid_isolation_single_evidence")
    environment_mutation = validator.validate_legacy_isolation_result(
        _load_isolation("valid_isolation_single_evidence"),
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context={**ISOLATION_CONTEXT, "environment_id": "staging"},
    )
    hash_mutation = _validate_isolation("hash_mismatch")
    path_mutation = _validate_isolation("unsafe_traversal")
    version_mutation = _validate_isolation("unsupported_schema_version")

    assert base_severance["validation_status"] == "VALID"
    assert base_isolation["validation_status"] == "VALID"
    assert {item["validation_status"] for item in [subject_mutation, candidate_mutation]} == {"RERUN_REQUIRED"}
    assert environment_mutation["validation_status"] == "RERUN_REQUIRED"
    assert hash_mutation["validation_status"] == "INVALID"
    assert path_mutation["validation_status"] == "INVALID"
    assert version_mutation["validation_status"] == "RERUN_REQUIRED"


def test_validator_does_not_mutate_inputs():
    envelope = _load_severance("valid_severance_blocked")
    context = deepcopy(EXPECTED_CONTEXT)
    frozen_envelope = deepcopy(envelope)
    frozen_context = deepcopy(context)

    report = validator.validate_severance_authorization(envelope, expected_context=context, now_utc=NOW)

    assert report["validation_status"] == "VALID"
    assert envelope == frozen_envelope
    assert context == frozen_context


def test_tool_error_is_distinct_from_validation_failure(monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(validator, "_validate_legacy_isolation_result_core", boom)

    report = validator.validate_legacy_isolation_result(
        _load_isolation("valid_isolation_single_evidence"),
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )

    assert report["validation_status"] == "TOOL_ERROR"
    assert report["recommended_agent_action"] == "STOP_BLOCKED"
    assert report["stop"] is True
    assert report["phase1_evaluation_completed"] is False


def test_no_forbidden_phase1_terms_or_v1_output_field_in_module():
    source = (ROOT / "source" / "spira_core" / "nesira_policy_profile_validator.py").read_text(encoding="utf-8")

    assert ("authenticated" + " payload") not in source
    assert '"evaluated"' not in source
    assert "Sigstore" not in source


def test_public_wheel_does_not_expose_nesira_phase1_validator(tmp_path):
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    wheel_sha = result.stdout.splitlines()[1]

    assert wheel_path.is_file()
    assert len(wheel_sha) == 64
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
    assert "spira_core/nesira_policy_profile_validator.py" not in names
    assert not any(name.startswith("research/nesira_policy_profile") for name in names)


def _load_severance(name: str) -> dict:
    return json.loads((SEVERANCE / f"{name}.json").read_text(encoding="utf-8"))


def _load_isolation(name: str) -> dict:
    return json.loads((ISOLATION / f"{name}.json").read_text(encoding="utf-8"))


def _validate_severance(name: str, context: dict) -> dict:
    if name == "malformed_json":
        return validator.validate_severance_authorization_bytes(
            (SEVERANCE / "malformed_json.json").read_bytes(),
            expected_context=context,
            now_utc=NOW,
        )
    return validator.validate_severance_authorization(_load_severance(name), expected_context=context, now_utc=NOW)


def _validate_isolation(name: str) -> dict:
    return validator.validate_legacy_isolation_result(
        _load_isolation(name),
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )


def _symlink_escape_result(tmp_path: Path) -> dict:
    root = tmp_path / "root"
    outside = tmp_path / "outside.txt"
    root.mkdir()
    outside.write_text("outside\n", encoding="utf-8")
    link = root / "escape.txt"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation not available on this platform")
    doc = deepcopy(_load_isolation("valid_isolation_single_evidence"))
    doc["evidence_manifest"] = [{"path": "escape.txt", "sha256": validator.sha256_hex_bytes(outside.read_bytes())}]
    return validator.validate_legacy_isolation_result(
        doc,
        profile=ISOLATION_PROFILE,
        evidence_root=root,
        current_context=ISOLATION_CONTEXT,
    )


def _directory_evidence_result(tmp_path: Path) -> dict:
    root = tmp_path / "regular_file_root"
    root.mkdir()
    (root / "adir").mkdir()
    doc = _load_isolation("valid_isolation_single_evidence")
    doc["evidence_manifest"] = [{"path": "adir", "sha256": validator.sha256_hex_bytes(b"")}]
    return validator.validate_legacy_isolation_result(
        doc,
        profile=ISOLATION_PROFILE,
        evidence_root=root,
        current_context=ISOLATION_CONTEXT,
    )


def _duplicate_evidence_result() -> dict:
    return _isolation_with_entries(
        [
            {"path": "evidence_a.txt", "sha256": _evidence_hash("evidence_a.txt")},
            {"path": "evidence_a.txt", "sha256": _evidence_hash("evidence_a.txt")},
        ]
    )


def _isolation_with_evidence(path: str, sha256: str) -> dict:
    return _isolation_with_entries([{"path": path, "sha256": sha256}])


def _isolation_with_entries(entries: list[dict]) -> dict:
    doc = _load_isolation("valid_isolation_single_evidence")
    doc["evidence_manifest"] = entries
    return validator.validate_legacy_isolation_result(
        doc,
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )


def _evidence_hash(name: str) -> str:
    return validator.sha256_hex_bytes((EVIDENCE / name).read_bytes())


def _assert_global_invariants(reports: list[dict]) -> None:
    for report in reports:
        assert report["recommended_agent_action"] != "PROCEED"
        assert report["stop"] is True
        assert "evaluated" not in report
