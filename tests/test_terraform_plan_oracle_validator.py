from __future__ import annotations

import copy
import json
from pathlib import Path

from spira_core import terraform_plan_oracle_validator as validator


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"


def test_valid_oracle_fixture_passes():
    report = validator.validate_oracle_document(_oracle())

    assert report["verdict"] == "PASS"
    assert report["status"] == "DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATION_PASS"
    assert report["counts"]["case_count"] == 40
    assert report["counts"]["mutation_relationship_count"] == 10
    assert "ORACLE_POPULATION" in report["not_authorized"]


def test_validator_accepts_machine_readable_bytes_input():
    data = json.dumps(_oracle(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    report = validator.validate_oracle_bytes(data, input_path="fixtures/valid_terraform_oracle.json")

    assert report["verdict"] == "PASS"
    assert report["input"]["path"] == "fixtures/valid_terraform_oracle.json"
    assert len(report["input"]["sha256"]) == 64


def test_json_parse_failure_is_validation_failure_not_tool_error():
    report = validator.validate_oracle_bytes(b"{")

    assert report["verdict"] == "FAIL"
    assert report["status"] == "ORACLE_VALIDATION_FAILED"
    assert _first_error(report) == "JSON_PARSE_FAILED"


def test_internal_exception_is_tool_error(monkeypatch):
    def boom(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(validator, "_validate_cases", boom)

    report = validator.validate_oracle_document(_oracle())

    assert report["verdict"] == "TOOL_ERROR"
    assert report["status"] == "ORACLE_VALIDATOR_TOOL_ERROR"
    assert _first_error(report) == "ORACLE_VALIDATOR_EXCEPTION"


def test_positive_resource_unknown_sensitive_and_provenance_fixture_passes():
    document = _oracle()
    case = _first_case(document)
    subject = case["subject"]
    case["expected_claims"].extend(
        [
            _claim("terraform_plan.resource_create", "TERRAFORM_RESOURCE_CREATE", subject, {"resource_address": "terraform_data.example"}),
            _claim("terraform_plan.action_sequence", "TERRAFORM_RESOURCE_ACTION_SEQUENCE", subject, {"action_sequence": ["create"]}),
            _claim("terraform_plan.resource_replace", "TERRAFORM_RESOURCE_REPLACE", subject, {"resource_address": "terraform_data.replace_me"}),
            _claim("terraform_plan.replace_path", "TERRAFORM_REPLACE_PATH_PRESENT", subject, {"json_pointer": "/resource_changes/0/change/replace_paths/0"}),
            _claim(
                "terraform_plan.unknown_path",
                "PLANNED_VALUE_UNKNOWN",
                subject,
                {"json_pointer": "/planned_values/root_module/resources/0/values/id"},
                status="NOT_EVALUATED",
            ),
            _claim(
                "terraform_plan.sensitive_path",
                "SENSITIVE_PATH_PRESENT",
                subject,
                {"json_pointer": "/planned_values/root_module/resources/0/values/sensitive"},
                status="NOT_EVALUATED",
            ),
        ]
    )
    case["explicit_lists"] = {
        "create_resources": ["terraform_data.example"],
        "update_resources": [],
        "delete_resources": [],
        "replace_resources": ["terraform_data.replace_me"],
        "read_resources": [],
        "noop_resources": [],
        "replace_paths": ["/resource_changes/0/change/replace_paths/0"],
        "unknown_paths": ["/planned_values/root_module/resources/0/values/id"],
        "sensitive_paths": ["/planned_values/root_module/resources/0/values/sensitive"],
        "not_evaluated": ["terraform_plan.sensitive_path", "terraform_plan.unknown_path"],
    }
    _refresh_case_identity(document, case)

    report = validator.validate_oracle_document(document)

    assert report["verdict"] == "PASS"


def test_negative_validator_fixtures_fail_with_expected_error_codes():
    fixtures = {
        "schema_nested_required": (_missing_nested_required_field, "SCHEMA_V1_VALIDATION_FAILED"),
        "forbidden_additional_property": (_forbidden_additional_property, "SCHEMA_V1_VALIDATION_FAILED"),
        "invalid_enum": (_invalid_enum, "SCHEMA_V1_VALIDATION_FAILED"),
        "missing_accepted_case": (_missing_accepted_case, "MISSING_ACCEPTED_CORPUS_CASE"),
        "extra_non_corpus_case": (_extra_non_corpus_case, "EXTRA_NON_CORPUS_CASE"),
        "subject_hash_mismatch": (_subject_hash_mismatch, "SUBJECT_HASH_MISMATCH"),
        "context_hash_mismatch": (_context_hash_mismatch, "CONTEXT_HASH_MISMATCH"),
        "unification_id_mismatch": (_unification_id_mismatch, "UNIFICATION_ID_MISMATCH"),
        "hash_only_without_bytes": (_bound_fingerprint_without_bytes, "BOUND_PROVENANCE_FINGERPRINT_CANONICAL_BYTES_NOT_AVAILABLE"),
        "unresolvable_evidence_locator": (_unresolvable_evidence_locator, "UNRESOLVABLE_EVIDENCE_LOCATOR"),
        "duplicate_claim_id": (_duplicate_claim_id, "DUPLICATE_CLAIM_ID"),
        "non_canonical_explicit_list": (_non_canonical_explicit_list, "NON_CANONICAL_EXPLICIT_LIST"),
        "replace_paths_mismatch": (_replace_paths_mismatch, "STRICT_LIST_MISMATCH"),
        "unknown_paths_mismatch": (_unknown_paths_mismatch, "STRICT_LIST_MISMATCH"),
        "sensitive_value_exposed": (_sensitive_value_exposed, "SENSITIVE_VALUE_EXPOSED"),
        "invalid_stop_action_pair": (_invalid_stop_action_pair, "SCHEMA_V1_VALIDATION_FAILED"),
        "mutation_missing_case": (_mutation_missing_case, "MUTATION_PAIR_REFERENCES_MISSING_CASE"),
        "mutation_relation_mismatch": (_mutation_relation_mismatch, "MUTATION_RELATION_MISMATCH"),
        "producer_output_observed": (_producer_output_observed, "SCHEMA_V1_VALIDATION_FAILED"),
    }

    for name, (mutate, expected) in fixtures.items():
        document = _oracle()
        mutate(document)

        report = validator.validate_oracle_document(document)

        assert report["verdict"] == "FAIL", name
        assert report["status"] == "ORACLE_VALIDATION_FAILED", name
        assert expected in _error_codes(report), name


def test_case_file_hash_mismatch_fixture_fails(monkeypatch):
    original = validator._manifest_cases

    def mismatched_manifest_cases(manifest):
        cases = {case_id: copy.deepcopy(case) for case_id, case in original(manifest).items()}
        first = next(iter(cases.values()))
        first_file = next(iter(first["files"]))
        first["files"][first_file] = "f" * 64
        return cases

    monkeypatch.setattr(validator, "_manifest_cases", mismatched_manifest_cases)

    report = validator.validate_oracle_document(_oracle())

    assert report["verdict"] == "FAIL"
    assert "CASE_FILE_HASH_MISMATCH" in _error_codes(report)


def _oracle() -> dict:
    manifest = _read_manifest()
    document = {
        "schema": "SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE",
        "schema_version": 1,
        "status": "DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_V1_LOCKED",
        "corpus_manifest_sha256": validator.CORPUS_MANIFEST_SHA256,
        "case_count": 40,
        "cases": [],
        "mutation_relationships": [],
        "not_claimed": [
            "APPLY_SUCCESS",
            "DOMAIN_4",
            "GATE_B_REUSE",
            "INFRASTRUCTURE_COMPLIANCE",
            "INFRASTRUCTURE_CORRECTNESS",
            "INFRASTRUCTURE_COST",
            "INFRASTRUCTURE_SECURITY",
            "KUBERNETES_SUPPORT",
            "LIVE_STATE_FRESHNESS",
            "MVP_INCLUSION",
            "RELEASE",
            "TERRAFORM_PROVIDER_SAFETY",
        ],
        "not_authorized": [
            "DOMAIN_4",
            "GATE_B",
            "MVP_BOUNDARY_AMENDMENT",
            "ORACLE_POPULATION_BEFORE_SCHEMA_ACCEPTANCE",
            "PRODUCER_IMPLEMENTATION",
            "RELEASE_VERSION_TAG_PYPI",
        ],
    }
    case_by_id = {}
    for manifest_case in manifest["cases"]:
        case = _case(document, manifest_case)
        document["cases"].append(case)
        case_by_id[case["case_id"]] = case
    for pair in manifest["mutation_pairs"]:
        base = case_by_id[pair["base_case_id"]]
        mutated = case_by_id[pair["mutated_case_id"]]
        document["mutation_relationships"].append(
            {
                "pair_id": pair["pair_id"],
                "base_case_id": pair["base_case_id"],
                "mutated_case_id": pair["mutated_case_id"],
                "declared_delta": pair["declared_delta"],
                "expected_claims_relation": pair["expected_claims_relation"],
                "expected_claims_root_relation": pair["expected_claims_relation"],
                "expected_unification_id_relation": "SAME"
                if base["context"]["unification_id_expected"] == mutated["context"]["unification_id_expected"]
                else "DIFFERENT",
            }
        )
    return document


def _case(document: dict, manifest_case: dict) -> dict:
    case_id = manifest_case["case_id"]
    plan_file = "plan.json" if "plan.json" in manifest_case["files"] else "plan.json.invalid"
    subject = {"type": "terraform_plan", "sha256": manifest_case["files"][plan_file]}
    claim_value = "order_equivalent" if case_id in {"syn_order_original", "syn_order_reordered"} else case_id
    case = {
        "case_id": case_id,
        "subject": subject,
        "context": {
            "context_sha256": "0" * 64,
            "run_identity_kind": "CONTEXTUAL_UNIFICATION_ID",
            "unification_id_expected": "0" * 64,
        },
        "optional_provenance": _provenance(manifest_case),
        "expected_claims": [
            {
                "claim_id": "terraform_plan.case_identity",
                "claim_type": "TERRAFORM_PLAN_FORMAT_VERSION",
                "status": "PASS" if plan_file == "plan.json" else "NOT_EVALUATED",
                "subject": subject,
                "value": {"string": claim_value},
                "evidence": [{"case_file": plan_file, "json_pointer": ""}],
            }
        ],
        "explicit_lists": _empty_lists(not_evaluated=["terraform_plan.case_identity"] if plan_file != "plan.json" else []),
        "policy_action": {
            "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
            "stop": plan_file != "plan.json",
            "recommended_agent_action": "REPORT_NOT_EVALUATED" if plan_file != "plan.json" else "REPORT_WITH_NOTES",
            "reason_codes": ["TERRAFORM_PLAN_JSON_INVALID"] if plan_file != "plan.json" else ["TERRAFORM_PLAN_NO_CHANGES"],
        },
        "mutation_membership": [],
        "not_claimed": [
            "APPLY_SUCCESS",
            "INFRASTRUCTURE_COMPLIANCE",
            "INFRASTRUCTURE_CORRECTNESS",
            "INFRASTRUCTURE_COST",
            "INFRASTRUCTURE_SECURITY",
            "LIVE_STATE_FRESHNESS",
        ],
    }
    case["context"]["context_sha256"] = validator.context_sha256(document, case, manifest_case)
    case["context"]["unification_id_expected"] = validator.unification_id(document, case)
    return case


def _claim(claim_id: str, claim_type: str, subject: dict, value: dict, *, status: str = "PASS") -> dict:
    return {
        "claim_id": claim_id,
        "claim_type": claim_type,
        "status": status,
        "subject": subject,
        "value": value,
        "evidence": [{"case_file": "plan.json", "json_pointer": ""}],
    }


def _refresh_case_identity(document: dict, case: dict) -> None:
    manifest_case = {item["case_id"]: item for item in _read_manifest()["cases"]}[case["case_id"]]
    case["context"]["context_sha256"] = validator.context_sha256(document, case, manifest_case)
    case["context"]["unification_id_expected"] = validator.unification_id(document, case)


def _provenance(manifest_case: dict) -> dict:
    files = manifest_case["files"]
    main_hash = files.get("main.tf")
    bound_or_na = {"state": "BOUND", "sha256": main_hash} if main_hash else {"state": "NOT_APPLICABLE"}
    return {
        "configuration_sha256": bound_or_na,
        "prior_state_sha256": {"state": "NOT_APPLICABLE"},
        "provider_lockfile_sha256": {"state": "NOT_APPLICABLE"},
        "variables_manifest_sha256": {"state": "NOT_APPLICABLE"},
        "generation_command_fingerprint": {"state": "NOT_APPLICABLE"},
        "workspace_or_fixture_identity": {"state": "NOT_APPLICABLE"},
    }


def _empty_lists(*, not_evaluated: list[str] | None = None) -> dict:
    return {
        "create_resources": [],
        "update_resources": [],
        "delete_resources": [],
        "replace_resources": [],
        "read_resources": [],
        "noop_resources": [],
        "replace_paths": [],
        "unknown_paths": [],
        "sensitive_paths": [],
        "not_evaluated": not_evaluated or [],
    }


def _read_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _first_case(document: dict) -> dict:
    return document["cases"][0]


def _missing_nested_required_field(document: dict) -> None:
    del _first_case(document)["context"]["context_sha256"]


def _forbidden_additional_property(document: dict) -> None:
    _first_case(document)["unexpected"] = True


def _invalid_enum(document: dict) -> None:
    _first_case(document)["policy_action"]["recommended_agent_action"] = "ASK_HUMAN"


def _missing_accepted_case(document: dict) -> None:
    document["cases"].pop()


def _extra_non_corpus_case(document: dict) -> None:
    extra = copy.deepcopy(_first_case(document))
    extra["case_id"] = "syn_extra_case"
    document["cases"].append(extra)


def _subject_hash_mismatch(document: dict) -> None:
    _first_case(document)["subject"]["sha256"] = "f" * 64


def _context_hash_mismatch(document: dict) -> None:
    _first_case(document)["context"]["context_sha256"] = "f" * 64


def _unification_id_mismatch(document: dict) -> None:
    _first_case(document)["context"]["unification_id_expected"] = "f" * 64


def _bound_fingerprint_without_bytes(document: dict) -> None:
    _first_case(document)["optional_provenance"]["generation_command_fingerprint"] = {
        "state": "BOUND",
        "fingerprint": "a" * 64,
    }


def _unresolvable_evidence_locator(document: dict) -> None:
    _first_case(document)["expected_claims"][0]["evidence"][0]["json_pointer"] = "/does/not/exist"


def _duplicate_claim_id(document: dict) -> None:
    _first_case(document)["expected_claims"].append(copy.deepcopy(_first_case(document)["expected_claims"][0]))


def _non_canonical_explicit_list(document: dict) -> None:
    case = _first_case(document)
    case["explicit_lists"]["create_resources"] = ["z", "a"]


def _replace_paths_mismatch(document: dict) -> None:
    case = _first_case(document)
    case["expected_claims"].append(
        {
            "claim_id": "terraform_plan.replace_path",
            "claim_type": "TERRAFORM_REPLACE_PATH_PRESENT",
            "status": "PASS",
            "subject": case["subject"],
            "value": {"json_pointer": "/resource_changes/0/change/replace_paths/0"},
            "evidence": [{"case_file": "plan.json", "json_pointer": ""}],
        }
    )


def _unknown_paths_mismatch(document: dict) -> None:
    case = _first_case(document)
    case["expected_claims"].append(
        {
            "claim_id": "terraform_plan.unknown_path",
            "claim_type": "PLANNED_VALUE_UNKNOWN",
            "status": "NOT_EVALUATED",
            "subject": case["subject"],
            "value": {"json_pointer": "/planned_values/root_module/resources/0/values/id"},
            "evidence": [{"case_file": "plan.json", "json_pointer": ""}],
        }
    )


def _sensitive_value_exposed(document: dict) -> None:
    _first_case(document)["expected_claims"][0]["value"] = {"string": "password=abc123"}


def _invalid_stop_action_pair(document: dict) -> None:
    _first_case(document)["policy_action"]["stop"] = True
    _first_case(document)["policy_action"]["recommended_agent_action"] = "PROCEED"


def _mutation_missing_case(document: dict) -> None:
    document["mutation_relationships"][0]["base_case_id"] = "syn_missing_case"


def _mutation_relation_mismatch(document: dict) -> None:
    rel = document["mutation_relationships"][0]
    rel["expected_unification_id_relation"] = "SAME" if rel["expected_unification_id_relation"] == "DIFFERENT" else "DIFFERENT"


def _producer_output_observed(document: dict) -> None:
    document["producer_output_seen"] = True


def _error_codes(report: dict) -> set[str]:
    return {check["error_code"] for check in report["checks"]}


def _first_error(report: dict) -> str:
    return report["checks"][0]["error_code"]
