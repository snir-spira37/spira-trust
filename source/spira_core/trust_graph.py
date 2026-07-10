from __future__ import annotations

import json
import platform
import re
import sys
import zipfile
from datetime import datetime, timezone
from email.parser import Parser
from hashlib import sha256
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Iterable, Mapping

from .bom import build_bill_of_materials, write_bill_of_materials
from .attestation_verify import evaluate_attestations
from .governance_engine import package_lock
from .policy_pack import PolicyPackUntrustedError, resolve_policy_inputs, write_policy_refusal
from .range_parser import evaluate_provided_versions, parse_specifier_set
from .sbom_consistency import evaluate_embedded_sbom_consistency
from .trust import run_artifact_trust_cycle


GRAPH_NOT_CLAIMED = [
    "local graph over explicitly provided artifacts only",
    "does not resolve dependencies",
    "does not access PyPI or the network",
    "does not download, install, import, or execute package code",
    "does not perform malware behavior analysis",
    "does not perform typosquatting detection",
    "does not perform Unicode confusable matching",
    "detects selected malformed marker classes; does not implement a complete PEP 508 marker validator",
    "V2 range checks evaluate only local provided wheel versions and supported numeric-tuple constraints",
    "V2 range checks do not resolve, fetch, suggest, or invent package versions",
    "unsupported V2 range specifiers are reported as UNVERIFIED notes, not silently passed or hard-blocked solely because unsupported",
    "PEP 770 embedded SBOM consistency is evaluated only when explicitly requested",
    "PEP 740 offline attestation checks use a narrow metadata/digest/identity subset and are not full Sigstore verification",
]

MAX_GRAPH_ARTIFACTS = 500


def normalize_pep503(name: str) -> str:
    """PEP 503-style distribution normalization only.

    This intentionally does not perform Unicode confusable folding, NFKC
    folding, fuzzy matching, typo correction, or visual-similarity matching.
    """

    return re.sub(r"[-_.]+", "-", name).lower()


def run_trust_graph(
    artifact_inputs: Iterable[str | Path],
    output_dir: str | Path,
    *,
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
    verify_embedded_sboms: bool = False,
    attestation_path: str | Path | None = None,
    attestation_trust_root_path: str | Path | None = None,
    attestation_trust_root_sha256: str | None = None,
) -> dict[str, Any]:
    artifact_inputs_list = list(artifact_inputs)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    try:
        policy_inputs = resolve_policy_inputs(
            output_dir=output,
            policy_pack_path=policy_pack_path,
            policy_sha256=policy_sha256,
            license_policy_path=license_policy_path,
            entry_point_policy_path=entry_point_policy_path,
            target_environment_path=target_environment_path,
            lockfile_path=lockfile_path,
        )
    except PolicyPackUntrustedError as exc:
        return write_policy_refusal(
            output,
            policy_pack_path=policy_pack_path,
            expected_sha256=policy_sha256,
            reason=str(exc),
        )
    license_policy_path = policy_inputs["license_policy_path"]
    entry_point_policy_path = policy_inputs["entry_point_policy_path"]
    target_environment_path = policy_inputs["target_environment_path"]
    lockfile_path = policy_inputs["lockfile_path"]
    effective_policy_path = policy_inputs["effective_policy_path"]
    artifacts = _discover_wheels(artifact_inputs_list)
    command_fingerprint = _command_fingerprint(
        artifacts,
        strict_closure=strict_closure,
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
        effective_policy_path=effective_policy_path,
        verify_embedded_sboms=verify_embedded_sboms,
        attestation_path=attestation_path,
        attestation_trust_root_path=attestation_trust_root_path,
        attestation_trust_root_sha256=attestation_trust_root_sha256,
        tool_version=tool_version,
    )
    if len(artifacts) > MAX_GRAPH_ARTIFACTS:
        return _scale_limit_report(
            output,
            artifacts,
            strict_closure=strict_closure,
            package_evidence=package_evidence,
            bundle_sha256=bundle_sha256,
            tool_version=tool_version,
            license_policy_path=license_policy_path,
            entry_point_policy_path=entry_point_policy_path,
            target_environment_path=target_environment_path,
            lockfile_path=lockfile_path,
            effective_policy_path=effective_policy_path,
            artifact_inputs=artifact_inputs_list,
        )
    nodes: dict[str, dict[str, Any]] = {}
    provided_by_name: dict[str, list[str]] = {}
    edges: list[dict[str, Any]] = []

    for artifact in artifacts:
        metadata = _read_wheel_metadata(artifact)
        package_name = metadata.get("Name") or artifact.stem
        normalized = normalize_pep503(package_name)
        version = metadata.get("Version")
        artifact_sha256 = _hash_file(artifact)
        node_id = _node_id(normalized, version, artifact_sha256)
        trust_output = output / "artifacts" / _safe_dir_name(node_id)
        trust_report = run_artifact_trust_cycle(artifact, trust_output, workspace_root=workspace_root)
        local_state = _local_state_from_trust(trust_report)
        node = {
            "id": node_id,
            "node_type": "provided_artifact",
            "package_name": package_name,
            "normalized_name": normalized,
            "version": version,
            "artifact_path": str(artifact.resolve()),
            "artifact_sha256": artifact_sha256,
            "local_review_status": local_state,
            "graph_status": local_state,
            "reasons": _node_reasons(trust_report, local_state),
            "evidence_refs": {
                "trust_report": trust_report.get("report_path"),
                "trust_summary": trust_report.get("summary_path"),
                "review_report": trust_report.get("review_report_path"),
            },
            "trust_status": trust_report.get("decision", {}).get("trust_status"),
            "review_verdict": trust_report.get("review_summary", {}).get("overall_verdict"),
            "declared_requirements": metadata.get("Requires-Dist", []),
            "propagated_notes": [],
        }
        nodes[node_id] = node
        provided_by_name.setdefault(normalized, []).append(node_id)

    for node in list(nodes.values()):
        for requirement in node.get("declared_requirements", []):
            parsed_requirement = _parse_requirement(requirement)
            if not parsed_requirement:
                continue
            dep = parsed_requirement["name"]
            required_version = parsed_requirement.get("exact_version")
            specifier = parsed_requirement.get("specifier") or ""
            dep_normalized = normalize_pep503(dep)
            relationship_type = _relationship_type(requirement)
            marker_error = _marker_error(requirement)
            if marker_error:
                range_evaluation = _range_note(specifier, f"range not evaluated because marker failed closed: {marker_error}")
                target_id = f"malformed-marker::{node['id']}::{len(edges)}"
                nodes[target_id] = {
                    "id": target_id,
                    "node_type": "malformed_declared_relationship",
                    "package_name": dep,
                    "normalized_name": dep_normalized,
                    "version": required_version,
                    "artifact_path": None,
                    "artifact_sha256": None,
                    "local_review_status": "BLOCK",
                    "graph_status": "BLOCK",
                    "reasons": [marker_error],
                    "evidence_refs": {},
                    "trust_status": None,
                    "review_verdict": None,
                    "declared_requirements": [],
                    "propagated_notes": [],
                }
                edges.append(
                    {
                        "from_node": node["id"],
                        "to_node": target_id,
                        "relationship_type": relationship_type,
                        "requirement_raw": requirement,
                        "required_name": dep,
                        "required_normalized_name": dep_normalized,
                        "required_exact_version": required_version,
                        "specifier_raw": specifier,
                        "parsed_constraint": range_evaluation["parsed_constraint"],
                        "evaluated": range_evaluation["evaluated"],
                        "satisfied_by_provided": range_evaluation["satisfied_by_provided"],
                        "note": range_evaluation["note"],
                        "range_evaluation": range_evaluation,
                        "source_metadata_file": "METADATA",
                        "matched_artifact": None,
                        "matched_artifacts": [],
                        "policy_source": None,
                        "boundary": "malformed marker is fail-closed graph evidence",
                    }
                )
                continue
            candidates = provided_by_name.get(dep_normalized, [])
            range_evaluation = _edge_range_evaluation(specifier, candidates, nodes)
            matches = [
                candidate
                for candidate in candidates
                if required_version is None or nodes[candidate].get("version") == required_version
            ]
            if len(matches) == 1:
                target_id = matches[0]
                matched_artifact = nodes[target_id].get("artifact_path")
                matched_artifacts = [matched_artifact]
            elif len(matches) > 1:
                target_id = f"ambiguous::{node['id']}::{dep_normalized}"
                matched_artifact = None
                matched_artifacts = [nodes[match].get("artifact_path") for match in matches]
                ambiguity_state = "BLOCK" if relationship_type == "depends_on_declared" else "WARN"
                if target_id not in nodes:
                    nodes[target_id] = {
                        "id": target_id,
                        "node_type": "declared_ambiguous_artifact",
                        "package_name": dep,
                        "normalized_name": dep_normalized,
                        "version": None,
                        "artifact_path": None,
                        "artifact_sha256": None,
                        "local_review_status": ambiguity_state,
                        "graph_status": ambiguity_state,
                        "reasons": ["multiple local wheels matched the declared name; v1 does not resolve versions"],
                        "evidence_refs": {},
                        "trust_status": None,
                        "review_verdict": None,
                        "declared_requirements": [],
                        "propagated_notes": [],
                        "matched_candidates": matched_artifacts,
                    }
            else:
                missing_suffix = f"=={required_version}" if required_version else ""
                target_id = f"missing::{dep_normalized}{missing_suffix}"
                matched_artifact = None
                matched_artifacts = []
                if target_id not in nodes:
                    nodes[target_id] = {
                        "id": target_id,
                        "node_type": "declared_missing_artifact",
                        "package_name": dep,
                        "normalized_name": dep_normalized,
                        "version": required_version,
                        "artifact_path": None,
                        "artifact_sha256": None,
                        "local_review_status": "UNVERIFIED",
                        "graph_status": "UNVERIFIED",
                        "reasons": [
                            "declared dependency was not provided as a local wheel"
                            if not candidates
                            else "declared exact version was not provided as a local wheel"
                        ],
                        "evidence_refs": {},
                        "trust_status": None,
                        "review_verdict": None,
                        "declared_requirements": [],
                        "propagated_notes": [],
                    }
            edges.append(
                {
                    "from_node": node["id"],
                    "to_node": target_id,
                    "relationship_type": relationship_type,
                    "requirement_raw": requirement,
                    "required_name": dep,
                    "required_normalized_name": dep_normalized,
                    "required_exact_version": required_version,
                    "specifier_raw": specifier,
                    "parsed_constraint": range_evaluation["parsed_constraint"],
                    "evaluated": range_evaluation["evaluated"],
                    "satisfied_by_provided": range_evaluation["satisfied_by_provided"],
                    "note": range_evaluation["note"],
                    "range_evaluation": range_evaluation,
                    "source_metadata_file": "METADATA",
                    "matched_artifact": matched_artifact,
                    "matched_artifacts": matched_artifacts,
                    "policy_source": None,
                    "boundary": "propagation effect is computed, not stored as authoritative input",
                }
            )

    root_node_ids = _root_nodes(nodes, edges)
    structural_events = []
    structural_events.extend(_apply_cycle_blocks(nodes, edges))
    structural_events.extend(_apply_pinned_version_conflict_blocks(nodes, edges, root_node_ids))
    structural_events.extend(_apply_range_conflict_blocks(nodes, edges, root_node_ids, provided_by_name))
    sbom_consistency_events = _apply_sbom_consistency_findings(nodes) if verify_embedded_sboms else []
    attestation_result = evaluate_attestations(
        [
            {"path": node.get("artifact_path"), "sha256": node.get("artifact_sha256")}
            for node in nodes.values()
            if node.get("node_type") == "provided_artifact"
        ],
        attestation_path=attestation_path,
        trust_root_path=attestation_trust_root_path,
        trust_root_sha256=attestation_trust_root_sha256,
    )
    attestation_events = _apply_attestation_findings(nodes, attestation_result)
    pre_policy_report = {
        "schema": "SPIRA_TRUST_GRAPH_V2_REPORT",
        "schema_version": "2.0",
        "root_nodes": root_node_ids,
        "nodes": list(nodes.values()),
        "edges": edges,
    }
    pre_policy_bom = build_bill_of_materials(
        pre_policy_report,
        tool_version=tool_version,
        bundle_sha256=bundle_sha256 or _env_nonempty("SPIRA_BUNDLE_SHA256"),
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
    )
    license_policy_events = _apply_license_policy_findings(nodes, pre_policy_bom)
    entry_point_policy_events = _apply_entry_point_policy_findings(nodes, pre_policy_bom)
    target_environment_events = _apply_target_environment_findings(nodes, pre_policy_bom)
    lockfile_events = _apply_lockfile_cross_check_findings(nodes, pre_policy_bom)
    propagation_events = (
        structural_events
        + license_policy_events
        + entry_point_policy_events
        + target_environment_events
        + lockfile_events
        + sbom_consistency_events
        + attestation_events
        + _propagate(nodes, edges, strict_closure=strict_closure)
    )
    root_verdict = _root_verdict(nodes, root_node_ids)
    summary = _summary(nodes, edges, propagation_events, root_node_ids, root_verdict, strict_closure=strict_closure)
    report = {
        "schema": "SPIRA_TRUST_GRAPH_V2_REPORT",
        "schema_version": "2.0",
        "verdict": root_verdict,
        "strict_closure": strict_closure,
        "command_fingerprint": command_fingerprint,
        "inputs": [str(path.resolve()) for path in artifacts],
        "counts": _counts(nodes, edges),
        "root_nodes": root_node_ids,
        "nodes": list(nodes.values()),
        "edges": edges,
        "propagation_events": propagation_events,
        "pep770_sbom_consistency": _sbom_consistency_summary(nodes, verify_embedded_sboms),
        "pep740_offline_attestations": attestation_result,
        "name_normalization": {
            "rule": "PEP_503_STYLE_ONLY",
            "not_performed": [
                "Unicode confusable folding",
                "NFKC folding for graph matching",
                "fuzzy matching",
                "typo correction",
                "visual similarity matching",
            ],
        },
        "not_claimed": list(GRAPH_NOT_CLAIMED),
    }
    report_path = output / "graph_report.json"
    summary_path = output / "graph_summary.txt"
    bom_path = output / "bill_of_materials.json"
    report["report_path"] = str(report_path.resolve())
    report["summary_path"] = str(summary_path.resolve())
    report["bill_of_materials_path"] = str(bom_path.resolve())
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(summary, encoding="utf-8", newline="\n")
    write_bill_of_materials(
        report,
        bom_path,
        tool_version=tool_version,
        bundle_sha256=bundle_sha256 or _env_nonempty("SPIRA_BUNDLE_SHA256"),
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
    )
    bom = json.loads(bom_path.read_text(encoding="utf-8"))
    report["license_policy_screening"] = _license_policy_summary(bom)
    report["entry_point_policy_screening"] = _entry_point_policy_summary(bom)
    report["target_environment_screening"] = _target_environment_summary(bom)
    report["lockfile_cross_check"] = _lockfile_cross_check_summary(bom)
    report["combined_policy_verdict"] = bom.get("combined_policy_verdict")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = _write_graph_evidence(
        output,
        artifacts,
        report_path,
        summary_path,
        bom_path,
        report,
        strict_closure=strict_closure,
        package_evidence=package_evidence,
        bundle_sha256=bundle_sha256,
        tool_version=tool_version,
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
        effective_policy_path=effective_policy_path,
        artifact_inputs=artifact_inputs_list,
    )
    report["input_manifest_path"] = evidence["input_manifest_path"]
    report["graph_evidence_manifest_path"] = evidence["graph_evidence_manifest_path"]
    report["bill_of_materials_path"] = str(bom_path.resolve())
    report["bill_of_materials_sha256"] = evidence["bill_of_materials_sha256"]
    report["graph_evidence_package"] = evidence.get("graph_evidence_package")
    report["summary_text"] = summary
    return report


def format_graph_summary(report: Mapping[str, Any]) -> str:
    text = report.get("summary_text")
    if isinstance(text, str):
        return text
    path = report.get("summary_path")
    if isinstance(path, str) and Path(path).is_file():
        return Path(path).read_text(encoding="utf-8")
    return "SPIRA Trust Graph Summary\n=========================\n[GRAPH_UNKNOWN] summary unavailable\n"


def graph_exit_code(report: Mapping[str, Any]) -> int:
    if report.get("verdict") == "POLICY_UNTRUSTED":
        return 5
    if report.get("verdict") == "SBOM_EXPORT_ERROR":
        return 6
    if str(report.get("verdict", "")).endswith("_INPUT_ERROR"):
        return 1
    verdict = report.get("verdict")
    if verdict == "GRAPH_BLOCK":
        return 1
    if verdict == "GRAPH_WARN":
        return 2
    return 0


def _write_graph_evidence(
    output: Path,
    artifacts: list[Path],
    report_path: Path,
    summary_path: Path,
    bom_path: Path,
    report: Mapping[str, Any],
    *,
    strict_closure: bool,
    package_evidence: bool,
    bundle_sha256: str | None,
    tool_version: str | None,
    license_policy_path: str | Path | None,
    entry_point_policy_path: str | Path | None,
    target_environment_path: str | Path | None,
    lockfile_path: str | Path | None,
    effective_policy_path: str | Path | None,
    artifact_inputs: Iterable[str | Path],
) -> dict[str, Any]:
    input_manifest_path = output / "input_manifest.json"
    graph_evidence_manifest_path = output / "graph_evidence_manifest.json"
    resolved_bundle_sha = bundle_sha256 or _env_nonempty("SPIRA_BUNDLE_SHA256")
    resolved_tool_version = tool_version or _tool_version()
    input_manifest = {
        "schema": "SPIRA_TRUST_GRAPH_INPUT_MANIFEST",
        "schema_version": "1.0",
        "created_at_utc": _utc(),
        "artifact_count": len(artifacts),
        "artifacts": [_input_manifest_entry(path) for path in artifacts],
        "normalization": {
            "rule": "PEP_503_STYLE_ONLY",
            "not_performed": [
                "Unicode confusable folding",
                "NFKC folding for graph matching",
                "fuzzy matching",
            ],
        },
        "not_claimed": [
            "input manifest records local files only",
            "does not prove installability",
            "does not resolve dependencies",
        ],
    }
    _write_json(input_manifest_path, input_manifest)

    graph_evidence_manifest = {
        "schema": "SPIRA_TRUST_GRAPH_EVIDENCE_MANIFEST",
        "schema_version": "2.0",
        "created_at_utc": _utc(),
        "graph_report_schema": str(report.get("schema", "UNKNOWN")),
        "graph_report_schema_version": str(report.get("schema_version", "UNKNOWN")),
        "tool_identity": {
            "tool_name": "spira-core graph",
            "tool_version": resolved_tool_version,
            "bundle_sha256": resolved_bundle_sha,
            "bundle_sha256_source": "argument_or_environment" if resolved_bundle_sha else "not_provided",
        },
        "environment_capture": _environment_capture(),
        "command": {
            "artifact_inputs": [str(Path(item)) for item in artifact_inputs],
            "strict_closure": strict_closure,
            "package_evidence": package_evidence,
            "license_policy_path": str(Path(license_policy_path).resolve()) if license_policy_path else None,
            "entry_point_policy_path": str(Path(entry_point_policy_path).resolve()) if entry_point_policy_path else None,
            "target_environment_path": str(Path(target_environment_path).resolve()) if target_environment_path else None,
            "lockfile_path": str(Path(lockfile_path).resolve()) if lockfile_path else None,
            "effective_policy_path": str(Path(effective_policy_path).resolve()) if effective_policy_path else None,
        },
        "graph": {
            "verdict": report.get("verdict"),
            "counts": report.get("counts", {}),
            "root_nodes": report.get("root_nodes", []),
        },
        "evidence_files": {
            "graph_report": _file_ref(report_path),
            "graph_summary": _file_ref(summary_path),
            "input_manifest": _file_ref(input_manifest_path),
            "bill_of_materials": _file_ref(bom_path),
        },
        "not_claimed": [
            "not an installability guarantee",
            "not a dependency resolver",
            "not PyPI/network access",
            "not full PEP 440 or PEP 508 range evaluation",
            "range-aware checks evaluate local provided wheel versions only",
            "unsupported range specifiers are reported as UNVERIFIED notes",
            "not complete PEP508 marker validation",
            "not malware scanning",
            "verdict is captured for the reported local inputs and tool identity only",
        ],
    }
    if not resolved_bundle_sha:
        graph_evidence_manifest["not_claimed"].append("bundle sha256 was not provided to this graph run")
    policy_file = Path(license_policy_path) if license_policy_path else None
    if policy_file is not None:
        graph_evidence_manifest["evidence_files"]["license_policy"] = _file_ref(policy_file)
    entry_policy_file = Path(entry_point_policy_path) if entry_point_policy_path else None
    if entry_policy_file is not None:
        graph_evidence_manifest["evidence_files"]["entry_point_policy"] = _file_ref(entry_policy_file)
    target_environment_file = Path(target_environment_path) if target_environment_path else None
    if target_environment_file is not None:
        graph_evidence_manifest["evidence_files"]["target_environment"] = _file_ref(target_environment_file)
    lockfile = Path(lockfile_path) if lockfile_path else None
    if lockfile is not None:
        graph_evidence_manifest["evidence_files"]["lockfile"] = _file_ref(lockfile)
    effective_policy_file = Path(effective_policy_path) if effective_policy_path else None
    if effective_policy_file is not None:
        graph_evidence_manifest["evidence_files"]["effective_policy"] = _file_ref(effective_policy_file)
    _write_json(graph_evidence_manifest_path, graph_evidence_manifest)

    result: dict[str, Any] = {
        "input_manifest_path": str(input_manifest_path.resolve()),
        "graph_evidence_manifest_path": str(graph_evidence_manifest_path.resolve()),
        "input_manifest_sha256": _hash_file(input_manifest_path),
        "graph_evidence_manifest_sha256": _hash_file(graph_evidence_manifest_path),
        "bill_of_materials_path": str(bom_path.resolve()),
        "bill_of_materials_sha256": _hash_file(bom_path),
    }
    if package_evidence:
        payload_files = [report_path, summary_path, bom_path, input_manifest_path, graph_evidence_manifest_path]
        if policy_file is not None:
            payload_files.append(policy_file)
        if entry_policy_file is not None:
            payload_files.append(entry_policy_file)
        if target_environment_file is not None:
            payload_files.append(target_environment_file)
        if lockfile is not None:
            payload_files.append(lockfile)
        if effective_policy_file is not None:
            payload_files.append(effective_policy_file)
        package_result = package_lock(
            package_name="SPIRA_GRAPH_EVIDENCE_PACKAGE_001_BASELINE",
            payload_files=payload_files,
            output_dir=output / "governance",
            lock_metadata={
                "classification": "SPIRA_TRUST_GRAPH_EVIDENCE_PACKAGE_001",
                "schema_version": "2.0",
                "graph_verdict": report.get("verdict"),
                "input_manifest_sha256": result["input_manifest_sha256"],
                "bill_of_materials_sha256": result["bill_of_materials_sha256"],
                "graph_evidence_manifest_sha256": result["graph_evidence_manifest_sha256"],
                "license_policy_sha256": _hash_file(policy_file) if policy_file is not None else None,
                "entry_point_policy_sha256": _hash_file(entry_policy_file) if entry_policy_file is not None else None,
                "target_environment_sha256": _hash_file(target_environment_file) if target_environment_file is not None else None,
                "lockfile_sha256": _hash_file(lockfile) if lockfile is not None else None,
                "effective_policy_sha256": _hash_file(effective_policy_file) if effective_policy_file is not None else None,
                "tool_version": resolved_tool_version,
                "bundle_sha256": resolved_bundle_sha,
            },
            not_claimed=graph_evidence_manifest["not_claimed"],
        )
        result["graph_evidence_package"] = package_result
        package_result_path = output / "graph_evidence_package_result.json"
        _write_json(package_result_path, package_result)
        result["graph_evidence_package_result_path"] = str(package_result_path.resolve())
    return result


def _input_manifest_entry(path: Path) -> dict[str, Any]:
    metadata = _read_wheel_metadata(path)
    package_name = metadata.get("Name") or path.stem
    normalized_name = normalize_pep503(package_name)
    archive_profile = _archive_profile(path)
    return {
        "path": str(path.resolve()),
        "filename": path.name,
        "sha256": _hash_file(path),
        "bytes": path.stat().st_size,
        "package_name": package_name,
        "normalized_name": normalized_name,
        "version": metadata.get("Version"),
        "metadata_path": metadata.get("metadata_path"),
        "record_path": metadata.get("record_path"),
        "file_count": archive_profile["file_count"],
        "total_uncompressed_bytes": archive_profile["total_uncompressed_bytes"],
    }


def _archive_profile(path: Path) -> dict[str, int]:
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return {
            "file_count": 0,
            "total_uncompressed_bytes": 0,
        }
    with archive:
        infos = archive.infolist()
        return {
            "file_count": sum(1 for info in infos if not info.is_dir()),
            "total_uncompressed_bytes": sum(info.file_size for info in infos if not info.is_dir()),
        }


def _file_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.resolve()),
        "sha256": _hash_file(path),
        "bytes": path.stat().st_size,
    }


def _tool_version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        try:
            return importlib_metadata.version("spira-review")
        except importlib_metadata.PackageNotFoundError:
            return "source-tree"


def _environment_capture() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "executable": sys.executable,
    }


def _env_nonempty(name: str) -> str | None:
    import os

    value = os.environ.get(name)
    return value if value else None


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _scale_limit_report(
    output: Path,
    artifacts: list[Path],
    *,
    strict_closure: bool,
    package_evidence: bool,
    bundle_sha256: str | None,
    tool_version: str | None,
    license_policy_path: str | Path | None,
    entry_point_policy_path: str | Path | None,
    target_environment_path: str | Path | None,
    lockfile_path: str | Path | None,
    effective_policy_path: str | Path | None,
    artifact_inputs: Iterable[str | Path],
) -> dict[str, Any]:
    reason = f"graph artifact count exceeds v1 limit: {len(artifacts)} > {MAX_GRAPH_ARTIFACTS}"
    report = {
        "schema": "SPIRA_TRUST_GRAPH_V2_REPORT",
        "schema_version": "2.0",
        "verdict": "GRAPH_BLOCK",
        "strict_closure": strict_closure,
        "inputs": [str(path.resolve()) for path in artifacts],
        "counts": {
            "provided_artifacts": len(artifacts),
            "declared_missing_artifacts": 0,
            "declared_ambiguous_artifacts": 0,
            "declared_relationships": 0,
            "blocked_nodes": 1,
            "warning_nodes": 0,
            "needs_human_nodes": 0,
            "unverified_nodes": 0,
        },
        "root_nodes": [],
        "nodes": [
            {
                "id": "graph-scale-limit",
                "node_type": "graph_limit",
                "package_name": "graph-scale-limit",
                "normalized_name": "graph-scale-limit",
                "version": None,
                "artifact_path": None,
                "artifact_sha256": None,
                "local_review_status": "BLOCK",
                "graph_status": "BLOCK",
                "reasons": [reason],
                "evidence_refs": {},
                "trust_status": None,
                "review_verdict": None,
                "declared_requirements": [],
                "propagated_notes": [],
            }
        ],
        "edges": [],
        "propagation_events": [{"from": "graph-scale-limit", "to": "graph-scale-limit", "effect": "BLOCK", "reason": reason}],
        "name_normalization": {
            "rule": "PEP_503_STYLE_ONLY",
            "not_performed": [
                "Unicode confusable folding",
                "NFKC folding for graph matching",
                "fuzzy matching",
                "typo correction",
                "visual similarity matching",
            ],
        },
        "not_claimed": list(GRAPH_NOT_CLAIMED) + ["v1 scale limit reached; graph relationships were not evaluated"],
    }
    summary = "\n".join(
        [
            "SPIRA Trust Graph Summary",
            "=========================",
            f"[GRAPH_BLOCK] {reason}",
            "",
            f"Artifacts provided: {len(artifacts)}",
            f"Max artifacts: {MAX_GRAPH_ARTIFACTS}",
            "",
            "Boundaries:",
            "- graph was blocked before per-artifact review",
            "- no resolver",
            "- no network/PyPI",
            "- no install or code execution",
            "",
        ]
    )
    report_path = output / "graph_report.json"
    summary_path = output / "graph_summary.txt"
    bom_path = output / "bill_of_materials.json"
    report["report_path"] = str(report_path.resolve())
    report["summary_path"] = str(summary_path.resolve())
    report["bill_of_materials_path"] = str(bom_path.resolve())
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    summary_path.write_text(summary, encoding="utf-8", newline="\n")
    write_bill_of_materials(
        report,
        bom_path,
        tool_version=tool_version,
        bundle_sha256=bundle_sha256 or _env_nonempty("SPIRA_BUNDLE_SHA256"),
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
    )
    bom = json.loads(bom_path.read_text(encoding="utf-8"))
    report["license_policy_screening"] = _license_policy_summary(bom)
    report["entry_point_policy_screening"] = _entry_point_policy_summary(bom)
    report["target_environment_screening"] = _target_environment_summary(bom)
    report["lockfile_cross_check"] = _lockfile_cross_check_summary(bom)
    report["combined_policy_verdict"] = bom.get("combined_policy_verdict")
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    evidence = _write_graph_evidence(
        output,
        artifacts,
        report_path,
        summary_path,
        bom_path,
        report,
        strict_closure=strict_closure,
        package_evidence=package_evidence,
        bundle_sha256=bundle_sha256,
        tool_version=tool_version,
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
        effective_policy_path=effective_policy_path,
        artifact_inputs=artifact_inputs,
    )
    report["input_manifest_path"] = evidence["input_manifest_path"]
    report["graph_evidence_manifest_path"] = evidence["graph_evidence_manifest_path"]
    report["bill_of_materials_path"] = str(bom_path.resolve())
    report["bill_of_materials_sha256"] = evidence["bill_of_materials_sha256"]
    report["graph_evidence_package"] = evidence.get("graph_evidence_package")
    report["summary_text"] = summary
    return report


def _discover_wheels(inputs: Iterable[str | Path]) -> list[Path]:
    wheels: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            wheels.extend(sorted(path.glob("*.whl")))
        elif path.is_file() and path.suffix == ".whl":
            wheels.append(path)
        else:
            raise ValueError(f"graph input must be a wheel file or directory containing wheels: {path}")
    unique = []
    seen = set()
    for wheel in wheels:
        resolved = wheel.resolve()
        if resolved not in seen:
            unique.append(wheel)
            seen.add(resolved)
    if not unique:
        raise ValueError("no wheel artifacts were provided for graph analysis")
    return unique


def _read_wheel_metadata(path: Path) -> dict[str, Any]:
    try:
        archive = zipfile.ZipFile(path)
    except zipfile.BadZipFile:
        return {"Requires-Dist": [], "metadata_error": "bad_zip_file"}
    with archive:
        metadata_names = sorted(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        record_names = sorted(name for name in archive.namelist() if name.endswith(".dist-info/RECORD"))
        if not metadata_names:
            return {"Requires-Dist": [], "record_path": record_names[0] if record_names else None}
        text = archive.read(metadata_names[0]).decode("utf-8", errors="replace")
    message = Parser().parsestr(text)
    return {
        "Name": message.get("Name"),
        "Version": message.get("Version"),
        "Requires-Dist": list(message.get_all("Requires-Dist", [])),
        "metadata_path": metadata_names[0],
        "record_path": record_names[0] if record_names else None,
    }


def _edge_range_evaluation(specifier: str, candidate_ids: list[str], nodes: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    provided_versions = [
        str(nodes[candidate].get("version"))
        for candidate in candidate_ids
        if nodes.get(candidate, {}).get("version") is not None
    ]
    parsed = parse_specifier_set(specifier)
    if not candidate_ids:
        return _range_note(specifier, "no local provided wheel versions exist for this declared name")
    if parsed.status != "SUPPORTED":
        return {
            "raw": specifier,
            "result": "UNVERIFIED",
            "parsed_constraint": _parsed_constraint_payload(parsed),
            "evaluated": False,
            "satisfied_by_provided": None,
            "satisfying_versions": [],
            "unsupported_provided_versions": [],
            "note": parsed.note,
        }
    evaluation = evaluate_provided_versions(specifier, provided_versions)
    return {
        "raw": specifier,
        "result": evaluation["result"],
        "parsed_constraint": _parsed_constraint_payload(parsed),
        "evaluated": evaluation["evaluated"],
        "satisfied_by_provided": evaluation["satisfied_by_provided"],
        "satisfying_versions": evaluation["satisfying_versions"],
        "unsupported_provided_versions": evaluation["unsupported_provided_versions"],
        "note": evaluation["note"],
    }


def _range_note(specifier: str, note: str) -> dict[str, Any]:
    parsed = parse_specifier_set(specifier)
    return {
        "raw": specifier,
        "result": "UNVERIFIED",
        "parsed_constraint": _parsed_constraint_payload(parsed),
        "evaluated": False,
        "satisfied_by_provided": None,
        "satisfying_versions": [],
        "unsupported_provided_versions": [],
        "note": note,
    }


def _parsed_constraint_payload(parsed: Any) -> dict[str, Any]:
    return {
        "raw": parsed.raw,
        "status": parsed.status,
        "constraints": [
            {
                "operator": constraint.operator,
                "version": list(constraint.version),
                "raw_version": constraint.raw_version,
            }
            for constraint in parsed.constraints
        ],
        "note": parsed.note,
    }


def _parse_requirement(requirement: str) -> dict[str, str | None] | None:
    match = re.match(r"\s*([A-Za-z0-9_.-]+)", requirement)
    if not match:
        return None
    name = match.group(1)
    before_marker = requirement.split(";", 1)[0]
    specifier = before_marker[match.end() :].strip()
    if specifier.startswith("(") and specifier.endswith(")"):
        specifier = specifier[1:-1].strip()
    exact = None
    exact_match = re.search(r"(?<![<>=!~])==\s*([A-Za-z0-9_.!+*-]+)", before_marker)
    if exact_match:
        exact = exact_match.group(1).strip()
    return {"name": name, "exact_version": exact, "specifier": specifier}


def _marker_error(requirement: str) -> str | None:
    if ";" not in requirement:
        return None
    marker = requirement.split(";", 1)[1].strip()
    if not marker:
        return "malformed environment marker: empty marker"
    if marker.count('"') % 2 or marker.count("'") % 2:
        return "malformed environment marker: unbalanced quotes"
    if re.search(r"\b(and|or)\s*$", marker, flags=re.IGNORECASE):
        return "malformed environment marker: dangling boolean operator"
    if re.search(r"(==|!=|<=|>=|<|>)\s*($|\)|\band\b|\bor\b)", marker):
        return "malformed environment marker: comparison without value"
    python_bounds = re.findall(r"python_version\s*([<>]=?)\s*['\"]([^'\"]+)['\"]", marker)
    if _python_version_bounds_are_impossible(python_bounds):
        return "unsatisfiable environment marker: python_version bounds conflict"
    return None


def _python_version_bounds_are_impossible(bounds: list[tuple[str, str]]) -> bool:
    lower: tuple[tuple[int, ...], bool] | None = None
    upper: tuple[tuple[int, ...], bool] | None = None
    for op, value in bounds:
        parsed = _parse_version_tuple(value)
        if parsed is None:
            continue
        if op in {">", ">="}:
            inclusive = op == ">="
            if lower is None or parsed > lower[0] or (parsed == lower[0] and not inclusive and lower[1]):
                lower = (parsed, inclusive)
        elif op in {"<", "<="}:
            inclusive = op == "<="
            if upper is None or parsed < upper[0] or (parsed == upper[0] and not inclusive and upper[1]):
                upper = (parsed, inclusive)
    if lower is None or upper is None:
        return False
    if lower[0] > upper[0]:
        return True
    if lower[0] == upper[0] and (not lower[1] or not upper[1]):
        return True
    return False


def _parse_version_tuple(value: str) -> tuple[int, ...] | None:
    parts = value.split(".")
    parsed: list[int] = []
    for part in parts:
        if not part.isdigit():
            return None
        parsed.append(int(part))
    return tuple(parsed)


def _relationship_type(requirement: str) -> str:
    lower = requirement.lower()
    if "extra ==" in lower or "extra==" in lower:
        return "depends_on_optional"
    return "depends_on_declared"


def _local_state_from_trust(trust_report: Mapping[str, Any]) -> str:
    trust_status = trust_report.get("decision", {}).get("trust_status")
    counts = trust_report.get("trust_adapter", {}).get("counts", {})
    if trust_status == "TRUST_BLOCK":
        return "BLOCK"
    if trust_status == "TRUST_WARN":
        return "WARN"
    if int(counts.get("free_text_note_count", 0)) > 0:
        return "NEEDS_HUMAN"
    return "VERIFIED_OK"


def _node_reasons(trust_report: Mapping[str, Any], state: str) -> list[str]:
    if state == "BLOCK":
        return list(trust_report.get("human_summary", {}).get("reasons", ["blocking trust evidence found"]))
    if state == "WARN":
        return list(trust_report.get("human_summary", {}).get("reasons", ["trust warning found"]))
    if state == "NEEDS_HUMAN":
        return ["free-text or surfaced context needs human judgment"]
    return ["single-artifact trust checks found no hard contradiction"]


def _propagate(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]], *, strict_closure: bool) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for _ in range(max(1, len(nodes))):
        changed = False
        for edge in edges:
            parent = nodes[edge["from_node"]]
            child = nodes[edge["to_node"]]
            effect = _edge_effect(child["graph_status"], edge["relationship_type"], strict_closure=strict_closure)
            if effect == "NOTE":
                note = f"{child['package_name']} requires attention: {', '.join(child.get('reasons', [])[:2])}"
                if note not in parent["propagated_notes"]:
                    parent["propagated_notes"].append(note)
                    events.append({"from": child["id"], "to": parent["id"], "effect": "NOTE", "reason": note})
                continue
            if effect and _state_rank(effect) > _state_rank(parent["graph_status"]):
                parent["graph_status"] = effect
                reason = f"{effect} propagated from {child['package_name']} via {edge['relationship_type']}"
                child_reasons = list(child.get("reasons", []))
                if child_reasons:
                    reason = f"{reason}: {child_reasons[0]}"
                parent["reasons"].append(reason)
                events.append({"from": child["id"], "to": parent["id"], "effect": effect, "reason": reason})
                changed = True
        if not changed:
            break
    return events


def _apply_license_policy_findings(nodes: dict[str, dict[str, Any]], bom: Mapping[str, Any]) -> list[dict[str, Any]]:
    screening = bom.get("license_policy_screening", {})
    if not screening.get("evaluated"):
        return []
    events = []
    for finding in screening.get("findings", []):
        node_id = finding.get("node_id")
        if node_id not in nodes:
            continue
        effect = "BLOCK" if finding.get("severity") == "BLOCK" else "WARN"
        node = nodes[node_id]
        reason = (
            f"license policy {effect.lower()}: term {finding.get('term')!r} "
            f"matched {finding.get('source_field')}"
        )
        if _state_rank(effect) > _state_rank(node["graph_status"]):
            node["graph_status"] = effect
        if reason not in node["reasons"]:
            node["reasons"].insert(0, reason)
        events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _apply_entry_point_policy_findings(nodes: dict[str, dict[str, Any]], bom: Mapping[str, Any]) -> list[dict[str, Any]]:
    screening = bom.get("entry_point_policy_screening", {})
    if not screening.get("evaluated"):
        return []
    events = []
    for finding in screening.get("findings", []):
        node_id = finding.get("node_id")
        if node_id not in nodes:
            continue
        effect = "BLOCK" if finding.get("severity") == "BLOCK" else "WARN"
        node = nodes[node_id]
        reason = (
            f"entry point policy {effect.lower()}: declared command "
            f"{finding.get('declared_command_name')!r} matched policy command "
            f"{finding.get('policy_command_name')!r}"
        )
        if _state_rank(effect) > _state_rank(node["graph_status"]):
            node["graph_status"] = effect
        if reason not in node["reasons"]:
            node["reasons"].insert(0, reason)
        events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _apply_target_environment_findings(nodes: dict[str, dict[str, Any]], bom: Mapping[str, Any]) -> list[dict[str, Any]]:
    screening = bom.get("target_environment_screening", {})
    if not screening.get("evaluated"):
        return []
    events = []
    for finding in screening.get("findings", []):
        node_id = finding.get("node_id")
        if node_id not in nodes:
            continue
        severity = finding.get("severity")
        reason = (
            f"target environment {str(severity).lower()}: {finding.get('field')} "
            f"{finding.get('observed')!r} vs target {finding.get('expected')!r}: {finding.get('note')}"
        )
        if severity == "NOTE":
            if reason not in nodes[node_id]["propagated_notes"]:
                nodes[node_id]["propagated_notes"].append(reason)
            events.append({"from": node_id, "to": node_id, "effect": "NOTE", "reason": reason})
            continue
        effect = "BLOCK" if severity == "BLOCK" else "WARN"
        node = nodes[node_id]
        if _state_rank(effect) > _state_rank(node["graph_status"]):
            node["graph_status"] = effect
        if reason not in node["reasons"]:
            node["reasons"].insert(0, reason)
        events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _apply_lockfile_cross_check_findings(nodes: dict[str, dict[str, Any]], bom: Mapping[str, Any]) -> list[dict[str, Any]]:
    screening = bom.get("lockfile_cross_check", {})
    if not screening.get("evaluated"):
        return []
    events = []
    for finding in screening.get("findings", []):
        node_id = finding.get("node_id")
        severity = finding.get("severity")
        reason = f"lockfile {str(severity).lower()}: {finding.get('kind')}: {finding.get('note')}"
        if not node_id or node_id not in nodes:
            if severity in {"BLOCK", "WARN"}:
                effect = "BLOCK" if severity == "BLOCK" else "WARN"
                for candidate_id, candidate in nodes.items():
                    if candidate.get("node_type") != "provided_artifact":
                        continue
                    if _state_rank(effect) > _state_rank(candidate["graph_status"]):
                        candidate["graph_status"] = effect
                    if reason not in candidate["reasons"]:
                        candidate["reasons"].insert(0, reason)
            events.append({"from": "lockfile", "to": "lockfile", "effect": severity, "reason": reason})
            continue
        if severity == "NOTE":
            if reason not in nodes[node_id]["propagated_notes"]:
                nodes[node_id]["propagated_notes"].append(reason)
            events.append({"from": node_id, "to": node_id, "effect": "NOTE", "reason": reason})
            continue
        effect = "BLOCK" if severity == "BLOCK" else "WARN"
        node = nodes[node_id]
        if _state_rank(effect) > _state_rank(node["graph_status"]):
            node["graph_status"] = effect
        if reason not in node["reasons"]:
            node["reasons"].insert(0, reason)
        events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _apply_sbom_consistency_findings(nodes: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    events = []
    for node_id, node in nodes.items():
        if node.get("node_type") != "provided_artifact":
            continue
        result = evaluate_embedded_sbom_consistency(
            str(node.get("artifact_path")),
            package_name=str(node.get("package_name") or ""),
            version=node.get("version"),
        )
        node["pep770_sbom_consistency"] = result
        if result.get("status") == "CONTRADICTION":
            reason = "PEP 770 embedded SBOM contradiction"
            for item in result.get("results", []) or []:
                findings = item.get("findings") or []
                if item.get("status") == "CONTRADICTION" and findings:
                    reason = f"{reason}: {findings[0]}"
                    break
            if _state_rank("BLOCK") > _state_rank(node["graph_status"]):
                node["graph_status"] = "BLOCK"
            if reason not in node["reasons"]:
                node["reasons"].insert(0, reason)
            events.append({"from": node_id, "to": node_id, "effect": "BLOCK", "reason": reason})
        elif result.get("status") in {"UNVERIFIED", "NO_WHEEL_SCOPED_SBOM"}:
            if result.get("status") == "NO_WHEEL_SCOPED_SBOM":
                reason = "PEP 770 embedded SBOM present but no wheel-scoped SBOM was identified by V1 parser"
            else:
                reason = "PEP 770 embedded SBOM present but not fully verified by V1 parser"
            if reason not in node["propagated_notes"]:
                node["propagated_notes"].append(reason)
            events.append({"from": node_id, "to": node_id, "effect": "NOTE", "reason": reason})
    return events


def _apply_attestation_findings(nodes: dict[str, dict[str, Any]], result: Mapping[str, Any]) -> list[dict[str, Any]]:
    top_status = str(result.get("status"))
    top_level_block_reasons = {
        "ATTESTATION_TRUST_ROOT_UNTRUSTED": "PEP 740 offline attestation trust root sha256 mismatch",
        "ATTESTATION_TRUST_ROOT_SHA_MISSING": "PEP 740 offline attestation trust root was supplied without sha256 pin",
        "ATTESTATION_TRUST_ROOT_MISSING": "PEP 740 offline attestation trust root file does not exist",
        "ATTESTATION_INPUT_ERROR": f"PEP 740 offline attestation input error: {result.get('reason')}",
    }
    if top_status in top_level_block_reasons:
        reason = top_level_block_reasons[top_status]
        events = []
        for node_id, node in nodes.items():
            if node.get("node_type") != "provided_artifact":
                continue
            if _state_rank("BLOCK") > _state_rank(node["graph_status"]):
                node["graph_status"] = "BLOCK"
            if reason not in node["reasons"]:
                node["reasons"].insert(0, reason)
            events.append({"from": "attestation", "to": node_id, "effect": "BLOCK", "reason": reason})
        return events
    if not result.get("evaluated"):
        return []
    by_filename = {
        Path(str(node.get("artifact_path") or "")).name: node_id
        for node_id, node in nodes.items()
        if node.get("node_type") == "provided_artifact"
    }
    events = []
    for finding in result.get("findings", []) or []:
        filename = finding.get("filename")
        node_id = by_filename.get(str(filename))
        status = str(finding.get("status"))
        effect = "BLOCK" if status in {"CONTRADICTION", "ATTESTATION_DIGEST_MISMATCH", "ATTESTATION_IDENTITY_NOT_ALLOWED"} else "NOTE"
        reason = f"PEP 740 offline attestation {str(finding.get('status')).lower()}: {finding.get('reason')}"
        if not node_id:
            events.append({"from": "attestation", "to": "attestation", "effect": effect, "reason": reason})
            continue
        node = nodes[node_id]
        if effect == "BLOCK":
            if _state_rank("BLOCK") > _state_rank(node["graph_status"]):
                node["graph_status"] = "BLOCK"
            if reason not in node["reasons"]:
                node["reasons"].insert(0, reason)
        else:
            if reason not in node["propagated_notes"]:
                node["propagated_notes"].append(reason)
        events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _sbom_consistency_summary(nodes: Mapping[str, dict[str, Any]], evaluated: bool) -> dict[str, Any]:
    if not evaluated:
        return {"evaluated": False, "status": "NOT_EVALUATED", "result_count": 0}
    results = [
        node.get("pep770_sbom_consistency")
        for node in nodes.values()
        if node.get("node_type") == "provided_artifact" and node.get("pep770_sbom_consistency")
    ]
    statuses = [result.get("status") for result in results if isinstance(result, Mapping)]
    if any(status == "CONTRADICTION" for status in statuses):
        status = "CONTRADICTION"
    elif any(status == "UNVERIFIED" for status in statuses):
        status = "UNVERIFIED"
    elif any(status == "NO_WHEEL_SCOPED_SBOM" for status in statuses):
        status = "NO_WHEEL_SCOPED_SBOM"
    elif any(status == "VERIFIED_OK" for status in statuses):
        status = "VERIFIED_OK"
    else:
        status = "NOT_EVALUATED"
    return {"evaluated": True, "status": status, "result_count": len(results), "results": results}


def _license_policy_summary(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("license_policy_screening", {})
    findings = screening.get("findings", [])
    return {
        "evaluated": bool(screening.get("evaluated")),
        "verdict": screening.get("verdict", "LICENSE_POLICY_NOT_PROVIDED"),
        "finding_count": len(findings),
        "blocked_count": sum(1 for finding in findings if finding.get("severity") == "BLOCK"),
        "warn_count": sum(1 for finding in findings if finding.get("severity") == "WARN"),
        "policy_ref": screening.get("policy_ref"),
        "not_claimed": screening.get("not_claimed", []),
    }


def _target_environment_summary(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("target_environment_screening", {})
    findings = screening.get("findings", [])
    return {
        "evaluated": bool(screening.get("evaluated")),
        "verdict": screening.get("verdict", "TARGET_ENVIRONMENT_NOT_PROVIDED"),
        "finding_count": len(findings),
        "blocked_count": sum(1 for finding in findings if finding.get("severity") == "BLOCK"),
        "warn_count": sum(1 for finding in findings if finding.get("severity") == "WARN"),
        "note_count": sum(1 for finding in findings if finding.get("severity") == "NOTE"),
        "target_ref": screening.get("target_ref"),
        "target": screening.get("target"),
        "not_claimed": screening.get("not_claimed", []),
    }


def _entry_point_policy_summary(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("entry_point_policy_screening", {})
    findings = screening.get("findings", [])
    return {
        "evaluated": bool(screening.get("evaluated")),
        "verdict": screening.get("verdict", "ENTRY_POINT_POLICY_NOT_PROVIDED"),
        "finding_count": len(findings),
        "blocked_count": sum(1 for finding in findings if finding.get("severity") == "BLOCK"),
        "warn_count": sum(1 for finding in findings if finding.get("severity") == "WARN"),
        "policy_ref": screening.get("policy_ref"),
        "match_mode": screening.get("match_mode"),
        "case_insensitive": screening.get("case_insensitive"),
        "not_claimed": screening.get("not_claimed", []),
    }


def _lockfile_cross_check_summary(bom: Mapping[str, Any]) -> dict[str, Any]:
    screening = bom.get("lockfile_cross_check", {})
    findings = screening.get("findings", [])
    return {
        "evaluated": bool(screening.get("evaluated")),
        "verdict": screening.get("verdict", "LOCKFILE_NOT_PROVIDED"),
        "finding_count": len(findings),
        "blocked_count": sum(1 for finding in findings if finding.get("severity") == "BLOCK"),
        "warn_count": sum(1 for finding in findings if finding.get("severity") == "WARN"),
        "note_count": sum(1 for finding in findings if finding.get("severity") == "NOTE"),
        "lockfile_ref": screening.get("lockfile_ref"),
        "entry_count": screening.get("entry_count", 0),
        "unsupported_entry_count": screening.get("unsupported_entry_count", 0),
        "not_claimed": screening.get("not_claimed", []),
    }


def _apply_cycle_blocks(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for edge in edges:
        if (
            nodes.get(edge["from_node"], {}).get("node_type") == "provided_artifact"
            and nodes.get(edge["to_node"], {}).get("node_type") == "provided_artifact"
        ):
            adjacency.setdefault(edge["from_node"], []).append((edge["to_node"], edge["relationship_type"]))

    cycles: list[tuple[list[str], list[str]]] = []
    visiting: list[str] = []
    visiting_edge_types: list[str] = []
    visited: set[str] = set()
    seen_cycles: set[tuple[str, ...]] = set()

    def visit(node_id: str) -> None:
        if node_id in visiting:
            index = visiting.index(node_id)
            cycle = visiting[index:]
            cycle_edge_types = visiting_edge_types[index:]
            key = tuple(sorted(cycle))
            if key not in seen_cycles:
                cycles.append((cycle, cycle_edge_types))
                seen_cycles.add(key)
            return
        if node_id in visited:
            return
        visiting.append(node_id)
        for child_id, relationship_type in adjacency.get(node_id, []):
            visiting_edge_types.append(relationship_type)
            visit(child_id)
            visiting_edge_types.pop()
        visiting.pop()
        visited.add(node_id)

    for node_id in adjacency:
        visit(node_id)

    events: list[dict[str, Any]] = []
    for cycle, cycle_edge_types in cycles:
        cycle_names = " -> ".join(nodes[node_id]["package_name"] for node_id in cycle + [cycle[0]])
        hard_cycle = all(edge_type == "depends_on_declared" for edge_type in cycle_edge_types)
        effect = "BLOCK" if hard_cycle else "WARN"
        reason = (
            f"circular declared relationship detected: {cycle_names}"
            if hard_cycle
            else f"optional/test circular relationship detected: {cycle_names}"
        )
        for node_id in cycle:
            if _state_rank(effect) > _state_rank(nodes[node_id]["graph_status"]):
                nodes[node_id]["graph_status"] = effect
            if reason not in nodes[node_id]["reasons"]:
                nodes[node_id]["reasons"].append(reason)
            events.append({"from": node_id, "to": node_id, "effect": effect, "reason": reason})
    return events


def _apply_pinned_version_conflict_blocks(
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    root_node_ids: list[str],
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        adjacency.setdefault(edge["from_node"], []).append(edge)

    events: list[dict[str, Any]] = []
    for root_id in root_node_ids:
        exact_versions_by_name: dict[str, set[str]] = {}
        stack = [root_id]
        visited: set[str] = set()
        while stack:
            node_id = stack.pop()
            if node_id in visited:
                continue
            visited.add(node_id)
            for edge in adjacency.get(node_id, []):
                if edge.get("relationship_type") != "depends_on_declared":
                    continue
                exact_version = edge.get("required_exact_version")
                normalized_name = edge.get("required_normalized_name")
                if exact_version and normalized_name:
                    exact_versions_by_name.setdefault(normalized_name, set()).add(exact_version)
                target_id = edge["to_node"]
                if nodes.get(target_id, {}).get("node_type") == "provided_artifact":
                    stack.append(target_id)
        conflicts = {
            name: sorted(versions)
            for name, versions in exact_versions_by_name.items()
            if len(versions) > 1
        }
        for name, versions in sorted(conflicts.items()):
            reason = f"pinned version conflict reachable from root: {name} requires {', '.join(versions)}"
            nodes[root_id]["graph_status"] = "BLOCK"
            if reason not in nodes[root_id]["reasons"]:
                nodes[root_id]["reasons"].append(reason)
            events.append({"from": root_id, "to": root_id, "effect": "BLOCK", "reason": reason})
    return events


def _apply_range_conflict_blocks(
    nodes: dict[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    root_node_ids: list[str],
    provided_by_name: Mapping[str, list[str]],
) -> list[dict[str, Any]]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        adjacency.setdefault(edge["from_node"], []).append(edge)

    events: list[dict[str, Any]] = []
    for root_id in root_node_ids:
        reachable = _reachable_provided_nodes(root_id, nodes, adjacency)
        constraints_by_name: dict[str, list[str]] = {}
        constraint_sources: dict[str, list[str]] = {}
        for node_id in sorted(reachable):
            for edge in adjacency.get(node_id, []):
                if edge.get("relationship_type") != "depends_on_declared":
                    continue
                normalized_name = edge.get("required_normalized_name")
                specifier = str(edge.get("specifier_raw") or "")
                if not normalized_name or not specifier:
                    continue
                if not provided_by_name.get(normalized_name):
                    continue
                range_eval = edge.get("range_evaluation", {})
                if range_eval.get("result") == "UNVERIFIED":
                    note = (
                        f"range constraint on {edge.get('required_name')} was not evaluated: "
                        f"{range_eval.get('note') or 'unsupported V2 specifier'}"
                    )
                    if note not in nodes[node_id]["propagated_notes"]:
                        nodes[node_id]["propagated_notes"].append(note)
                        events.append({"from": node_id, "to": node_id, "effect": "NOTE", "reason": note})
                    continue
                constraints_by_name.setdefault(normalized_name, []).append(specifier)
                constraint_sources.setdefault(normalized_name, []).append(
                    f"{nodes[node_id]['package_name']} declares {edge.get('required_name')}{specifier}"
                )

        for normalized_name, specifiers in sorted(constraints_by_name.items()):
            provided_versions = [
                str(nodes[candidate].get("version"))
                for candidate in provided_by_name.get(normalized_name, [])
                if nodes.get(candidate, {}).get("version") is not None
            ]
            if not provided_versions:
                continue
            combined = ",".join(specifiers)
            evaluation = evaluate_provided_versions(combined, provided_versions)
            if evaluation["result"] == "CONFLICT":
                reason = (
                    f"range conflict reachable from root: {normalized_name} provided versions "
                    f"{provided_versions} satisfy none of supported constraints {specifiers}: {evaluation['note']}"
                )
                nodes[root_id]["graph_status"] = "BLOCK"
                if reason not in nodes[root_id]["reasons"]:
                    nodes[root_id]["reasons"].append(reason)
                events.append(
                    {
                        "from": root_id,
                        "to": root_id,
                        "effect": "BLOCK",
                        "reason": reason,
                        "provided_versions": provided_versions,
                        "constraints": specifiers,
                        "constraint_sources": constraint_sources.get(normalized_name, []),
                    }
                )
    return events


def _reachable_provided_nodes(
    root_id: str,
    nodes: Mapping[str, dict[str, Any]],
    adjacency: Mapping[str, list[dict[str, Any]]],
) -> set[str]:
    reachable: set[str] = set()
    stack = [root_id]
    while stack:
        node_id = stack.pop()
        if node_id in reachable:
            continue
        if nodes.get(node_id, {}).get("node_type") != "provided_artifact":
            continue
        reachable.add(node_id)
        for edge in adjacency.get(node_id, []):
            target_id = edge.get("to_node")
            if target_id and nodes.get(target_id, {}).get("node_type") == "provided_artifact":
                stack.append(target_id)
    return reachable


def _edge_effect(child_state: str, relationship_type: str, *, strict_closure: bool) -> str | None:
    if child_state == "BLOCK":
        if relationship_type in {"depends_on_optional", "depends_on_dev", "depends_on_test"}:
            return "WARN"
        return "BLOCK"
    if child_state == "WARN":
        return "WARN"
    if child_state == "UNVERIFIED":
        return "WARN" if strict_closure else None
    if child_state == "NEEDS_HUMAN":
        return "NOTE"
    return None


def _state_rank(state: str) -> int:
    return {"VERIFIED_OK": 0, "NEEDS_HUMAN": 1, "UNVERIFIED": 2, "WARN": 3, "BLOCK": 4}.get(state, 0)


def _root_nodes(nodes: Mapping[str, dict[str, Any]], edges: list[dict[str, Any]]) -> list[str]:
    child_ids = {edge["to_node"] for edge in edges}
    roots = [
        node_id
        for node_id, node in nodes.items()
        if node.get("node_type") == "provided_artifact" and node_id not in child_ids
    ]
    return sorted(roots) or sorted(node_id for node_id, node in nodes.items() if node.get("node_type") == "provided_artifact")


def _root_verdict(nodes: Mapping[str, dict[str, Any]], root_node_ids: list[str]) -> str:
    root_states = [nodes[node_id]["graph_status"] for node_id in root_node_ids]
    if any(state == "BLOCK" for state in root_states):
        return "GRAPH_BLOCK"
    if any(state == "WARN" for state in root_states):
        return "GRAPH_WARN"
    if _has_unverified_relationship(nodes, root_node_ids):
        return "GRAPH_OK_WITH_UNVERIFIED"
    if any(node.get("graph_status") == "NEEDS_HUMAN" for node in nodes.values()):
        return "GRAPH_OK_WITH_NOTES"
    return "GRAPH_OK"


def _has_unverified_relationship(nodes: Mapping[str, dict[str, Any]], root_node_ids: list[str]) -> bool:
    return any(node.get("graph_status") == "UNVERIFIED" for node in nodes.values())


def _counts(nodes: Mapping[str, dict[str, Any]], edges: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "provided_artifacts": sum(1 for node in nodes.values() if node.get("node_type") == "provided_artifact"),
        "declared_missing_artifacts": sum(
            1 for node in nodes.values() if node.get("node_type") == "declared_missing_artifact"
        ),
        "declared_ambiguous_artifacts": sum(
            1 for node in nodes.values() if node.get("node_type") == "declared_ambiguous_artifact"
        ),
        "malformed_declared_relationships": sum(
            1 for node in nodes.values() if node.get("node_type") == "malformed_declared_relationship"
        ),
        "declared_relationships": len(edges),
        "blocked_nodes": sum(1 for node in nodes.values() if node.get("graph_status") == "BLOCK"),
        "warning_nodes": sum(1 for node in nodes.values() if node.get("graph_status") == "WARN"),
        "needs_human_nodes": sum(1 for node in nodes.values() if node.get("graph_status") == "NEEDS_HUMAN"),
        "unverified_nodes": sum(1 for node in nodes.values() if node.get("graph_status") == "UNVERIFIED"),
    }


def _summary(
    nodes: Mapping[str, dict[str, Any]],
    edges: list[dict[str, Any]],
    events: list[dict[str, Any]],
    root_node_ids: list[str],
    verdict: str,
    *,
    strict_closure: bool,
) -> str:
    counts = _counts(nodes, edges)
    if verdict == "GRAPH_BLOCK":
        header = f"[GRAPH_BLOCK] {counts['blocked_nodes']} blocking node(s) affected the graph"
    elif verdict == "GRAPH_WARN":
        header = "[GRAPH_WARN] graph has non-terminal propagated risk"
    elif verdict == "GRAPH_OK_WITH_UNVERIFIED":
        header = "[GRAPH_OK_WITH_UNVERIFIED] No blocking contradictions found, but graph is incomplete."
    elif verdict == "GRAPH_OK_WITH_NOTES":
        header = "[GRAPH_OK_WITH_NOTES] No blocking contradictions found, but human notes are present."
    else:
        header = "[GRAPH_OK] No blocking contradictions or unverified declared artifacts found."
    lines = [
        "SPIRA Trust Graph Summary",
        "=========================",
        header,
        "",
        f"Artifacts provided: {counts['provided_artifacts']}",
        f"Declared relationships: {counts['declared_relationships']}",
        f"Declared artifacts not provided: {counts['declared_missing_artifacts']}",
        f"Declared artifacts ambiguous: {counts['declared_ambiguous_artifacts']}",
        f"Malformed declared relationships: {counts['malformed_declared_relationships']}",
        f"Blocked nodes: {counts['blocked_nodes']}",
        f"Warning nodes: {counts['warning_nodes']}",
        f"Human-note nodes: {counts['needs_human_nodes']}",
        f"Strict closure: {strict_closure}",
        "",
        "Root nodes:",
    ]
    for node_id in root_node_ids:
        node = nodes[node_id]
        lines.append(f"- {node['package_name']} {node.get('version') or ''} [{node['graph_status']}]".rstrip())
    if events:
        lines.extend(["", "Propagation:"])
        for event in events[:8]:
            child = nodes.get(event["from"], {"package_name": event["from"]})
            parent = nodes.get(event["to"], {"package_name": event["to"]})
            lines.append(f"- {event['effect']} from {child['package_name']} to {parent['package_name']}: {event['reason']}")
    missing = [node for node in nodes.values() if node.get("node_type") == "declared_missing_artifact"]
    if missing:
        lines.extend(["", "Unverified declared artifacts:"])
        for node in missing[:8]:
            lines.append(f"- {node['package_name']} was declared but no matching local wheel was provided")
        if not strict_closure:
            lines.append("Use --strict-closure to elevate missing declared artifacts to GRAPH_WARN.")
    ambiguous = [node for node in nodes.values() if node.get("node_type") == "declared_ambiguous_artifact"]
    if ambiguous:
        lines.extend(["", "Ambiguous declared artifacts:"])
        for node in ambiguous[:8]:
            lines.append(f"- {node['package_name']} matched multiple local wheels; v1 does not resolve versions")
    lines.extend(
        [
            "",
            "Boundaries:",
            "- no resolver",
            "- no network/PyPI",
            "- no install or code execution",
            "- PEP 503-style name normalization only; no Unicode confusable folding",
            "",
        ]
    )
    return "\n".join(lines)


def _node_id(normalized_name: str, version: str | None, artifact_sha256: str) -> str:
    suffix = version or "unknown"
    return f"{normalized_name}=={suffix}::{artifact_sha256[:12]}"


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _command_fingerprint(
    artifacts: list[Path],
    *,
    strict_closure: bool,
    license_policy_path: str | Path | None,
    entry_point_policy_path: str | Path | None,
    target_environment_path: str | Path | None,
    lockfile_path: str | Path | None,
    effective_policy_path: str | Path | None,
    verify_embedded_sboms: bool,
    attestation_path: str | Path | None,
    attestation_trust_root_path: str | Path | None,
    attestation_trust_root_sha256: str | None,
    tool_version: str | None,
) -> str:
    payload = {
        "schema": "SPIRA_GRAPH_COMMAND_FINGERPRINT_V1",
        "command": "graph",
        "strict_closure": strict_closure,
        "artifact_sha256_values": sorted(_hash_file(path) for path in artifacts),
        "policies": {
            "license_policy_sha256": _optional_file_sha(license_policy_path),
            "entry_point_policy_sha256": _optional_file_sha(entry_point_policy_path),
            "target_environment_sha256": _optional_file_sha(target_environment_path),
            "lockfile_sha256": _optional_file_sha(lockfile_path),
            "effective_policy_sha256": _optional_file_sha(effective_policy_path),
        },
        "pep770_verify_embedded_sboms": verify_embedded_sboms,
        "pep740": {
            "attestation_sha256": _optional_file_sha(attestation_path),
            "trust_root_sha256": _optional_file_sha(attestation_trust_root_path),
            "trust_root_pin": attestation_trust_root_sha256,
        },
        "tool_version": tool_version or _tool_version(),
    }
    return _stable_digest(payload)


def _optional_file_sha(path_value: str | Path | None) -> str | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_file():
        return None
    return _hash_file(path)


def _stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _safe_dir_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_") or "artifact"
