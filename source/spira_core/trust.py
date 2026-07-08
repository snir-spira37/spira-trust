from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from .contracts import new_trace_id, utc_now
from .core import _decision015
from .ledger import SpiraCoreLedger
from .review import (
    CLAIMED_NOT_RAW_VERIFIABLE,
    CONTRADICTION,
    NEEDS_HUMAN_JUDGMENT,
    VERIFIED_RAW,
    VERIFIED_RUNTIME,
    review_artifact,
)


TRUST_NOT_CLAIMED = [
    "artifact trust is a local non-production triage decision",
    "does not certify package safety or security",
    "does not auto-classify README/free-text prose",
    "does not replace human review",
    "does not close E",
    "does not modify Stone 015 decision logic",
]


def adapt_review_to_015_metrics(review: Mapping[str, Any]) -> dict[str, Any]:
    counts = dict(review.get("verdict_counts", {}))
    claims = list(review.get("claims", []))
    verified_count = int(counts.get(VERIFIED_RAW, 0)) + int(counts.get(VERIFIED_RUNTIME, 0))
    contradiction_count = int(counts.get(CONTRADICTION, 0))
    claimed_not_raw_verifiable_count = int(counts.get(CLAIMED_NOT_RAW_VERIFIABLE, 0))
    free_text_note_count = int(counts.get(NEEDS_HUMAN_JUDGMENT, 0))
    unverifiable_count = claimed_not_raw_verifiable_count + free_text_note_count
    total_units = max(1, verified_count + contradiction_count + unverifiable_count)
    unresolved_ratio = unverifiable_count / total_units

    integrity_failure = _has_integrity_failure(review, claims)
    if integrity_failure:
        risk = 0.95
        risk_basis = "integrity_failure"
    elif contradiction_count:
        risk = min(1.0, 0.85 + 0.05 * (contradiction_count - 1))
        risk_basis = "condition_matched_contradiction"
    else:
        risk = min(0.7, 0.1 + 0.4 * unresolved_ratio)
        risk_basis = "unverifiable_ratio_without_hard_gap"

    load = min(1.0, 0.2 + 0.6 * unresolved_ratio)
    coherence = max(0.0, min(1.0, (verified_count / total_units) - (0.25 * contradiction_count)))
    payload = {
        "requested_action": "trust_artifact",
        "current_metrics": {
            "risk": round(risk, 6),
            "load": round(load, 6),
            "coherence": round(coherence, 6),
        },
        "options": {"mode": "normal", "force_override": False},
    }
    return {
        "verdict": "SPIRA_ARTIFACT_TRUST_ADAPTER_READY",
        "decision_payload": payload,
        "counts": {
            "verified_count": verified_count,
            "contradiction_count": contradiction_count,
            "claimed_not_raw_verifiable_count": claimed_not_raw_verifiable_count,
            "free_text_note_count": free_text_note_count,
            "unverifiable_count": unverifiable_count,
            "total_units": total_units,
        },
        "ratios": {"unresolved_ratio": round(unresolved_ratio, 6)},
        "risk_basis": risk_basis,
        "integrity_failure": integrity_failure,
        "mapping_rules": [
            "integrity failure maps to risk=0.95",
            "condition-matched contradiction maps to risk>=0.85",
            "unverifiable/free-text claims increase uncertainty but do not alone create contradiction",
            "verified structured/runtime claims increase coherence",
            "free-text notes are human context, not structured gaps by themselves",
        ],
        "not_claimed": [
            "adapter maps review findings to trust metrics only",
            "does not auto-interpret README/free-text prose",
            "does not certify artifact safety",
            "does not tune thresholds per artifact",
        ],
    }


def run_artifact_trust_cycle(
    artifact_path: str | Path,
    output_dir: str | Path,
    *,
    workspace_root: str | Path | None = None,
    ledger_root: str | Path | None = None,
) -> dict[str, Any]:
    workspace = Path(workspace_root).resolve() if workspace_root else Path.cwd().resolve()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    trace_id = new_trace_id()
    review = review_artifact(artifact_path, output / "review", package=True)
    adapter = adapt_review_to_015_metrics(review)
    decision = _decision015(workspace, adapter["decision_payload"], output_dir=output / "decision015")
    trust_status = _trust_status(decision, adapter)
    basis = _trust_basis(review, adapter, decision)
    summary = _human_summary(review, adapter, decision, trust_status)
    report = {
        "schema": "SPIRA_ARTIFACT_TRUST_CYCLE_001",
        "created_at_utc": utc_now(),
        "trace_id": trace_id,
        "artifact": review.get("artifact", {}),
        "review_summary": {
            "overall_verdict": review.get("overall_verdict"),
            "verdict_counts": review.get("verdict_counts", {}),
            "claim_count": len(review.get("claims", [])),
            "free_text_surface_count": len(review.get("free_text_surfaces", [])),
            "package_post_lock_pass": review.get("package_lock", {}).get("post_lock_pass"),
        },
        "trust_adapter": adapter,
        "decision": {
            "trust_status": trust_status,
            "decision": decision.get("decision"),
            "reason_code": decision.get("reason_code"),
            "decision_source": decision.get("decision_source"),
            "coherence_state": decision.get("coherence_state"),
            "raw_response": decision,
        },
        "basis": basis,
        "human_summary": summary,
        "review_report_path": str((output / "review" / f"review_{Path(artifact_path).stem}" / "foreign_artifact_review_report.json").resolve()),
        "not_claimed": list(TRUST_NOT_CLAIMED),
    }
    report["report_sha256"] = _hash_json(report)
    report_path = output / "artifact_trust_report.json"
    summary_path = output / "artifact_trust_summary.txt"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(format_trust_summary(report), encoding="utf-8", newline="\n")
    ledger = SpiraCoreLedger(ledger_root or (output / "ledger"))
    record = ledger.append(
        {
            "trace_id": trace_id,
            "workflow_id": "artifact_trust_cycle",
            "status": trust_status,
            "response_without_ledger_sha": report,
        }
    )
    report["ledger"] = {
        "entry_sha256": record["entry_sha256"],
        "previous_sha256": record["previous_sha256"],
        "ledger_path": str(ledger.ledger_path.resolve()),
    }
    report["report_path"] = str(report_path.resolve())
    report["summary_path"] = str(summary_path.resolve())
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(format_trust_summary(report), encoding="utf-8", newline="\n")
    return report


def _has_integrity_failure(review: Mapping[str, Any], claims: list[Any]) -> bool:
    package_verify = review.get("package_verify")
    if isinstance(package_verify, Mapping) and package_verify.get("post_lock_pass") is False:
        return True
    for claim in claims:
        if not isinstance(claim, Mapping):
            continue
        if claim.get("claim") != "Wheel RECORD hashes match archive contents":
            continue
        evidence = claim.get("evidence")
        if claim.get("verdict") == CONTRADICTION:
            return True
        if isinstance(evidence, Mapping) and evidence.get("pass") is False:
            return True
    return False


def _trust_status(decision: Mapping[str, Any], adapter: Mapping[str, Any]) -> str:
    value = decision.get("decision")
    counts = adapter.get("counts", {})
    contradiction_count = int(counts.get("contradiction_count", 0))
    claimed_not_raw_verifiable_count = int(counts.get("claimed_not_raw_verifiable_count", 0))
    integrity_failure = bool(adapter.get("integrity_failure"))
    if value == "BLOCK":
        return "TRUST_BLOCK"
    if integrity_failure or contradiction_count > 0:
        return "TRUST_BLOCK"
    if value == "WARN":
        if claimed_not_raw_verifiable_count == 0:
            return "TRUST_OK_WITH_NOTES"
        return "TRUST_WARN"
    if value == "ALLOW":
        return "TRUST_OK"
    return "TRUST_UNKNOWN"


def _trust_basis(review: Mapping[str, Any], adapter: Mapping[str, Any], decision: Mapping[str, Any]) -> dict[str, Any]:
    counts = adapter.get("counts", {})
    return {
        "verdict": "SPIRA_ARTIFACT_TRUST_BASIS_READY",
        "review_overall_verdict": review.get("overall_verdict"),
        "decision_reason_code": decision.get("reason_code"),
        "metrics": adapter.get("decision_payload", {}).get("current_metrics", {}),
        "counts": counts,
        "risk_basis": adapter.get("risk_basis"),
        "human_review_required": int(counts.get("unverifiable_count", 0)) > 0,
        "trust_status_mapping_version": "SPIRA_ARTIFACT_TRUST_ADAPTER_SPEC_002",
        "post_observation_correction_disclosed": True,
        "not_claimed": [
            "basis explains wrapper-visible review findings and 015 output only",
            "does not claim complete package audit",
            "TRUST_OK_WITH_NOTES can still require human reading of surfaced free text",
        ],
    }


def _human_summary(
    review: Mapping[str, Any],
    adapter: Mapping[str, Any],
    decision: Mapping[str, Any],
    trust_status: str,
) -> dict[str, Any]:
    counts = adapter.get("counts", {})
    package_lock_pass = review.get("package_lock", {}).get("post_lock_pass")
    if trust_status == "TRUST_BLOCK":
        headline = "Do not trust this artifact without fixing the blocking evidence."
    elif trust_status == "TRUST_WARN":
        headline = "Review this artifact manually before trusting it."
    elif trust_status == "TRUST_OK_WITH_NOTES":
        headline = "No hard gap was found, but human reading is still required for surfaced notes."
    elif trust_status == "TRUST_OK":
        headline = "No hard gap was found in the checks SPIRA ran."
    else:
        headline = "SPIRA could not produce a stable trust verdict."

    reasons: list[str] = []
    if adapter.get("integrity_failure"):
        reasons.append("Wheel RECORD or package-lock integrity failed.")
    if int(counts.get("contradiction_count", 0)):
        reasons.append(f"{counts.get('contradiction_count')} contradiction(s) were found.")
    if int(counts.get("claimed_not_raw_verifiable_count", 0)):
        reasons.append(f"{counts.get('claimed_not_raw_verifiable_count')} structured claim(s) were not raw-verifiable.")
    if int(counts.get("free_text_note_count", 0)):
        reasons.append(f"{counts.get('free_text_note_count')} free-text surface(s) need human judgment.")
    if not reasons:
        reasons.append("Structured metadata and RECORD checks found no hard gap.")

    return {
        "headline": headline,
        "artifact": review.get("artifact", {}).get("path"),
        "trust_status": trust_status,
        "review_overall_verdict": review.get("overall_verdict"),
        "decision_reason_code": decision.get("reason_code"),
        "verified_count": int(counts.get("verified_count", 0)),
        "claimed_not_raw_verifiable_count": int(counts.get("claimed_not_raw_verifiable_count", 0)),
        "free_text_note_count": int(counts.get("free_text_note_count", 0)),
        "contradiction_count": int(counts.get("contradiction_count", 0)),
        "integrity_failure": bool(adapter.get("integrity_failure")),
        "package_lock_pass": package_lock_pass,
        "reasons": reasons,
        "not_claimed": [
            "not a malware scanner",
            "not a security certification",
            "not complete package audit",
            "does not execute code from the artifact under review",
            "free text is surfaced for a human, not auto-interpreted",
        ],
    }


def format_trust_summary(report: Mapping[str, Any], *, color: bool = False, full_evidence: bool = False) -> str:
    summary = report.get("human_summary", {})
    artifact = summary.get("artifact") or report.get("artifact", {}).get("path") or "unknown artifact"
    trust_status = summary.get("trust_status", report.get("decision", {}).get("trust_status", "TRUST_UNKNOWN"))
    review_verdict = report.get("review_summary", {}).get("overall_verdict", "UNKNOWN_REVIEW")
    status_line = _format_status_line(str(trust_status), str(review_verdict), color=color)
    evidence_lines = _evidence_highlights(report)
    lines = [
        "SPIRA Trust Summary",
        "===================",
        status_line,
        "",
        f"Artifact: {artifact}",
        f"Verdict: {trust_status}",
        f"Review: {review_verdict}",
        f"Meaning: {summary.get('headline', 'No human summary available.')}",
        "",
        "Why:",
    ]
    for reason in summary.get("reasons", []):
        lines.append(f"- {reason}")
    if evidence_lines:
        lines.extend(["", "Key evidence:"])
        lines.extend(f"- {line}" for line in evidence_lines)
    lines.extend(
        [
            "",
            "Counts:",
            f"- verified_raw_or_runtime: {summary.get('verified_count', 0)}",
            f"- claimed_not_raw_verifiable: {summary.get('claimed_not_raw_verifiable_count', 0)}",
            f"- free_text_needs_human: {summary.get('free_text_note_count', 0)}",
            f"- contradictions: {summary.get('contradiction_count', 0)}",
            f"- integrity_failure: {summary.get('integrity_failure', False)}",
            f"- package_lock_pass: {summary.get('package_lock_pass', None)}",
            "",
            "Boundaries:",
        ]
    )
    for boundary in summary.get("not_claimed", []):
        lines.append(f"- {boundary}")
    lines.extend(
        [
            "",
            f"JSON report: {report.get('report_path', 'not written yet')}",
            f"Summary file: {report.get('summary_path', 'not written yet')}",
            "",
        ]
    )
    if full_evidence:
        lines.extend(
            [
                "Detailed evidence:",
                f"- Review report: {report.get('review_report_path', 'not available')}",
                f"- Ledger: {report.get('ledger', {}).get('ledger_path', 'not available')}",
                "",
            ]
        )
    return "\n".join(lines)


def _format_status_line(trust_status: str, review_verdict: str, *, color: bool = False) -> str:
    label = {
        "TRUST_BLOCK": "BLOCK",
        "TRUST_WARN": "WARN",
        "TRUST_OK_WITH_NOTES": "OK_WITH_NOTES",
        "TRUST_OK": "OK",
    }.get(trust_status, "UNKNOWN")
    line = f"[{label}] {review_verdict}"
    if not color:
        return line
    color_code = {
        "BLOCK": "31",
        "WARN": "33",
        "OK_WITH_NOTES": "32",
        "OK": "32",
    }.get(label, "0")
    return f"\033[{color_code}m{line}\033[0m"


def _evidence_highlights(report: Mapping[str, Any], *, limit: int = 8) -> list[str]:
    review_report_path = report.get("review_report_path")
    if not isinstance(review_report_path, str):
        return []
    path = Path(review_report_path)
    if not path.is_file():
        return []
    try:
        review_report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []

    highlights: list[str] = []
    for claim in review_report.get("claims", []):
        if not isinstance(claim, Mapping):
            continue
        if claim.get("verdict") != CONTRADICTION:
            continue
        claim_name = claim.get("claim", "contradiction")
        gap_type = claim.get("gap_type")
        evidence = claim.get("evidence", {})
        if isinstance(gap_type, str):
            highlights.append(f"{claim_name}: {gap_type}")
        if isinstance(evidence, Mapping):
            _extend_path_highlights(highlights, "Missing expected file", evidence.get("missing_files"))
            _extend_path_highlights(highlights, "Undocumented archive file", evidence.get("undocumented_files"))
            _extend_path_highlights(highlights, "Unhashed non-RECORD file", evidence.get("unhashed_files"))
            for mismatch in evidence.get("mismatches", []) or []:
                if isinstance(mismatch, Mapping):
                    highlights.append(f"Hash/size mismatch: {mismatch.get('file', 'unknown file')}")
        if len(highlights) >= limit:
            break
    return highlights[:limit]


def _extend_path_highlights(lines: list[str], label: str, paths: Any, *, limit: int = 3) -> None:
    if not isinstance(paths, list):
        return
    for value in paths[:limit]:
        lines.append(f"{label}: {value}")


def _hash_json(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()
