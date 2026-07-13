from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from . import terraform_plan_producer
from . import test_build_failure_producer


SCHEMA = "SPIRA_MVP_UNIFIED_LOCAL_RESULT_V1"
CONTRACT_SCHEMA = "SPIRA_MVP_UNIFIED_AGENT_CONTRACT_V1"
SUPPORTED_DOMAINS = {
    "python_artifact",
    "pytest_result",
    "terraform_plan",
}
DOMAIN1_BASELINE_ROOT = "85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c"


class MvpUnifiedError(ValueError):
    """Raised when routing would be ambiguous or outside the accepted MVP boundary."""


def route(
    *,
    domain: str | None = None,
    evidence_path: str | Path | None = None,
    case_id: str | None = None,
    root: str | Path,
) -> dict[str, Any]:
    """Route evidence to an accepted domain producer and wrap it in the unified MVP envelope."""

    resolved_domain = resolve_domain(domain=domain, evidence_path=evidence_path)
    if case_id is None and resolved_domain != "python_artifact":
        raise MvpUnifiedError("case_id is required for pytest_result and terraform_plan routing")
    return produce_case(resolved_domain, case_id=case_id, root=root)


def resolve_domain(*, domain: str | None = None, evidence_path: str | Path | None = None) -> str:
    if domain is not None:
        if domain not in SUPPORTED_DOMAINS:
            raise MvpUnifiedError(f"unsupported domain: {domain}")
        return domain
    if evidence_path is None:
        raise MvpUnifiedError("explicit domain is required when evidence path is not provided")
    path = Path(evidence_path)
    candidates = []
    name = path.name.lower()
    if name in {"metadata.json", "junit.xml"} or "test_build_failure_contract" in path.as_posix():
        candidates.append("pytest_result")
    if name in {"plan.json", "plan.json.invalid"} or "terraform_plan_contract" in path.as_posix():
        candidates.append("terraform_plan")
    if path.suffix.lower() == ".whl":
        candidates.append("python_artifact")
    candidates = sorted(set(candidates))
    if len(candidates) != 1:
        raise MvpUnifiedError("AMBIGUOUS_DOMAIN")
    return candidates[0]


def produce_domain(domain: str, *, root: str | Path) -> dict[str, Any]:
    if domain == "python_artifact":
        return domain1_summary(root=root)
    if domain == "pytest_result":
        cases = test_build_failure_producer.produce_cases(_read_json(_domain2_manifest(root)), root=root)
        return {"domain": domain, "cases": [wrap_case(domain, item) for item in cases]}
    if domain == "terraform_plan":
        produced = terraform_plan_producer.produce_cases(_read_json(_domain3_manifest(root)), root=root)
        return {
            "domain": domain,
            "cases": [wrap_case(domain, item) for item in produced["cases"]],
            "mutation_relationships": deepcopy(produced["mutation_relationships"]),
        }
    raise MvpUnifiedError(f"unsupported domain: {domain}")


def produce_case(domain: str, *, case_id: str | None, root: str | Path) -> dict[str, Any]:
    if domain == "python_artifact":
        return wrap_domain1_record(case_id=case_id, root=root)
    domain_result = produce_domain(domain, root=root)
    for item in domain_result["cases"]:
        if item["case_id"] == case_id:
            return item
    raise MvpUnifiedError(f"case not found for {domain}: {case_id}")


def wrap_case(domain: str, producer_output: Mapping[str, Any]) -> dict[str, Any]:
    output = deepcopy(dict(producer_output))
    projection = producer_contract_projection(domain, output)
    direct_hash = sha256_canonical(projection)
    envelope = {
        "schema": SCHEMA,
        "schema_version": 1,
        "domain": domain,
        "case_id": output["case_id"],
        "stop": projection["policy_action"]["stop"],
        "recommended_agent_action": projection["policy_action"]["recommended_agent_action"],
        "reason_codes": projection["policy_action"]["reason_codes"],
        "not_evaluated": projection["not_evaluated"],
        "block": projection["block"],
        "proof_reference": projection["proof_reference"],
        "evidence_pointers": projection["evidence_pointers"],
        "not_claimed": projection["not_claimed"],
        "direct_contract_hash": direct_hash,
        "unified_contract_hash": direct_hash,
        "semantic_drift": False,
        "producer_output": output,
    }
    return envelope


def wrap_domain1_record(*, case_id: str | None, root: str | Path) -> dict[str, Any]:
    baseline = _read_json(_domain1_baseline(root))
    records = baseline.get("records") or []
    if case_id is None:
        record = records[0]
    else:
        record = next((item for item in records if item.get("artifact_sha256") == case_id), None)
        if record is None:
            raise MvpUnifiedError(f"Domain 1 artifact not found: {case_id}")
    output = {
        "case_id": record["artifact_sha256"],
        "artifact_sha256": record["artifact_sha256"],
        "subject": {
            "type": record["subject_type"],
            "sha256": record["subject_sha256"],
        },
        "claims_identity": {
            "canonical_claims_bytes_sha256": record["canonical_claims_bytes_sha256"],
            "claims_merkle_root": record["claims_merkle_root"],
        },
        "context_sha256": record["context_sha256"],
        "unification_id": record["unification_id"],
        "policy_action": {
            "stop": bool(record["stop"]),
            "recommended_agent_action": record["recommended_agent_action"],
            "reason_codes": list(record["reason_codes"]),
            "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        },
        "not_evaluated": list(record["not_evaluated"]),
        "worst_claim_status": record["worst_claim_status"],
        "proof_reference": {
            "id": record["unification_id"],
            "root": record["claims_merkle_root"],
            "compact_reference_bytes_sha256": record["compact_reference_bytes_sha256"],
        },
        "not_claimed": ["software_safety", "package_safety", "universal_supply_chain_coverage"],
    }
    projection = producer_contract_projection("python_artifact", output)
    contract_hash = sha256_canonical(projection)
    return {
        "schema": SCHEMA,
        "schema_version": 1,
        "domain": "python_artifact",
        "case_id": output["case_id"],
        "stop": projection["policy_action"]["stop"],
        "recommended_agent_action": projection["policy_action"]["recommended_agent_action"],
        "reason_codes": projection["policy_action"]["reason_codes"],
        "not_evaluated": projection["not_evaluated"],
        "block": projection["block"],
        "proof_reference": projection["proof_reference"],
        "evidence_pointers": [],
        "not_claimed": projection["not_claimed"],
        "direct_contract_hash": contract_hash,
        "unified_contract_hash": contract_hash,
        "semantic_drift": False,
        "producer_output": output,
    }


def domain1_summary(*, root: str | Path) -> dict[str, Any]:
    baseline = _read_json(_domain1_baseline(root))
    return {
        "domain": "python_artifact",
        "baseline_root": baseline.get("domain1_identity_baseline_root"),
        "accepted_baseline_root": DOMAIN1_BASELINE_ROOT,
        "record_count": len(baseline.get("records") or []),
        "baseline_root_check": "PASS"
        if baseline.get("domain1_identity_baseline_root") == DOMAIN1_BASELINE_ROOT and len(baseline.get("records") or []) == 1954
        else "FAIL",
    }


def producer_contract_projection(domain: str, output: Mapping[str, Any]) -> dict[str, Any]:
    if domain == "python_artifact":
        action = dict(output["policy_action"])
        return {
            "domain": domain,
            "case_id": output["case_id"],
            "subject": output["subject"],
            "claims": output["claims_identity"],
            "policy_action": _sorted_action(action),
            "not_evaluated": sorted(output.get("not_evaluated") or []),
            "block": [output["worst_claim_status"]] if output.get("worst_claim_status") == "BLOCK" else [],
            "proof_reference": output["proof_reference"],
            "evidence_pointers": [],
            "not_claimed": sorted(output.get("not_claimed") or []),
        }
    if domain == "pytest_result":
        action = dict(output["produced_policy_action"])
        return {
            "domain": domain,
            "case_id": output["case_id"],
            "subject": {
                "scope_identity_sha256": output["produced_scope_identity"].get("scope_identity_sha256"),
                "result_identity_sha256": output["produced_result_identity"].get("result_identity_sha256"),
            },
            "claims": output["produced_claims"],
            "explicit_lists": output["produced_explicit_lists"],
            "policy_action": _sorted_action(action),
            "not_evaluated": sorted(output.get("produced_not_evaluated") or []),
            "block": _block_claim_ids(output["produced_claims"]),
            "proof_reference": {
                "scope_identity_sha256": output["produced_scope_identity"].get("scope_identity_sha256"),
                "result_identity_sha256": output["produced_result_identity"].get("result_identity_sha256"),
            },
            "evidence_pointers": output.get("produced_evidence_locators") or [],
            "not_claimed": sorted(output.get("produced_not_claimed") or []),
        }
    if domain == "terraform_plan":
        action = dict(output["produced_policy_action"])
        return {
            "domain": domain,
            "case_id": output["case_id"],
            "subject": output["produced_subject"],
            "context": output["produced_context"],
            "claims": output["produced_claims"],
            "explicit_lists": output["produced_explicit_lists"],
            "policy_action": _sorted_action(action),
            "not_evaluated": sorted(output.get("produced_explicit_lists", {}).get("not_evaluated") or []),
            "block": _block_claim_ids(output["produced_claims"]),
            "proof_reference": {
                "id": output["produced_context"].get("unification_id_expected"),
                "context_sha256": output["produced_context"].get("context_sha256"),
            },
            "evidence_pointers": output.get("produced_evidence_locators") or [],
            "not_claimed": sorted(output.get("produced_not_claimed") or []),
        }
    raise MvpUnifiedError(f"unsupported domain: {domain}")


def agent_contract(envelope: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": CONTRACT_SCHEMA,
        "schema_version": 1,
        "domain": envelope["domain"],
        "case_id": envelope["case_id"],
        "stop": envelope["stop"],
        "recommended_agent_action": envelope["recommended_agent_action"],
        "reason_codes": envelope["reason_codes"],
        "not_evaluated": envelope["not_evaluated"],
        "block": envelope["block"],
        "proof_reference": envelope["proof_reference"],
        "producer_contract_hash": envelope["direct_contract_hash"],
        "evidence_pointer_count": len(envelope.get("evidence_pointers") or []),
        "not_claimed": envelope["not_claimed"],
    }


def domain_contract_for_agent(domain: str, producer_output: Mapping[str, Any]) -> dict[str, Any]:
    projection = producer_contract_projection(domain, producer_output)
    return {
        "schema": "SPIRA_DOMAIN_COMPACT_AGENT_CONTRACT_V1",
        "schema_version": 1,
        "domain": domain,
        "case_id": projection["case_id"],
        "policy_action": projection["policy_action"],
        "not_evaluated": projection["not_evaluated"],
        "block": projection["block"],
        "proof_reference": projection["proof_reference"],
        "producer_contract_hash": sha256_canonical(projection),
        "evidence_pointer_count": len(projection.get("evidence_pointers") or []),
        "not_claimed": projection["not_claimed"],
    }


def raw_evidence_payload(domain: str, case_id: str, *, root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    if domain == "python_artifact":
        record = wrap_domain1_record(case_id=case_id, root=root)["producer_output"]
        return {"domain": domain, "case_id": case_id, "raw_baseline_record": record}
    if domain == "pytest_result":
        manifest_case = _manifest_case(_read_json(_domain2_manifest(root)), case_id)
        return {"domain": domain, "case_id": case_id, "sources": _case_file_payloads(manifest_case.get("input_sources", []), root_path)}
    if domain == "terraform_plan":
        manifest_case = _manifest_case(_read_json(_domain3_manifest(root)), case_id)
        files = [
            {"path": f"research/terraform_plan_contract/cases/{case_id}/{name}", "source_id": name}
            for name in sorted(manifest_case.get("files") or {})
        ]
        return {"domain": domain, "case_id": case_id, "sources": _case_file_payloads(files, root_path)}
    raise MvpUnifiedError(f"unsupported domain: {domain}")


def sha256_canonical(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sorted_action(action: Mapping[str, Any]) -> dict[str, Any]:
    item = dict(action)
    item["reason_codes"] = sorted(item.get("reason_codes") or [])
    return item


def _block_claim_ids(claims: list[Mapping[str, Any]]) -> list[str]:
    return sorted(str(claim.get("claim_id")) for claim in claims if claim.get("status") == "BLOCK")


def _case_file_payloads(sources: list[Mapping[str, Any]], root: Path) -> list[dict[str, Any]]:
    payloads = []
    for source in sources:
        path = source.get("path")
        if not path:
            continue
        full_path = root / str(path)
        if not full_path.exists():
            continue
        raw = full_path.read_bytes()
        payloads.append(
            {
                "source_id": source.get("source_id"),
                "path": str(path),
                "sha256": sha256(raw).hexdigest(),
                "byte_count": len(raw),
                "text": raw.decode("utf-8", errors="replace"),
            }
        )
    return payloads


def _manifest_case(manifest: Mapping[str, Any], case_id: str) -> Mapping[str, Any]:
    for item in manifest.get("cases", []):
        if item.get("case_id") == case_id:
            return item
    raise MvpUnifiedError(f"case not found: {case_id}")


def _domain1_baseline(root: str | Path) -> Path:
    return Path(root) / "research" / "unification_proof_corpus" / "results" / "domain1_identity_baseline_v1.json"


def _domain2_manifest(root: str | Path) -> Path:
    return Path(root) / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json"


def _domain3_manifest(root: str | Path) -> Path:
    return Path(root) / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
