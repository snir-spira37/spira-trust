from __future__ import annotations

from typing import Any, Mapping


SEVERITY_RANK = {
    "NOT_EVALUATED": -1,
    "OK": 0,
    "NOTE": 1,
    "WARN": 2,
    "BLOCK": 3,
}

AGENT_ACTIONS = {
    "PROCEED",
    "ASK_HUMAN",
    "STOP_BLOCKED",
    "REPORT_NOT_EVALUATED",
    "REPORT_WITH_NOTES",
    "RERUN_REQUIRED",
}

DECISION_SEMANTICS_VERSION = "SPIRA_DECISION_SEMANTICS_V2"
NESIRA_LAYER = "nesira_phase2_assessment"
NESIRA_EXECUTION_MARKER = "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION"
NESIRA_VERDICT_SUFFICIENT = "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
NESIRA_VERDICT_INSUFFICIENT = "TRUST_INSUFFICIENT"
NESIRA_VERDICT_NOT_EVALUATED = "TRUST_NOT_EVALUATED"
NESIRA_FORBIDDEN_OUTPUT_KEYS = {
    "automatic_remediation",
    "combined_action",
    "execute",
    "permission_to_sever",
    "run_isolation",
    "safe_to_sever",
    "sever",
    "severance_authorized",
}


def agent_default_decision(
    verdict: str | None,
    *,
    not_evaluated_layers: list[str] | None = None,
) -> dict[str, Any]:
    not_evaluated = list(not_evaluated_layers or [])
    if verdict == "GRAPH_BLOCK":
        return {"stop": True, "stop_source": "default", "recommended_agent_action": "STOP_BLOCKED"}
    if verdict == "GRAPH_WARN":
        return {"stop": True, "stop_source": "default", "recommended_agent_action": "ASK_HUMAN"}
    if verdict == "GRAPH_OK_WITH_UNVERIFIED":
        return {"stop": True, "stop_source": "default", "recommended_agent_action": "REPORT_NOT_EVALUATED"}
    if verdict == "GRAPH_OK_WITH_NOTES":
        action = "REPORT_NOT_EVALUATED" if not_evaluated else "REPORT_WITH_NOTES"
        return {"stop": bool(not_evaluated), "stop_source": "default", "recommended_agent_action": action}
    if verdict == "GRAPH_OK" and not_evaluated:
        return {"stop": True, "stop_source": "default", "recommended_agent_action": "REPORT_NOT_EVALUATED"}
    if verdict == "GRAPH_OK":
        return {"stop": False, "stop_source": "default", "recommended_agent_action": "PROCEED"}
    return {"stop": True, "stop_source": "default", "recommended_agent_action": "RERUN_REQUIRED"}


def agent_reason_codes(
    agent_decision: Mapping[str, Any],
    *,
    verdict: str | None,
    not_evaluated_layers: list[str] | None = None,
    blockers: list[str] | None = None,
    warnings: list[str] | None = None,
) -> list[str]:
    action = str(agent_decision.get("recommended_agent_action") or "")
    not_evaluated = list(not_evaluated_layers or [])
    codes: list[str] = []
    if action == "STOP_BLOCKED" or blockers:
        codes.append("BLOCKING_FINDINGS")
    if action == "ASK_HUMAN" or warnings:
        codes.append("HUMAN_REVIEW_REQUIRED")
    if action == "REPORT_NOT_EVALUATED" or not_evaluated:
        codes.append("REPORT_NOT_EVALUATED")
    if action == "REPORT_WITH_NOTES":
        codes.append("REPORT_WITH_NOTES")
    if action == "RERUN_REQUIRED":
        codes.append("RERUN_REQUIRED")
    if action == "PROCEED" and not codes:
        codes.append("NO_STOP_CONDITION")
    if verdict and str(verdict).endswith("_WITH_NOTES"):
        codes.append("NOTES_PRESENT")
    return sorted(dict.fromkeys(codes))


def build_combined_policy_verdict(report: Mapping[str, Any], bom: Mapping[str, Any]) -> dict[str, Any]:
    per_layer = [
        _graph_core_layer(report),
        _pep770_layer(report, bom),
        _pep740_layer(report, bom),
        _license_layer(bom),
        _entry_point_layer(bom),
        _target_environment_layer(bom),
        _lockfile_layer(bom),
    ]
    nesira_layer = _nesira_phase2_layer(report, bom)
    if nesira_layer is not None:
        per_layer.append(nesira_layer)
    evaluated = [layer for layer in per_layer if layer["status"] != "NOT_EVALUATED"]
    not_evaluated = [layer for layer in per_layer if layer["status"] == "NOT_EVALUATED"]
    winning_status = "OK"
    if evaluated:
        winning_status = max((layer["status"] for layer in evaluated), key=lambda status: SEVERITY_RANK[status])
    decided_by = [
        layer["layer"]
        for layer in evaluated
        if layer["status"] == winning_status and SEVERITY_RANK[winning_status] > SEVERITY_RANK["OK"]
    ]
    if winning_status == "OK":
        decided_by = [layer["layer"] for layer in evaluated if layer["status"] == "OK"]
    return {
        "schema": "SPIRA_COMBINED_POLICY_VERDICT_V1",
        "schema_version": "1.0",
        "combined_verdict": _combined_verdict(winning_status),
        "winning_status": winning_status,
        "per_layer": per_layer,
        "decided_by": decided_by,
        "evaluated_layers": [layer["layer"] for layer in evaluated],
        "not_evaluated_layers": [layer["layer"] for layer in not_evaluated],
        "summary": _summary(winning_status, evaluated, not_evaluated, decided_by),
        "not_claimed": [
            "aggregator only; creates no new evidence",
            "does not replace per-layer detail",
            "GRAPH_OK reflects evaluated layers only, not unprovided policies",
            "a not-evaluated layer is not a passed layer",
        ],
    }


def _graph_core_layer(report: Mapping[str, Any]) -> dict[str, Any]:
    verdict = str(report.get("verdict", "GRAPH_OK"))
    status = "OK"
    if verdict == "GRAPH_BLOCK":
        status = "BLOCK"
    elif verdict == "GRAPH_WARN":
        status = "WARN"
    elif verdict == "GRAPH_OK_WITH_UNVERIFIED":
        status = "NOTE"
    return {
        "layer": "graph_core",
        "status": status,
        "evaluated": True,
        "source_verdict": verdict,
        "evidence_ref": "graph_report.json",
        "finding_count": len(report.get("propagation_events", [])),
        "notes": "core graph, artifact integrity, dependency/range, and propagated status",
    }


def _license_layer(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("license_policy_screening", {})
    return _policy_layer(
        layer="license_policy",
        screening=screening,
        verdict_map={
            "LICENSE_POLICY_BLOCK": "BLOCK",
            "LICENSE_POLICY_WARN": "WARN",
            "LICENSE_POLICY_PASS": "OK",
        },
    )


def _pep770_layer(report: Mapping[str, Any], bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = report.get("pep770_sbom_consistency") or bom.get("pep770_sbom_consistency") or {}
    if not screening.get("evaluated"):
        return {
            "layer": "pep770_sbom_consistency",
            "status": "NOT_EVALUATED",
            "evaluated": False,
            "source_verdict": screening.get("status", "NOT_EVALUATED"),
            "evidence_ref": "graph_report.json",
            "finding_count": 0,
            "notes": "embedded SBOM consistency was not requested; this layer did not run",
        }
    source_status = str(screening.get("status", "UNVERIFIED"))
    status = {
        "CONTRADICTION": "BLOCK",
        "INVALID": "BLOCK",
        "UNVERIFIED": "NOTE",
        "NO_WHEEL_SCOPED_SBOM": "NOTE",
        "VERIFIED_OK": "OK",
        "NOT_EVALUATED": "NOT_EVALUATED",
    }.get(source_status, "NOTE")
    return {
        "layer": "pep770_sbom_consistency",
        "status": status,
        "evaluated": True,
        "source_verdict": source_status,
        "evidence_ref": "graph_report.json",
        "finding_count": int(screening.get("result_count") or 0),
        "notes": "evaluated embedded SBOM consistency for provided local wheels only",
    }


def _pep740_layer(report: Mapping[str, Any], bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = report.get("pep740_offline_attestations") or bom.get("pep740_offline_attestations") or {}
    source_status = str(screening.get("status", "ATTESTATION_NOT_EVALUATED"))
    if source_status == "ATTESTATION_NOT_EVALUATED" or not screening.get("attestation_path"):
        return {
            "layer": "pep740_offline_attestations",
            "status": "NOT_EVALUATED",
            "evaluated": False,
            "source_verdict": source_status,
            "evidence_ref": "graph_report.json",
            "finding_count": 0,
            "notes": "attestations were not supplied; this layer did not run",
        }
    status = {
        "ATTESTATION_VERIFIED": "OK",
        "ATTESTATION_UNVERIFIED": "NOTE",
        "ATTESTATION_DIGEST_MISMATCH": "BLOCK",
        "ATTESTATION_IDENTITY_NOT_ALLOWED": "BLOCK",
        "ATTESTATION_CONTRADICTION": "BLOCK",
        "ATTESTATION_TRUST_ROOT_UNTRUSTED": "BLOCK",
        "ATTESTATION_TRUST_ROOT_SHA_MISSING": "BLOCK",
        "ATTESTATION_TRUST_ROOT_MISSING": "BLOCK",
        "ATTESTATION_INPUT_ERROR": "BLOCK",
    }.get(source_status, "NOTE")
    return {
        "layer": "pep740_offline_attestations",
        "status": status,
        "evaluated": bool(screening.get("evaluated")) or status == "BLOCK",
        "source_verdict": source_status,
        "evidence_ref": "graph_report.json",
        "finding_count": len(screening.get("findings", []) or []),
        "policy_ref": screening.get("trust_root"),
        "notes": "evaluated local attestation metadata/digest and explicit trust-root identity policy when pinned",
    }


def _entry_point_layer(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("entry_point_policy_screening", {})
    return _policy_layer(
        layer="entry_point_policy",
        screening=screening,
        verdict_map={
            "ENTRY_POINT_POLICY_BLOCK": "BLOCK",
            "ENTRY_POINT_POLICY_WARN": "WARN",
            "ENTRY_POINT_POLICY_PASS": "OK",
        },
    )


def _target_environment_layer(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("target_environment_screening", {})
    return _policy_layer(
        layer="target_environment",
        screening=screening,
        verdict_map={
            "TARGET_ENVIRONMENT_BLOCK": "BLOCK",
            "TARGET_ENVIRONMENT_WARN": "WARN",
            "TARGET_ENVIRONMENT_NOTES": "NOTE",
            "TARGET_ENVIRONMENT_PASS": "OK",
        },
    )


def _lockfile_layer(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("lockfile_cross_check", {})
    return _policy_layer(
        layer="lockfile_cross_check",
        screening=screening,
        verdict_map={
            "LOCKFILE_CROSS_CHECK_BLOCK": "BLOCK",
            "LOCKFILE_CROSS_CHECK_WARN": "WARN",
            "LOCKFILE_CROSS_CHECK_NOTES": "NOTE",
            "LOCKFILE_CROSS_CHECK_PASS": "OK",
        },
    )


def _nesira_phase2_layer(report: Mapping[str, Any], bom: Mapping[str, Any]) -> dict[str, Any] | None:
    assessment = report.get(NESIRA_LAYER) or bom.get(NESIRA_LAYER)
    required = bool(
        report.get("nesira_phase2_assessment_required")
        or bom.get("nesira_phase2_assessment_required")
        or (report.get("nesira_phase2_policy") or {}).get("required")
        or (bom.get("nesira_phase2_policy") or {}).get("required")
    )
    if assessment is None:
        if not required:
            return None
        return _nesira_not_evaluated("NESIRA_PHASE2_ASSESSMENT_MISSING", "Nesira Phase 2 assessment was required but not supplied")
    if not isinstance(assessment, Mapping):
        return _nesira_not_evaluated("NESIRA_PHASE2_ASSESSMENT_MALFORMED", "Nesira Phase 2 assessment was malformed")
    if _contains_forbidden_output_key(assessment):
        return _nesira_block("NESIRA_PHASE2_FORBIDDEN_ACTION_FIELD", assessment, "Nesira assessment contained an action-like field")

    verdict = assessment.get("verdict")
    execution_marker = assessment.get("execution_marker")
    assumptions = _string_list(assessment.get("assumptions"))
    trust_roots = _string_list(assessment.get("trust_roots_used"))
    reason_codes = _string_list(assessment.get("reason_codes"))

    if execution_marker != NESIRA_EXECUTION_MARKER:
        return _nesira_block("NESIRA_PHASE2_EXECUTION_MARKER_MISMATCH", assessment, "Nesira assessment marker did not match assessment-only contract")
    if verdict == NESIRA_VERDICT_SUFFICIENT:
        if not assumptions:
            return _nesira_block("NESIRA_PHASE2_ASSUMPTIONS_MISSING", assessment, "Sufficient Nesira assessment did not carry assumptions")
        if _nesira_isolation_present(assessment) and "PT-ISOLATION-01" not in assumptions:
            return _nesira_block("NESIRA_PHASE2_ISOLATION_CAVEAT_MISSING", assessment, "Sufficient isolation assessment did not carry PT-ISOLATION-01")
        return {
            "layer": NESIRA_LAYER,
            "status": "OK",
            "evaluated": True,
            "source_verdict": NESIRA_VERDICT_SUFFICIENT,
            "evidence_ref": "nesira_phase2_assessment",
            "finding_count": 0,
            "notes": "evaluated read-only Nesira Phase 2 assessment under declared roots and recorded NOT_PROVEN assumptions",
            "nesira_verdict": NESIRA_VERDICT_SUFFICIENT,
            "nesira_assumptions": assumptions,
            "nesira_trust_roots_used": trust_roots,
            "nesira_execution_marker": NESIRA_EXECUTION_MARKER,
            "nesira_reason_codes": reason_codes,
        }
    if verdict == NESIRA_VERDICT_INSUFFICIENT:
        return _nesira_block("NESIRA_PHASE2_TRUST_INSUFFICIENT", assessment, "Nesira Phase 2 assessment was insufficient")
    if verdict == NESIRA_VERDICT_NOT_EVALUATED:
        return _nesira_not_evaluated("NESIRA_PHASE2_TRUST_NOT_EVALUATED", "Nesira Phase 2 assessment was not evaluated", assessment)
    return _nesira_not_evaluated("NESIRA_PHASE2_ASSESSMENT_MALFORMED", "Nesira Phase 2 assessment verdict was not recognized", assessment)


def _nesira_block(reason: str, assessment: Mapping[str, Any], notes: str) -> dict[str, Any]:
    return {
        "layer": NESIRA_LAYER,
        "status": "BLOCK",
        "evaluated": True,
        "source_verdict": str(assessment.get("verdict") or reason),
        "evidence_ref": "nesira_phase2_assessment",
        "finding_count": 1,
        "notes": notes,
        "reason_codes": [reason],
        "nesira_verdict": assessment.get("verdict"),
        "nesira_assumptions": _string_list(assessment.get("assumptions")),
        "nesira_trust_roots_used": _string_list(assessment.get("trust_roots_used")),
        "nesira_execution_marker": assessment.get("execution_marker"),
        "nesira_reason_codes": _string_list(assessment.get("reason_codes")),
    }


def _nesira_not_evaluated(reason: str, notes: str, assessment: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = assessment or {}
    return {
        "layer": NESIRA_LAYER,
        "status": "NOT_EVALUATED",
        "evaluated": False,
        "source_verdict": str(payload.get("verdict") or reason),
        "evidence_ref": "nesira_phase2_assessment",
        "finding_count": 0,
        "notes": notes,
        "reason_codes": [reason],
        "nesira_verdict": payload.get("verdict"),
        "nesira_assumptions": _string_list(payload.get("assumptions")),
        "nesira_trust_roots_used": _string_list(payload.get("trust_roots_used")),
        "nesira_execution_marker": payload.get("execution_marker"),
        "nesira_reason_codes": _string_list(payload.get("reason_codes")),
    }


def _policy_layer(layer: str, screening: Mapping[str, Any], verdict_map: Mapping[str, str]) -> dict[str, Any]:
    if not screening.get("evaluated"):
        return {
            "layer": layer,
            "status": "NOT_EVALUATED",
            "evaluated": False,
            "source_verdict": screening.get("verdict", "NOT_PROVIDED"),
            "evidence_ref": "bill_of_materials.json",
            "finding_count": 0,
            "notes": "policy file was not provided; this layer did not run",
        }
    source_verdict = str(screening.get("verdict", "UNKNOWN"))
    status = verdict_map.get(source_verdict, "NOTE")
    return {
        "layer": layer,
        "status": status,
        "evaluated": True,
        "source_verdict": source_verdict,
        "evidence_ref": "bill_of_materials.json",
        "finding_count": len(screening.get("findings", [])),
        "policy_ref": screening.get("policy_ref") or screening.get("target_ref") or screening.get("lockfile_ref"),
        "notes": "evaluated from explicit user-provided policy or target file",
    }


def _combined_verdict(status: str) -> str:
    return {
        "BLOCK": "GRAPH_BLOCK",
        "WARN": "GRAPH_WARN",
        "NOTE": "GRAPH_OK_WITH_NOTES",
        "OK": "GRAPH_OK",
    }.get(status, "GRAPH_OK")


def _summary(
    winning_status: str,
    evaluated: list[dict[str, Any]],
    not_evaluated: list[dict[str, Any]],
    decided_by: list[str],
) -> str:
    if winning_status == "OK":
        return (
            f"GRAPH_OK across {len(evaluated)} evaluated layer(s); "
            f"{len(not_evaluated)} layer(s) were not evaluated."
        )
    return (
        f"{_combined_verdict(winning_status)} decided by {', '.join(decided_by)}; "
        f"{len(evaluated)} evaluated layer(s), {len(not_evaluated)} not evaluated."
    )


def _contains_forbidden_output_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in NESIRA_FORBIDDEN_OUTPUT_KEYS:
                return True
            if _contains_forbidden_output_key(item):
                return True
    if isinstance(value, list):
        return any(_contains_forbidden_output_key(item) for item in value)
    return False


def _nesira_isolation_present(assessment: Mapping[str, Any]) -> bool:
    sub_assessments = assessment.get("sub_assessments")
    if isinstance(sub_assessments, Mapping) and "isolation" in sub_assessments:
        return True
    breakdown = assessment.get("per_domain_breakdown")
    return isinstance(breakdown, Mapping) and "isolation" in breakdown


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted(dict.fromkeys(str(item) for item in value))
