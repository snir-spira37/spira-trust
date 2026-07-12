from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from . import test_build_failure_oracle_validator as validator


DECISION_SEMANTICS_VERSION = "SPIRA_DECISION_SEMANTICS_V2"


def produce_cases(manifest: Mapping[str, Any], *, root: str | Path) -> list[dict[str, Any]]:
    cases = [produce_case(case, root=root) for case in manifest.get("cases", [])]
    attach_identity_relationships(cases, manifest.get("mutation_pairs", []))
    return sorted(cases, key=lambda item: item["case_id"])


def produce_case(corpus_case: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    evidence = collect_evidence(corpus_case, root=root)
    sources = [producer_source(source) for source in corpus_case.get("input_sources", [])]
    scope = scope_identity(corpus_case, evidence, root=root)
    classification = classify_evidence(corpus_case, evidence, root=root)
    result = result_identity(scope["scope_identity_sha256"], classification)
    return {
        "case_id": str(corpus_case["case_id"]),
        "case_schema_version": 2,
        "input_manifest_sha256": hash_json(sources),
        "input_sources": sources,
        "supported_input": True,
        "produced_source_sufficiency": source_sufficiency(corpus_case, evidence),
        "produced_scope_identity": scope,
        "produced_result_identity": result,
        "produced_policy_action": policy_action(classification),
        "produced_identity_relationships": [],
        "produced_claims": claims(classification),
        "produced_explicit_lists": {
            "blocking_cases": classification["blocking_cases"],
            "nonblocking_cases": classification["nonblocking_cases"],
        },
        "produced_not_evaluated": classification["not_evaluated"],
        "produced_not_claimed": ["software_safety", "producer_correctness"],
        "produced_evidence_locators": evidence_locators(sources),
    }


def collect_evidence(corpus_case: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    sources: dict[str, dict[str, Any]] = {}
    text: dict[str, str] = {}
    json_sources: dict[str, Any] = {}
    for source in corpus_case.get("input_sources", []):
        item = dict(source)
        path = item.get("path")
        if path:
            full_path = root_path / str(path)
            item["path_exists"] = full_path.exists()
            if full_path.exists():
                if item.get("media_type") == "application/json":
                    json_sources[str(item["source_id"])] = json.loads(full_path.read_text(encoding="utf-8"))
                else:
                    text[str(item["source_id"])] = full_path.read_text(encoding="utf-8", errors="replace")
        else:
            item["path_exists"] = False
        sources[str(item["source_id"])] = item
    return {
        "sources": sources,
        "text": text,
        "json": json_sources,
        "exit_code": evidence_exit_code(corpus_case, json_sources),
        "public_raw_outputs_withheld": any(
            source.get("source_state") == "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW"
            for source in corpus_case.get("input_sources", [])
        ),
    }


def evidence_exit_code(corpus_case: Mapping[str, Any], json_sources: Mapping[str, Any]) -> int | None:
    direct = corpus_case.get("exit_code")
    if isinstance(direct, int):
        return direct
    materialization = json_sources.get("public_run_materialization")
    if isinstance(materialization, Mapping) and isinstance(materialization.get("exit_code"), int):
        return int(materialization["exit_code"])
    metadata = json_sources.get("metadata")
    if isinstance(metadata, Mapping) and isinstance(metadata.get("exit_code"), int):
        return int(metadata["exit_code"])
    return None


def scope_identity(corpus_case: Mapping[str, Any], evidence: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    ids = collected_test_ids(corpus_case, root=root)
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
        "collection_deterministic": collection_deterministic(corpus_case, evidence, ids),
        "scope_identity_sha256": validator.scope_identity_hash(projection),
        "scope_projection": projection,
        "scope_projection_sha256": validator.sha256_hex(projection),
        "collection_manifest_sha256": collection_hash,
        "canonical_collected_test_ids": ids,
    }


def collection_deterministic(corpus_case: Mapping[str, Any], evidence: Mapping[str, Any], ids: list[str]) -> bool:
    required_scope_fields = [
        "project_identity",
        "source_revision",
        "normalized_selection_command",
        "python_version_contract",
        "pytest_version",
        "relevant_plugin_contract",
    ]
    for field in required_scope_fields:
        value = corpus_case.get(field)
        if value is None or value == "":
            return False
        if field != "relevant_plugin_contract" and value == []:
            return False
    if not ids:
        return False
    return not any(
        not source.get("capture_complete", False)
        for source in evidence["sources"].values()
        if source["source_id"] == "metadata"
    )


def source_sufficiency(corpus_case: Mapping[str, Any], evidence: Mapping[str, Any]) -> dict[str, str]:
    console = evidence["text"].get("console", "")
    junit = evidence["text"].get("junit", "")
    conflict = console_junit_conflict(console, junit)
    incomplete = source_incomplete(evidence)
    malformed_junit = junit_incomplete_or_malformed(junit)
    result: dict[str, str] = {}
    for source in corpus_case.get("input_sources", []):
        source_id = str(source["source_id"])
        if source_id == "generation_instructions":
            result[source_id] = "NOT_APPLICABLE"
        elif conflict and source_id in {"console", "junit"}:
            result[source_id] = "CONFLICTING"
        elif source_id in {"console", "junit"} and source.get("source_state") == "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW":
            result[source_id] = "NOT_EVALUATED"
        elif incomplete and not source.get("capture_complete", False):
            result[source_id] = "NOT_EVALUATED"
        elif source_id == "junit" and malformed_junit:
            result[source_id] = "NOT_EVALUATED"
        else:
            result[source_id] = "ANSWERED"
    return result


def classify_evidence(corpus_case: Mapping[str, Any], evidence: Mapping[str, Any], *, root: str | Path) -> dict[str, Any]:
    exit_code = evidence["exit_code"]
    console = evidence["text"].get("console", "")
    junit = evidence["text"].get("junit", "")
    test_id = primary_test_id(corpus_case, root=root)
    base = {
        "result_status": "EMITTED",
        "process_state": "COMPLETED",
        "result_state": "PASSED" if exit_code == 0 or console_has_only_nonblocking(console) else "FAILED",
        "blocking_cases": [],
        "nonblocking_cases": [],
        "failure_classes": [],
        "run_level_failures": [],
        "stop": False,
        "action": "PROCEED",
        "reason_codes": ["TESTS_PASSED"],
        "not_evaluated": [],
    }
    if evidence["public_raw_outputs_withheld"]:
        return not_evaluated(base, "PUBLIC_RUN_OUTPUT_WITHHELD")
    if source_incomplete(evidence) or junit_incomplete_or_malformed(junit):
        return not_evaluated(base, "TEST_RESULT_EVIDENCE_INCOMPLETE")
    if console_junit_conflict(console, junit):
        return not_evaluated(base, "TEST_EVIDENCE_CONFLICT")
    if " SKIPPED" in console or " XFAIL" in console:
        outcome = "SKIPPED" if " SKIPPED" in console else "XFAILED"
        base["nonblocking_cases"] = [
            {
                "test_id": test_id,
                "observed_outcome": outcome,
                "reason_category": outcome.lower(),
                "rerun_target": test_id,
            }
        ]
        base["action"] = "REPORT_WITH_NOTES"
        base["reason_codes"] = ["TEST_NOTES"]
        return finalize(base)
    if " XPASS" in console:
        base.update(
            {
                "result_state": "FAILED",
                "blocking_cases": [
                    {
                        "test_id": test_id,
                        "observed_outcome": "XPASSED_BLOCKING",
                        "failure_class": "ASSERTION_FAILURE",
                        "reason_category": "xpassed_strict",
                        "rerun_target": test_id,
                    }
                ],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
        return finalize(base)
    run_level = run_level_failure_from_evidence(console, exit_code)
    if run_level is not None:
        base.update(
            {
                "process_state": process_state_for_run_level(run_level),
                "result_state": "ERROR",
                "run_level_failures": [run_level],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
        return finalize(base)
    failed_ids = failed_test_ids(console)
    if failed_ids or junit_has_failure(junit):
        ids = failed_ids or [test_id]
        base.update(
            {
                "process_state": "COMPLETED",
                "result_state": "FAILED",
                "blocking_cases": [
                    {
                        "test_id": item,
                        "observed_outcome": "FAILED",
                        "failure_class": "ASSERTION_FAILURE",
                        "rerun_target": item,
                    }
                    for item in ids
                ],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
        return finalize(base)
    if exit_code not in {None, 0}:
        base.update(
            {
                "process_state": "ERROR",
                "result_state": "ERROR",
                "run_level_failures": ["PROCESS_ERROR"],
                "stop": True,
                "action": "STOP_BLOCKED",
                "reason_codes": ["TEST_FAILURE"],
            }
        )
    return finalize(base)


def result_identity(scope_hash: str, classification: Mapping[str, Any]) -> dict[str, Any]:
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


def policy_action(classification: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "stop": classification["stop"],
        "recommended_agent_action": classification["action"],
        "reason_codes": classification["reason_codes"],
        "decision_semantics_version": DECISION_SEMANTICS_VERSION,
    }


def claims(classification: Mapping[str, Any]) -> list[dict[str, Any]]:
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


def attach_identity_relationships(cases: list[dict[str, Any]], pairs: list[Mapping[str, Any]]) -> None:
    by_id = {case["case_id"]: case for case in cases}
    for pair in pairs:
        source = str(pair["source_case_id"])
        mutated = str(pair["mutated_case_id"])
        if source not in by_id or mutated not in by_id:
            continue
        by_id[source]["produced_identity_relationships"].append(identity_relationship(mutated, pair))
        by_id[mutated]["produced_identity_relationships"].append(identity_relationship(source, pair))
    for case in cases:
        case["produced_identity_relationships"] = sorted(
            case["produced_identity_relationships"], key=lambda item: item["related_case_id"]
        )


def identity_relationship(related_case_id: str, pair: Mapping[str, Any]) -> dict[str, Any]:
    mutation_type = str(pair["mutation_type"])
    stable_result_mutation = mutation_type in {
        "declared_formatting_mutation",
        "declared_path_mutation",
        "instruction_injection_mutation",
    }
    relation = {
        "related_case_id": related_case_id,
        "run_identity_relation": "DIFFERENT",
        "scope_identity_relation": "SAME",
        "result_identity_relation": "SAME" if stable_result_mutation else "DIFFERENT",
    }
    delta_type = delta_type_for_mutation(mutation_type)
    if delta_type is not None:
        relation["declared_input_deltas"] = [
            {
                "source_id": "console",
                "delta_type": delta_type,
                "description": pair["description"],
                "forbidden_semantic_fields": delta_fields(delta_type),
            }
        ]
    return relation


def not_evaluated(base: Mapping[str, Any], reason_code: str) -> dict[str, Any]:
    action = "RERUN_REQUIRED" if reason_code == "TEST_EVIDENCE_CONFLICT" else "REPORT_NOT_EVALUATED"
    return finalize(
        {
            **base,
            "result_status": "NOT_EVALUATED",
            "stop": True,
            "action": action,
            "reason_codes": [reason_code],
            "not_evaluated": ["result_identity"],
            "blocking_cases": [],
            "nonblocking_cases": [],
            "run_level_failures": [],
        }
    )


def finalize(classification: dict[str, Any]) -> dict[str, Any]:
    derived = sorted(
        {
            str(item["failure_class"])
            for item in classification["blocking_cases"] + classification["nonblocking_cases"]
            if "failure_class" in item
        }
        | set(classification["run_level_failures"])
    )
    classification["failure_classes"] = derived
    classification["blocking_cases"] = sorted_unique_objects(classification["blocking_cases"])
    classification["nonblocking_cases"] = sorted_unique_objects(classification["nonblocking_cases"])
    classification["reason_codes"] = sorted(set(classification["reason_codes"]))
    classification["not_evaluated"] = sorted(set(classification["not_evaluated"]))
    return classification


def producer_source(source: Mapping[str, Any]) -> dict[str, Any]:
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


def evidence_locators(sources: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    locators = []
    for source in sources:
        locator_type = "process_metadata_field" if source["source_id"] in {"exit_code", "metadata"} else "document_field"
        locators.append(
            {
                "source_id": str(source["source_id"]),
                "locator_type": locator_type,
                "locator": str(source["source_id"]),
            }
        )
    return sorted(locators, key=lambda item: item["source_id"])


def collected_test_ids(corpus_case: Mapping[str, Any], *, root: str | Path) -> list[str]:
    ids = extract_test_ids(corpus_case, root=root)
    if not ids:
        ids = [primary_test_id(corpus_case, root=root)]
    return sorted(set(ids))


def primary_test_id(corpus_case: Mapping[str, Any], *, root: str | Path) -> str:
    ids = extract_test_ids(corpus_case, root=root)
    if ids:
        return sorted(set(ids))[0]
    command_parts = [
        str(part)
        for part in corpus_case.get("normalized_selection_command", [])
        if part != "pytest" and not str(part).startswith("-")
    ]
    if command_parts:
        return command_parts[-1]
    return f"tests/{corpus_case['case_id']}.py::test_case"


def extract_test_ids(corpus_case: Mapping[str, Any], *, root: str | Path) -> list[str]:
    ids: list[str] = []
    root_path = Path(root)
    for source in corpus_case.get("input_sources", []):
        if source.get("source_id") != "console":
            continue
        path = source.get("path")
        if not path:
            continue
        full_path = root_path / str(path)
        if not full_path.exists():
            continue
        ids.extend(nodeids(full_path.read_text(encoding="utf-8", errors="replace")))
    return ids


def nodeids(text: str) -> list[str]:
    found = []
    for match in re.finditer(r"((?:[A-Za-z]:)?/?[A-Za-z0-9_./:-]*tests/[A-Za-z0-9_./:-]+\.py::[A-Za-z0-9_:\[\].-]+)", text):
        item = match.group(1).replace("\\", "/")
        if "/tests/" in item:
            item = "tests/" + item.split("/tests/", 1)[1]
        found.append(item)
    return found


def console_has_only_nonblocking(console: str) -> bool:
    return bool(console) and not any(token in console for token in (" FAILED", "ERROR", "Traceback", "Timeout"))


def source_incomplete(evidence: Mapping[str, Any]) -> bool:
    return any(not source.get("capture_complete", False) for source in evidence["sources"].values())


def junit_incomplete_or_malformed(junit: str) -> bool:
    if not junit:
        return False
    if not junit.strip().endswith(">") or "<testsuite" not in junit or "</testsuite>" not in junit:
        return True
    return "tests=" not in junit and "failures=" not in junit


def console_junit_conflict(console: str, junit: str) -> bool:
    return bool(console and junit and " PASSED" in console and " FAILED" not in console and junit_has_failure(junit))


def junit_has_failure(junit: str) -> bool:
    return "<failure" in junit or re.search(r"failures=['\"]?[1-9]", junit) is not None


def failed_test_ids(console: str) -> list[str]:
    ids = []
    for line in console.splitlines():
        if " FAILED" not in line:
            continue
        match = re.search(r"((?:[A-Za-z]:)?/?[A-Za-z0-9_./:-]*tests/[A-Za-z0-9_./:-]+\.py::[^\s]+)", line)
        if match:
            item = match.group(1).replace("\\", "/")
            if "/tests/" in item:
                item = "tests/" + item.split("/tests/", 1)[1]
            ids.append(item)
    return sorted(set(ids))


def run_level_failure_from_evidence(console: str, exit_code: int | None) -> str | None:
    checks = [
        ("Timeout", "TIMEOUT"),
        ("ERROR collecting", "COLLECTION_ERROR"),
        ("ImportError", "IMPORT_ERROR"),
        ("SyntaxError", "SYNTAX_ERROR"),
        ("ERROR at setup", "FIXTURE_SETUP_ERROR"),
        ("ERROR at teardown", "FIXTURE_TEARDOWN_ERROR"),
        ("KeyboardInterrupt", "PROCESS_INTERRUPTED"),
        ("terminated by signal", "PROCESS_CRASH"),
        ("no tests collected", "PROCESS_ERROR"),
    ]
    for needle, failure_class in checks:
        if needle in console:
            return failure_class
    if exit_code in {2, 3, 4, 5} and not failed_test_ids(console):
        return "PROCESS_ERROR"
    return None


def process_state_for_run_level(failure_class: str) -> str:
    if failure_class == "TIMEOUT":
        return "TIMEOUT"
    if failure_class == "PROCESS_INTERRUPTED":
        return "INTERRUPTED"
    if failure_class == "PROCESS_CRASH":
        return "CRASH"
    return "ERROR"


def delta_type_for_mutation(mutation_type: str) -> str | None:
    return {
        "declared_formatting_mutation": "TRACEBACK_FORMATTING_CHANGED",
        "declared_path_mutation": "TEMP_PATH_CHANGED",
        "instruction_injection_mutation": "UNRELATED_STDOUT_ADDED",
    }.get(mutation_type)


def delta_fields(delta_type: str) -> list[str]:
    return {
        "TRACEBACK_FORMATTING_CHANGED": ["traceback_formatting"],
        "TEMP_PATH_CHANGED": ["temp_path"],
        "UNRELATED_STDOUT_ADDED": ["stdout"],
    }[delta_type]


def sorted_unique_objects(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique = {json.dumps(item, sort_keys=True, separators=(",", ":")): item for item in items}
    return [unique[key] for key in sorted(unique)]


def hash_json(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
