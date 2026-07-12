from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping


STATUS_SCHEMA = "SPIRA_AGENT_STATUS_V1"
STATUS_SCHEMA_VERSION = "1.0"
AGENT_ARTIFACT_STATUS_SCHEMA = "SPIRA_AGENT_ARTIFACT_STATUS_V1"
AGENT_ARTIFACT_STATUS_SCHEMA_VERSION = "1.1"


def build_agent_status(
    artifact_inputs: Iterable[str | Path],
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    artifacts = _discover_wheels(artifact_inputs)
    current = [_artifact_ref(path) for path in artifacts]
    summaries = _load_summaries(Path(state_dir) if state_dir else Path.cwd() / ".spira" / "agent_summaries")
    by_sha: dict[str, list[dict[str, Any]]] = {}
    by_filename: dict[str, list[dict[str, Any]]] = {}
    for summary in summaries:
        for artifact in summary.get("artifacts", []) or []:
            if artifact.get("sha256"):
                by_sha.setdefault(str(artifact["sha256"]), []).append(summary)
            if artifact.get("filename"):
                by_filename.setdefault(str(artifact["filename"]), []).append(summary)

    checked = []
    unchecked = []
    changed = []
    for artifact in current:
        matches = by_sha.get(artifact["sha256"], [])
        if matches:
            checked.append(_status_entry(artifact, matches))
            continue
        filename_matches = by_filename.get(artifact["filename"], [])
        if filename_matches:
            changed.append(_status_entry(artifact, filename_matches, changed_since_check=True))
        else:
            unchecked.append(artifact)

    matching_summaries = _unique_summaries([entry for item in checked + changed for entry in item.get("summaries", [])])
    not_evaluated = sorted(
        {
            str(layer)
            for summary in matching_summaries
            for layer in summary.get("not_evaluated", []) or []
        }
    )
    verdict_counts: dict[str, int] = {}
    action_counts: dict[str, int] = {}
    for summary in matching_summaries:
        verdict_counts[str(summary.get("verdict"))] = verdict_counts.get(str(summary.get("verdict")), 0) + 1
        action = str(summary.get("recommended_agent_action"))
        action_counts[action] = action_counts.get(action, 0) + 1
    return {
        "schema": STATUS_SCHEMA,
        "schema_version": STATUS_SCHEMA_VERSION,
        "created_at": _utc(),
        "state_dir": str((Path(state_dir) if state_dir else Path.cwd() / ".spira" / "agent_summaries").resolve()),
        "counts": {
            "artifacts": len(current),
            "checked": len(checked),
            "unchecked": len(unchecked),
            "changed_since_check": len(changed),
            "summaries_indexed": len(summaries),
        },
        "checked": checked,
        "unchecked": unchecked,
        "changed_since_check": changed,
        "not_evaluated": not_evaluated,
        "verdict_counts": verdict_counts,
        "recommended_agent_action_counts": action_counts,
        "not_claimed": [
            "status is an index over agent_summary.json files",
            "status re-hashes current artifacts before matching cache state",
            "status does not replace per-run agent_summary.json",
            "status does not approve artifacts",
        ],
    }


def build_agent_artifact_status(
    artifact_path: str | Path,
    *,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    path = Path(artifact_path)
    if not path.is_file() or path.suffix != ".whl":
        return _agent_status_miss(
            artifact={"path": str(path), "filename": path.name, "sha256": None},
            reason_code="ARTIFACT_NOT_FOUND",
            checked=False,
            stale=False,
            changed_since_check=False,
            summary_path=None,
            summary_count=0,
        )
    artifact = _artifact_ref(path)
    summaries = _load_summaries(Path(state_dir) if state_dir else Path.cwd() / ".spira" / "agent_summaries")
    sha_matches = _summaries_for_sha(summaries, str(artifact["sha256"]))
    if sha_matches:
        return _agent_status_hit(artifact, _latest_summary(sha_matches), summary_count=len(sha_matches))
    filename_matches = _summaries_for_filename(summaries, str(artifact["filename"]))
    if filename_matches:
        latest = _latest_summary(filename_matches)
        return _agent_status_miss(
            artifact=artifact,
            reason_code="ARTIFACT_CHANGED_SINCE_CHECK",
            checked=False,
            stale=True,
            changed_since_check=True,
            summary_path=latest.get("_loaded_from"),
            summary_count=len(filename_matches),
            previous_artifact_sha256=_first_artifact_sha(latest),
        )
    return _agent_status_miss(
        artifact=artifact,
        reason_code="ARTIFACT_NOT_CHECKED",
        checked=False,
        stale=False,
        changed_since_check=False,
        summary_path=None,
        summary_count=0,
    )


def format_agent_status(status: Mapping[str, Any]) -> str:
    counts = status.get("counts", {}) or {}
    lines = [
        "SPIRA Agent Status",
        "==================",
        f"Artifacts: {counts.get('artifacts', 0)}",
        f"Checked: {counts.get('checked', 0)}",
        f"Unchecked: {counts.get('unchecked', 0)}",
        f"Changed since check: {counts.get('changed_since_check', 0)}",
    ]
    if status.get("not_evaluated"):
        lines.append(f"Not evaluated layers present: {', '.join(status.get('not_evaluated') or [])}")
    if status.get("unchecked"):
        lines.append("")
        lines.append("Unchecked:")
        for artifact in status.get("unchecked", [])[:8]:
            lines.append(f"- {artifact.get('filename')} {artifact.get('sha256')}")
    if status.get("changed_since_check"):
        lines.append("")
        lines.append("Changed since check:")
        for artifact in status.get("changed_since_check", [])[:8]:
            lines.append(f"- {artifact.get('artifact', {}).get('filename')}")
    return "\n".join(lines) + "\n"


def format_agent_artifact_status(status: Mapping[str, Any]) -> str:
    lines = [
        "SPIRA Agent Artifact Status",
        "===========================",
        f"Artifact: {status.get('filename')}",
        f"Checked: {status.get('checked')}",
        f"Changed since check: {status.get('changed_since_check')}",
        f"Stop: {status.get('stop')}",
        f"Action: {status.get('recommended_agent_action')}",
    ]
    if status.get("reason_codes"):
        lines.append(f"Reason codes: {', '.join(status.get('reason_codes') or [])}")
    if status.get("summary_path"):
        lines.append(f"Summary: {status.get('summary_path')}")
    return "\n".join(lines) + "\n"


def _status_entry(
    artifact: Mapping[str, Any],
    summaries: list[dict[str, Any]],
    *,
    changed_since_check: bool = False,
) -> dict[str, Any]:
    refs = []
    for summary in summaries:
        refs.append(
            {
                "schema": summary.get("schema"),
                "created_at": summary.get("created_at"),
                "verdict": summary.get("verdict"),
                "stop": summary.get("stop"),
                "recommended_agent_action": summary.get("recommended_agent_action"),
                "not_evaluated": summary.get("not_evaluated", []),
                "summary_of": summary.get("summary_of", {}),
                "agent_summary_path": summary.get("_loaded_from"),
            }
        )
    return {
        "artifact": dict(artifact),
        "changed_since_check": changed_since_check,
        "summaries": refs,
    }


def _unique_summaries(items: list[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = str(item.get("agent_summary_path") or json.dumps(item.get("summary_of", {}), sort_keys=True))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _agent_status_hit(artifact: Mapping[str, Any], summary: Mapping[str, Any], *, summary_count: int) -> dict[str, Any]:
    contract = summary.get("agent_action_contract") if isinstance(summary.get("agent_action_contract"), Mapping) else summary
    approval = summary.get("approval") if isinstance(summary.get("approval"), Mapping) else {}
    not_evaluated = _canonical_list(contract.get("not_evaluated") or summary.get("not_evaluated") or [])
    action = contract.get("recommended_agent_action")
    if action == "REPORT_NOT_EVALUATED" and not not_evaluated:
        return _agent_status_miss(
            artifact=artifact,
            reason_code="NOT_EVALUATED_DETAILS_MISSING",
            checked=False,
            stale=True,
            changed_since_check=False,
            summary_path=summary.get("_loaded_from"),
            summary_count=summary_count,
        )
    return {
        "schema": AGENT_ARTIFACT_STATUS_SCHEMA,
        "schema_version": AGENT_ARTIFACT_STATUS_SCHEMA_VERSION,
        "created_at": _utc(),
        "filename": artifact.get("filename"),
        "artifact_sha256": artifact.get("sha256"),
        "checked": True,
        "stale": False,
        "changed_since_check": False,
        "approved": bool(approval.get("approved", False)),
        "approval_source": approval.get("approval_source", "unverified"),
        "decision_semantics_version": contract.get("decision_semantics_version") or summary.get("decision_semantics_version"),
        "action_verdict": contract.get("action_verdict") or summary.get("action_verdict"),
        "stop": contract.get("stop"),
        "recommended_agent_action": action,
        "reason_codes": list(contract.get("reason_codes") or summary.get("reason_codes") or []),
        "summary_path": summary.get("_loaded_from"),
        "summary_count": summary_count,
        "evidence": contract.get("evidence"),
        "not_evaluated": not_evaluated,
        "not_evaluated_count": len(not_evaluated),
        "scope": "index_only",
    }


def _agent_status_miss(
    *,
    artifact: Mapping[str, Any],
    reason_code: str,
    checked: bool,
    stale: bool,
    changed_since_check: bool,
    summary_path: Any,
    summary_count: int,
    previous_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    result = {
        "schema": AGENT_ARTIFACT_STATUS_SCHEMA,
        "schema_version": AGENT_ARTIFACT_STATUS_SCHEMA_VERSION,
        "created_at": _utc(),
        "filename": artifact.get("filename"),
        "artifact_sha256": artifact.get("sha256"),
        "checked": checked,
        "stale": stale,
        "changed_since_check": changed_since_check,
        "approved": False,
        "approval_source": "unverified",
        "decision_semantics_version": None,
        "action_verdict": None,
        "stop": True,
        "recommended_agent_action": "RERUN_REQUIRED",
        "reason_codes": [reason_code],
        "summary_path": summary_path,
        "summary_count": summary_count,
        "evidence": None,
        "not_evaluated": [],
        "not_evaluated_count": 0,
        "scope": "index_only",
    }
    if previous_artifact_sha256:
        result["previous_artifact_sha256"] = previous_artifact_sha256
    return result

def _summaries_for_sha(summaries: list[dict[str, Any]], sha_value: str) -> list[dict[str, Any]]:
    return [
        summary
        for summary in summaries
        for artifact in summary.get("artifacts", []) or []
        if str(artifact.get("sha256")) == sha_value
    ]


def _summaries_for_filename(summaries: list[dict[str, Any]], filename: str) -> list[dict[str, Any]]:
    return [
        summary
        for summary in summaries
        for artifact in summary.get("artifacts", []) or []
        if str(artifact.get("filename")) == filename
    ]


def _latest_summary(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(summaries, key=lambda item: (str(item.get("created_at") or ""), str(item.get("_loaded_from") or "")))[-1]


def _first_artifact_sha(summary: Mapping[str, Any]) -> str | None:
    for artifact in summary.get("artifacts", []) or []:
        if artifact.get("sha256"):
            return str(artifact["sha256"])
    return None


def _canonical_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values})


def _load_summaries(state_dir: Path) -> list[dict[str, Any]]:
    if not state_dir.is_dir():
        return []
    summaries = []
    for path in sorted(state_dir.glob("*.agent_summary.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("schema") != "SPIRA_AGENT_SUMMARY_V1":
            continue
        data["_loaded_from"] = str(path.resolve())
        summaries.append(data)
    return summaries


def _discover_wheels(inputs: Iterable[str | Path]) -> list[Path]:
    wheels: list[Path] = []
    for value in inputs:
        path = Path(value)
        if path.is_dir():
            wheels.extend(sorted(child for child in path.rglob("*.whl") if child.is_file()))
        elif path.is_file() and path.suffix == ".whl":
            wheels.append(path)
    return sorted({path.resolve() for path in wheels})


def _artifact_ref(path: Path) -> dict[str, Any]:
    return {"path": str(path.resolve()), "filename": path.name, "sha256": sha256(path.read_bytes()).hexdigest()}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
