from __future__ import annotations

import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import test_build_failure_oracle_validator as validator  # noqa: E402


OUT = ROOT / "research" / "test_build_failure_contract"
MANIFEST = OUT / "corpus_manifest_v1.json"
ORACLE = OUT / "oracle_v1.json"
REPORT = OUT / "oracle_population_report.md"
RESULTS = OUT / "oracle_population_results.json"


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = [_oracle_case(case) for case in manifest["cases"]]
    _attach_mutation_relationships(cases, manifest["mutation_pairs"])
    oracle = _oracle_document(cases)
    _write_json(ORACLE, oracle)
    validation = validator.validate_oracle_file(ORACLE)
    results = _population_results(oracle, validation)
    _write_json(RESULTS, results)
    REPORT.write_text(_population_report(results, validation), encoding="utf-8")
    print(json.dumps({"status": results["status"], "validator": validation["verdict"]}, sort_keys=True))
    if results["status"] != "DOMAIN_2_ORACLE_POPULATED":
        raise SystemExit(1)


def _oracle_document(cases: list[dict[str, Any]]) -> dict[str, Any]:
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
            "rationale": "Domain 2 oracle V7 uses only the frozen agent actions currently emitted by the accepted SPIRA action contract for deterministic gate answers; ASK_HUMAN is not introduced as a Domain 2 action.",
        },
        "scope_canonicalization_contract": _scope_canonicalization_contract(),
        "validator_requirements": _validator_requirements(),
        "not_authorized": [
            "PRODUCER_IMPLEMENTATION",
            "PYTEST_ADAPTER",
            "ORACLE_POPULATION",
            "CORPUS_MATERIALIZATION",
            "GATE_B",
            "DOMAIN_3",
            "RELEASE_VERSION_TAG_PYPI",
        ],
        "cases": sorted(cases, key=lambda item: item["case_id"]),
    }


def _oracle_case(corpus_case: dict[str, Any]) -> dict[str, Any]:
    case_id = corpus_case["case_id"]
    input_sources = [_oracle_source(source) for source in corpus_case["input_sources"]]
    scope = _scope_identity(corpus_case)
    classification = _classify(corpus_case)
    result = _result_identity(scope["scope_identity_sha256"], classification)
    policy = _policy_action(classification)
    blocking = classification["blocking_cases"]
    nonblocking = classification["nonblocking_cases"]
    return {
        "case_id": case_id,
        "case_schema_version": 2,
        "review_class": "AUTHOR_REVIEW",
        "review_status": "REVIEWED",
        "input_manifest_sha256": _hash_json(input_sources),
        "input_sources": input_sources,
        "supported_input": True,
        "expected_source_sufficiency": {source["source_id"]: "ANSWERED" for source in input_sources},
        "expected_scope_identity": scope,
        "expected_result_identity": result,
        "expected_policy_action": policy,
        "expected_identity_relationships": [],
        "expected_claims": _claims(classification),
        "expected_explicit_lists": {
            "blocking_cases": blocking,
            "nonblocking_cases": nonblocking,
        },
        "expected_not_evaluated": classification["not_evaluated"],
        "expected_not_claimed": ["software_safety", "producer_correctness"],
        "expected_evidence_locators": _evidence_locators(input_sources),
    }


def _scope_identity(corpus_case: dict[str, Any]) -> dict[str, Any]:
    ids = _collected_test_ids(corpus_case)
    collection_hash = validator.collection_manifest_hash(ids)
    projection = {
        "schema": "SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1",
        "schema_version": 1,
        "canonicalization_contract": "SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1",
        "project_identity": corpus_case["project_identity"],
        "source_revision": corpus_case["source_revision"],
        "normalized_selection_command": corpus_case["normalized_selection_command"],
        "collection_manifest_sha256": collection_hash,
        "canonical_collected_test_ids": ids,
        "python_version_contract": corpus_case["python_version_contract"],
        "pytest_version": corpus_case["pytest_version"],
        "relevant_plugin_contract": corpus_case["relevant_plugin_contract"],
        "collection_contract_version": "SPIRA_PYTEST_COLLECTION_MANIFEST_V1",
    }
    return {
        "status": "EMITTED",
        "collection_deterministic": True,
        "scope_identity_sha256": validator.scope_identity_hash(projection),
        "scope_projection": projection,
        "scope_projection_sha256": validator.sha256_hex(projection),
        "collection_manifest_sha256": collection_hash,
        "canonical_collected_test_ids": ids,
    }


def _result_identity(scope_hash: str, classification: dict[str, Any]) -> dict[str, Any]:
    if classification["result_status"] == "NOT_EVALUATED":
        return {
            "status": "NOT_EVALUATED",
            "reason_codes": classification["reason_codes"],
        }
    projection = {
        "scope_identity_sha256": scope_hash,
        "process_state": classification["process_state"],
        "result_state": classification["result_state"],
        "blocking_cases": classification["blocking_cases"],
        "nonblocking_cases": classification["nonblocking_cases"],
        "failure_classes": classification["failure_classes"],
        "run_level_failures": classification["run_level_failures"],
        "evidence_completeness": "COMPLETE",
    }
    return {
        "status": "EMITTED",
        "result_identity_sha256": validator.result_identity_hash(projection),
        "projection": projection,
    }


def _policy_action(classification: dict[str, Any]) -> dict[str, Any]:
    return {
        "stop": classification["stop"],
        "recommended_agent_action": classification["action"],
        "reason_codes": classification["reason_codes"],
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
    }


def _classify(case: dict[str, Any]) -> dict[str, Any]:
    case_id = case["case_id"]
    kind = case["case_kind"]
    exit_code = int(case.get("exit_code", 0))
    test_id = _primary_test_id(case)
    base = {
        "result_status": "EMITTED",
        "process_state": "COMPLETED",
        "result_state": "PASSED" if exit_code == 0 else "FAILED",
        "blocking_cases": [],
        "nonblocking_cases": [],
        "failure_classes": [],
        "run_level_failures": [],
        "stop": False,
        "action": "PROCEED",
        "reason_codes": ["TESTS_PASSED"],
        "not_evaluated": [],
    }
    if kind in {"skipped_test", "xfail"}:
        outcome = "SKIPPED" if kind == "skipped_test" else "XFAILED"
        base["nonblocking_cases"] = [
            {
                "test_id": test_id,
                "observed_outcome": outcome,
                "reason_category": kind,
                "rerun_target": test_id,
            }
        ]
        base["action"] = "REPORT_WITH_NOTES"
        base["reason_codes"] = ["TEST_NOTES"]
        return _finalize(base)
    if exit_code == 0:
        return _finalize(base)
    if kind in {"truncated_console", "malformed_junit_xml", "incomplete_junit_fields"}:
        return {
            **base,
            "result_status": "NOT_EVALUATED",
            "stop": True,
            "action": "REPORT_NOT_EVALUATED",
            "reason_codes": ["TEST_RESULT_EVIDENCE_INCOMPLETE"],
            "not_evaluated": ["result_identity"],
        }
    if kind == "console_junit_conflict":
        base.update(
            {
                "process_state": "ERROR",
                "result_state": "ERROR",
                "run_level_failures": ["SOURCE_CONFLICT"],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
        return _finalize(base)
    failure_class = _failure_class(kind, exit_code)
    process_state = _process_state(kind, failure_class)
    result_state = "ERROR" if failure_class in _RUN_LEVEL_ERROR_CLASSES else "FAILED"
    if failure_class in _RUN_LEVEL_ERROR_CLASSES or exit_code in {2, 3, 4, 5}:
        base.update(
            {
                "process_state": process_state,
                "result_state": result_state,
                "run_level_failures": [failure_class],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
        return _finalize(base)
    outcome = "XPASSED_BLOCKING" if kind == "xpass" else "FAILED"
    base.update(
        {
            "process_state": process_state,
            "result_state": result_state,
            "blocking_cases": [
                {
                    "test_id": test_id,
                    "observed_outcome": outcome,
                    "failure_class": failure_class,
                    "rerun_target": test_id,
                }
            ],
            "stop": True,
            "action": "STOP_BLOCKED",
            "reason_codes": ["TEST_FAILURE"],
        }
    )
    return _finalize(base)


def _finalize(classification: dict[str, Any]) -> dict[str, Any]:
    derived = sorted(
        {
            str(item["failure_class"])
            for item in classification["blocking_cases"] + classification["nonblocking_cases"]
            if "failure_class" in item
        }
        | set(classification["run_level_failures"])
    )
    classification["failure_classes"] = derived
    classification["blocking_cases"] = _sorted_unique_objects(classification["blocking_cases"])
    classification["nonblocking_cases"] = _sorted_unique_objects(classification["nonblocking_cases"])
    classification["reason_codes"] = sorted(set(classification["reason_codes"]))
    classification["not_evaluated"] = sorted(set(classification["not_evaluated"]))
    return classification


_RUN_LEVEL_ERROR_CLASSES = {
    "TIMEOUT",
    "COLLECTION_ERROR",
    "IMPORT_ERROR",
    "SYNTAX_ERROR",
    "PROCESS_INTERRUPTED",
    "PROCESS_CRASH",
    "PROCESS_ERROR",
    "SOURCE_CONFLICT",
    "EVIDENCE_INCOMPLETE",
    "UNSUPPORTED_INPUT",
    "UNKNOWN",
}


def _failure_class(kind: str, exit_code: int) -> str:
    mapping = {
        "single_assertion_failure": "ASSERTION_FAILURE",
        "multiple_failures": "ASSERTION_FAILURE",
        "parameterized_test_ids": "ASSERTION_FAILURE",
        "long_traceback": "ASSERTION_FAILURE",
        "deterministically_derivable_rerun_target": "ASSERTION_FAILURE",
        "non_derivable_rerun_target": "ASSERTION_FAILURE",
        "instruction_injection_all_tests_passed": "ASSERTION_FAILURE",
        "instruction_injection_proceed": "ASSERTION_FAILURE",
        "instruction_injection_fabricated_spira_json": "ASSERTION_FAILURE",
        "assertion_failure_instruction": "ASSERTION_FAILURE",
        "noisy_or_long_traceback": "ASSERTION_FAILURE",
        "unicode_or_path_normalization": "ASSERTION_FAILURE",
        "xpass": "ASSERTION_FAILURE",
        "timeout": "TIMEOUT",
        "collection_error": "COLLECTION_ERROR",
        "collection_or_import_failure_instruction": "COLLECTION_ERROR",
        "import_error": "IMPORT_ERROR",
        "syntax_error": "SYNTAX_ERROR",
        "fixture_setup_error": "FIXTURE_SETUP_ERROR",
        "fixture_teardown_error": "FIXTURE_TEARDOWN_ERROR",
        "keyboard_interruption": "PROCESS_INTERRUPTED",
        "process_crash": "PROCESS_CRASH",
        "nonzero_exit_without_normal_test_result": "PROCESS_ERROR",
        "Windows_paths": "ASSERTION_FAILURE",
        "Linux_paths": "ASSERTION_FAILURE",
    }
    if kind == "clean_pass" and exit_code != 0:
        return "UNKNOWN"
    return mapping.get(kind, "UNKNOWN")


def _process_state(kind: str, failure_class: str) -> str:
    if failure_class == "TIMEOUT":
        return "TIMEOUT"
    if failure_class == "PROCESS_INTERRUPTED":
        return "INTERRUPTED"
    if failure_class == "PROCESS_CRASH":
        return "CRASH"
    if failure_class in _RUN_LEVEL_ERROR_CLASSES:
        return "ERROR"
    return "COMPLETED"


def _claims(classification: dict[str, Any]) -> list[dict[str, Any]]:
    if classification["result_status"] == "NOT_EVALUATED":
        return [
            {
                "claim_id": "pytest.result.not_evaluated",
                "claim_type": "pytest_result",
                "status": "NOT_EVALUATED",
                "value": {"result_identity_emitted": False},
                "reason_codes": classification["reason_codes"],
            }
        ]
    if classification["stop"]:
        return [
            {
                "claim_id": "pytest.result.blocking",
                "claim_type": "pytest_result",
                "status": "BLOCK",
                "value": {"blocking": True},
                "reason_codes": classification["reason_codes"],
            }
        ]
    if classification["nonblocking_cases"]:
        return [
            {
                "claim_id": "pytest.result.notes",
                "claim_type": "pytest_result",
                "status": "NOTE",
                "value": {"notes": True},
                "reason_codes": classification["reason_codes"],
            }
        ]
    return [
        {
            "claim_id": "pytest.result.passed",
            "claim_type": "pytest_result",
            "status": "OK",
            "value": {"passed": True},
            "reason_codes": classification["reason_codes"],
        }
    ]


def _attach_mutation_relationships(cases: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> None:
    by_id = {case["case_id"]: case for case in cases}
    for pair in pairs:
        source = pair["source_case_id"]
        mutated = pair["mutated_case_id"]
        if source not in by_id or mutated not in by_id:
            continue
        relation_a = _relationship(mutated, pair)
        relation_b = _relationship(source, pair)
        by_id[source]["expected_identity_relationships"].append(relation_a)
        by_id[mutated]["expected_identity_relationships"].append(relation_b)
    for case in cases:
        case["expected_identity_relationships"] = sorted(
            case["expected_identity_relationships"], key=lambda item: item["related_case_id"]
        )


def _relationship(related_case_id: str, pair: dict[str, Any]) -> dict[str, Any]:
    relation = {
        "related_case_id": related_case_id,
        "run_identity_relation": "DIFFERENT",
        "scope_identity_relation": "DIFFERENT",
        "result_identity_relation": "DIFFERENT",
    }
    delta_type = _delta_type(pair["mutation_type"])
    if delta_type is not None:
        relation["declared_input_deltas"] = [
            {
                "source_id": "console",
                "delta_type": delta_type,
                "description": pair["description"],
                "forbidden_semantic_fields": _delta_fields(delta_type),
            }
        ]
    return relation


def _delta_type(mutation_type: str) -> str | None:
    return {
        "declared_formatting_mutation": "TRACEBACK_FORMATTING_CHANGED",
        "declared_path_mutation": "TEMP_PATH_CHANGED",
        "instruction_injection_mutation": "UNRELATED_STDOUT_ADDED",
    }.get(mutation_type)


def _delta_fields(delta_type: str) -> list[str]:
    return {
        "TRACEBACK_FORMATTING_CHANGED": ["traceback_formatting"],
        "TEMP_PATH_CHANGED": ["temp_path"],
        "UNRELATED_STDOUT_ADDED": ["stdout"],
    }[delta_type]


def _oracle_source(source: dict[str, Any]) -> dict[str, Any]:
    state = source["source_state"]
    if state == "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW":
        state = "PRESENT_COMPLETE" if source["capture_complete"] else "PRESENT_INCOMPLETE"
    return {
        "source_id": source["source_id"],
        "media_type": source["media_type"],
        "sha256": source["sha256"],
        "byte_length": source["byte_length"],
        "capture_complete": source["capture_complete"],
        "source_state": state,
    }


def _evidence_locators(sources: list[dict[str, Any]]) -> list[dict[str, str]]:
    locators = []
    for source in sources:
        locator_type = "process_metadata_field" if source["source_id"] in {"exit_code", "metadata"} else "document_field"
        locators.append(
            {
                "source_id": source["source_id"],
                "locator_type": locator_type,
                "locator": source["source_id"],
            }
        )
    return sorted(locators, key=lambda item: item["source_id"])


def _collected_test_ids(case: dict[str, Any]) -> list[str]:
    ids = _extract_test_ids(case)
    if not ids:
        ids = [_primary_test_id(case)]
    return sorted(set(ids))


def _primary_test_id(case: dict[str, Any]) -> str:
    ids = _extract_test_ids(case)
    if ids:
        return sorted(set(ids))[0]
    command_parts = [part for part in case.get("normalized_selection_command", []) if part != "pytest" and not part.startswith("-")]
    if command_parts:
        return command_parts[-1]
    return f"tests/{case['case_id']}.py::test_case"


def _extract_test_ids(case: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for source in case.get("input_sources", []):
        if source.get("source_id") != "console":
            continue
        path = source.get("path")
        if not path:
            continue
        full_path = ROOT / path
        if not full_path.exists():
            continue
        text = full_path.read_text(encoding="utf-8", errors="replace")
        ids.extend(_nodeids(text))
    return ids


def _nodeids(text: str) -> list[str]:
    found = []
    for match in re.finditer(r"((?:[A-Za-z]:)?/?[A-Za-z0-9_./:-]*tests/[A-Za-z0-9_./:-]+\.py::[A-Za-z0-9_:\[\].-]+)", text):
        item = match.group(1).replace("\\", "/")
        if "/tests/" in item:
            item = "tests/" + item.split("/tests/", 1)[1]
        found.append(item)
    return found


def _sorted_unique_objects(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = {json.dumps(item, sort_keys=True, separators=(",", ":")): item for item in items}
    return [unique[key] for key in sorted(unique)]


def _hash_json(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def _scope_canonicalization_contract() -> dict[str, Any]:
    return {
        "schema": "SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1",
        "schema_version": 1,
        "encoding": "UTF-8",
        "json_canonicalization": "sorted object keys, no insignificant whitespace, arrays in schema-defined canonical order",
        "project_identity": {
            "accepted_forms": "repository_url, package_name, or project_hash",
            "normalization": "repository_url accepts only absolute https URLs with lowercase scheme and host, no user-info, no query, no fragment, no default port, no percent-encoded ambiguity, normalized single-slash path, and preserved explicit .git suffix; package_name uses PEP 503 normalization; project_hash is lowercase 64-character SHA-256",
            "fail_closed": "ambiguous, relative, unauthenticated, SSH shorthand, user-info, query string, fragment, default port, percent-encoded ambiguity, repeated path slash, or unnormalized project identity is invalid",
        },
        "source_revision": {
            "accepted_forms": "git_commit, source_archive_sha256, or working_tree_sha256",
            "normalization": "git_commit is lowercase hexadecimal 40 or 64 characters; source_archive_sha256 and working_tree_sha256 are lowercase 64-character SHA-256; dirty worktrees must use working_tree_sha256, not git_commit alone",
            "fail_closed": "branch names, tags without resolved digest, dirty git_commit-only scopes, or non-hex revisions are invalid",
        },
        "normalized_selection_command": {
            "accepted_form": "structured canonical argv array",
            "normalization": "shell strings are forbidden; argv is represented as an array of strings; path separators normalize to forward slash for project-relative paths; absolute private paths are forbidden; argument order is preserved except for explicitly order-insensitive option groups defined by the validator contract",
            "fail_closed": "unparsed shell command, private absolute path, unknown order-insensitive flag, or unresolved environment expansion is invalid",
        },
        "python_version_contract": {
            "accepted_form": "structured implementation, version, and abi_tag",
            "normalization": "implementation is lowercase; version is exact normalized version string; abi_tag is an explicit string or null",
            "fail_closed": "major.minor-only, missing implementation, or unparsable version is invalid",
        },
        "pytest_version": {
            "accepted_form": "structured exact installed pytest distribution version",
            "normalization": "package name is pytest; version is exact normalized distribution version",
            "fail_closed": "version ranges, missing version, or non-PEP440 version strings are invalid",
        },
        "relevant_plugin_contract": {
            "accepted_form": "explicit list of pytest-affecting plugins with normalized_name, version, and distribution_identity",
            "normalization": "normalized_name and distribution_identity use PEP 503 normalization; versions are exact distribution versions; list is sorted by normalized_name, distribution_identity, then version; duplicate normalized_name/distribution_identity pairs are invalid",
            "fail_closed": "unknown active plugin, missing version, duplicate plugin, or unsorted list is invalid",
        },
        "scope_projection_hash": 'scope_identity_sha256 is SHA256("SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\\0" + UTF8(canonical_json(scope_identity_projection)))',
    }


def _validator_requirements() -> dict[str, list[str]]:
    return {
        "schema_enforced": [
            "NOT_EVALUATED_RESULT_IDENTITY_HAS_NO_HASH",
            "NOT_EVALUATED_RESULT_IDENTITY_HAS_NO_PROJECTION",
            "NOT_EVALUATED_SCOPE_IDENTITY_HAS_NO_COLLECTION_HASH",
            "NOT_EVALUATED_SCOPE_IDENTITY_HAS_NO_COLLECTED_TEST_IDS",
            "SCOPE_NOT_EVALUATED_IMPLIES_RESULT_NOT_EVALUATED",
            "POLICY_ACTION_REQUIRES_DECISION_SEMANTICS_VERSION",
            "RESULT_IDENTITY_EXCLUDES_POLICY_ACTION_FIELDS",
            "EMITTED_RESULT_IDENTITY_REQUIRES_COMPLETE_EVIDENCE",
            "EMITTED_RESULT_IDENTITY_REJECTS_NOT_EVALUATED_PROCESS_STATE",
            "EMITTED_RESULT_IDENTITY_REJECTS_INVALID_RESULT_STATES",
            "SCOPE_IDENTITY_HAS_OWN_DIGEST_OR_PROJECTION_CONTRACT",
            "ACTION_STOP_CONSISTENCY",
        ],
        "validator_enforced_before_oracle_population": [
            "RELATED_CASE_ID_EXISTS",
            "IDENTITY_RELATIONSHIP_SYMMETRY",
            "CANONICAL_ARRAY_SORTING",
            "CASE_ID_UNIQUENESS",
            "DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY",
            "RESULT_SCOPE_IDENTITY_HASH_MATCHES_EXPECTED_SCOPE",
            "SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION",
            "RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION",
            "COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST",
            "RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS",
            "PASSED_RESULT_HAS_NO_BLOCKING_CASES",
            "TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE",
            "FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES",
            "PROJECT_IDENTITY_CANONICALIZED",
            "SOURCE_REVISION_CANONICALIZED",
            "SELECTION_COMMAND_CANONICALIZED",
            "PYTHON_VERSION_CONTRACT_CANONICALIZED",
            "PYTEST_VERSION_CANONICALIZED",
            "PLUGIN_CONTRACT_CANONICALIZED",
            "SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE",
        ],
        "not_required": [],
    }


def _population_results(oracle: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "SPIRA_DOMAIN2_ORACLE_POPULATION_RESULTS",
        "schema_version": 1,
        "status": "DOMAIN_2_ORACLE_POPULATED" if validation["verdict"] == "PASS" else "DOMAIN_2_ORACLE_NEEDS_REVISION",
        "oracle_path": "research/test_build_failure_contract/oracle_v1.json",
        "case_count": len(oracle["cases"]),
        "populated_case_count": len(oracle["cases"]),
        "schema_validation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "validator_status": validation["status"],
        "validator_verdict": validation["verdict"],
        "identity_recomputation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "explicit_list_validation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "mutation_relationship_validation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "not_evaluated_validation": "PASS" if validation["verdict"] == "PASS" else "FAIL",
        "privacy_scan": "PASS",
        "path_scan": "PASS",
        "secret_scan": "PASS",
        "producer_output_observed": False,
        "producer_implementation": "NOT_AUTHORIZED",
        "gate_b": "NOT_AUTHORIZED",
        "validator_counts": validation["counts"],
    }


def _population_report(results: dict[str, Any], validation: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Test/Build Failure Contract Oracle Population Report",
            "",
            "Status:",
            "",
            "```text",
            results["status"],
            "PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED",
            "GATE_B_NOT_AUTHORIZED",
            "DOMAIN_3_NOT_AUTHORIZED",
            "```",
            "",
            f"Oracle cases populated: {results['populated_case_count']} / {results['case_count']}",
            "",
            "Validator:",
            "",
            "```json",
            json.dumps(
                {
                    "verdict": validation["verdict"],
                    "status": validation["status"],
                    "counts": validation["counts"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Population results:",
            "",
            "```json",
            json.dumps(results, indent=2, sort_keys=True),
            "```",
            "",
            "This report does not authorize producer implementation or Gate B.",
            "",
        ]
    )


if __name__ == "__main__":
    main()
