from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


RESULT_SCHEMA = "SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE_VALIDATION_RESULT"
RESULT_SCHEMA_VERSION = 1
ORACLE_SCHEMA = "SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE"
ORACLE_SCHEMA_VERSION = 1
ORACLE_STATUS = "DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_V1_LOCKED"
CORPUS_MANIFEST_SHA256 = "28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c"
CONTEXT_TAG = "SPIRA_TERRAFORM_PLAN_CONTEXT_V1\0"
CLAIMS_TAG = "SPIRA_TERRAFORM_PLAN_CLAIMS_IDENTITY_V1\0"
CLAIMS_ROOT_TAG = "SPIRA_TERRAFORM_PLAN_CLAIMS_ROOT_V1\0"
UNIFICATION_TAG = "SPIRA_TERRAFORM_PLAN_UNIFICATION_ID_V1\0"

NOT_AUTHORIZED = [
    "ORACLE_POPULATION",
    "PRODUCER_IMPLEMENTATION",
    "GATE_B",
    "DOMAIN_4",
    "MVP_BOUNDARY_AMENDMENT",
    "RELEASE_VERSION_TAG_PYPI",
]

RESOURCE_LIST_BY_CLAIM = {
    "TERRAFORM_RESOURCE_CREATE": "create_resources",
    "TERRAFORM_RESOURCE_UPDATE": "update_resources",
    "TERRAFORM_RESOURCE_DELETE": "delete_resources",
    "TERRAFORM_RESOURCE_REPLACE": "replace_resources",
    "TERRAFORM_RESOURCE_READ": "read_resources",
    "TERRAFORM_RESOURCE_NOOP": "noop_resources",
}

ACTION_BY_CLAIM = {
    "TERRAFORM_RESOURCE_CREATE": ["create"],
    "TERRAFORM_RESOURCE_UPDATE": ["update"],
    "TERRAFORM_RESOURCE_DELETE": ["delete"],
    "TERRAFORM_RESOURCE_READ": ["read"],
    "TERRAFORM_RESOURCE_NOOP": ["no-op"],
}

SECRET_PATTERN = re.compile(r"(secret|password|token|private[_ -]?key|credential|api[_ -]?key|access[_ -]?key)", re.I)


class TerraformPlanOracleValidatorToolError(RuntimeError):
    """Raised when the validator cannot complete its own work."""


def validate_oracle_bytes(data: bytes, *, input_path: str | Path | None = None) -> dict[str, Any]:
    try:
        document = json.loads(data.decode("utf-8"))
    except Exception as exc:
        return _report(
            input_path=input_path,
            input_sha256=sha256(data).hexdigest(),
            errors=[_check("JSON_PARSE", "FAIL", "JSON_PARSE_FAILED", details={"error": str(exc)})],
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
    root: str | Path | None = None,
) -> dict[str, Any]:
    input_sha = sha256(input_bytes).hexdigest() if input_bytes is not None else sha256(
        canonical_json_bytes(document)
    ).hexdigest()
    repo_root = Path(root) if root is not None else _repo_root()
    errors: list[dict[str, Any]] = []
    try:
        schema = _load_json(repo_root / "research" / "terraform_plan_contract" / "oracle_schema_v1.schema.json")
        manifest_path = repo_root / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"
        manifest = _load_json(manifest_path)
        errors.extend(_validate_schema(document, schema))
        cases = list(document.get("cases") or []) if isinstance(document.get("cases"), list) else []
        relationships = (
            list(document.get("mutation_relationships") or [])
            if isinstance(document.get("mutation_relationships"), list)
            else []
        )
        errors.extend(_validate_corpus_binding(document, manifest, manifest_path, cases, relationships, repo_root))
        errors.extend(_validate_cases(document, manifest, cases, repo_root))
        errors.extend(_validate_mutation_relationships(manifest, cases, relationships))
        errors.extend(_validate_not_claimed(document))
    except Exception as exc:
        return _report(
            input_path=input_path,
            input_sha256=input_sha,
            errors=[
                _check(
                    "VALIDATOR_INTERNAL",
                    "TOOL_ERROR",
                    "ORACLE_VALIDATOR_EXCEPTION",
                    details={"error": str(exc)},
                )
            ],
            tool_error=True,
        )
    return _report(input_path=input_path, input_sha256=input_sha, errors=errors, document=document)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(value: Any, *, tag: str = "") -> str:
    return sha256(tag.encode("utf-8") + canonical_json_bytes(value)).hexdigest()


def context_sha256(document: Mapping[str, Any], case: Mapping[str, Any], manifest_case: Mapping[str, Any]) -> str:
    projection = {
        "domain_tag": "SPIRA_TERRAFORM_PLAN_CONTEXT_V1",
        "corpus_manifest_sha256": document.get("corpus_manifest_sha256"),
        "case_id": case.get("case_id"),
        "subject": case.get("subject"),
        "optional_provenance": case.get("optional_provenance"),
        "evidence_file_hashes": manifest_case.get("files", {}),
    }
    return sha256_hex(projection, tag=CONTEXT_TAG)


def claims_identity(case: Mapping[str, Any]) -> str:
    claims = [_claim_identity_projection(claim) for claim in case.get("expected_claims", [])]
    claims.sort(key=lambda item: item.get("claim_id", ""))
    return sha256_hex(claims, tag=CLAIMS_TAG)


def claims_merkle_root(case: Mapping[str, Any]) -> str:
    leaves = [sha256_hex(_claim_identity_projection(claim), tag=CLAIMS_TAG) for claim in case.get("expected_claims", [])]
    return sha256_hex(sorted(leaves), tag=CLAIMS_ROOT_TAG)


def unification_id(document: Mapping[str, Any], case: Mapping[str, Any]) -> str:
    projection = {
        "subject": case.get("subject"),
        "claims_root": claims_merkle_root(case),
        "context_sha256": case.get("context", {}).get("context_sha256"),
        "policy_action": case.get("policy_action"),
        "decision_semantics_version": case.get("policy_action", {}).get("decision_semantics_version"),
    }
    return sha256_hex(projection, tag=UNIFICATION_TAG)


def _claim_identity_projection(claim: Any) -> Any:
    if not isinstance(claim, Mapping):
        return claim
    return {key: value for key, value in claim.items() if key != "subject"}


def _validate_schema(document: Mapping[str, Any], schema: Mapping[str, Any]) -> list[dict[str, Any]]:
    violations = _schema_errors(document, schema, schema, path="$")
    if not violations:
        return []
    return [
        _check(
            "SCHEMA_V1_VALIDATION",
            "FAIL",
            "SCHEMA_V1_VALIDATION_FAILED",
            details={"violations": violations[:25], "violation_count": len(violations)},
        )
    ]


def _validate_corpus_binding(
    document: Mapping[str, Any],
    manifest: Mapping[str, Any],
    manifest_path: Path,
    cases: list[Mapping[str, Any]],
    relationships: list[Mapping[str, Any]],
    repo_root: Path,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if sha256(manifest_path.read_bytes()).hexdigest() != CORPUS_MANIFEST_SHA256:
        errors.append(_check("CORPUS_BINDING", "FAIL", "ACCEPTED_CORPUS_MANIFEST_HASH_MISMATCH"))
    if document.get("corpus_manifest_sha256") != CORPUS_MANIFEST_SHA256:
        errors.append(_check("CORPUS_BINDING", "FAIL", "ORACLE_CORPUS_MANIFEST_HASH_MISMATCH"))
    manifest_cases = _manifest_cases(manifest)
    document_ids = [case.get("case_id") for case in cases]
    if len(document_ids) != len(set(document_ids)):
        errors.append(_check("CASE_INTEGRITY", "FAIL", "DUPLICATE_CASE_ID"))
    missing = sorted(set(manifest_cases) - set(document_ids))
    extra = sorted(set(document_ids) - set(manifest_cases))
    if missing:
        errors.append(_check("CASE_INTEGRITY", "FAIL", "MISSING_ACCEPTED_CORPUS_CASE", details={"case_ids": missing}))
    if extra:
        errors.append(_check("CASE_INTEGRITY", "FAIL", "EXTRA_NON_CORPUS_CASE", details={"case_ids": extra}))
    manifest_pairs = {pair["pair_id"]: pair for pair in manifest.get("mutation_pairs", [])}
    relationship_ids = [item.get("pair_id") for item in relationships]
    if len(relationship_ids) != len(set(relationship_ids)):
        errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "DUPLICATE_MUTATION_PAIR_ID"))
    missing_pairs = sorted(set(manifest_pairs) - set(relationship_ids))
    extra_pairs = sorted(set(relationship_ids) - set(manifest_pairs))
    if missing_pairs:
        errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "MISSING_ACCEPTED_MUTATION_PAIR", details={"pair_ids": missing_pairs}))
    if extra_pairs:
        errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "EXTRA_MUTATION_PAIR", details={"pair_ids": extra_pairs}))
    if _contains_key(document, "producer_output") or _contains_key(document, "producer_output_seen"):
        errors.append(_check("CORPUS_BINDING", "FAIL", "PRODUCER_OUTPUT_OBSERVED"))
    for case_id, manifest_case in manifest_cases.items():
        case_dir = repo_root / "research" / "terraform_plan_contract" / "cases" / case_id
        for filename, expected_hash in (manifest_case.get("files") or {}).items():
            file_path = case_dir / filename
            if not file_path.exists():
                errors.append(_check("CASE_INTEGRITY", "FAIL", "CASE_FILE_MISSING", case_id=case_id, details={"file": filename}))
                continue
            actual_hash = sha256(file_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                errors.append(_check("CASE_INTEGRITY", "FAIL", "CASE_FILE_HASH_MISMATCH", case_id=case_id, details={"file": filename}))
    return errors


def _validate_cases(
    document: Mapping[str, Any],
    manifest: Mapping[str, Any],
    cases: list[Mapping[str, Any]],
    repo_root: Path,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    manifest_cases = _manifest_cases(manifest)
    for case in cases:
        case_id = str(case.get("case_id", ""))
        manifest_case = manifest_cases.get(case_id)
        if manifest_case is None:
            continue
        errors.extend(_validate_case_hashes(document, case, manifest_case, repo_root))
        errors.extend(_validate_claims(case, manifest_case, repo_root))
        errors.extend(_validate_explicit_lists(case))
        errors.extend(_validate_optional_provenance(case, manifest_case))
        errors.extend(_validate_policy_action(case))
    return errors


def _validate_case_hashes(
    document: Mapping[str, Any],
    case: Mapping[str, Any],
    manifest_case: Mapping[str, Any],
    repo_root: Path,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_id = str(case.get("case_id", ""))
    files = manifest_case.get("files") or {}
    plan_file = "plan.json" if "plan.json" in files else "plan.json.invalid"
    subject = case.get("subject") if isinstance(case.get("subject"), Mapping) else {}
    if subject.get("sha256") != files.get(plan_file):
        errors.append(_check("HASH_RECOMPUTATION", "FAIL", "SUBJECT_HASH_MISMATCH", case_id=case_id))
    expected_context = context_sha256(document, case, manifest_case)
    if case.get("context", {}).get("context_sha256") != expected_context:
        errors.append(_check("HASH_RECOMPUTATION", "FAIL", "CONTEXT_HASH_MISMATCH", case_id=case_id))
    expected_unification = unification_id(document, case)
    if case.get("context", {}).get("unification_id_expected") != expected_unification:
        errors.append(_check("HASH_RECOMPUTATION", "FAIL", "UNIFICATION_ID_MISMATCH", case_id=case_id))
    return errors


def _validate_claims(case: Mapping[str, Any], manifest_case: Mapping[str, Any], repo_root: Path) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_id = str(case.get("case_id", ""))
    subject = case.get("subject")
    claims = list(case.get("expected_claims") or [])
    claim_ids = [claim.get("claim_id") for claim in claims if isinstance(claim, Mapping)]
    if len(claim_ids) != len(set(claim_ids)):
        errors.append(_check("CLAIM_VALIDATION", "FAIL", "DUPLICATE_CLAIM_ID", case_id=case_id))
    for claim in claims:
        if not isinstance(claim, Mapping):
            continue
        if claim.get("subject") != subject:
            errors.append(_check("CLAIM_VALIDATION", "FAIL", "CLAIM_SUBJECT_MISMATCH", case_id=case_id))
        claim_type = claim.get("claim_type")
        value = claim.get("value") if isinstance(claim.get("value"), Mapping) else {}
        if claim_type in ACTION_BY_CLAIM and "action_sequence" in value and value.get("action_sequence") != ACTION_BY_CLAIM[claim_type]:
            errors.append(_check("RESOURCE_ACTION_SEQUENCE", "FAIL", "ACTION_SEQUENCE_MISMATCH", case_id=case_id))
        if claim_type == "TERRAFORM_RESOURCE_ACTION_SEQUENCE" and value.get("action_sequence") not in (
            ["create"],
            ["update"],
            ["delete"],
            ["read"],
            ["no-op"],
            ["delete", "create"],
            ["create", "delete"],
        ):
            errors.append(_check("RESOURCE_ACTION_SEQUENCE", "FAIL", "ACTION_SEQUENCE_MISMATCH", case_id=case_id))
        if claim_type == "TERRAFORM_RESOURCE_REPLACE" and "action_sequence" in value:
            action_sequence = value.get("action_sequence")
            if action_sequence not in (["delete", "create"], ["create", "delete"]):
                errors.append(_check("RESOURCE_ACTION_SEQUENCE", "FAIL", "REPLACE_ACTION_SEQUENCE_INVALID", case_id=case_id))
        if claim_type in ("PLANNED_VALUE_UNKNOWN", "SENSITIVE_PATH_PRESENT") and claim.get("status") != "NOT_EVALUATED":
            errors.append(_check("NOT_EVALUATED", "FAIL", "STRUCTURAL_UNKNOWN_OR_SENSITIVE_NOT_NOT_EVALUATED", case_id=case_id))
        if "string" in value and SECRET_PATTERN.search(str(value["string"])):
            errors.append(_check("SENSITIVE_VALUE_ABSENCE", "FAIL", "SENSITIVE_VALUE_EXPOSED", case_id=case_id))
        errors.extend(_validate_evidence_locators(case_id, claim.get("evidence") or [], manifest_case, repo_root))
    return errors


def _validate_evidence_locators(
    case_id: str,
    evidence: list[Any],
    manifest_case: Mapping[str, Any],
    repo_root: Path,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_dir = repo_root / "research" / "terraform_plan_contract" / "cases" / case_id
    files = manifest_case.get("files") or {}
    for item in evidence:
        if not isinstance(item, Mapping):
            continue
        filename = item.get("case_file")
        pointer = item.get("json_pointer")
        if filename not in files:
            errors.append(_check("EVIDENCE_LOCATOR", "FAIL", "EVIDENCE_FILE_NOT_IN_MANIFEST", case_id=case_id, details={"file": filename}))
            continue
        file_path = case_dir / str(filename)
        if filename in ("plan.json", "metadata.json"):
            try:
                data = json.loads(file_path.read_text(encoding="utf-8"))
            except Exception:
                errors.append(_check("EVIDENCE_LOCATOR", "FAIL", "EVIDENCE_JSON_UNREADABLE", case_id=case_id, details={"file": filename}))
                continue
            if not _json_pointer_exists(data, str(pointer)):
                errors.append(_check("EVIDENCE_LOCATOR", "FAIL", "UNRESOLVABLE_EVIDENCE_LOCATOR", case_id=case_id, details={"file": filename, "pointer": pointer}))
        elif filename in ("plan.json.invalid", "main.tf") and pointer not in ("", "/"):
            errors.append(_check("EVIDENCE_LOCATOR", "FAIL", "UNRESOLVABLE_EVIDENCE_LOCATOR", case_id=case_id, details={"file": filename, "pointer": pointer}))
    return errors


def _validate_explicit_lists(case: Mapping[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_id = str(case.get("case_id", ""))
    explicit = case.get("explicit_lists") if isinstance(case.get("explicit_lists"), Mapping) else {}
    for name, values in explicit.items():
        if isinstance(values, list):
            if values != sorted(values):
                errors.append(_check("STRICT_LIST_EQUIVALENCE", "FAIL", "NON_CANONICAL_EXPLICIT_LIST", case_id=case_id, details={"list": name}))
            if len(values) != len(set(values)):
                errors.append(_check("STRICT_LIST_EQUIVALENCE", "FAIL", "DUPLICATE_EXPLICIT_LIST_ITEM", case_id=case_id, details={"list": name}))
    derived = _derive_explicit_lists(case)
    for name, expected in derived.items():
        if list(explicit.get(name, [])) != expected:
            errors.append(
                _check(
                    "STRICT_LIST_EQUIVALENCE",
                    "FAIL",
                    "STRICT_LIST_MISMATCH",
                    case_id=case_id,
                    details={"list": name, "expected": expected, "actual": explicit.get(name, [])},
                )
            )
    return errors


def _derive_explicit_lists(case: Mapping[str, Any]) -> dict[str, list[str]]:
    lists = {
        "create_resources": [],
        "update_resources": [],
        "delete_resources": [],
        "replace_resources": [],
        "read_resources": [],
        "noop_resources": [],
        "replace_paths": [],
        "unknown_paths": [],
        "sensitive_paths": [],
        "not_evaluated": [],
    }
    for claim in case.get("expected_claims", []) or []:
        if not isinstance(claim, Mapping):
            continue
        claim_type = claim.get("claim_type")
        value = claim.get("value") if isinstance(claim.get("value"), Mapping) else {}
        if claim_type in RESOURCE_LIST_BY_CLAIM and "resource_address" in value:
            lists[RESOURCE_LIST_BY_CLAIM[claim_type]].append(str(value["resource_address"]))
        if claim_type == "TERRAFORM_REPLACE_PATH_PRESENT" and "json_pointer" in value:
            lists["replace_paths"].append(str(value["json_pointer"]))
        if claim_type == "PLANNED_VALUE_UNKNOWN" and "json_pointer" in value:
            lists["unknown_paths"].append(str(value["json_pointer"]))
        if claim_type == "SENSITIVE_PATH_PRESENT" and "json_pointer" in value:
            lists["sensitive_paths"].append(str(value["json_pointer"]))
        if claim.get("status") == "NOT_EVALUATED":
            lists["not_evaluated"].append(str(claim.get("claim_id")))
    return {key: sorted(set(values)) for key, values in lists.items()}


def _validate_optional_provenance(case: Mapping[str, Any], manifest_case: Mapping[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_id = str(case.get("case_id", ""))
    manifest_hashes = set((manifest_case.get("files") or {}).values())
    provenance = case.get("optional_provenance") if isinstance(case.get("optional_provenance"), Mapping) else {}
    for name, entry in provenance.items():
        if not isinstance(entry, Mapping):
            continue
        state = entry.get("state")
        if state == "BOUND":
            if "sha256" in entry and entry["sha256"] not in manifest_hashes:
                errors.append(_check("OPTIONAL_PROVENANCE", "FAIL", "BOUND_PROVENANCE_HASH_NOT_RECOMPUTABLE", case_id=case_id, details={"field": name}))
            if "fingerprint" in entry:
                errors.append(_check("OPTIONAL_PROVENANCE", "FAIL", "BOUND_PROVENANCE_FINGERPRINT_CANONICAL_BYTES_NOT_AVAILABLE", case_id=case_id, details={"field": name}))
    return errors


def _validate_policy_action(case: Mapping[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_id = str(case.get("case_id", ""))
    action = case.get("policy_action") if isinstance(case.get("policy_action"), Mapping) else {}
    reasons = action.get("reason_codes") if isinstance(action.get("reason_codes"), list) else []
    if reasons != sorted(reasons) or len(reasons) != len(set(reasons)):
        errors.append(_check("POLICY_ACTION", "FAIL", "REASON_CODES_NOT_CANONICAL", case_id=case_id))
    if action.get("stop") is False and action.get("recommended_agent_action") not in ("PROCEED", "REPORT_WITH_NOTES"):
        errors.append(_check("POLICY_ACTION", "FAIL", "ACTION_STOP_INCONSISTENT", case_id=case_id))
    if action.get("stop") is True and action.get("recommended_agent_action") not in (
        "STOP_BLOCKED",
        "RERUN_REQUIRED",
        "REPORT_NOT_EVALUATED",
    ):
        errors.append(_check("POLICY_ACTION", "FAIL", "ACTION_STOP_INCONSISTENT", case_id=case_id))
    claim_types = {claim.get("claim_type") for claim in case.get("expected_claims", []) if isinstance(claim, Mapping)}
    if "TERRAFORM_PLAN_ERRORED" in claim_types and action.get("recommended_agent_action") not in (
        "STOP_BLOCKED",
        "REPORT_NOT_EVALUATED",
    ):
        errors.append(_check("POLICY_ACTION", "FAIL", "PLAN_ERRORED_ACTION_MISMATCH", case_id=case_id))
    return errors


def _validate_mutation_relationships(
    manifest: Mapping[str, Any],
    cases: list[Mapping[str, Any]],
    relationships: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    case_by_id = {case.get("case_id"): case for case in cases}
    manifest_pairs = {pair["pair_id"]: pair for pair in manifest.get("mutation_pairs", [])}
    for relationship in relationships:
        if not isinstance(relationship, Mapping):
            continue
        pair_id = str(relationship.get("pair_id", ""))
        manifest_pair = manifest_pairs.get(pair_id)
        if manifest_pair is None:
            continue
        if relationship.get("declared_delta") != manifest_pair.get("declared_delta"):
            errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "DECLARED_DELTA_MISMATCH", pair_id=pair_id))
        if relationship.get("expected_claims_relation") != manifest_pair.get("expected_claims_relation"):
            errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "MANIFEST_CLAIMS_RELATION_MISMATCH", pair_id=pair_id))
        base = case_by_id.get(relationship.get("base_case_id"))
        mutated = case_by_id.get(relationship.get("mutated_case_id"))
        if base is None or mutated is None:
            errors.append(_check("MUTATION_RELATIONSHIP", "FAIL", "MUTATION_PAIR_REFERENCES_MISSING_CASE", pair_id=pair_id))
            continue
        errors.extend(_check_relation(pair_id, "expected_claims_relation", relationship, claims_identity(base), claims_identity(mutated)))
        errors.extend(_check_relation(pair_id, "expected_claims_root_relation", relationship, claims_merkle_root(base), claims_merkle_root(mutated)))
        errors.extend(
            _check_relation(
                pair_id,
                "expected_unification_id_relation",
                relationship,
                base.get("context", {}).get("unification_id_expected"),
                mutated.get("context", {}).get("unification_id_expected"),
            )
        )
    return errors


def _check_relation(pair_id: str, field: str, relationship: Mapping[str, Any], left: Any, right: Any) -> list[dict[str, Any]]:
    expected = relationship.get(field)
    actual = "SAME" if left == right else "DIFFERENT"
    if expected != actual:
        return [
            _check(
                "MUTATION_RELATIONSHIP",
                "FAIL",
                "MUTATION_RELATION_MISMATCH",
                pair_id=pair_id,
                details={"field": field, "expected": expected, "actual": actual},
            )
        ]
    if actual not in ("SAME", "DIFFERENT"):
        return [_check("MUTATION_RELATIONSHIP", "FAIL", "RELATIONSHIP_NOT_SYMMETRIC", pair_id=pair_id)]
    return []


def _validate_not_claimed(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    required = {
        "INFRASTRUCTURE_CORRECTNESS",
        "INFRASTRUCTURE_SECURITY",
        "INFRASTRUCTURE_COST",
        "INFRASTRUCTURE_COMPLIANCE",
        "APPLY_SUCCESS",
        "LIVE_STATE_FRESHNESS",
        "GATE_B_REUSE",
        "TERRAFORM_PROVIDER_SAFETY",
        "KUBERNETES_SUPPORT",
        "DOMAIN_4",
        "MVP_INCLUSION",
        "RELEASE",
    }
    present = set(document.get("not_claimed") or [])
    if not required.issubset(present):
        return [_check("NOT_CLAIMED", "FAIL", "NOT_CLAIMED_BOUNDARY_MISSING", details={"missing": sorted(required - present)})]
    return []


def _schema_errors(value: Any, schema: Any, root_schema: Mapping[str, Any], *, path: str) -> list[str]:
    if schema is True:
        return []
    if schema is False:
        return [f"{path}: false schema"]
    if not isinstance(schema, Mapping):
        return []
    if "$ref" in schema:
        return _schema_errors(value, _resolve_ref(str(schema["$ref"]), root_schema), root_schema, path=path)
    errors: list[str] = []
    if "type" in schema and not _schema_type_matches(value, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}")
        return errors
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")
    if isinstance(value, str) and "pattern" in schema:
        try:
            if re.search(str(schema["pattern"]), value) is None:
                errors.append(f"{path}: pattern mismatch")
        except re.error as exc:
            raise TerraformPlanOracleValidatorToolError(f"invalid schema pattern at {path}: {exc}") from exc
    if isinstance(value, list):
        if "minItems" in schema and len(value) < int(schema["minItems"]):
            errors.append(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(value) > int(schema["maxItems"]):
            errors.append(f"{path}: more than maxItems")
        if schema.get("uniqueItems") is True and len({_json_key(item) for item in value}) != len(value):
            errors.append(f"{path}: duplicate array items")
        if isinstance(schema.get("items"), Mapping):
            for index, item in enumerate(value):
                errors.extend(_schema_errors(item, schema["items"], root_schema, path=f"{path}[{index}]"))
    if isinstance(value, Mapping):
        if "minProperties" in schema and len(value) < int(schema["minProperties"]):
            errors.append(f"{path}: fewer than minProperties")
        if "maxProperties" in schema and len(value) > int(schema["maxProperties"]):
            errors.append(f"{path}: more than maxProperties")
        for field in schema.get("required") or []:
            if field not in value:
                errors.append(f"{path}: missing required field {field}")
        properties = schema.get("properties") or {}
        for field, item in value.items():
            if field in properties:
                errors.extend(_schema_errors(item, properties[field], root_schema, path=f"{path}.{field}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property {field}")
            elif isinstance(schema.get("additionalProperties"), Mapping):
                errors.extend(_schema_errors(item, schema["additionalProperties"], root_schema, path=f"{path}.{field}"))
    for sub_schema in schema.get("allOf") or []:
        errors.extend(_schema_errors(value, sub_schema, root_schema, path=path))
    if "anyOf" in schema and not any(not _schema_errors(value, sub, root_schema, path=path) for sub in schema["anyOf"]):
        errors.append(f"{path}: anyOf constraint not satisfied")
    if "not" in schema and not _schema_errors(value, schema["not"], root_schema, path=path):
        errors.append(f"{path}: not constraint matched")
    if "if" in schema and not _schema_errors(value, schema["if"], root_schema, path=path):
        if "then" in schema:
            errors.extend(_schema_errors(value, schema["then"], root_schema, path=path))
    return errors


def _resolve_ref(ref: str, root_schema: Mapping[str, Any]) -> Any:
    if not ref.startswith("#/"):
        raise TerraformPlanOracleValidatorToolError(f"unsupported schema ref: {ref}")
    target: Any = root_schema
    for part in ref[2:].split("/"):
        target = target[part]
    return target


def _schema_type_matches(value: Any, expected: Any) -> bool:
    if isinstance(expected, list):
        return any(_schema_type_matches(value, item) for item in expected)
    return {
        "object": isinstance(value, Mapping),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool),
        "null": value is None,
    }.get(str(expected), True)


def _json_pointer_exists(value: Any, pointer: str) -> bool:
    if pointer in ("", "/"):
        return True
    if not pointer.startswith("/"):
        return False
    current = value
    for raw_part in pointer.split("/")[1:]:
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(current, Mapping):
            if part not in current:
                return False
            current = current[part]
        elif isinstance(current, list):
            if not part.isdigit() or int(part) >= len(current):
                return False
            current = current[int(part)]
        else:
            return False
    return True


def _report(
    *,
    input_path: str | Path | None,
    input_sha256: str,
    errors: list[dict[str, Any]],
    document: Mapping[str, Any] | None = None,
    tool_error: bool = False,
) -> dict[str, Any]:
    verdict = "PASS"
    status = "DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATION_PASS"
    if tool_error:
        verdict = "TOOL_ERROR"
        status = "ORACLE_VALIDATOR_TOOL_ERROR"
    elif errors:
        verdict = "FAIL"
        status = "ORACLE_VALIDATION_FAILED"
    checks = errors or [_check("VALIDATION", "PASS", "ALL_VALIDATION_CHECKS_PASSED")]
    return {
        "schema": RESULT_SCHEMA,
        "schema_version": RESULT_SCHEMA_VERSION,
        "verdict": verdict,
        "status": status,
        "input": {"path": str(input_path) if input_path is not None else None, "sha256": input_sha256},
        "counts": {
            "case_count": len(document.get("cases", [])) if isinstance(document, Mapping) else 0,
            "validated_case_count": len(document.get("cases", [])) if verdict == "PASS" and isinstance(document, Mapping) else 0,
            "mutation_relationship_count": len(document.get("mutation_relationships", [])) if isinstance(document, Mapping) else 0,
            "error_count": len(errors),
        },
        "checks": checks,
        "not_authorized": NOT_AUTHORIZED,
    }


def _check(
    check_id: str,
    status: str,
    error_code: str,
    *,
    case_id: str | None = None,
    pair_id: str | None = None,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"check_id": check_id, "status": status, "error_code": error_code}
    if case_id is not None:
        item["case_id"] = case_id
    if pair_id is not None:
        item["pair_id"] = pair_id
    if details:
        item["details"] = dict(details)
    return item


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_cases(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {case["case_id"]: case for case in manifest.get("cases", [])}


def _json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, Mapping):
        return key in value or any(_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_contains_key(item, key) for item in value)
    return False
