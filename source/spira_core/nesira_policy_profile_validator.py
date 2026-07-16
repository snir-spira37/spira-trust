from __future__ import annotations

import base64
import binascii
import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Mapping


RESULT_SCHEMA = "SPIRA_NESIRA_PHASE1_VALIDATION_RESULT_V1_1"
RESULT_SCHEMA_VERSION = "1.1"

ARTIFACT_SEVERANCE = "SEVERANCE_AUTHORIZATION"
ARTIFACT_ISOLATION = "LEGACY_ISOLATION_RESULT"

STATUS_VALID = "VALID"
STATUS_INVALID = "INVALID"
STATUS_NOT_EVALUATED = "NOT_EVALUATED"
STATUS_RERUN_REQUIRED = "RERUN_REQUIRED"
STATUS_TOOL_ERROR = "TOOL_ERROR"

ACTION_STOP_BLOCKED = "STOP_BLOCKED"
ACTION_REPORT_NOT_EVALUATED = "REPORT_NOT_EVALUATED"
ACTION_RERUN_REQUIRED = "RERUN_REQUIRED"

SCOPE_STRUCTURE_BINDING = "STRUCTURE_AND_BINDING"
SCOPE_STRUCTURE_EVIDENCE = "STRUCTURE_AND_EVIDENCE"

DSSE_PAYLOAD_TYPE = "application/vnd.in-toto+json"
IN_TOTO_STATEMENT_TYPE = "https://in-toto.io/Statement/v1"
SEVERANCE_PREDICATE_TYPE = "https://spira.dev/nesira/severance-authorization/v1"
LEGACY_ISOLATION_SCHEMA = "SPIRA_LEGACY_ISOLATION_RESULT_V1"

SEVERANCE_NOT_CLAIMED = [
    "signature_verified",
    "signer_identity_established",
    "signer_authority_established",
    "payload_trusted",
    "severance_authorized",
    "action_approved",
    "safe_to_proceed",
]

ISOLATION_NOT_CLAIMED = [
    "isolation_execution_observed",
    "isolation_execution_trusted",
    "sandbox_created",
    "container_created",
    "severance_authorized",
    "action_approved",
    "safe_to_proceed",
]

SEVERANCE_TRUST_NOT_EVALUATED = [
    "signature_verification",
    "signer_identity",
    "signer_authority",
    "severance_authorization",
]

ISOLATION_TRUST_NOT_EVALUATED = [
    "isolation_execution_observation",
    "isolation_execution_trust",
    "severance_authorization",
]


class NesiraPhase1ValidatorToolError(RuntimeError):
    """Raised when the Phase 1 validator cannot complete its own work."""


def validate_severance_authorization_bytes(
    data: bytes,
    *,
    expected_context: Mapping[str, Any],
    now_utc: datetime,
    limits: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    try:
        envelope = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return _result(
            artifact_type=ARTIFACT_SEVERANCE,
            validation_status=STATUS_RERUN_REQUIRED,
            evaluation_scope=SCOPE_STRUCTURE_BINDING,
            phase1_evaluation_completed=False,
            reason_codes=["NESIRA_PHASE1_MALFORMED_JSON"],
            blocking_items=["malformed JSON"],
            not_evaluated=["decoded DSSE payload"],
            not_claimed=SEVERANCE_NOT_CLAIMED,
            checks=[_check("JSON_PARSE", "FAIL", "MALFORMED_JSON", details={"error": str(exc)})],
            rerun_required=True,
        )
    return validate_severance_authorization(
        envelope,
        expected_context=expected_context,
        now_utc=now_utc,
        limits=limits,
    )


def validate_severance_authorization(
    envelope: Mapping[str, Any],
    *,
    expected_context: Mapping[str, Any],
    now_utc: datetime,
    limits: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    _ = limits
    try:
        return _validate_severance_authorization_core(
            deepcopy(envelope),
            expected_context=deepcopy(expected_context),
            now_utc=_require_aware_utc(now_utc),
        )
    except Exception as exc:
        return _tool_error(ARTIFACT_SEVERANCE, SCOPE_STRUCTURE_BINDING, str(exc), SEVERANCE_NOT_CLAIMED)


def validate_legacy_isolation_result(
    result: Mapping[str, Any],
    *,
    profile: Mapping[str, Any],
    evidence_root: Path,
    current_context: Mapping[str, Any],
    limits: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    _ = limits
    try:
        return _validate_legacy_isolation_result_core(
            deepcopy(result),
            profile=deepcopy(profile),
            evidence_root=Path(evidence_root),
            current_context=deepcopy(current_context),
        )
    except Exception as exc:
        return _tool_error(ARTIFACT_ISOLATION, SCOPE_STRUCTURE_EVIDENCE, str(exc), ISOLATION_NOT_CLAIMED)


def validate_legacy_isolation_result_bytes(
    data: bytes,
    *,
    profile: Mapping[str, Any],
    evidence_root: Path,
    current_context: Mapping[str, Any],
    limits: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    try:
        result = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return _result(
            artifact_type=ARTIFACT_ISOLATION,
            validation_status=STATUS_RERUN_REQUIRED,
            evaluation_scope=SCOPE_STRUCTURE_EVIDENCE,
            phase1_evaluation_completed=False,
            reason_codes=["NESIRA_PHASE1_MALFORMED_JSON"],
            blocking_items=["malformed JSON"],
            not_evaluated=["legacy isolation result"],
            not_claimed=ISOLATION_NOT_CLAIMED,
            checks=[_check("JSON_PARSE", "FAIL", "MALFORMED_JSON", details={"error": str(exc)})],
            rerun_required=True,
        )
    return validate_legacy_isolation_result(
        result,
        profile=profile,
        evidence_root=evidence_root,
        current_context=current_context,
        limits=limits,
    )


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _validate_severance_authorization_core(
    envelope: Mapping[str, Any],
    *,
    expected_context: Mapping[str, Any],
    now_utc: datetime,
) -> dict[str, Any]:
    if not isinstance(envelope, Mapping):
        return _rerun_severance("NESIRA_PHASE1_MALFORMED_DSSE_ENVELOPE", "malformed DSSE envelope")
    if envelope.get("payloadType") != DSSE_PAYLOAD_TYPE:
        return _rerun_severance("DSSE_PAYLOAD_TYPE_INVALID", "malformed DSSE envelope")
    payload_text = _decode_dsse_payload(envelope)
    if not isinstance(payload_text, str):
        return payload_text
    try:
        statement = json.loads(payload_text)
    except Exception as exc:
        return _rerun_severance(
            "DSSE_PAYLOAD_JSON_INVALID",
            "payload decode failure",
            details={"error": str(exc)},
        )
    schema_errors = _validate_severance_statement_shape(statement)
    if schema_errors:
        return _invalid_severance(
            "SEVERANCE_SCHEMA_INVALID",
            "schema violation",
            details={"violations": schema_errors},
        )
    predicate = statement["predicate"]
    if predicate.get("schema_version") != "1.0":
        return _rerun_severance("SEVERANCE_SCHEMA_VERSION_UNSUPPORTED", "unsupported schema version")
    missing_context = _missing_fields(
        expected_context,
        [
            "subject_sha256",
            "candidate_sha256",
            "legacy_dependency_id",
            "operation",
            "environment_id",
            "evidence_sha256",
            "policy_id",
            "source_commit",
            "state_version",
        ],
    )
    if missing_context:
        return _not_evaluated_severance(
            "SEVERANCE_EXPECTED_CONTEXT_MISSING",
            "missing expected context",
            details={"missing": missing_context},
        )
    context_mismatch = _first_context_mismatch(
        predicate,
        expected_context,
        [
            "subject_sha256",
            "candidate_sha256",
            "legacy_dependency_id",
            "operation",
            "environment_id",
            "evidence_sha256",
            "policy_id",
            "source_commit",
            "state_version",
        ],
    )
    if context_mismatch:
        field, expected, actual = context_mismatch
        return _rerun_severance(
            f"SEVERANCE_{field.upper()}_MISMATCH",
            "subject/context mismatch",
            details={"field": field, "expected": expected, "actual": actual},
        )
    temporal = _validate_temporal_binding(predicate, now_utc)
    if temporal is not None:
        return temporal
    return _result(
        artifact_type=ARTIFACT_SEVERANCE,
        validation_status=STATUS_VALID,
        evaluation_scope=SCOPE_STRUCTURE_BINDING,
        phase1_evaluation_completed=True,
        reason_codes=[
            "NESIRA_PHASE1_STRUCTURE_AND_BINDING_VALID",
            "NESIRA_PHASE1_SIGNATURE_TRUST_NOT_EVALUATED",
            "NESIRA_PHASE1_SIGNER_AUTHORITY_NOT_EVALUATED",
        ],
        blocking_items=[],
        not_evaluated=SEVERANCE_TRUST_NOT_EVALUATED,
        not_claimed=SEVERANCE_NOT_CLAIMED,
        subject_identity={"sha256": predicate["subject_sha256"]},
        context_identity={
            "candidate_sha256": predicate["candidate_sha256"],
            "environment_id": predicate["environment_id"],
            "policy_id": predicate["policy_id"],
        },
        evidence_references=[{"sha256": predicate["evidence_sha256"], "kind": "declared_evidence"}],
        checks=[_check("PHASE1_STRUCTURE_AND_BINDING", "PASS", "ALL_AUTHORIZED_PHASE1_CHECKS_PASSED")],
        decoded_payload_sha256=sha256_hex_bytes(payload_text.encode("utf-8")),
    )


def _decode_dsse_payload(envelope: Mapping[str, Any]) -> str | dict[str, Any]:
    payload = envelope.get("payload")
    if not isinstance(payload, str):
        return _rerun_severance("DSSE_PAYLOAD_MISSING", "malformed DSSE envelope")
    try:
        payload_bytes = base64.b64decode(payload.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        return _rerun_severance("DSSE_PAYLOAD_BASE64_INVALID", "payload decode failure", details={"error": str(exc)})
    try:
        return payload_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        return _rerun_severance("DSSE_PAYLOAD_UTF8_INVALID", "payload decode failure", details={"error": str(exc)})


def _validate_severance_statement_shape(statement: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(statement, Mapping):
        return ["statement must be object"]
    if statement.get("_type") != IN_TOTO_STATEMENT_TYPE:
        errors.append("_type")
    if statement.get("predicateType") != SEVERANCE_PREDICATE_TYPE:
        errors.append("predicateType")
    subjects = statement.get("subject")
    if not isinstance(subjects, list) or not subjects:
        errors.append("subject")
    else:
        digest = subjects[0].get("digest") if isinstance(subjects[0], Mapping) else None
        if not isinstance(digest, Mapping) or not _is_sha256(digest.get("sha256")):
            errors.append("subject.digest.sha256")
    predicate = statement.get("predicate")
    if not isinstance(predicate, Mapping):
        return errors + ["predicate"]
    required = [
        "schema_version",
        "subject_sha256",
        "candidate_sha256",
        "legacy_dependency_id",
        "operation",
        "environment_id",
        "evidence_sha256",
        "policy_id",
        "source_commit",
        "state_version",
        "issued_at",
        "expires_at",
    ]
    for field in required:
        if field not in predicate:
            errors.append(f"predicate.{field}")
    for field in ("subject_sha256", "candidate_sha256", "evidence_sha256"):
        if field in predicate and not _is_sha256(predicate[field]):
            errors.append(f"predicate.{field}")
    return errors


def _validate_temporal_binding(predicate: Mapping[str, Any], now_utc: datetime) -> dict[str, Any] | None:
    try:
        issued = _parse_utc(predicate["issued_at"])
        expires = _parse_utc(predicate["expires_at"])
    except Exception as exc:
        return _rerun_severance("SEVERANCE_TEMPORAL_BINDING_INVALID", "artifact must be regenerated", details={"error": str(exc)})
    if issued > now_utc:
        return _rerun_severance("SEVERANCE_ISSUED_AT_IN_FUTURE", "artifact must be regenerated")
    if expires <= now_utc:
        return _rerun_severance("SEVERANCE_EXPIRED", "artifact must be regenerated")
    return None


def _validate_legacy_isolation_result_core(
    result: Mapping[str, Any],
    *,
    profile: Mapping[str, Any],
    evidence_root: Path,
    current_context: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(result, Mapping):
        return _invalid_isolation("LEGACY_ISOLATION_RESULT_SCHEMA_INVALID", "schema violation")
    if result.get("schema") != LEGACY_ISOLATION_SCHEMA or result.get("schema_version") != "1.0":
        return _rerun_isolation("LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED", "unsupported schema version")
    schema_errors = _validate_isolation_shape(result)
    if schema_errors:
        return _invalid_isolation(
            "LEGACY_ISOLATION_RESULT_SCHEMA_INVALID",
            "schema violation",
            details={"violations": schema_errors},
        )
    context_mismatch = _first_context_mismatch(
        result,
        current_context,
        ["profile_id", "environment_id", "candidate_sha256", "legacy_dependency_id"],
    )
    if context_mismatch:
        field, expected, actual = context_mismatch
        return _rerun_isolation(
            f"LEGACY_ISOLATION_{field.upper()}_MISMATCH",
            "subject/context mismatch",
            details={"field": field, "expected": expected, "actual": actual},
        )
    if profile.get("profile_id") != result.get("profile_id"):
        return _rerun_isolation("LEGACY_ISOLATION_PROFILE_MISMATCH", "subject/context mismatch")
    if profile.get("schema_version") not in (None, "1.0"):
        return _rerun_isolation("LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED", "unsupported schema version")
    missing_context = _missing_fields(
        current_context,
        ["profile_id", "environment_id", "candidate_sha256", "legacy_dependency_id"],
    )
    if missing_context:
        return _not_evaluated_isolation(
            "LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING",
            "missing expected context",
            details={"missing": missing_context},
        )
    evidence_checks = _validate_evidence_manifest(result["evidence_manifest"], evidence_root)
    if evidence_checks is not None:
        return evidence_checks
    return _result(
        artifact_type=ARTIFACT_ISOLATION,
        validation_status=STATUS_VALID,
        evaluation_scope=SCOPE_STRUCTURE_EVIDENCE,
        phase1_evaluation_completed=True,
        reason_codes=[
            "NESIRA_PHASE1_STRUCTURE_AND_EVIDENCE_VALID",
            "NESIRA_PHASE1_ISOLATION_TRUST_NOT_EVALUATED",
        ],
        blocking_items=[],
        not_evaluated=ISOLATION_TRUST_NOT_EVALUATED,
        not_claimed=ISOLATION_NOT_CLAIMED,
        subject_identity={"candidate_sha256": result["candidate_sha256"]},
        context_identity={"environment_id": result["environment_id"], "profile_id": result["profile_id"]},
        evidence_references=[
            {"path": item["path"], "sha256": item["sha256"]} for item in result["evidence_manifest"]
        ],
        checks=[_check("PHASE1_STRUCTURE_AND_EVIDENCE", "PASS", "ALL_AUTHORIZED_PHASE1_CHECKS_PASSED")],
    )


def _validate_isolation_shape(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "schema",
        "schema_version",
        "profile_id",
        "environment_id",
        "candidate_sha256",
        "legacy_dependency_id",
        "evidence_manifest",
        "control_probes",
    ]
    for field in required:
        if field not in result:
            errors.append(field)
    for field in ("candidate_sha256",):
        if field in result and not _is_sha256(result[field]):
            errors.append(field)
    if "evidence_manifest" in result and not isinstance(result["evidence_manifest"], list):
        errors.append("evidence_manifest")
    if "control_probes" in result and not isinstance(result["control_probes"], list):
        errors.append("control_probes")
    return errors


def _validate_evidence_manifest(items: list[Any], evidence_root: Path) -> dict[str, Any] | None:
    root = evidence_root.resolve()
    seen_paths: set[str] = set()
    for item in items:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str) or not _is_sha256(item.get("sha256")):
            return _invalid_isolation("LEGACY_ISOLATION_EVIDENCE_SCHEMA_INVALID", "schema violation")
        relative = item["path"]
        normalized = _normalize_evidence_path(relative)
        unsafe = _unsafe_relative_path(relative, normalized)
        if unsafe:
            return _invalid_isolation(
                "LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH",
                "unsafe evidence path",
                details={"path": _safe_path_label(relative), "reason": unsafe},
            )
        path = root / normalized
        if not path.exists():
            return _not_evaluated_isolation(
                "LEGACY_ISOLATION_EVIDENCE_FILE_MISSING",
                "missing evidence file",
                details={"path": normalized},
            )
        try:
            resolved = path.resolve()
        except OSError as exc:
            return _tool_error(ARTIFACT_ISOLATION, SCOPE_STRUCTURE_EVIDENCE, exc, ISOLATION_NOT_CLAIMED)
        if not _is_within(resolved, root) or path.is_symlink():
            return _invalid_isolation(
                "LEGACY_ISOLATION_SYMLINK_ESCAPE",
                "symlink escape",
                details={"path": normalized},
            )
        if not path.is_file():
            return _invalid_isolation(
                "LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE",
                "evidence path is not a regular file",
                details={"path": normalized},
            )
        canonical = resolved.relative_to(root).as_posix()
        if canonical in seen_paths:
            return _invalid_isolation(
                "LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH",
                "duplicate evidence path",
                details={"path": canonical},
            )
        seen_paths.add(canonical)
        actual_hash = sha256_hex_bytes(path.read_bytes())
        if actual_hash != item["sha256"]:
            return _invalid_isolation(
                "LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH",
                "hash mismatch",
                details={"path": canonical, "expected": item["sha256"], "actual": actual_hash},
            )
    return None


def _normalize_evidence_path(path: str) -> str:
    return path.replace("\\", "/")


def _unsafe_relative_path(raw_path: str, normalized_path: str) -> str | None:
    if raw_path == "":
        return "empty evidence path"
    if raw_path.startswith(("/", "\\")):
        return "absolute evidence path"
    if normalized_path.startswith("//"):
        return "UNC or network evidence path"
    if re.match(r"^[A-Za-z]:", raw_path):
        return "drive-qualified evidence path"
    if re.match(r"^[A-Za-z]:", normalized_path):
        return "drive-qualified evidence path"
    path = PurePosixPath(normalized_path)
    if path.is_absolute():
        return "absolute evidence path"
    if any(part in ("..", "") for part in path.parts):
        return "traversal or empty path component"
    return None


def _safe_path_label(path: str) -> str:
    return _normalize_evidence_path(path).replace("\\", "/")


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _first_context_mismatch(
    actual: Mapping[str, Any],
    expected: Mapping[str, Any],
    fields: list[str],
) -> tuple[str, Any, Any] | None:
    for field in fields:
        if field in expected and actual.get(field) != expected.get(field):
            return field, expected.get(field), actual.get(field)
    return None


def _missing_fields(value: Mapping[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in value]


def _result(
    *,
    artifact_type: str,
    validation_status: str,
    evaluation_scope: str | None,
    phase1_evaluation_completed: bool,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
    not_claimed: list[str],
    checks: list[dict[str, Any]],
    recommended_agent_action: str | None = None,
    rerun_required: bool = False,
    subject_identity: Mapping[str, Any] | None = None,
    context_identity: Mapping[str, Any] | None = None,
    evidence_references: list[Mapping[str, Any]] | None = None,
    proof_references: list[Mapping[str, Any]] | None = None,
    tool_errors: list[Mapping[str, Any]] | None = None,
    decoded_payload_sha256: str | None = None,
) -> dict[str, Any]:
    action = recommended_agent_action or _action_for_status(validation_status)
    if action == "PROCEED":
        raise NesiraPhase1ValidatorToolError("Phase 1 validator attempted to return PROCEED")
    result = {
        "schema": RESULT_SCHEMA,
        "schema_version": RESULT_SCHEMA_VERSION,
        "artifact_type": artifact_type,
        "validation_status": validation_status,
        "phase1_evaluation_completed": bool(phase1_evaluation_completed),
        "evaluation_scope": evaluation_scope,
        "stop": True,
        "recommended_agent_action": action,
        "reason_codes": sorted(set(reason_codes)),
        "blocking_items": sorted(set(blocking_items)),
        "not_evaluated": sorted(set(not_evaluated)),
        "not_claimed": sorted(set(not_claimed)),
        "subject_identity": dict(subject_identity or {}),
        "context_identity": dict(context_identity or {}),
        "evidence_references": list(evidence_references or []),
        "proof_references": list(proof_references or []),
        "tool_errors": list(tool_errors or []),
        "checks": list(checks),
        "rerun_required": bool(rerun_required),
    }
    if decoded_payload_sha256 is not None:
        result["decoded_payload_sha256"] = decoded_payload_sha256
    return result


def _action_for_status(status: str) -> str:
    if status == STATUS_VALID:
        return ACTION_REPORT_NOT_EVALUATED
    if status == STATUS_INVALID:
        return ACTION_STOP_BLOCKED
    if status == STATUS_NOT_EVALUATED:
        return ACTION_REPORT_NOT_EVALUATED
    if status == STATUS_RERUN_REQUIRED:
        return ACTION_RERUN_REQUIRED
    if status == STATUS_TOOL_ERROR:
        return ACTION_STOP_BLOCKED
    raise NesiraPhase1ValidatorToolError(f"unsupported status: {status}")


def _invalid_severance(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_SEVERANCE,
        validation_status=STATUS_INVALID,
        evaluation_scope=SCOPE_STRUCTURE_BINDING,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[item],
        not_evaluated=SEVERANCE_TRUST_NOT_EVALUATED,
        not_claimed=SEVERANCE_NOT_CLAIMED,
        checks=[_check("SEVERANCE_VALIDATION", "FAIL", reason, details=details)],
    )


def _rerun_severance(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_SEVERANCE,
        validation_status=STATUS_RERUN_REQUIRED,
        evaluation_scope=SCOPE_STRUCTURE_BINDING,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[item],
        not_evaluated=SEVERANCE_TRUST_NOT_EVALUATED,
        not_claimed=SEVERANCE_NOT_CLAIMED,
        checks=[_check("SEVERANCE_VALIDATION", "FAIL", reason, details=details)],
        rerun_required=True,
    )


def _not_evaluated_severance(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_SEVERANCE,
        validation_status=STATUS_NOT_EVALUATED,
        evaluation_scope=SCOPE_STRUCTURE_BINDING,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[],
        not_evaluated=SEVERANCE_TRUST_NOT_EVALUATED + [item],
        not_claimed=SEVERANCE_NOT_CLAIMED,
        checks=[_check("SEVERANCE_VALIDATION", "FAIL", reason, details=details)],
    )


def _invalid_isolation(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_ISOLATION,
        validation_status=STATUS_INVALID,
        evaluation_scope=SCOPE_STRUCTURE_EVIDENCE,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[item],
        not_evaluated=ISOLATION_TRUST_NOT_EVALUATED,
        not_claimed=ISOLATION_NOT_CLAIMED,
        checks=[_check("LEGACY_ISOLATION_VALIDATION", "FAIL", reason, details=details)],
    )


def _not_evaluated_isolation(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_ISOLATION,
        validation_status=STATUS_NOT_EVALUATED,
        evaluation_scope=SCOPE_STRUCTURE_EVIDENCE,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[],
        not_evaluated=ISOLATION_TRUST_NOT_EVALUATED + [item],
        not_claimed=ISOLATION_NOT_CLAIMED,
        checks=[_check("LEGACY_ISOLATION_VALIDATION", "FAIL", reason, details=details)],
    )


def _rerun_isolation(reason: str, item: str, *, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _result(
        artifact_type=ARTIFACT_ISOLATION,
        validation_status=STATUS_RERUN_REQUIRED,
        evaluation_scope=SCOPE_STRUCTURE_EVIDENCE,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[item],
        not_evaluated=ISOLATION_TRUST_NOT_EVALUATED,
        not_claimed=ISOLATION_NOT_CLAIMED,
        checks=[_check("LEGACY_ISOLATION_VALIDATION", "FAIL", reason, details=details)],
        rerun_required=True,
    )


def _tool_error(artifact_type: str, scope: str, error: object, not_claimed: list[str]) -> dict[str, Any]:
    error_type = type(error).__name__ if not isinstance(error, str) else "RuntimeError"
    return _result(
        artifact_type=artifact_type,
        validation_status=STATUS_TOOL_ERROR,
        evaluation_scope=scope,
        phase1_evaluation_completed=False,
        reason_codes=["NESIRA_PHASE1_VALIDATOR_TOOL_ERROR"],
        blocking_items=["internal validator defect"],
        not_evaluated=["Phase 1 validator result unavailable due to tool error"],
        not_claimed=not_claimed,
        checks=[
            _check(
                "VALIDATOR_INTERNAL",
                "TOOL_ERROR",
                "NESIRA_PHASE1_VALIDATOR_TOOL_ERROR",
                details={"error": "internal validator defect", "error_type": error_type},
            )
        ],
        tool_errors=[{"error": "internal validator defect", "error_type": error_type}],
    )


def _check(
    check_id: str,
    status: str,
    reason_code: str,
    *,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"check_id": check_id, "status": status, "reason_code": reason_code}
    if details:
        item["details"] = dict(details)
    return item


def _parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("expected timestamp string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return _require_aware_utc(parsed)


def _require_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return value.astimezone(timezone.utc)


def _is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True
