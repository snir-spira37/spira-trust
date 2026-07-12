from __future__ import annotations

import copy
import json

from spira_core import test_build_failure_oracle_validator as validator


def test_valid_oracle_fixture_passes():
    document = _oracle()

    report = validator.validate_oracle_document(document)

    assert report["verdict"] == "PASS"
    assert report["status"] == "ORACLE_VALIDATION_PASS"
    assert report["counts"]["case_count"] == 1
    assert report["checks"][0]["status"] == "PASS"
    assert "ORACLE_POPULATION" in report["not_authorized"]


def test_validator_accepts_machine_readable_bytes_input():
    data = json.dumps(_oracle(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    report = validator.validate_oracle_bytes(data, input_path="fixtures/valid.json")

    assert report["verdict"] == "PASS"
    assert report["input"]["path"] == "fixtures/valid.json"
    assert len(report["input"]["sha256"]) == 64


def test_json_parse_failure_is_tool_error_not_oracle_finding():
    report = validator.validate_oracle_bytes(b"{")

    assert report["verdict"] == "TOOL_ERROR"
    assert report["status"] == "ORACLE_VALIDATOR_TOOL_ERROR"
    assert report["checks"][0]["error_code"] == "JSON_PARSE_FAILED"


def test_internal_exception_is_tool_error(monkeypatch):
    def boom(_cases):
        raise RuntimeError("boom")

    monkeypatch.setattr(validator, "_validate_cases", boom)

    report = validator.validate_oracle_document(_oracle())

    assert report["verdict"] == "TOOL_ERROR"
    assert report["status"] == "ORACLE_VALIDATOR_TOOL_ERROR"
    assert report["checks"][0]["error_code"] == "ORACLE_VALIDATOR_EXCEPTION"


def test_multiple_cases_with_symmetric_relationships_pass():
    document = _oracle()
    first = document["cases"][0]
    second = copy.deepcopy(first)
    second["case_id"] = "case_b"
    first["expected_identity_relationships"] = [
        _relationship("case_b", "DIFFERENT", "SAME", "SAME", with_delta=True)
    ]
    second["expected_identity_relationships"] = [
        _relationship("case_a", "DIFFERENT", "SAME", "SAME", with_delta=True)
    ]
    document["cases"].append(second)

    report = validator.validate_oracle_document(document)

    assert report["verdict"] == "PASS"
    assert report["counts"]["case_count"] == 2
    assert report["counts"]["relationship_count"] == 2


def test_not_evaluated_scope_implies_not_evaluated_result_passes():
    document = _oracle()
    case = document["cases"][0]
    case["expected_scope_identity"] = {
        "status": "NOT_EVALUATED",
        "collection_deterministic": False,
        "reason_codes": ["COLLECTION_NOT_DETERMINISTIC"],
    }
    case["expected_result_identity"] = {
        "status": "NOT_EVALUATED",
        "reason_codes": ["SCOPE_IDENTITY_NOT_EVALUATED"],
    }

    report = validator.validate_oracle_document(document)

    assert report["verdict"] == "PASS"


def test_report_with_notes_stop_false_passes():
    document = _oracle()
    document["cases"][0]["expected_policy_action"] = {
        "stop": False,
        "recommended_agent_action": "REPORT_WITH_NOTES",
        "reason_codes": ["TEST_NOTES"],
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
    }

    report = validator.validate_oracle_document(document)

    assert report["verdict"] == "PASS"


def test_negative_validator_fixtures_fail_with_expected_error_codes():
    cases = {
        "hash_only_scope_projection": (_hash_only_scope_projection, "PROJECTION_BYTES_NOT_AVAILABLE"),
        "hash_only_result_projection": (_hash_only_result_projection, "PROJECTION_BYTES_NOT_AVAILABLE"),
        "scope_hash_mismatch": (_scope_hash_mismatch, "SCOPE_IDENTITY_HASH_MISMATCH"),
        "result_hash_mismatch": (_result_hash_mismatch, "RESULT_IDENTITY_HASH_MISMATCH"),
        "collection_manifest_mismatch": (_collection_manifest_mismatch, "COLLECTION_MANIFEST_HASH_MISMATCH"),
        "duplicate_case_id": (_duplicate_case_id, "DUPLICATE_CASE_ID"),
        "missing_related_case": (_missing_related_case, "RELATED_CASE_MISSING"),
        "asymmetric_relationship": (_asymmetric_relationship, "RELATIONSHIP_NOT_SYMMETRIC"),
        "unsorted_canonical_array": (_unsorted_canonical_array, "ARRAY_NOT_CANONICALLY_SORTED"),
        "duplicate_set_member": (_duplicate_set_member, "DUPLICATE_SET_MEMBER"),
        "strict_list_mismatch": (_strict_list_mismatch, "BLOCKING_LIST_MISMATCH"),
        "invalid_declared_delta": (_invalid_declared_delta, "DECLARED_DELTA_INVALID_FIELD"),
        "stop_false_with_stop_blocked": (_stop_false_with_stop_blocked, "ACTION_STOP_INCONSISTENT"),
        "stop_true_with_proceed": (_stop_true_with_proceed, "ACTION_STOP_INCONSISTENT"),
        "passed_result_with_blocking": (_passed_result_with_blocking, "PASSED_RESULT_HAS_BLOCKING_CASES"),
        "timeout_without_run_failure": (_timeout_without_run_failure, "TIMEOUT_PROCESS_MISSING_TIMEOUT_FAILURE"),
        "failure_classes_not_derived": (_failure_classes_not_derived, "FAILURE_CLASSES_NOT_DERIVED"),
        "ambiguous_repository_url": (_ambiguous_repository_url, "REPOSITORY_URL_NOT_CANONICAL"),
        "shell_command_string": (_shell_command_string, "SHELL_COMMAND_STRING_NOT_ALLOWED"),
        "dirty_revision_as_git_commit": (_dirty_revision_as_git_commit, "SOURCE_REVISION_NOT_CANONICAL"),
        "unknown_plugin": (_unknown_plugin, "UNKNOWN_ACTIVE_PLUGIN"),
        "duplicate_plugin": (_duplicate_plugin, "PLUGIN_DUPLICATE"),
        "not_evaluated_identity_with_hash": (_not_evaluated_identity_with_hash, "NOT_EVALUATED_IDENTITY_HAS_HASH"),
        "not_evaluated_identity_with_projection": (
            _not_evaluated_identity_with_projection,
            "NOT_EVALUATED_IDENTITY_HAS_PROJECTION",
        ),
        "emitted_identity_incomplete_evidence": (
            _emitted_identity_incomplete_evidence,
            "EMITTED_IDENTITY_WITH_INCOMPLETE_EVIDENCE",
        ),
    }

    for name, (mutate, expected) in cases.items():
        document = _oracle()
        mutate(document)

        report = validator.validate_oracle_document(document)

        assert report["verdict"] == "FAIL", name
        assert report["status"] == "ORACLE_VALIDATION_FAILED", name
        assert expected in _error_codes(report), name


def _oracle():
    case = _case("case_a")
    return {
        "schema": "SPIRA_TEST_BUILD_FAILURE_ORACLE_V7",
        "schema_version": 7,
        "status": "ORACLE_SCHEMA_V7_LOCKED",
        "methodology": {
            "methodology_document": "research/test_build_failure_contract_methodology.md",
            "identity_model_document": "research/test_build_failure_contract_dual_identity_model_v2.md",
            "identity_model_review_document": "research/test_build_failure_contract_dual_identity_model_v2_review.md",
            "schema_v1_review_document": "research/test_build_failure_contract_oracle_schema_v1_review.md",
            "schema_v2_review_document": "research/test_build_failure_contract_oracle_schema_v2_review.md",
            "schema_v3_review_document": "research/test_build_failure_contract_oracle_schema_v3_review.md",
            "schema_v4_review_document": "research/test_build_failure_contract_oracle_schema_v4_review.md",
            "schema_v5_review_document": "research/test_build_failure_contract_oracle_schema_v5_review.md",
            "schema_v6_review_document": "research/test_build_failure_contract_oracle_schema_v6_review.md",
            "domain_slice": "Python pytest test-run evidence",
        },
        "identity_model": {
            "run_identity": "CONTEXTUAL",
            "result_identity": "POLICY_INDEPENDENT",
            "scope_identity_precondition": "REQUIRED_BEFORE_RESULT_IDENTITY",
            "policy_action_binding": "OUTSIDE_RESULT_IDENTITY",
        },
        "action_enum_policy": {
            "policy": "FROZEN_AGENT_ACTION_SUBSET_FOR_DOMAIN_2_ORACLE_V7",
            "included_actions": ["PROCEED", "STOP_BLOCKED", "RERUN_REQUIRED", "REPORT_NOT_EVALUATED", "REPORT_WITH_NOTES"],
            "excluded_actions": ["ASK_HUMAN"],
            "rationale": "Domain 2 oracle V7 uses the frozen deterministic gate actions.",
        },
        "scope_canonicalization_contract": {
            "schema": "SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1",
            "schema_version": 1,
            "encoding": "UTF-8",
            "json_canonicalization": "sorted object keys, no insignificant whitespace, arrays in schema-defined canonical order",
            "project_identity": {},
            "source_revision": {},
            "normalized_selection_command": {},
            "python_version_contract": {},
            "pytest_version": {},
            "relevant_plugin_contract": {},
            "scope_projection_hash": "scope_identity_sha256 is SHA256(tag + canonical_json(scope_identity_projection))",
        },
        "validator_requirements": {
            "schema_enforced": [],
            "validator_enforced_before_oracle_population": [],
            "not_required": [],
        },
        "not_authorized": [
            "PRODUCER_IMPLEMENTATION",
            "PYTEST_ADAPTER",
            "ORACLE_POPULATION",
            "CORPUS_MATERIALIZATION",
            "GATE_B",
            "DOMAIN_3",
            "RELEASE_VERSION_TAG_PYPI",
        ],
        "cases": [case],
    }


def _case(case_id):
    test_ids = [
        "tests/test_alpha.py::test_fail",
        "tests/test_alpha.py::test_skip",
    ]
    collection_hash = validator.collection_manifest_hash(test_ids)
    scope_projection = {
        "schema": "SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1",
        "schema_version": 1,
        "canonicalization_contract": "SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1",
        "project_identity": {
            "kind": "repository_url",
            "value": "https://github.com/example/project.git",
        },
        "source_revision": {
            "kind": "git_commit",
            "value": "a" * 40,
        },
        "normalized_selection_command": ["pytest", "-q", "tests"],
        "collection_manifest_sha256": collection_hash,
        "canonical_collected_test_ids": test_ids,
        "python_version_contract": {
            "implementation": "cpython",
            "version": "3.12.4",
            "abi_tag": "cp312",
        },
        "pytest_version": {
            "package": "pytest",
            "version": "8.3.2",
        },
        "relevant_plugin_contract": [
            {
                "normalized_name": "pytest-timeout",
                "version": "2.3.1",
                "distribution_identity": "pytest-timeout",
            }
        ],
        "collection_contract_version": "SPIRA_PYTEST_COLLECTION_MANIFEST_V1",
    }
    scope_hash = validator.scope_identity_hash(scope_projection)
    blocking = [
        {
            "test_id": "tests/test_alpha.py::test_fail",
            "observed_outcome": "FAILED",
            "failure_class": "ASSERTION_FAILURE",
            "rerun_target": "tests/test_alpha.py::test_fail",
        }
    ]
    nonblocking = [
        {
            "test_id": "tests/test_alpha.py::test_skip",
            "observed_outcome": "SKIPPED",
            "reason_category": "requires network",
            "rerun_target": "tests/test_alpha.py::test_skip",
        }
    ]
    result_projection = {
        "scope_identity_sha256": scope_hash,
        "process_state": "COMPLETED",
        "result_state": "FAILED",
        "blocking_cases": blocking,
        "nonblocking_cases": nonblocking,
        "failure_classes": ["ASSERTION_FAILURE"],
        "run_level_failures": [],
        "evidence_completeness": "COMPLETE",
    }
    return {
        "case_id": case_id,
        "case_schema_version": 2,
        "review_class": "AUTHOR_REVIEW",
        "review_status": "REVIEWED",
        "input_manifest_sha256": "b" * 64,
        "input_sources": [
            {
                "source_id": "stdout",
                "media_type": "text/plain",
                "sha256": "c" * 64,
                "byte_length": 100,
                "capture_complete": True,
                "source_state": "PRESENT_COMPLETE",
            }
        ],
        "supported_input": True,
        "expected_source_sufficiency": {"stdout": "ANSWERED"},
        "expected_scope_identity": {
            "status": "EMITTED",
            "collection_deterministic": True,
            "scope_identity_sha256": scope_hash,
            "scope_projection": scope_projection,
            "scope_projection_sha256": validator.sha256_hex(scope_projection),
            "collection_manifest_sha256": collection_hash,
            "canonical_collected_test_ids": test_ids,
        },
        "expected_result_identity": {
            "status": "EMITTED",
            "result_identity_sha256": validator.result_identity_hash(result_projection),
            "projection": result_projection,
        },
        "expected_policy_action": {
            "stop": True,
            "recommended_agent_action": "STOP_BLOCKED",
            "reason_codes": ["TEST_FAILURE"],
            "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        },
        "expected_identity_relationships": [],
        "expected_claims": [
            {
                "claim_id": "pytest.result.failed",
                "claim_type": "pytest_result",
                "status": "BLOCK",
                "value": {"failed": True},
                "reason_codes": ["TEST_FAILURE"],
            }
        ],
        "expected_explicit_lists": {
            "blocking_cases": blocking,
            "nonblocking_cases": nonblocking,
        },
        "expected_not_evaluated": [],
        "expected_not_claimed": ["safety"],
        "expected_evidence_locators": [
            {
                "source_id": "stdout",
                "locator_type": "line_span",
                "locator": "1-5",
            }
        ],
    }


def _relationship(related, run, scope, result, *, with_delta=False):
    relation = {
        "related_case_id": related,
        "run_identity_relation": run,
        "scope_identity_relation": scope,
        "result_identity_relation": result,
    }
    if with_delta:
        relation["declared_input_deltas"] = [
            {
                "source_id": "stdout",
                "delta_type": "DURATION_CHANGED",
                "description": "duration changed only",
                "forbidden_semantic_fields": ["duration"],
            }
        ]
    return relation


def _error_codes(report):
    return {check["error_code"] for check in report["checks"]}


def _first_case(document):
    return document["cases"][0]


def _scope(document):
    return _first_case(document)["expected_scope_identity"]


def _scope_projection(document):
    return _scope(document)["scope_projection"]


def _result(document):
    return _first_case(document)["expected_result_identity"]


def _result_projection(document):
    return _result(document)["projection"]


def _hash_only_scope_projection(document):
    scope = _scope(document)
    del scope["scope_projection"]


def _hash_only_result_projection(document):
    result = _result(document)
    del result["projection"]


def _scope_hash_mismatch(document):
    _scope(document)["scope_identity_sha256"] = "0" * 64


def _result_hash_mismatch(document):
    _result(document)["result_identity_sha256"] = "0" * 64


def _collection_manifest_mismatch(document):
    _scope(document)["collection_manifest_sha256"] = "0" * 64


def _duplicate_case_id(document):
    document["cases"].append(copy.deepcopy(document["cases"][0]))


def _missing_related_case(document):
    _first_case(document)["expected_identity_relationships"] = [_relationship("missing", "SAME", "SAME", "SAME")]


def _asymmetric_relationship(document):
    second = copy.deepcopy(_first_case(document))
    second["case_id"] = "case_b"
    _first_case(document)["expected_identity_relationships"] = [_relationship("case_b", "SAME", "SAME", "SAME")]
    document["cases"].append(second)


def _unsorted_canonical_array(document):
    _scope_projection(document)["canonical_collected_test_ids"] = list(reversed(_scope_projection(document)["canonical_collected_test_ids"]))


def _duplicate_set_member(document):
    ids = _scope_projection(document)["canonical_collected_test_ids"]
    _scope_projection(document)["canonical_collected_test_ids"] = [ids[0], ids[0]]


def _strict_list_mismatch(document):
    _first_case(document)["expected_explicit_lists"]["blocking_cases"] = []


def _invalid_declared_delta(document):
    second = copy.deepcopy(_first_case(document))
    second["case_id"] = "case_b"
    _first_case(document)["expected_identity_relationships"] = [
        {
            "related_case_id": "case_b",
            "run_identity_relation": "DIFFERENT",
            "scope_identity_relation": "SAME",
            "result_identity_relation": "SAME",
            "declared_input_deltas": [
                {
                    "source_id": "stdout",
                    "delta_type": "DURATION_CHANGED",
                    "description": "bad field",
                    "forbidden_semantic_fields": ["result_state"],
                }
            ],
        }
    ]
    second["expected_identity_relationships"] = [_relationship("case_a", "DIFFERENT", "SAME", "SAME", with_delta=True)]
    document["cases"].append(second)


def _stop_false_with_stop_blocked(document):
    _first_case(document)["expected_policy_action"]["stop"] = False


def _stop_true_with_proceed(document):
    _first_case(document)["expected_policy_action"]["recommended_agent_action"] = "PROCEED"


def _passed_result_with_blocking(document):
    _result_projection(document)["result_state"] = "PASSED"


def _timeout_without_run_failure(document):
    _result_projection(document)["process_state"] = "TIMEOUT"


def _failure_classes_not_derived(document):
    _result_projection(document)["failure_classes"] = []


def _ambiguous_repository_url(document):
    _scope_projection(document)["project_identity"]["value"] = "https://github.com/example/project.git?ref=main"


def _shell_command_string(document):
    _scope_projection(document)["normalized_selection_command"] = "pytest -q tests"


def _dirty_revision_as_git_commit(document):
    _scope_projection(document)["source_revision"]["value"] = "main"


def _unknown_plugin(document):
    _scope_projection(document)["relevant_plugin_contract"][0]["normalized_name"] = "unknown-plugin"


def _duplicate_plugin(document):
    plugins = _scope_projection(document)["relevant_plugin_contract"]
    plugins.append(copy.deepcopy(plugins[0]))


def _not_evaluated_identity_with_hash(document):
    result = _result(document)
    result.clear()
    result.update(
        {
            "status": "NOT_EVALUATED",
            "result_identity_sha256": "1" * 64,
            "reason_codes": ["TEST_RESULT_EVIDENCE_INCOMPLETE"],
        }
    )


def _not_evaluated_identity_with_projection(document):
    result = _result(document)
    projection = result["projection"]
    result.clear()
    result.update(
        {
            "status": "NOT_EVALUATED",
            "projection": projection,
            "reason_codes": ["TEST_RESULT_EVIDENCE_INCOMPLETE"],
        }
    )


def _emitted_identity_incomplete_evidence(document):
    _result_projection(document)["evidence_completeness"] = "INCOMPLETE"
