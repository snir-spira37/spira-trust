from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


VALIDATOR_RESULT_SCHEMA = "SPIRA_DOMAIN2_ORACLE_VALIDATOR_RESULT"
VALIDATOR_RESULT_SCHEMA_VERSION = 1
VALIDATOR_SPEC = "SPIRA_DOMAIN2_ORACLE_VALIDATOR_SPEC_V1"
ORACLE_SCHEMA = "SPIRA_TEST_BUILD_FAILURE_ORACLE_V7"
ORACLE_SCHEMA_VERSION = 7
ORACLE_STATUS = "ORACLE_SCHEMA_V7_LOCKED"
SCOPE_TAG = "SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\0"
RESULT_TAG = "SPIRA_PYTEST_RESULT_IDENTITY_PROJECTION_V1\0"
COLLECTION_TAG = "SPIRA_PYTEST_COLLECTION_MANIFEST_V1\0"

NOT_AUTHORIZED = [
    "ORACLE_POPULATION",
    "VALIDATOR_IMPLEMENTATION_BEYOND_THIS_SPEC",
    "CORPUS_MATERIALIZATION",
    "PRODUCER_IMPLEMENTATION",
    "GATE_B",
    "DOMAIN_3",
]

FAIL_CHECKS = {
    "DUPLICATE_CASE_ID": "CASE_ID_UNIQUENESS",
    "RELATED_CASE_MISSING": "RELATED_CASE_ID_EXISTS",
    "SELF_RELATION_NOT_AUTHORIZED": "RELATED_CASE_ID_EXISTS",
    "ARRAY_NOT_CANONICALLY_SORTED": "CANONICAL_ARRAY_SORTING",
    "DUPLICATE_SET_MEMBER": "CANONICAL_ARRAY_SORTING",
    "PLUGIN_LIST_NOT_CANONICAL": "PLUGIN_CONTRACT_CANONICALIZED",
    "PROJECT_IDENTITY_NOT_CANONICAL": "PROJECT_IDENTITY_CANONICALIZED",
    "REPOSITORY_URL_NOT_CANONICAL": "PROJECT_IDENTITY_CANONICALIZED",
    "PROJECT_HASH_INVALID": "PROJECT_IDENTITY_CANONICALIZED",
    "SOURCE_REVISION_NOT_CANONICAL": "SOURCE_REVISION_CANONICALIZED",
    "DIRTY_TREE_WITH_GIT_COMMIT_ONLY": "SOURCE_REVISION_CANONICALIZED",
    "SOURCE_REVISION_DIGEST_INVALID": "SOURCE_REVISION_CANONICALIZED",
    "SELECTION_COMMAND_NOT_CANONICAL": "SELECTION_COMMAND_CANONICALIZED",
    "SHELL_COMMAND_STRING_NOT_ALLOWED": "SELECTION_COMMAND_CANONICALIZED",
    "PRIVATE_ABSOLUTE_PATH_NOT_ALLOWED": "SELECTION_COMMAND_CANONICALIZED",
    "UNRESOLVED_ENVIRONMENT_EXPANSION": "SELECTION_COMMAND_CANONICALIZED",
    "PYTHON_VERSION_CONTRACT_NOT_CANONICAL": "PYTHON_VERSION_CONTRACT_CANONICALIZED",
    "PYTEST_VERSION_NOT_CANONICAL": "PYTEST_VERSION_CANONICALIZED",
    "PLUGIN_CONTRACT_NOT_CANONICAL": "PLUGIN_CONTRACT_CANONICALIZED",
    "PLUGIN_DUPLICATE": "PLUGIN_CONTRACT_CANONICALIZED",
    "PLUGIN_LIST_UNSORTED": "PLUGIN_CONTRACT_CANONICALIZED",
    "UNKNOWN_ACTIVE_PLUGIN": "PLUGIN_CONTRACT_CANONICALIZED",
    "SCOPE_IDENTITY_HASH_MISMATCH": "SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION",
    "RESULT_SCOPE_IDENTITY_MISMATCH": "RESULT_SCOPE_IDENTITY_HASH_MATCHES_EXPECTED_SCOPE",
    "RESULT_IDENTITY_HASH_MISMATCH": "RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION",
    "COLLECTION_MANIFEST_HASH_MISMATCH": "COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST",
    "PROJECTION_BYTES_NOT_AVAILABLE": "SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION",
    "BLOCKING_LIST_MISMATCH": "RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS",
    "NONBLOCKING_LIST_MISMATCH": "RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS",
    "STRICT_LIST_CONTRACT_VIOLATION": "RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS",
    "RELATIONSHIP_NOT_SYMMETRIC": "IDENTITY_RELATIONSHIP_SYMMETRY",
    "RELATIONSHIP_CONFLICT": "IDENTITY_RELATIONSHIP_SYMMETRY",
    "DECLARED_DELTA_RELATIONSHIP_MISMATCH": "DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY",
    "DECLARED_DELTA_UNKNOWN_SOURCE": "DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY",
    "DECLARED_DELTA_INVALID_FIELD": "DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY",
    "DECLARED_DELTA_TOO_BROAD": "DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY",
    "ACTION_STOP_INCONSISTENT": "ACTION_STOP_CONSISTENCY",
    "DECISION_SEMANTICS_VERSION_INVALID": "ACTION_STOP_CONSISTENCY",
    "ASK_HUMAN_NOT_AUTHORIZED": "ACTION_STOP_CONSISTENCY",
    "PASSED_RESULT_HAS_BLOCKING_CASES": "PASSED_RESULT_HAS_NO_BLOCKING_CASES",
    "TIMEOUT_PROCESS_MISSING_TIMEOUT_FAILURE": "TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE",
    "FAILURE_CLASSES_NOT_DERIVED": "FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES",
    "TEST_TIMEOUT_RUN_TIMEOUT_CONFUSED": "FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES",
    "IDENTITY_BEARING_TEST_OUTCOME_DROPPED": "FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES",
    "NOT_EVALUATED_IDENTITY_HAS_HASH": "NOT_EVALUATED_RESULT_IDENTITY_HAS_NO_HASH",
    "NOT_EVALUATED_IDENTITY_HAS_PROJECTION": "NOT_EVALUATED_RESULT_IDENTITY_HAS_NO_PROJECTION",
    "NOT_EVALUATED_SCOPE_HAS_COLLECTION_IDENTITY": "NOT_EVALUATED_SCOPE_IDENTITY_HAS_NO_COLLECTION_HASH",
    "SCOPE_NOT_EVALUATED_RESULT_EMITTED": "SCOPE_NOT_EVALUATED_IMPLIES_RESULT_NOT_EVALUATED",
    "EMITTED_IDENTITY_WITH_INCOMPLETE_EVIDENCE": "EMITTED_RESULT_IDENTITY_REQUIRES_COMPLETE_EVIDENCE",
    "EMITTED_IDENTITY_WITH_INVALID_STATE": "EMITTED_RESULT_IDENTITY_REJECTS_INVALID_RESULT_STATES",
}


class OracleValidatorToolError(RuntimeError):
    """Raised when the validator itself cannot complete its work."""


def validate_oracle_bytes(data: bytes, *, input_path: str | Path | None = None) -> dict[str, Any]:
    try:
        document = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return _report(
            input_path=input_path,
            input_sha256=sha256(data).hexdigest(),
            errors=[_check("JSON_PARSE", "TOOL_ERROR", "JSON_PARSE_FAILED", details={"error": str(exc)})],
            tool_error=True,
        )
    return validate_oracle_document(document, input_path=input_path, input_bytes=data)


def validate_oracle_file(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    return validate_oracle_bytes(file_path.read_bytes(), input_path=file_path)


def validate_oracle_document(
    document: Mapping[str, Any],
    *,
    input_path: str | Path | None = None,
    input_bytes: bytes | None = None,
) -> dict[str, Any]:
    input_sha = sha256(input_bytes).hexdigest() if input_bytes is not None else sha256(
        canonical_json_bytes(document)
    ).hexdigest()
    errors: list[dict[str, Any]] = []
    try:
        errors.extend(_validate_schema_shape(document))
        cases = list(document.get("cases") or []) if isinstance(document.get("cases"), list) else []
        if not errors:
            errors.extend(_validate_case_ids(cases))
            errors.extend(_validate_cases(cases))
            errors.extend(_validate_relationships(cases))
    except Exception as exc:
        return _report(
            input_path=input_path,
            input_sha256=input_sha,
            errors=[_check("VALIDATOR_INTERNAL", "TOOL_ERROR", "ORACLE_VALIDATOR_EXCEPTION", details={"error": str(exc)})],
            tool_error=True,
        )
    return _report(input_path=input_path, input_sha256=input_sha, errors=errors, document=document)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(value: Any, *, tag: str = "") -> str:
    return sha256(tag.encode("utf-8") + canonical_json_bytes(value)).hexdigest()


def scope_identity_hash(scope_projection: Mapping[str, Any]) -> str:
    return sha256_hex(scope_projection, tag=SCOPE_TAG)


def result_identity_hash(result_projection: Mapping[str, Any]) -> str:
    return sha256_hex(result_projection, tag=RESULT_TAG)


def collection_manifest_hash(test_ids: list[str]) -> str:
    return sha256_hex(test_ids, tag=COLLECTION_TAG)


def _validate_schema_shape(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required = [
        "schema",
        "schema_version",
        "status",
        "methodology",
        "identity_model",
        "action_enum_policy",
        "scope_canonicalization_contract",
        "validator_requirements",
        "not_authorized",
        "cases",
    ]
    for field in required:
        if field not in document:
            errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_REQUIRED_FIELD_MISSING", details={"field": field}))
    if document.get("schema") != ORACLE_SCHEMA:
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_ID_INVALID"))
    if document.get("schema_version") != ORACLE_SCHEMA_VERSION:
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_VERSION_INVALID"))
    if document.get("status") != ORACLE_STATUS:
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_STATUS_INVALID"))
    if not isinstance(document.get("cases"), list):
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_CASES_NOT_ARRAY"))
    for blocked in ["ORACLE_POPULATION", "CORPUS_MATERIALIZATION", "PRODUCER_IMPLEMENTATION", "GATE_B", "DOMAIN_3"]:
        if blocked not in (document.get("not_authorized") or []):
            errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_NOT_AUTHORIZED_BOUNDARY_MISSING", details={"item": blocked}))
    return errors


def _validate_case_ids(cases: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    seen: set[str] = set()
    for case in cases:
        case_id = str(case.get("case_id", ""))
        if not case_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", case_id):
            errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_CASE_ID_INVALID", case_id=case_id or None))
            continue
        if case_id in seen:
            errors.append(_failure("DUPLICATE_CASE_ID", case_id=case_id))
        seen.add(case_id)
    known = seen
    for case in cases:
        case_id = str(case.get("case_id", ""))
        for relation in case.get("expected_identity_relationships") or []:
            related = relation.get("related_case_id")
            if related == case_id:
                errors.append(_failure("SELF_RELATION_NOT_AUTHORIZED", case_id=case_id))
            elif related not in known:
                errors.append(_failure("RELATED_CASE_MISSING", case_id=case_id, details={"related_case_id": related}))
    return errors


def _validate_cases(cases: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case.get("case_id", ""))
        errors.extend(_validate_required_case_shape(case))
        errors.extend(_validate_scope(case, case_id))
        errors.extend(_validate_result(case, case_id))
        errors.extend(_validate_policy_action(case, case_id))
        errors.extend(_validate_explicit_lists(case, case_id))
        errors.extend(_validate_semantics(case, case_id))
        errors.extend(_validate_deltas(case, case_id))
        errors.extend(_validate_claim_outcomes(case, case_id))
    return errors


def _validate_required_case_shape(case: Mapping[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    required = [
        "case_id",
        "case_schema_version",
        "input_sources",
        "expected_scope_identity",
        "expected_result_identity",
        "expected_policy_action",
        "expected_identity_relationships",
        "expected_explicit_lists",
    ]
    for field in required:
        if field not in case:
            errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_CASE_REQUIRED_FIELD_MISSING", case_id=str(case.get("case_id") or ""), details={"field": field}))
    return errors


def _validate_scope(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    scope = case.get("expected_scope_identity") or {}
    if scope.get("status") == "NOT_EVALUATED":
        if any(field in scope for field in ["scope_identity_sha256", "scope_projection", "scope_projection_sha256", "collection_manifest_sha256", "canonical_collected_test_ids"]):
            errors.append(_failure("NOT_EVALUATED_SCOPE_HAS_COLLECTION_IDENTITY", case_id=case_id))
        result = case.get("expected_result_identity") or {}
        if result.get("status") == "EMITTED":
            errors.append(_failure("SCOPE_NOT_EVALUATED_RESULT_EMITTED", case_id=case_id))
        return errors
    if scope.get("status") != "EMITTED":
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_SCOPE_STATUS_INVALID", case_id=case_id))
        return errors
    projection = scope.get("scope_projection")
    if projection is None:
        errors.append(_failure("PROJECTION_BYTES_NOT_AVAILABLE", case_id=case_id, details={"identity": "scope"}))
        return errors
    errors.extend(_validate_scope_projection(projection, case_id))
    expected_hash = scope_identity_hash(projection)
    if scope.get("scope_identity_sha256") != expected_hash:
        errors.append(_failure("SCOPE_IDENTITY_HASH_MISMATCH", case_id=case_id))
    if scope.get("scope_projection_sha256") and scope.get("scope_projection_sha256") != sha256_hex(projection):
        errors.append(_failure("SCOPE_IDENTITY_HASH_MISMATCH", case_id=case_id, details={"field": "scope_projection_sha256"}))
    ids = projection.get("canonical_collected_test_ids") or []
    if scope.get("collection_manifest_sha256") != collection_manifest_hash(ids):
        errors.append(_failure("COLLECTION_MANIFEST_HASH_MISMATCH", case_id=case_id))
    if scope.get("canonical_collected_test_ids") != ids:
        errors.append(_failure("COLLECTION_MANIFEST_HASH_MISMATCH", case_id=case_id, details={"field": "canonical_collected_test_ids"}))
    return errors


def _validate_scope_projection(projection: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    project = projection.get("project_identity") or {}
    kind = project.get("kind")
    value = str(project.get("value") or "")
    if kind == "repository_url":
        if not _is_canonical_repository_url(value):
            errors.append(_failure("REPOSITORY_URL_NOT_CANONICAL", case_id=case_id))
    elif kind == "package_name":
        if value != _pep503(value):
            errors.append(_failure("PROJECT_IDENTITY_NOT_CANONICAL", case_id=case_id))
    elif kind == "project_hash":
        if not _is_sha256(value):
            errors.append(_failure("PROJECT_HASH_INVALID", case_id=case_id))
    else:
        errors.append(_failure("PROJECT_IDENTITY_NOT_CANONICAL", case_id=case_id))

    revision = projection.get("source_revision") or {}
    rev_kind = revision.get("kind")
    rev_value = str(revision.get("value") or "")
    if rev_kind == "git_commit":
        if not re.fullmatch(r"([0-9a-f]{40}|[0-9a-f]{64})", rev_value):
            errors.append(_failure("SOURCE_REVISION_NOT_CANONICAL", case_id=case_id))
    elif rev_kind in {"source_archive_sha256", "working_tree_sha256"}:
        if not _is_sha256(rev_value):
            errors.append(_failure("SOURCE_REVISION_DIGEST_INVALID", case_id=case_id))
    else:
        errors.append(_failure("SOURCE_REVISION_NOT_CANONICAL", case_id=case_id))

    command = projection.get("normalized_selection_command")
    if not isinstance(command, list):
        errors.append(_failure("SHELL_COMMAND_STRING_NOT_ALLOWED", case_id=case_id))
    else:
        for part in command:
            if not isinstance(part, str) or not part:
                errors.append(_failure("SELECTION_COMMAND_NOT_CANONICAL", case_id=case_id))
            if isinstance(part, str) and (part.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", part)):
                errors.append(_failure("PRIVATE_ABSOLUTE_PATH_NOT_ALLOWED", case_id=case_id))
            if isinstance(part, str) and ("$" in part or "%" in part):
                errors.append(_failure("UNRESOLVED_ENVIRONMENT_EXPANSION", case_id=case_id))

    ids = projection.get("canonical_collected_test_ids") or []
    if len(ids) != len(set(ids)):
        errors.append(_failure("DUPLICATE_SET_MEMBER", case_id=case_id, details={"field": "canonical_collected_test_ids"}))
    elif ids != sorted(ids):
        errors.append(_failure("ARRAY_NOT_CANONICALLY_SORTED", case_id=case_id, details={"field": "canonical_collected_test_ids"}))
    py = projection.get("python_version_contract") or {}
    if py.get("implementation") not in {"cpython", "pypy"} or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+([+][A-Za-z0-9_.-]+)?", str(py.get("version") or "")):
        errors.append(_failure("PYTHON_VERSION_CONTRACT_NOT_CANONICAL", case_id=case_id))
    pytest = projection.get("pytest_version") or {}
    if pytest.get("package") != "pytest" or not re.fullmatch(r"[0-9]+([.][0-9]+)*([A-Za-z0-9_.!+-]+)?", str(pytest.get("version") or "")):
        errors.append(_failure("PYTEST_VERSION_NOT_CANONICAL", case_id=case_id))
    plugins = projection.get("relevant_plugin_contract") or []
    plugin_keys = [(p.get("normalized_name"), p.get("distribution_identity"), p.get("version")) for p in plugins]
    if plugin_keys != sorted(plugin_keys):
        errors.append(_failure("PLUGIN_LIST_UNSORTED", case_id=case_id))
    if len(plugin_keys) != len(set(plugin_keys)):
        errors.append(_failure("PLUGIN_DUPLICATE", case_id=case_id))
    for plugin in plugins:
        if plugin.get("normalized_name") != _pep503(str(plugin.get("normalized_name") or "")) or plugin.get("distribution_identity") != _pep503(str(plugin.get("distribution_identity") or "")) or not plugin.get("version"):
            errors.append(_failure("PLUGIN_CONTRACT_NOT_CANONICAL", case_id=case_id))
        if plugin.get("normalized_name") == "unknown-plugin":
            errors.append(_failure("UNKNOWN_ACTIVE_PLUGIN", case_id=case_id))
    return errors


def _validate_result(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    result = case.get("expected_result_identity") or {}
    if result.get("status") == "NOT_EVALUATED":
        if "result_identity_sha256" in result:
            errors.append(_failure("NOT_EVALUATED_IDENTITY_HAS_HASH", case_id=case_id))
        if "projection" in result:
            errors.append(_failure("NOT_EVALUATED_IDENTITY_HAS_PROJECTION", case_id=case_id))
        return errors
    if result.get("status") != "EMITTED":
        errors.append(_check("JSON_SCHEMA_V7_VALIDATION", "FAIL", "SCHEMA_RESULT_STATUS_INVALID", case_id=case_id))
        return errors
    projection = result.get("projection")
    if projection is None:
        errors.append(_failure("PROJECTION_BYTES_NOT_AVAILABLE", case_id=case_id, details={"identity": "result"}))
        return errors
    scope = case.get("expected_scope_identity") or {}
    if scope.get("status") != "EMITTED":
        errors.append(_failure("SCOPE_NOT_EVALUATED_RESULT_EMITTED", case_id=case_id))
    if projection.get("scope_identity_sha256") != scope.get("scope_identity_sha256"):
        errors.append(_failure("RESULT_SCOPE_IDENTITY_MISMATCH", case_id=case_id))
    if result.get("result_identity_sha256") != result_identity_hash(projection):
        errors.append(_failure("RESULT_IDENTITY_HASH_MISMATCH", case_id=case_id))
    if projection.get("evidence_completeness") != "COMPLETE":
        errors.append(_failure("EMITTED_IDENTITY_WITH_INCOMPLETE_EVIDENCE", case_id=case_id))
    if projection.get("process_state") == "NOT_EVALUATED" or projection.get("result_state") in {"NOT_EVALUATED", "CONFLICTING", "UNSUPPORTED"}:
        errors.append(_failure("EMITTED_IDENTITY_WITH_INVALID_STATE", case_id=case_id))
    return errors


def _validate_explicit_lists(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    result = case.get("expected_result_identity") or {}
    if result.get("status") == "NOT_EVALUATED":
        return errors
    projection = result.get("projection") or {}
    expected = case.get("expected_explicit_lists") or {}
    for field, code in [("blocking_cases", "BLOCKING_LIST_MISMATCH"), ("nonblocking_cases", "NONBLOCKING_LIST_MISMATCH")]:
        left = projection.get(field) or []
        right = expected.get(field) or []
        if left != right:
            errors.append(_failure(code, case_id=case_id))
        if left != _sorted_unique_objects(left):
            errors.append(_failure("STRICT_LIST_CONTRACT_VIOLATION", case_id=case_id, details={"field": field}))
    return errors


def _validate_policy_action(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    action = case.get("expected_policy_action") or {}
    errors: list[dict[str, Any]] = []
    if action.get("decision_semantics_version") != "SPIRA_DECISION_SEMANTICS_V2":
        errors.append(_failure("DECISION_SEMANTICS_VERSION_INVALID", case_id=case_id))
    recommended = action.get("recommended_agent_action")
    if recommended == "ASK_HUMAN":
        errors.append(_failure("ASK_HUMAN_NOT_AUTHORIZED", case_id=case_id))
    if action.get("stop") is False and recommended not in {"PROCEED", "REPORT_WITH_NOTES"}:
        errors.append(_failure("ACTION_STOP_INCONSISTENT", case_id=case_id))
    if action.get("stop") is True and recommended not in {"STOP_BLOCKED", "RERUN_REQUIRED", "REPORT_NOT_EVALUATED"}:
        errors.append(_failure("ACTION_STOP_INCONSISTENT", case_id=case_id))
    return errors


def _validate_semantics(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    result = case.get("expected_result_identity") or {}
    if result.get("status") == "NOT_EVALUATED":
        return errors
    projection = result.get("projection") or {}
    blocking = projection.get("blocking_cases") or []
    nonblocking = projection.get("nonblocking_cases") or []
    run_failures = projection.get("run_level_failures") or []
    if projection.get("result_state") == "PASSED" and blocking:
        errors.append(_failure("PASSED_RESULT_HAS_BLOCKING_CASES", case_id=case_id))
    if projection.get("process_state") == "TIMEOUT" and "TIMEOUT" not in run_failures:
        errors.append(_failure("TIMEOUT_PROCESS_MISSING_TIMEOUT_FAILURE", case_id=case_id))
    derived = sorted(
        {
            str(item.get("failure_class"))
            for item in blocking + nonblocking
            if item.get("failure_class")
        }
        | {str(item) for item in run_failures}
    )
    if sorted(projection.get("failure_classes") or []) != derived:
        errors.append(_failure("FAILURE_CLASSES_NOT_DERIVED", case_id=case_id))
    for item in blocking + nonblocking:
        if item.get("observed_outcome") in {"SKIPPED", "XFAILED", "XPASSED_NONBLOCKING", "XPASSED_BLOCKING"} and not item.get("reason_category"):
            errors.append(_failure("IDENTITY_BEARING_TEST_OUTCOME_DROPPED", case_id=case_id))
    return errors


def _validate_deltas(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    sources = {source.get("source_id") for source in case.get("input_sources") or []}
    allowed_fields = {
        "duration",
        "timestamp",
        "pid",
        "ansi_formatting",
        "whitespace",
        "temp_path",
        "traceback_formatting",
        "console_order",
        "stdout",
        "stderr",
    }
    for relation in case.get("expected_identity_relationships") or []:
        for delta in relation.get("declared_input_deltas") or []:
            if delta.get("source_id") not in sources:
                errors.append(_failure("DECLARED_DELTA_UNKNOWN_SOURCE", case_id=case_id))
            fields = delta.get("forbidden_semantic_fields") or []
            if any(str(field).lower() == "noise" for field in fields) or str(delta.get("description", "")).lower() == "noise":
                errors.append(_failure("DECLARED_DELTA_TOO_BROAD", case_id=case_id))
            if any(field not in allowed_fields for field in fields):
                errors.append(_failure("DECLARED_DELTA_INVALID_FIELD", case_id=case_id))
            if relation.get("result_identity_relation") == "SAME" and not fields:
                errors.append(_failure("DECLARED_DELTA_RELATIONSHIP_MISMATCH", case_id=case_id))
    return errors


def _validate_relationships(cases: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    by_id = {case.get("case_id"): case for case in cases}
    for case in cases:
        case_id = str(case.get("case_id", ""))
        for relation in case.get("expected_identity_relationships") or []:
            related_id = relation.get("related_case_id")
            related = by_id.get(related_id)
            if not related:
                continue
            reciprocal = None
            for candidate in related.get("expected_identity_relationships") or []:
                if candidate.get("related_case_id") == case_id:
                    reciprocal = candidate
                    break
            if reciprocal is None:
                errors.append(_failure("RELATIONSHIP_NOT_SYMMETRIC", case_id=case_id, details={"related_case_id": related_id}))
                continue
            for field in ["run_identity_relation", "scope_identity_relation", "result_identity_relation"]:
                if relation.get(field) != reciprocal.get(field):
                    errors.append(_failure("RELATIONSHIP_CONFLICT", case_id=case_id, details={"related_case_id": related_id, "field": field}))
    return errors


def _validate_claim_outcomes(case: Mapping[str, Any], case_id: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    claims = case.get("expected_claims") or []
    if claims != _sorted_unique_objects(claims, key_field="claim_id"):
        errors.append(_failure("ARRAY_NOT_CANONICALLY_SORTED", case_id=case_id, details={"field": "expected_claims"}))
    return errors


def _report(
    *,
    input_path: str | Path | None,
    input_sha256: str,
    errors: list[dict[str, Any]],
    document: Mapping[str, Any] | None = None,
    tool_error: bool = False,
) -> dict[str, Any]:
    checks = errors or [_check("ORACLE_VALIDATOR_ALL_CHECKS", "PASS")]
    verdict = "TOOL_ERROR" if tool_error else ("FAIL" if errors else "PASS")
    status = "ORACLE_VALIDATOR_TOOL_ERROR" if tool_error else ("ORACLE_VALIDATION_FAILED" if errors else "ORACLE_VALIDATION_PASS")
    cases = list(document.get("cases") or []) if document else []
    relationship_count = sum(len(case.get("expected_identity_relationships") or []) for case in cases)
    delta_count = sum(
        len(relation.get("declared_input_deltas") or [])
        for case in cases
        for relation in case.get("expected_identity_relationships") or []
    )
    return {
        "schema": VALIDATOR_RESULT_SCHEMA,
        "schema_version": VALIDATOR_RESULT_SCHEMA_VERSION,
        "validator_spec": VALIDATOR_SPEC,
        "oracle_schema": ORACLE_SCHEMA,
        "verdict": verdict,
        "status": status,
        "checked_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "input": {
            "path": _safe_path(input_path),
            "sha256": input_sha256,
        },
        "counts": {
            "case_count": len(cases),
            "relationship_count": relationship_count,
            "declared_delta_count": delta_count,
            "error_count": len(errors),
            "warning_count": 0,
        },
        "checks": checks,
        "not_authorized": NOT_AUTHORIZED,
    }


def _check(
    check_id: str,
    status: str,
    error_code: str | None = None,
    *,
    case_id: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "status": status,
        "error_code": error_code,
        "case_id": case_id,
        "details": dict(details or {}),
    }


def _failure(error_code: str, *, case_id: str | None = None, details: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _check(FAIL_CHECKS.get(error_code, "ORACLE_VALIDATOR_CHECK"), "FAIL", error_code, case_id=case_id, details=details)


def _safe_path(path: str | Path | None) -> str | None:
    if path is None:
        return None
    value = str(path).replace("\\", "/")
    if re.match(r"^[A-Za-z]:/", value) or value.startswith("/"):
        return Path(value).name
    return value


def _is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[0-9a-f]{64}", value))


def _pep503(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _is_canonical_repository_url(value: str) -> bool:
    if not re.fullmatch(r"https://[a-z0-9.-]+/[A-Za-z0-9._/-]+([.]git)?", value):
        return False
    if any(part in value for part in ["?", "#", "@", "%"]):
        return False
    if ":443/" in value:
        return False
    path = value.split("/", 3)[3]
    return "//" not in path and not path.endswith("/")


def _sorted_unique_objects(values: list[Any], *, key_field: str | None = None) -> list[Any]:
    if key_field:
        sorted_values = sorted(values, key=lambda item: (str(item.get(key_field, "")), canonical_json_bytes(item)))
    else:
        sorted_values = sorted(values, key=canonical_json_bytes)
    unique: list[Any] = []
    seen: set[bytes] = set()
    for value in sorted_values:
        encoded = canonical_json_bytes(value)
        if encoded not in seen:
            unique.append(value)
            seen.add(encoded)
    return unique
