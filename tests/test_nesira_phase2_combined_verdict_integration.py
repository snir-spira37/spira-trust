from __future__ import annotations

import copy

from spira_core.combined_verdict import agent_default_decision, build_combined_policy_verdict


def test_no_nesira_input_leaves_existing_combined_verdict_behavior_unchanged():
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {})

    assert _layer(decision, "nesira_phase2_assessment") is None
    assert decision["combined_verdict"] == "GRAPH_OK"
    assert decision["not_evaluated_layers"] == [
        "pep770_sbom_consistency",
        "pep740_offline_attestations",
        "license_policy",
        "entry_point_policy",
        "target_environment",
        "lockfile_cross_check",
    ]


def test_nesira_sufficient_does_not_upgrade_existing_block():
    decision = build_combined_policy_verdict(_report("GRAPH_BLOCK"), {"nesira_phase2_assessment": _nesira_sufficient()})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "OK"
    assert decision["combined_verdict"] == "GRAPH_BLOCK"
    assert decision["winning_status"] == "BLOCK"


def test_nesira_sufficient_does_not_upgrade_existing_warning():
    decision = build_combined_policy_verdict(_report("GRAPH_WARN"), {"nesira_phase2_assessment": _nesira_sufficient()})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "OK"
    assert decision["combined_verdict"] == "GRAPH_WARN"
    assert decision["winning_status"] == "WARN"


def test_nesira_insufficient_blocks_graph_ok():
    assessment = _nesira_sufficient()
    assessment["verdict"] = "TRUST_INSUFFICIENT"
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": assessment})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "BLOCK"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_TRUST_INSUFFICIENT"]
    assert decision["combined_verdict"] == "GRAPH_BLOCK"
    agent = agent_default_decision(decision["combined_verdict"], not_evaluated_layers=decision["not_evaluated_layers"])
    assert agent["stop"] is True
    assert agent["recommended_agent_action"] == "STOP_BLOCKED"


def test_required_nesira_not_evaluated_is_not_a_pass():
    assessment = _nesira_sufficient()
    assessment["verdict"] = "TRUST_NOT_EVALUATED"
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": assessment})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "NOT_EVALUATED"
    assert "nesira_phase2_assessment" in decision["not_evaluated_layers"]
    assert decision["combined_verdict"] == "GRAPH_OK"
    agent = agent_default_decision(decision["combined_verdict"], not_evaluated_layers=decision["not_evaluated_layers"])
    assert agent["stop"] is True
    assert agent["recommended_agent_action"] == "REPORT_NOT_EVALUATED"


def test_missing_required_nesira_is_not_a_pass():
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment_required": True})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "NOT_EVALUATED"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_ASSESSMENT_MISSING"]
    assert "nesira_phase2_assessment" in decision["not_evaluated_layers"]


def test_malformed_nesira_artifact_fails_closed_as_not_evaluated():
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": ["not", "an", "object"]})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "NOT_EVALUATED"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_ASSESSMENT_MALFORMED"]
    assert "nesira_phase2_assessment" in decision["not_evaluated_layers"]


def test_sufficient_nesira_carries_conditionality_into_combined_layer():
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": _nesira_sufficient()})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "OK"
    assert layer["nesira_verdict"] == "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
    assert "PT-ISOLATION-01" in layer["nesira_assumptions"]
    assert layer["nesira_trust_roots_used"] == [
        "attestation-root-main@1",
        "authority-root-main@1",
        "identity-root-main@1",
        "signing-root-main@1",
    ]
    assert layer["nesira_execution_marker"] == "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION"


def test_sufficient_nesira_without_isolation_caveat_fails_closed():
    assessment = _nesira_sufficient()
    assessment["assumptions"] = [item for item in assessment["assumptions"] if item != "PT-ISOLATION-01"]
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": assessment})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "BLOCK"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_ISOLATION_CAVEAT_MISSING"]
    assert decision["combined_verdict"] == "GRAPH_BLOCK"


def test_action_looking_nesira_artifact_fails_closed():
    assessment = _nesira_sufficient()
    assessment["safe_to_sever"] = True
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": assessment})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "BLOCK"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_FORBIDDEN_ACTION_FIELD"]
    assert decision["combined_verdict"] == "GRAPH_BLOCK"


def test_execution_marker_mismatch_fails_closed():
    assessment = _nesira_sufficient()
    assessment["execution_marker"] = "SEVERANCE_AUTHORIZATION"
    decision = build_combined_policy_verdict(_report("GRAPH_OK"), {"nesira_phase2_assessment": assessment})

    layer = _require_layer(decision, "nesira_phase2_assessment")
    assert layer["status"] == "BLOCK"
    assert layer["reason_codes"] == ["NESIRA_PHASE2_EXECUTION_MARKER_MISMATCH"]


def _report(verdict: str) -> dict:
    return {
        "verdict": verdict,
        "nodes": [],
        "propagation_events": [{"effect": "BLOCK", "reason": "graph contradiction"}] if verdict == "GRAPH_BLOCK" else [],
    }


def _nesira_sufficient() -> dict:
    return copy.deepcopy(
        {
            "verdict": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
            "execution_marker": "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION",
            "assumptions": [
                "PT-AUTHORITY-01",
                "PT-CLOCK-01",
                "PT-CRYPTO-01",
                "PT-IDENTITY-01",
                "PT-ISOLATION-01",
                "PT-KEYLEGIT-01",
                "PT-META-01",
                "PT-REVOKE-01",
            ],
            "trust_roots_used": [
                "attestation-root-main@1",
                "authority-root-main@1",
                "identity-root-main@1",
                "signing-root-main@1",
            ],
            "reason_codes": [
                "authority:AUTHORITY_EXPLICIT_ALLOW_UNDER_DECLARED_ROOTS",
                "identity:IDENTITY_BOUND_UNDER_DECLARED_ROOTS",
                "isolation:ATTESTATION_VERIFIED_UNDER_DECLARED_AUTHORITY",
                "signature:SIGNATURE_VERIFIED_UNDER_DECLARED_ROOTS",
            ],
            "per_domain_breakdown": {
                "authority": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
                "identity": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
                "isolation": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
                "signature": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
            },
            "sub_assessments": {
                "isolation": {
                    "sub_verdict": "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS",
                    "assumption_ids": ["PT-ISOLATION-01"],
                }
            },
        }
    )


def _layer(decision: dict, name: str) -> dict | None:
    for layer in decision["per_layer"]:
        if layer["layer"] == name:
            return layer
    return None


def _require_layer(decision: dict, name: str) -> dict:
    layer = _layer(decision, name)
    assert layer is not None
    return layer
