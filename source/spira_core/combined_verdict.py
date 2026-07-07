from __future__ import annotations

from typing import Any, Mapping


SEVERITY_RANK = {
    "NOT_EVALUATED": -1,
    "OK": 0,
    "NOTE": 1,
    "WARN": 2,
    "BLOCK": 3,
}


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
        "UNVERIFIED": "NOTE",
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
