from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping

from .drift import drift_exit_code, run_baseline_drift


REBASELINE_SCHEMA = "SPIRA_REBASELINE_REPORT_V1"
REBASELINE_SCHEMA_VERSION = "1.0"


def run_rebaseline(
    artifact_inputs: Iterable[str | Path],
    output_dir: str | Path,
    *,
    from_baseline: str | Path,
    baseline_sha256: str,
    yes: bool = False,
    workspace_root: str | Path | None = None,
    strict_closure: bool = False,
    package_evidence: bool = True,
    bundle_sha256: str | None = None,
    tool_version: str | None = None,
    license_policy_path: str | Path | None = None,
    entry_point_policy_path: str | Path | None = None,
    target_environment_path: str | Path | None = None,
    lockfile_path: str | Path | None = None,
    policy_pack_path: str | Path | None = None,
    policy_sha256: str | None = None,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    old_baseline = Path(from_baseline)
    old_baseline_sha_before = _hash_file(old_baseline) if old_baseline.is_file() else None
    drift = run_baseline_drift(
        old_baseline,
        artifact_inputs,
        output / "drift_preview",
        baseline_sha256=baseline_sha256,
        workspace_root=workspace_root,
        strict_closure=strict_closure,
        package_evidence=package_evidence,
        bundle_sha256=bundle_sha256,
        tool_version=tool_version,
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
        policy_pack_path=policy_pack_path,
        policy_sha256=policy_sha256,
    )
    drift_exit = drift_exit_code(drift)
    if drift_exit == 4:
        return _write_report(
            output,
            _report(
                old_baseline,
                old_baseline_sha_before,
                drift,
                exit_code=4,
                status="BASELINE_UNTRUSTED",
                yes=yes,
            ),
        )
    if drift_exit == 1:
        return _write_report(
            output,
            _report(old_baseline, old_baseline_sha_before, drift, exit_code=1, status="CURRENT_POLICY_BLOCK", yes=yes),
        )
    if drift_exit == 2:
        return _write_report(
            output,
            _report(old_baseline, old_baseline_sha_before, drift, exit_code=2, status="CURRENT_POLICY_WARN", yes=yes),
        )
    if not yes:
        return _write_report(
            output,
            _report(
                old_baseline,
                old_baseline_sha_before,
                drift,
                exit_code=6,
                status="REBASELINE_REQUIRES_CONFIRMATION",
                yes=yes,
            ),
        )

    current_bom = Path(drift["current_ref"]["generated_bom_path"])
    new_baseline_dir = output / "new_baseline"
    new_baseline_dir.mkdir(parents=True, exist_ok=True)
    new_baseline = new_baseline_dir / "bill_of_materials.json"
    shutil.copy2(current_bom, new_baseline)
    new_sha = _hash_file(new_baseline)
    report = _report(
        old_baseline,
        old_baseline_sha_before,
        drift,
        exit_code=0,
        status="REBASELINE_WRITTEN",
        yes=yes,
    )
    report["new_baseline"] = {
        "path": str(new_baseline.resolve()),
        "sha256": new_sha,
        "pin_instruction": f"use --baseline-sha256 {new_sha}",
    }
    report["old_baseline_unchanged"] = _hash_file(old_baseline) == old_baseline_sha_before
    return _write_report(output, report)


def format_rebaseline_summary(report: Mapping[str, Any]) -> str:
    text = report.get("summary_text")
    if isinstance(text, str):
        return text
    return "SPIRA Rebaseline Summary\n=========================\n[UNKNOWN] summary unavailable\n"


def rebaseline_exit_code(report: Mapping[str, Any]) -> int:
    return int(report.get("summary", {}).get("exit_code", 1))


def _report(
    old_baseline: Path,
    old_baseline_sha: str | None,
    drift: Mapping[str, Any],
    *,
    exit_code: int,
    status: str,
    yes: bool,
) -> dict[str, Any]:
    drift_summary = dict(drift.get("summary", {}))
    return {
        "schema": REBASELINE_SCHEMA,
        "schema_version": REBASELINE_SCHEMA_VERSION,
        "created_at_utc": _utc(),
        "status": status,
        "summary": {
            "exit_code": exit_code,
            "requires_human_confirmation": exit_code == 6,
            "confirmed_with_yes": yes,
            "drift_exit_code": drift_summary.get("exit_code"),
            "added_count": drift_summary.get("added_count", 0),
            "removed_count": drift_summary.get("removed_count", 0),
            "changed_count": drift_summary.get("changed_count", 0),
            "subtree_digest_changed_count": drift_summary.get("subtree_digest_changed_count", 0),
            "version_changed_count": drift_summary.get("version_changed_count", 0),
        },
        "old_baseline": {
            "path": str(old_baseline.resolve()),
            "sha256": old_baseline_sha,
        },
        "drift_preview": {
            "report_path": drift.get("report_path"),
            "summary_path": drift.get("summary_path"),
            "summary": drift_summary,
        },
        "new_baseline": None,
        "old_baseline_unchanged": None,
        "not_claimed": [
            "rebaseline is human approval, not proof of safety",
            "drift command never mutates the baseline",
            "rebaseline does not auto-accept future drift",
            "CI templates must not run rebaseline automatically",
        ],
    }


def _write_report(output: Path, report: dict[str, Any]) -> dict[str, Any]:
    summary = _summary_text(report)
    report["summary_text"] = summary
    report_path = output / "rebaseline_report.json"
    summary_path = output / "rebaseline_summary.txt"
    report["report_path"] = str(report_path.resolve())
    report["summary_path"] = str(summary_path.resolve())
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(summary, encoding="utf-8", newline="\n")
    return report


def _summary_text(report: Mapping[str, Any]) -> str:
    status = report.get("status")
    summary = report.get("summary", {})
    lines = [
        "SPIRA Rebaseline Summary",
        "=========================",
        f"[{status}]",
        "",
        f"Added: {summary.get('added_count', 0)}",
        f"Removed: {summary.get('removed_count', 0)}",
        f"Changed: {summary.get('changed_count', 0)}",
        f"Subtree digest changed: {summary.get('subtree_digest_changed_count', 0)}",
        f"Version changed: {summary.get('version_changed_count', 0)}",
        "",
    ]
    new_baseline = report.get("new_baseline")
    if isinstance(new_baseline, Mapping):
        lines.append(f"New baseline: {new_baseline.get('path')}")
        lines.append(f"New baseline sha256: {new_baseline.get('sha256')}")
        lines.append(str(new_baseline.get("pin_instruction")))
    else:
        lines.append("No new baseline was written.")
        if summary.get("exit_code") == 6:
            lines.append("Re-run with --yes after reviewing the drift preview to approve this state.")
    lines.append("")
    lines.append("Boundary: rebaseline is human approval, not proof of safety.")
    lines.append("")
    return "\n".join(lines)


def _hash_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
