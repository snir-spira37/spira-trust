from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Mapping

from .combined_verdict import DECISION_SEMANTICS_VERSION, agent_default_decision, agent_reason_codes
from .unification_proof import build_unification_proof, build_unification_reference


AGENT_SUMMARY_SCHEMA = "SPIRA_AGENT_SUMMARY_V1"
AGENT_SUMMARY_SCHEMA_VERSION = "1.0"
AGENT_ACTION_SCHEMA = "SPIRA_AGENT_ACTION_V1"
AGENT_ACTION_SCHEMA_VERSION = "1.0"


def write_agent_summary(
    graph_result: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    output_dir: str | Path,
    evidence_pack_path: str | Path | None = None,
    include_local_paths: bool = False,
    state_dir: str | Path | None = None,
) -> dict[str, Any]:
    output = Path(output_dir)
    summary = build_agent_summary(
        graph_result,
        decision,
        output_dir=output,
        evidence_pack_path=evidence_pack_path,
        include_local_paths=include_local_paths,
    )
    proof = build_unification_proof(summary, decision)
    proof_path = output / "unification_proof.json"
    proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary["unification"] = build_unification_reference(
        proof,
        proof_path=_path_ref(proof_path, output, include_local_paths=include_local_paths),
    )
    if isinstance(graph_result, dict):
        graph_result["unification_proof_path"] = str(proof_path.resolve())
    summary_path = output / "agent_summary.json"
    summary_path.write_text(_agent_json(summary) + "\n", encoding="utf-8", newline="\n")
    summary["agent_summary_path"] = str(summary_path.resolve())
    _write_state_copy(summary, state_dir=state_dir)
    return summary


def build_agent_summary(
    graph_result: Mapping[str, Any],
    decision: Mapping[str, Any],
    *,
    output_dir: str | Path,
    evidence_pack_path: str | Path | None = None,
    include_local_paths: bool = False,
) -> dict[str, Any]:
    output = Path(output_dir)
    decision_block = decision.get("decision", {}) or {}
    layers = decision.get("layers", {}) or {}
    not_evaluated = list(layers.get("not_evaluated_layers") or [])
    verdict = str(decision_block.get("verdict") or graph_result.get("verdict") or "GRAPH_UNKNOWN")
    combined_verdict = decision_block.get("combined_verdict")
    action_verdict = str(combined_verdict or verdict)
    agent_decision = agent_default_decision(action_verdict, not_evaluated_layers=not_evaluated)
    artifacts = _artifact_refs(graph_result, include_local_paths=include_local_paths)
    artifact_sha_values = [item["sha256"] for item in artifacts if item.get("sha256")]
    artifact_set_sha = _stable_digest({"artifact_sha256_values": sorted(artifact_sha_values)})
    command_fingerprint = str(graph_result.get("command_fingerprint") or _stable_digest(_command_payload(graph_result)))
    blockers = _findings(graph_result, effect="BLOCK")
    warnings = _findings(graph_result, effect="WARN")
    notes = _findings(graph_result, effect="NOTE")
    policy_sha = _effective_policy_sha(graph_result)
    reason_codes = agent_reason_codes(
        agent_decision,
        verdict=action_verdict,
        not_evaluated_layers=not_evaluated,
        blockers=blockers,
        warnings=warnings,
    )
    evidence = {
        "decision": _path_ref(decision.get("decision_json_path"), output, include_local_paths=include_local_paths),
        "decision_markdown": _path_ref(decision.get("decision_markdown_path"), output, include_local_paths=include_local_paths),
        "graph_summary": _path_ref(graph_result.get("summary_path"), output, include_local_paths=include_local_paths),
        "graph_report": _path_ref(graph_result.get("report_path"), output, include_local_paths=include_local_paths),
        "bill_of_materials": _path_ref(graph_result.get("bill_of_materials_path"), output, include_local_paths=include_local_paths),
        "evidence_pack": _path_ref(evidence_pack_path, output, include_local_paths=include_local_paths),
    }
    action_contract = {
        "schema": AGENT_ACTION_SCHEMA,
        "schema_version": AGENT_ACTION_SCHEMA_VERSION,
        "decision_semantics_version": DECISION_SEMANTICS_VERSION,
        "artifact_sha256": artifact_sha_values[0] if len(artifact_sha_values) == 1 else None,
        "artifact_set_sha256": artifact_set_sha,
        "policy_sha256": policy_sha,
        "command_fingerprint": command_fingerprint,
        "graph_verdict": verdict,
        "combined_verdict": combined_verdict,
        "action_verdict": action_verdict,
        "stop": agent_decision["stop"],
        "stop_source": agent_decision["stop_source"],
        "recommended_agent_action": agent_decision["recommended_agent_action"],
        "reason_codes": reason_codes,
        "not_evaluated": not_evaluated,
        "evidence": evidence.get("decision") or evidence.get("graph_report"),
    }
    summary = {
        "schema": AGENT_SUMMARY_SCHEMA,
        "schema_version": AGENT_SUMMARY_SCHEMA_VERSION,
        "created_at": _utc(),
        "tool": {"name": "spira-trust", "version": _tool_version()},
        "decision_semantics_version": DECISION_SEMANTICS_VERSION,
        "agent_action_contract": action_contract,
        "verdict": verdict,
        "combined_verdict": combined_verdict,
        "action_verdict": action_verdict,
        "winning_status": decision_block.get("winning_status"),
        "exit_code": decision_block.get("exit_code"),
        "stop": agent_decision["stop"],
        "stop_source": agent_decision["stop_source"],
        "recommended_agent_action": agent_decision["recommended_agent_action"],
        "reason_codes": reason_codes,
        "not_evaluated": not_evaluated,
        "evidence": evidence,
        "summary_of": {
            "artifact_count": len(artifacts),
            "artifact_sha256_values": sorted(artifact_sha_values),
            "artifact_set_sha256": artifact_set_sha,
            "command_fingerprint": command_fingerprint,
            "tool_version": _tool_version(),
            "decision_semantics_version": DECISION_SEMANTICS_VERSION,
            "policy_sha256": policy_sha,
            "decision_sha256": _file_sha(decision.get("decision_json_path")),
            "graph_report_sha256": _file_sha(graph_result.get("report_path")),
        },
        "artifacts": artifacts,
        "approval": {
            "approved": False,
            "approval_source": "unverified",
        },
        "not_claimed": [
            "agent summary is an index over existing SPIRA evidence",
            "does not create new trust evidence",
            "does not turn NOT_EVALUATED into OK",
            "does not ask the agent to infer gate policy from prose",
            "approval metadata does not alter graph or combined verdicts",
        ],
    }
    if blockers:
        summary["blockers"] = blockers
    if warnings:
        summary["warnings"] = warnings
    if notes:
        summary["notes"] = notes
    proof = build_unification_proof(summary, decision)
    summary["unification"] = build_unification_reference(proof)
    return summary


def _write_state_copy(summary: Mapping[str, Any], *, state_dir: str | Path | None) -> None:
    state_root = Path(state_dir) if state_dir else Path.cwd() / ".spira" / "agent_summaries"
    state_root.mkdir(parents=True, exist_ok=True)
    summary_of = summary.get("summary_of", {}) or {}
    key = _stable_digest(
        {
            "artifact_set_sha256": summary_of.get("artifact_set_sha256"),
            "command_fingerprint": summary_of.get("command_fingerprint"),
            "tool_version": summary_of.get("tool_version"),
        }
    )
    path = state_root / f"{key}.agent_summary.json"
    path.write_text(_agent_json(summary) + "\n", encoding="utf-8", newline="\n")


def _artifact_refs(graph_result: Mapping[str, Any], *, include_local_paths: bool) -> list[dict[str, Any]]:
    refs = []
    for node in graph_result.get("nodes", []) or []:
        if node.get("node_type") != "provided_artifact":
            continue
        path_value = node.get("artifact_path")
        entry = {
            "name": node.get("package_name"),
            "version": node.get("version"),
            "filename": Path(str(path_value or "")).name,
            "sha256": node.get("artifact_sha256"),
        }
        if include_local_paths and path_value:
            entry["path"] = str(Path(str(path_value)).resolve())
        refs.append(entry)
    return sorted(refs, key=lambda item: (str(item.get("name") or ""), str(item.get("version") or ""), str(item.get("sha256") or "")))


def _findings(graph_result: Mapping[str, Any], *, effect: str) -> list[str]:
    findings = []
    for event in graph_result.get("propagation_events", []) or []:
        if event.get("effect") == effect and event.get("reason"):
            findings.append(str(event["reason"]))
    if effect == "BLOCK":
        for node in graph_result.get("nodes", []) or []:
            if node.get("graph_status") == "BLOCK":
                findings.extend(str(reason) for reason in node.get("reasons", []) or [])
    return sorted(dict.fromkeys(findings))


def _command_payload(graph_result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "command": "graph",
        "strict_closure": bool(graph_result.get("strict_closure")),
        "inputs": sorted(str(value) for value in graph_result.get("inputs", []) or []),
        "pep770_status": (graph_result.get("pep770_sbom_consistency") or {}).get("status"),
        "pep740_status": (graph_result.get("pep740_offline_attestations") or {}).get("status"),
    }


def _path_ref(value: Any, base_dir: Path, *, include_local_paths: bool) -> str | None:
    if not value:
        return None
    path = Path(str(value))
    if include_local_paths:
        return str(path.resolve())
    try:
        return path.resolve().relative_to(base_dir.resolve()).as_posix()
    except ValueError:
        return path.name


def _file_sha(value: Any) -> str | None:
    if not value:
        return None
    path = Path(str(value))
    if not path.is_file():
        return None
    return sha256(path.read_bytes()).hexdigest()


def _effective_policy_sha(graph_result: Mapping[str, Any]) -> str | None:
    bom_path = graph_result.get("bill_of_materials_path")
    if not bom_path:
        return None
    try:
        bom = json.loads(Path(str(bom_path)).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    governance = bom.get("governance_evidence") if isinstance(bom, dict) else None
    if isinstance(governance, Mapping):
        value = governance.get("effective_policy_sha256")
        return str(value) if value else None
    value = bom.get("effective_policy_sha256") if isinstance(bom, dict) else None
    return str(value) if value else None


def _stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _agent_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _tool_version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        return "source-tree"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
