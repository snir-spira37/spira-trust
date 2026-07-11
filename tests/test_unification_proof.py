from __future__ import annotations

import copy

from spira_core.unification_proof import (
    UnificationProofError,
    build_unification_proof,
    inclusion_proof,
    merkle_root,
    verify_inclusion,
)


def test_merkle_root_is_order_independent_and_changes_on_claim_change():
    claims = [
        _claim("spira.layer.graph_core", "OK"),
        _claim("spira.layer.pep740_offline_attestations", "NOT_EVALUATED"),
        _claim("spira.layer.lockfile_cross_check", "BLOCK"),
    ]

    root_a = merkle_root(claims)
    root_b = merkle_root(list(reversed(claims)))

    assert root_a == root_b

    changed = copy.deepcopy(claims)
    changed[0]["status"] = "NOTE"

    assert merkle_root(changed) != root_a


def test_inclusion_proof_verifies_claim_membership():
    claims = [
        _claim("spira.layer.graph_core", "OK"),
        _claim("spira.layer.pep770_sbom_consistency", "NOTE"),
        _claim("spira.layer.pep740_offline_attestations", "NOT_EVALUATED"),
    ]
    target = claims[1]

    proof = inclusion_proof(claims, target["claim_id"])

    assert verify_inclusion(target, proof) is True

    tampered = copy.deepcopy(target)
    tampered["status"] = "BLOCK"

    assert verify_inclusion(tampered, proof) is False


def test_unification_id_changes_for_artifact_policy_or_claim_change():
    summary = _summary()
    decision = _decision()

    proof = build_unification_proof(summary, decision)
    same = build_unification_proof(copy.deepcopy(summary), copy.deepcopy(decision))

    assert same["unification_id"] == proof["unification_id"]

    artifact_changed = copy.deepcopy(summary)
    artifact_changed["agent_action_contract"]["artifact_sha256"] = "b" * 64
    artifact_changed["agent_action_contract"]["artifact_set_sha256"] = "c" * 64
    assert build_unification_proof(artifact_changed, decision)["unification_id"] != proof["unification_id"]

    policy_changed = copy.deepcopy(summary)
    policy_changed["agent_action_contract"]["policy_sha256"] = "d" * 64
    assert build_unification_proof(policy_changed, decision)["unification_id"] != proof["unification_id"]

    claim_changed = copy.deepcopy(decision)
    claim_changed["layers"]["per_layer"][0]["status"] = "BLOCK"
    claim_changed["layers"]["per_layer"][0]["source_verdict"] = "GRAPH_BLOCK"
    assert build_unification_proof(summary, claim_changed)["roots"]["claims_merkle_root"] != proof["roots"]["claims_merkle_root"]


def test_unification_decision_matches_agent_action_contract():
    summary = _summary()
    decision = _decision()

    proof = build_unification_proof(summary, decision)

    assert proof["decision"]["stop"] == summary["agent_action_contract"]["stop"]
    assert proof["decision"]["recommended_agent_action"] == summary["agent_action_contract"]["recommended_agent_action"]
    assert proof["decision"]["reason_codes"] == summary["agent_action_contract"]["reason_codes"]
    assert proof["coverage"]["not_evaluated"] == ["spira.layer.pep740_offline_attestations"]
    assert proof["not_claimed"]


def test_unification_rejects_unknown_claim_status():
    summary = _summary()
    decision = _decision()
    decision["layers"]["per_layer"][0]["status"] = "TYPO_OK"

    try:
        build_unification_proof(summary, decision)
    except UnificationProofError as error:
        assert "unknown claim status" in str(error)
    else:
        raise AssertionError("expected UnificationProofError")


def test_unification_rejects_missing_or_invalid_subject_hash():
    summary = _summary()
    decision = _decision()
    summary["agent_action_contract"]["artifact_sha256"] = None
    summary["agent_action_contract"]["artifact_set_sha256"] = None

    try:
        build_unification_proof(summary, decision)
    except UnificationProofError as error:
        assert "subject_sha256" in str(error)
    else:
        raise AssertionError("expected UnificationProofError")


def test_unification_rejects_duplicate_claim_ids():
    summary = _summary()
    decision = _decision()
    duplicate = copy.deepcopy(decision["layers"]["per_layer"][0])
    decision["layers"]["per_layer"].append(duplicate)

    try:
        build_unification_proof(summary, decision)
    except UnificationProofError as error:
        assert "duplicate claim_id" in str(error)
    else:
        raise AssertionError("expected UnificationProofError")


def _claim(claim_id: str, status: str) -> dict:
    return {
        "schema": "SPIRA_CLAIM_V1",
        "schema_version": "1.0",
        "claim_id": claim_id,
        "subject_sha256": "a" * 64,
        "status": status,
        "value": {
            "layer": claim_id.rsplit(".", 1)[-1],
            "evaluated": status != "NOT_EVALUATED",
            "source_verdict": status,
            "finding_count": 0,
        },
        "producer": {"name": "spira-trust", "version": "source-tree"},
        "evidence_ref": "graph_report.json",
        "policy_ref": None,
        "reason_codes": [status],
    }


def _summary() -> dict:
    return {
        "schema": "SPIRA_AGENT_SUMMARY_V1",
        "tool": {"name": "spira-trust", "version": "source-tree"},
        "agent_action_contract": {
            "schema": "SPIRA_AGENT_ACTION_V1",
            "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
            "artifact_sha256": "a" * 64,
            "artifact_set_sha256": "f" * 64,
            "policy_sha256": None,
            "command_fingerprint": "1" * 64,
            "graph_verdict": "GRAPH_OK",
            "combined_verdict": "GRAPH_OK_WITH_NOTES",
            "action_verdict": "GRAPH_OK_WITH_NOTES",
            "stop": True,
            "recommended_agent_action": "REPORT_NOT_EVALUATED",
            "reason_codes": ["REPORT_NOT_EVALUATED"],
            "not_evaluated": ["pep740_offline_attestations"],
        },
        "summary_of": {
            "artifact_set_sha256": "f" * 64,
            "command_fingerprint": "1" * 64,
            "tool_version": "source-tree",
            "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
            "policy_sha256": None,
            "decision_sha256": "2" * 64,
            "graph_report_sha256": "3" * 64,
        },
    }


def _decision() -> dict:
    return {
        "layers": {
            "per_layer": [
                {
                    "layer": "graph_core",
                    "status": "OK",
                    "evaluated": True,
                    "source_verdict": "GRAPH_OK",
                    "evidence_ref": "graph_report.json",
                    "finding_count": 0,
                },
                {
                    "layer": "pep740_offline_attestations",
                    "status": "NOT_EVALUATED",
                    "evaluated": False,
                    "source_verdict": "ATTESTATION_NOT_EVALUATED",
                    "evidence_ref": "graph_report.json",
                    "finding_count": 0,
                },
            ]
        }
    }
