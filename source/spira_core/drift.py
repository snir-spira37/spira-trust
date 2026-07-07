from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping

from .governance_engine import package_lock
from .trust_graph import run_trust_graph


DRIFT_SCHEMA = "SPIRA_BASELINE_DRIFT_REPORT_V1"
DRIFT_SCHEMA_VERSION = "1.0"

DRIFT_NOT_CLAIMED = [
    "drift is relative to the supplied baseline",
    "NO_DRIFT against an unpinned baseline only proves the wheels match that baseline file",
    "baseline authenticity is not verified unless --baseline-sha256 is supplied",
    "drift is not proof that a change is bad",
    "policy change is not package content change",
    "version bump may appear as added and removed identities plus version_changed",
    "not a resolver",
    "not automatic re-baselining",
    "not a guarantee of install success",
]


def run_baseline_drift(
    baseline_bom_path: str | Path,
    artifact_inputs: Iterable[str | Path],
    output_dir: str | Path,
    *,
    baseline_sha256: str | None = None,
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
    baseline_path = Path(baseline_bom_path)
    if not baseline_path.is_file():
        report = _refusal_report(
            baseline_path,
            actual_sha256=None,
            expected_sha256=baseline_sha256,
            trust="BASELINE_FILE_MISSING",
            reason=f"baseline file does not exist: {baseline_path}",
        )
        return _write_drift_outputs(output, report, package_evidence=False)
    actual_baseline_sha = _hash_file(baseline_path)
    trust = _baseline_trust(actual_baseline_sha, baseline_sha256)
    if trust == "PINNED_MISMATCH":
        report = _refusal_report(
            baseline_path,
            actual_sha256=actual_baseline_sha,
            expected_sha256=baseline_sha256,
            trust="PINNED_MISMATCH",
            reason="baseline sha256 pin mismatch",
        )
        return _write_drift_outputs(output, report, package_evidence=False)

    baseline_bom = json.loads(baseline_path.read_text(encoding="utf-8"))
    current_output = output / "current_graph"
    current_report = run_trust_graph(
        artifact_inputs,
        current_output,
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
    current_bom_path = Path(current_report["bill_of_materials_path"])
    current_bom = json.loads(current_bom_path.read_text(encoding="utf-8"))
    drift = _compare_boms(baseline_bom, current_bom)
    current_policy_verdict = current_bom.get("combined_policy_verdict", {}).get("combined_verdict")
    exit_code = _drift_exit_code(current_report.get("verdict"), drift["drift_detected"])
    report = {
        "schema": DRIFT_SCHEMA,
        "schema_version": DRIFT_SCHEMA_VERSION,
        "created_at_utc": _utc(),
        "baseline_ref": {
            "path": str(baseline_path.resolve()),
            "actual_sha256": actual_baseline_sha,
            "expected_sha256": baseline_sha256,
            "trust": trust,
        },
        "current_ref": {
            "generated_bom_path": str(current_bom_path.resolve()),
            "generated_bom_sha256": _hash_file(current_bom_path),
            "graph_report_path": str(Path(current_report["report_path"]).resolve()),
            "graph_report_sha256": _hash_file(Path(current_report["report_path"])),
        },
        "summary": {
            "added_count": len(drift["added"]),
            "removed_count": len(drift["removed"]),
            "changed_count": len(drift["changed"]),
            "subtree_digest_changed_count": len(drift["subtree_digest_changed"]),
            "version_changed_count": len(drift["version_changed"]),
            "policy_status_changed_count": len(drift["policy_status_changed"]),
            "policy_or_config_changed_count": len(drift["policy_or_config_changed"]),
            "unchanged_count": len(drift["unchanged"]),
            "drift_detected": drift["drift_detected"],
            "baseline_trust": trust,
            "current_policy_verdict": current_policy_verdict,
            "exit_code": exit_code,
        },
        "artifacts": drift["artifacts"],
        "added": drift["added"],
        "removed": drift["removed"],
        "changed": drift["changed"],
        "subtree_digest_changed": drift["subtree_digest_changed"],
        "version_changed": drift["version_changed"],
        "policy_status_changed": drift["policy_status_changed"],
        "policy_or_config_changed": drift["policy_or_config_changed"],
        "unchanged": drift["unchanged"],
        "not_claimed": list(DRIFT_NOT_CLAIMED),
    }
    return _write_drift_outputs(output, report, package_evidence=package_evidence)


def format_drift_summary(report: Mapping[str, Any]) -> str:
    text = report.get("summary_text")
    if isinstance(text, str):
        return text
    path = report.get("summary_path")
    if isinstance(path, str) and Path(path).is_file():
        return Path(path).read_text(encoding="utf-8")
    return "SPIRA Baseline Drift Summary\n============================\n[UNKNOWN] summary unavailable\n"


def drift_exit_code(report: Mapping[str, Any]) -> int:
    return int(report.get("summary", {}).get("exit_code", 1))


def _compare_boms(baseline_bom: Mapping[str, Any], current_bom: Mapping[str, Any]) -> dict[str, Any]:
    baseline = _artifact_map(baseline_bom)
    current = _artifact_map(current_bom)
    baseline_keys = set(baseline)
    current_keys = set(current)
    added_keys = sorted(current_keys - baseline_keys)
    removed_keys = sorted(baseline_keys - current_keys)
    shared_keys = sorted(baseline_keys & current_keys)
    artifacts = []
    changed = []
    subtree_changed = []
    unchanged = []
    for key in shared_keys:
        before = baseline[key]
        after = current[key]
        own_changed = before.get("sha256") != after.get("sha256")
        subtree_digest_changed = _subtree_digest(before) != _subtree_digest(after)
        record = {
            "identity": _identity_payload(key),
            "status": "changed" if own_changed or subtree_digest_changed else "unchanged",
            "own_wheel_sha256_changed": own_changed,
            "subtree_integrity_digest_changed": subtree_digest_changed,
            "baseline_sha256": before.get("sha256"),
            "current_sha256": after.get("sha256"),
            "baseline_subtree_integrity_digest": _subtree_digest(before),
            "current_subtree_integrity_digest": _subtree_digest(after),
        }
        artifacts.append(record)
        if own_changed:
            changed.append(record)
        if subtree_digest_changed:
            subtree_changed.append(record)
        if not own_changed and not subtree_digest_changed:
            unchanged.append(record)

    added = [_artifact_delta_record(current[key], "added") for key in added_keys]
    removed = [_artifact_delta_record(baseline[key], "removed") for key in removed_keys]
    artifacts.extend(added)
    artifacts.extend(removed)
    version_changed = _version_changes(baseline, current)
    policy_delta = _bom_policy_delta(baseline_bom, current_bom)
    policy_status_changed = [policy_delta] if policy_delta["kind"] == "policy_status_changed" else []
    policy_or_config_changed = [policy_delta] if policy_delta["kind"] == "policy_or_config_changed" else []
    drift_detected = any(
        [
            added,
            removed,
            changed,
            subtree_changed,
            version_changed,
            policy_status_changed,
            policy_or_config_changed,
        ]
    )
    return {
        "artifacts": artifacts,
        "added": added,
        "removed": removed,
        "changed": changed,
        "subtree_digest_changed": subtree_changed,
        "version_changed": version_changed,
        "policy_status_changed": policy_status_changed,
        "policy_or_config_changed": policy_or_config_changed,
        "unchanged": unchanged,
        "drift_detected": drift_detected,
    }


def _artifact_map(bom: Mapping[str, Any]) -> dict[tuple[str, str | None], Mapping[str, Any]]:
    result = {}
    for artifact in bom.get("artifacts", []):
        if not artifact.get("sha256"):
            continue
        key = (str(artifact.get("normalized_name") or artifact.get("name")), artifact.get("version"))
        result[key] = artifact
    return result


def _bom_policy_delta(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    before_policy = _bom_policy_fingerprint(before)
    after_policy = _bom_policy_fingerprint(after)
    before_status = before_policy["status"]
    after_status = after_policy["status"]
    if before_policy["config_hash"] == after_policy["config_hash"]:
        changed = before_status != after_status
        return {
            "changed": changed,
            "kind": "policy_status_changed" if changed else "unchanged",
            "baseline_status": before_status,
            "current_status": after_status,
            "baseline_policy_hash": before_policy["config_hash"],
            "current_policy_hash": after_policy["config_hash"],
        }
    return {
        "changed": True,
        "kind": "policy_or_config_changed",
        "baseline_status": before_status,
        "current_status": after_status,
        "baseline_policy_hash": before_policy["config_hash"],
        "current_policy_hash": after_policy["config_hash"],
    }


def _bom_policy_fingerprint(bom: Mapping[str, Any]) -> dict[str, Any]:
    sections = {
        "license_policy": _policy_ref(bom.get("license_policy_screening", {})),
        "entry_point_policy": _policy_ref(bom.get("entry_point_policy_screening", {})),
        "target_environment": _policy_ref(bom.get("target_environment_screening", {})),
    }
    config_hash = sha256(json.dumps(sections, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "config_hash": config_hash,
        "status": bom.get("combined_policy_verdict", {}).get("combined_verdict"),
        "policy_refs": sections,
    }


def _policy_ref(section: Any) -> dict[str, Any]:
    if not isinstance(section, Mapping) or not section.get("evaluated"):
        return {"evaluated": False, "sha256": None}
    ref = section.get("policy_ref") or section.get("target_ref") or {}
    return {
        "evaluated": True,
        "sha256": ref.get("sha256"),
        "schema": section.get("schema"),
        "schema_version": section.get("schema_version"),
    }


def _artifact_policy_fingerprint(artifact: Mapping[str, Any]) -> dict[str, Any]:
    policy_source = {
        "license_policy_evaluated": artifact.get("license_visibility", {}).get("policy_evaluated"),
        "entry_point_policy_evaluated": artifact.get("entry_points_visibility", {}).get("policy_evaluated"),
        "wheel_tag_policy_evaluated": artifact.get("wheel_tag_visibility", {}).get("policy_evaluated"),
    }
    config_hash = sha256(json.dumps(policy_source, sort_keys=True).encode("utf-8")).hexdigest()
    return {
        "config_hash": config_hash,
        "status": artifact.get("graph_status") or artifact.get("status"),
    }


def _version_changes(
    baseline: Mapping[tuple[str, str | None], Mapping[str, Any]],
    current: Mapping[tuple[str, str | None], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    baseline_versions: dict[str, set[str | None]] = {}
    current_versions: dict[str, set[str | None]] = {}
    for name, version in baseline:
        baseline_versions.setdefault(name, set()).add(version)
    for name, version in current:
        current_versions.setdefault(name, set()).add(version)
    records = []
    for name in sorted(set(baseline_versions) & set(current_versions)):
        before = baseline_versions[name]
        after = current_versions[name]
        if before != after:
            records.append(
                {
                    "normalized_name": name,
                    "baseline_versions": sorted(v for v in before if v is not None),
                    "current_versions": sorted(v for v in after if v is not None),
                    "note": "version_changed is reported in addition to artifact-level added/removed identities",
                }
            )
    return records


def _drift_exit_code(graph_verdict: Any, drift_detected: bool) -> int:
    if graph_verdict == "GRAPH_BLOCK":
        return 1
    if graph_verdict == "GRAPH_WARN":
        return 2
    if drift_detected:
        return 3
    return 0


def _refusal_report(
    baseline_path: Path,
    *,
    actual_sha256: str | None,
    expected_sha256: str | None,
    trust: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "schema": DRIFT_SCHEMA,
        "schema_version": DRIFT_SCHEMA_VERSION,
        "created_at_utc": _utc(),
        "baseline_ref": {
            "path": str(baseline_path.resolve()),
            "actual_sha256": actual_sha256,
            "expected_sha256": expected_sha256,
            "trust": trust,
        },
        "reason": reason,
        "current_ref": None,
        "summary": {
            "added_count": 0,
            "removed_count": 0,
            "changed_count": 0,
            "subtree_digest_changed_count": 0,
            "version_changed_count": 0,
            "policy_status_changed_count": 0,
            "policy_or_config_changed_count": 0,
            "unchanged_count": 0,
            "drift_detected": False,
            "baseline_trust": trust,
            "current_policy_verdict": None,
            "exit_code": 4,
        },
        "artifacts": [],
        "not_claimed": list(DRIFT_NOT_CLAIMED),
    }


def _write_drift_outputs(output: Path, report: dict[str, Any], *, package_evidence: bool) -> dict[str, Any]:
    report_path = output / "drift_report.json"
    summary_path = output / "drift_summary.txt"
    summary_text = _summary_text(report)
    report["report_path"] = str(report_path.resolve())
    report["summary_path"] = str(summary_path.resolve())
    report["summary_text"] = summary_text
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(summary_text, encoding="utf-8", newline="\n")
    if package_evidence and report.get("summary", {}).get("exit_code") != 4:
        package_result = package_lock(
            package_name="SPIRA_DRIFT_EVIDENCE_PACKAGE_001_BASELINE",
            payload_files=[report_path, summary_path],
            output_dir=output / "governance",
            lock_metadata={
                "classification": "SPIRA_BASELINE_DRIFT_EVIDENCE_PACKAGE_001",
                "schema_version": DRIFT_SCHEMA_VERSION,
                "drift_exit_code": report.get("summary", {}).get("exit_code"),
                "baseline_trust": report.get("baseline_ref", {}).get("trust"),
                "drift_detected": report.get("summary", {}).get("drift_detected"),
            },
            not_claimed=DRIFT_NOT_CLAIMED,
        )
        report["drift_evidence_package"] = package_result
        package_result_path = output / "drift_evidence_package_result.json"
        package_result_path.write_text(json.dumps(package_result, indent=2) + "\n", encoding="utf-8", newline="\n")
        report["drift_evidence_package_result_path"] = str(package_result_path.resolve())
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def _summary_text(report: Mapping[str, Any]) -> str:
    summary = report.get("summary", {})
    exit_code = summary.get("exit_code")
    if exit_code == 4:
        reason = report.get("reason") or "baseline could not be trusted"
        headline = f"[BASELINE_UNTRUSTED] {reason}; drift was not computed"
    elif exit_code == 1:
        headline = "[BLOCK] current policies produced a blocking verdict"
    elif exit_code == 2:
        headline = "[WARN] current policies produced a warning verdict"
    elif exit_code == 3:
        headline = "[DRIFT_DETECTED] baseline and current local wheels differ"
    else:
        headline = "[NO_DRIFT] baseline and current local wheels match"
    return "\n".join(
        [
            "SPIRA Baseline Drift Summary",
            "============================",
            headline,
            "",
            f"Baseline trust: {report.get('baseline_ref', {}).get('trust')}",
            f"Added: {summary.get('added_count', 0)}",
            f"Removed: {summary.get('removed_count', 0)}",
            f"Changed own wheel bytes: {summary.get('changed_count', 0)}",
            f"Subtree digest changed: {summary.get('subtree_digest_changed_count', 0)}",
            f"Version changed: {summary.get('version_changed_count', 0)}",
            f"Policy status changed: {summary.get('policy_status_changed_count', 0)}",
            f"Policy/config changed: {summary.get('policy_or_config_changed_count', 0)}",
            "",
            "Boundary: drift is a fact, not a verdict; re-baseline is a human decision.",
            "",
        ]
    )


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _baseline_trust(actual_sha256: str, expected_sha256: str | None) -> str:
    if expected_sha256 is None:
        return "UNPINNED"
    if actual_sha256.lower() == expected_sha256.lower():
        return "PINNED_MATCH"
    return "PINNED_MISMATCH"


def _artifact_delta_record(artifact: Mapping[str, Any], status: str) -> dict[str, Any]:
    return {
        "identity": {
            "normalized_name": artifact.get("normalized_name"),
            "version": artifact.get("version"),
        },
        "status": status,
        "sha256": artifact.get("sha256"),
        "subtree_integrity_digest": _subtree_digest(artifact),
    }


def _identity_payload(key: tuple[str, str | None]) -> dict[str, Any]:
    return {"normalized_name": key[0], "version": key[1]}


def _subtree_digest(artifact: Mapping[str, Any]) -> Any:
    return artifact.get("integrity", {}).get("subtree_integrity_digest")


def _hash_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
