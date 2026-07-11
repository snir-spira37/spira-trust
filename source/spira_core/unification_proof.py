from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata as importlib_metadata
from typing import Any, Mapping

from .combined_verdict import DECISION_SEMANTICS_VERSION


UNIFICATION_PROOF_SCHEMA = "SPIRA_UNIFICATION_PROOF_V1"
UNIFICATION_REFERENCE_SCHEMA = "SPIRA_UNIFICATION_REFERENCE_V1"
CLAIM_SCHEMA = "SPIRA_CLAIM_V1"


STATUS_RANK = {
    "OK": 0,
    "NOTE": 1,
    "WARN": 2,
    "NOT_EVALUATED": 3,
    "RERUN_REQUIRED": 4,
    "BLOCK": 5,
}


class UnificationProofError(ValueError):
    """Raised when a proof-carrying action contract would be ambiguous or unbound."""


def build_unification_proof(summary: Mapping[str, Any], decision: Mapping[str, Any]) -> dict[str, Any]:
    contract = summary.get("agent_action_contract", {}) or {}
    summary_of = summary.get("summary_of", {}) or {}
    claims = build_claims(summary, decision)
    validate_claim_set(claims)
    claims_root = merkle_root(claims)
    policy_sha = str(contract.get("policy_sha256") or "")
    subject_sha = str(contract.get("artifact_sha256") or contract.get("artifact_set_sha256") or "")
    validate_sha256(subject_sha, field="subject_sha256")
    context_sha = sha256_hex(
        {
            "subject_sha256": subject_sha,
            "artifact_set_sha256": contract.get("artifact_set_sha256"),
            "command_fingerprint": contract.get("command_fingerprint"),
            "policy_sha256": contract.get("policy_sha256"),
            "tool_version": summary_of.get("tool_version") or (summary.get("tool") or {}).get("version"),
            "decision_semantics_version": contract.get("decision_semantics_version") or DECISION_SEMANTICS_VERSION,
            "decision_sha256": summary_of.get("decision_sha256"),
            "graph_report_sha256": summary_of.get("graph_report_sha256"),
        }
    )
    decision_obj = {
        "semantics_version": contract.get("decision_semantics_version") or DECISION_SEMANTICS_VERSION,
        "verdict": contract.get("action_verdict") or summary.get("action_verdict"),
        "graph_verdict": contract.get("graph_verdict") or summary.get("verdict"),
        "combined_verdict": contract.get("combined_verdict") or summary.get("combined_verdict"),
        "stop": bool(contract.get("stop")),
        "recommended_agent_action": contract.get("recommended_agent_action"),
        "reason_codes": sorted(dict.fromkeys(contract.get("reason_codes") or [])),
        "not_evaluated": sorted(dict.fromkeys(contract.get("not_evaluated") or [])),
    }
    unification_id = tagged_hash(
        "SPIRA:UNIFICATION:V1",
        subject_sha,
        claims_root,
        policy_sha,
        context_sha,
        str(decision_obj["semantics_version"]),
        sha256_hex(decision_obj),
    )
    not_evaluated = sorted(
        dict.fromkeys(
            [
                str(claim.get("claim_id"))
                for claim in claims
                if claim.get("status") == "NOT_EVALUATED"
            ]
        )
    )
    return {
        "schema": UNIFICATION_PROOF_SCHEMA,
        "schema_version": "1.0",
        "created_at": utc_now(),
        "subject": {
            "type": "python_wheel" if contract.get("artifact_sha256") else "python_wheel_set",
            "sha256": subject_sha,
            "artifact_set_sha256": contract.get("artifact_set_sha256"),
        },
        "roots": {
            "claims_merkle_root": claims_root,
            "policy_sha256": contract.get("policy_sha256"),
            "context_sha256": context_sha,
        },
        "decision": decision_obj,
        "coverage": {
            "claim_count": len(claims),
            "not_evaluated": not_evaluated,
            "worst_claim_status": worst_claim_status(claims),
        },
        "claims": claims,
        "proof": {
            "inclusion_proofs_available": True,
            "hash_algorithm": "sha256",
            "canonicalization": "json-sort-keys-no-extra-whitespace-utf8",
            "domain_separation": "leaf=0x00 node=0x01",
        },
        "unification_id": unification_id,
        "not_claimed": [
            "unification proof binds claims, policy/context roots, and action; it does not prove the artifact is safe",
            "hashes prove byte binding, not producer identity or truth by themselves",
            "signatures or attestations are separate identity layers",
            "not-evaluated claims remain explicit and are not treated as OK",
        ],
    }


def build_unification_reference(proof: Mapping[str, Any], *, proof_path: str | None = None) -> dict[str, Any]:
    roots = proof.get("roots", {}) or {}
    return {
        "id": proof.get("unification_id"),
        "root": roots.get("claims_merkle_root"),
        "p": proof_path,
    }


def build_claims(summary: Mapping[str, Any], decision: Mapping[str, Any]) -> list[dict[str, Any]]:
    layers = ((decision.get("layers", {}) or {}).get("per_layer", []) or [])
    contract = summary.get("agent_action_contract", {}) or {}
    subject_sha = str(contract.get("artifact_sha256") or contract.get("artifact_set_sha256") or "")
    claims: list[dict[str, Any]] = []
    for layer in layers:
        if not isinstance(layer, Mapping):
            continue
        layer_name = str(layer.get("layer") or "unknown")
        status = normalize_claim_status(str(layer.get("status") or "NOT_EVALUATED"))
        claim = {
            "schema": CLAIM_SCHEMA,
            "schema_version": "1.0",
            "claim_id": f"spira.layer.{layer_name}",
            "subject_sha256": subject_sha,
            "status": status,
            "value": {
                "layer": layer_name,
                "evaluated": bool(layer.get("evaluated")),
                "source_verdict": layer.get("source_verdict"),
                "finding_count": int(layer.get("finding_count") or 0),
            },
            "producer": {
                "name": "spira-trust",
                "version": tool_version(),
            },
            "evidence_ref": layer.get("evidence_ref"),
            "policy_ref": layer.get("policy_ref"),
            "reason_codes": reason_codes_for_claim(layer_name, status, layer),
        }
        claims.append(claim)
    if not claims:
        claims.append(
            {
                "schema": CLAIM_SCHEMA,
                "schema_version": "1.0",
                "claim_id": "spira.layers",
                "subject_sha256": subject_sha,
                "status": "NOT_EVALUATED",
                "value": {
                    "layer": "combined_policy_verdict",
                    "evaluated": False,
                    "source_verdict": "MISSING_PER_LAYER_CLAIMS",
                    "finding_count": 0,
                },
                "producer": {
                    "name": "spira-trust",
                    "version": tool_version(),
                },
                "evidence_ref": None,
                "policy_ref": None,
                "reason_codes": ["MISSING_PER_LAYER_CLAIMS"],
            }
        )
    return sorted(claims, key=lambda claim: str(claim.get("claim_id") or ""))


def normalize_claim_status(status: str) -> str:
    status = status.upper()
    if status in STATUS_RANK:
        return status
    raise UnificationProofError(f"unknown claim status: {status}")


def validate_claim_set(claims: list[Mapping[str, Any]]) -> None:
    seen: set[str] = set()
    for claim in claims:
        claim_id = str(claim.get("claim_id") or "")
        if not claim_id:
            raise UnificationProofError("claim_id is required")
        if claim_id in seen:
            raise UnificationProofError(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        validate_sha256(str(claim.get("subject_sha256") or ""), field=f"{claim_id}.subject_sha256")
        normalize_claim_status(str(claim.get("status") or ""))


def validate_sha256(value: str, *, field: str) -> None:
    if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise UnificationProofError(f"{field} must be a lowercase 64-character SHA-256 hex value")


def reason_codes_for_claim(layer_name: str, status: str, layer: Mapping[str, Any]) -> list[str]:
    codes = []
    if status == "BLOCK":
        codes.append("BLOCKING_CLAIM")
    if status == "WARN":
        codes.append("WARNING_CLAIM")
    if status == "NOTE":
        codes.append("NOTE_CLAIM")
    if status == "NOT_EVALUATED":
        codes.append("CLAIM_NOT_EVALUATED")
    if status == "RERUN_REQUIRED":
        codes.append("CLAIM_RERUN_REQUIRED")
    source = layer.get("source_verdict")
    if source:
        codes.append(str(source))
    codes.append(layer_name)
    return sorted(dict.fromkeys(codes))


def worst_claim_status(claims: list[Mapping[str, Any]]) -> str:
    if not claims:
        return "NOT_EVALUATED"
    return max((str(claim.get("status") or "NOT_EVALUATED") for claim in claims), key=lambda status: STATUS_RANK.get(status, 1))


def inclusion_proof(claims: list[Mapping[str, Any]], claim_id: str) -> dict[str, Any]:
    ordered = sorted([dict(claim) for claim in claims], key=lambda claim: str(claim.get("claim_id") or ""))
    ids = [str(claim.get("claim_id") or "") for claim in ordered]
    if claim_id not in ids:
        raise KeyError(claim_id)
    target = ids.index(claim_id)
    leaves = [leaf_hash(claim) for claim in ordered]
    proof = _inclusion_path(leaves, target)
    return {
        "claim_id": claim_id,
        "leaf_index": target,
        "leaf_count": len(leaves),
        "siblings": proof,
        "root": _build_hash(leaves).hex() if leaves else sha256(b"").hexdigest(),
    }


def verify_inclusion(claim: Mapping[str, Any], proof: Mapping[str, Any]) -> bool:
    current = leaf_hash(claim)
    for item in proof.get("siblings", []) or []:
        sibling = bytes.fromhex(str(item.get("hash")))
        if item.get("position") == "left":
            current = node_hash(sibling, current)
        else:
            current = node_hash(current, sibling)
    return current.hex() == proof.get("root")


def merkle_root(claims: list[Mapping[str, Any]]) -> str:
    leaves = [leaf_hash(claim) for claim in sorted(claims, key=lambda claim: str(claim.get("claim_id") or ""))]
    if not leaves:
        return sha256(b"").hexdigest()
    return _build_hash(leaves).hex()


def _inclusion_path(items: list[bytes], index: int) -> list[dict[str, str]]:
    if len(items) <= 1:
        return []
    split = _split_point(len(items))
    if index < split:
        return _inclusion_path(items[:split], index) + [{"position": "right", "hash": _build_hash(items[split:]).hex()}]
    return _inclusion_path(items[split:], index - split) + [{"position": "left", "hash": _build_hash(items[:split]).hex()}]


def _build_hash(items: list[bytes]) -> bytes:
    if len(items) == 1:
        return items[0]
    split = _split_point(len(items))
    return node_hash(_build_hash(items[:split]), _build_hash(items[split:]))


def _split_point(length: int) -> int:
    if length < 2:
        raise ValueError("length must be at least 2")
    return 1 << ((length - 1).bit_length() - 1)


def leaf_hash(value: Mapping[str, Any]) -> bytes:
    return sha256(b"\x00" + canonical_bytes(value)).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b"\x01" + left + right).digest()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def tagged_hash(tag: str, *parts: str) -> str:
    return sha256("\x00".join([tag, *parts]).encode("utf-8")).hexdigest()


def tool_version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        return "source-tree"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
