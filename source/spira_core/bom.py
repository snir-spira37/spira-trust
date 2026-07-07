from __future__ import annotations

import json
import re
import zipfile
from datetime import datetime, timezone
from email.parser import Parser
from hashlib import sha256
from importlib import metadata as importlib_metadata
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

from .combined_verdict import build_combined_policy_verdict
from .entry_points_policy import evaluate_entry_point_policy, extract_entry_points, load_entry_point_policy
from .license_policy import evaluate_license_policy, load_license_policy
from .lockfile_policy import evaluate_lockfile_cross_check, load_lockfile_policy
from .target_environment import evaluate_target_environment, load_target_environment, parse_wheel_tags


BOM_SCHEMA = "SPIRA_BILL_OF_MATERIALS_V1"
BOM_SCHEMA_VERSION = "1.0"
DIGEST_COVERS_FIELDS = [
    "wheel_sha256",
    "normalized_name",
    "version",
    "metadata_license",
    "license_classifiers",
    "license_file_sha256_values",
    "sorted_child_subtree_integrity_digest_values",
]
BOM_NOT_CLAIMED = [
    "BOM is computed over provided local wheels only",
    "transitive/depth fields do not infer dependencies beyond disk",
    "declared missing dependencies remain declared_missing",
    "license_visibility is not legal advice or legal compliance certification",
    "license_visibility records declared and file evidence without comparing or reconciling them",
    "license policy findings are out of scope for V3-A",
    "subtree_integrity_digest is tamper-evidence versus a trusted baseline, not a safety proof",
    "subtree_integrity_digest covers only provided local nodes, not missing or inferred dependencies",
    "embedded SBOM visibility records files under .dist-info/sboms as evidence only and does not trust, parse, merge, or validate their contents",
    "does not execute package code",
]
_LICENSE_NAME_RE = re.compile(r"^(LICENSE|COPYING|NOTICE)(?:$|[.-].*)$", re.IGNORECASE)
_BLOCKED_LICENSE_SUFFIXES = {".py", ".pyc", ".pyo", ".so", ".dll", ".dylib", ".pyd", ".exe"}
_SBOM_FORMAT_HINTS = {
    ".json": "json",
    ".xml": "xml",
    ".spdx": "spdx",
    ".rdf": "rdf",
    ".ttl": "turtle",
    ".txt": "text",
}


def write_bill_of_materials(
    report: Mapping[str, Any],
    output_path: str | Path,
    *,
    tool_version: str | None = None,
    bundle_sha256: str | None = None,
    license_policy_path: str | Path | None = None,
    entry_point_policy_path: str | Path | None = None,
    target_environment_path: str | Path | None = None,
    lockfile_path: str | Path | None = None,
) -> dict[str, Any]:
    bom = build_bill_of_materials(
        report,
        tool_version=tool_version,
        bundle_sha256=bundle_sha256,
        license_policy_path=license_policy_path,
        entry_point_policy_path=entry_point_policy_path,
        target_environment_path=target_environment_path,
        lockfile_path=lockfile_path,
    )
    path = Path(output_path)
    path.write_text(json.dumps(bom, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return bom


def build_bill_of_materials(
    report: Mapping[str, Any],
    *,
    tool_version: str | None = None,
    bundle_sha256: str | None = None,
    license_policy_path: str | Path | None = None,
    entry_point_policy_path: str | Path | None = None,
    target_environment_path: str | Path | None = None,
    lockfile_path: str | Path | None = None,
) -> dict[str, Any]:
    nodes = {node["id"]: dict(node) for node in report.get("nodes", [])}
    edges = [dict(edge) for edge in report.get("edges", [])]
    provided_ids = {
        node_id for node_id, node in nodes.items()
        if node.get("node_type") == "provided_artifact"
    }
    missing_ids = {
        node_id for node_id, node in nodes.items()
        if node.get("node_type") == "declared_missing_artifact"
    }
    provided_children = _provided_children(edges, nodes)
    provided_parents = _provided_parents(provided_children)
    all_children = _all_children(edges)
    all_parents = _all_parents(edges)
    roots = list(report.get("root_nodes", []))
    depths = _depths_over_provided_subgraph(roots, provided_children, provided_ids)
    license_visibility = {
        node_id: _license_visibility(nodes[node_id])
        for node_id in provided_ids
    }
    entry_points_visibility = {
        node_id: extract_entry_points(str(nodes[node_id].get("artifact_path")))
        for node_id in provided_ids
    }
    wheel_tag_visibility = {
        node_id: parse_wheel_tags(str(nodes[node_id].get("artifact_path")))
        for node_id in provided_ids
    }
    embedded_sbom_visibility = {
        node_id: _embedded_sbom_visibility(Path(str(nodes[node_id].get("artifact_path"))))
        for node_id in provided_ids
    }
    digest_state = _DigestState(nodes, provided_children, license_visibility)
    artifact_entries = []

    for node_id in sorted(provided_ids | missing_ids):
        node = nodes[node_id]
        if node_id in provided_ids:
            visibility = license_visibility[node_id]
            digest = digest_state.digest_for(node_id)
            relationship = _relationship_for_provided(
                node_id,
                roots=roots,
                provided_children=provided_children,
                provided_parents=provided_parents,
                depths=depths,
            )
            artifact_entries.append(
                {
                    "node_id": node_id,
                    "name": node.get("package_name"),
                    "normalized_name": node.get("normalized_name"),
                    "version": node.get("version"),
                    "path": node.get("artifact_path"),
                    "sha256": node.get("artifact_sha256"),
                    "depth": depths.get(node_id, 0),
                    "relationship": relationship,
                    "parents": sorted(all_parents.get(node_id, [])),
                    "children": sorted(all_children.get(node_id, [])),
                    "trust_status": node.get("trust_status"),
                    "review_verdict": node.get("review_verdict"),
                    "graph_status": node.get("graph_status"),
                    "local_review_status": node.get("local_review_status"),
                    "license_visibility": visibility,
                    "entry_points_visibility": entry_points_visibility[node_id],
                    "wheel_tag_visibility": wheel_tag_visibility[node_id],
                    "embedded_sbom_visibility": embedded_sbom_visibility[node_id],
                    "integrity": {
                        "record_verified": _record_verified(node),
                        "contradictions": _contradictions(node),
                        "digest_covers_fields": list(DIGEST_COVERS_FIELDS),
                        "subtree_integrity_digest": digest,
                        "subtree_digest_covers": "provided local subtree only",
                        "cycle_detected": node_id in digest_state.cycle_nodes,
                    },
                }
            )
        else:
            artifact_entries.append(
                {
                    "node_id": node_id,
                    "name": node.get("package_name"),
                    "normalized_name": node.get("normalized_name"),
                    "version": node.get("version"),
                    "path": None,
                    "sha256": None,
                    "depth": _missing_depth(node_id, all_parents, depths),
                    "relationship": "declared_missing",
                    "parents": sorted(all_parents.get(node_id, [])),
                    "children": [],
                    "license_visibility": {
                        "metadata_license": None,
                        "license_classifiers": [],
                        "license_file_present": False,
                        "license_files": [],
                        "declared_only": True,
                        "policy_evaluated": False,
                    },
                    "entry_points_visibility": {
                        "entry_points_file_present": False,
                        "entry_points_path": None,
                        "declared_entry_points": [],
                        "parse_error": None,
                        "entry_points_digest": None,
                        "entry_points_digest_covers_fields": [],
                        "declared_only": True,
                        "policy_evaluated": False,
                    },
                    "wheel_tag_visibility": {
                        "parsed": False,
                        "filename": None,
                        "python_tag": None,
                        "abi_tag": None,
                        "platform_tag": None,
                        "parse_error": "no local wheel was provided",
                        "wheel_tags_digest": None,
                        "wheel_tags_digest_covers_fields": [],
                        "declared_only": True,
                        "policy_evaluated": False,
                    },
                    "embedded_sbom_visibility": {
                        "embedded_sbom_file_present": False,
                        "embedded_sbom_files": [],
                        "embedded_sbom_count": 0,
                        "evidence_only": True,
                        "trusted_as_input": False,
                        "parsed": False,
                        "merged": False,
                    },
                    "integrity": {
                        "record_verified": False,
                        "contradictions": [],
                        "digest_covers_fields": list(DIGEST_COVERS_FIELDS),
                        "subtree_integrity_digest": None,
                        "subtree_digest_covers": "not covered: dependency was declared but no local wheel was provided",
                        "cycle_detected": False,
                    },
                }
            )

    bom = {
        "schema": BOM_SCHEMA,
        "schema_version": BOM_SCHEMA_VERSION,
        "source_graph": {
            "schema": report.get("schema"),
            "schema_version": report.get("schema_version"),
            "verdict": report.get("verdict"),
        },
        "created_at_utc": _utc(),
        "generated_by": {
            "tool": "spira-core graph",
            "tool_version": tool_version or _tool_version(),
            "bundle_sha256": bundle_sha256,
            "graph_schema": report.get("schema"),
            "graph_schema_version": report.get("schema_version"),
        },
        "scope": {
            "input_model": "provided local wheels only",
            "relationship_model": "declared relationships from wheel METADATA only",
            "transitive_model": "provided-wheel subgraph only; no inference beyond disk",
        },
        "digest_covers_fields": list(DIGEST_COVERS_FIELDS),
        "roots": sorted(roots),
        "artifacts": artifact_entries,
        "license_visibility": _license_visibility_summary(artifact_entries),
        "entry_points_visibility": _entry_points_visibility_summary(artifact_entries),
        "wheel_tag_visibility": _wheel_tag_visibility_summary(artifact_entries),
        "embedded_sbom_visibility": _embedded_sbom_visibility_summary(artifact_entries),
        "pep770_sbom_consistency": report.get("pep770_sbom_consistency", {"evaluated": False, "status": "NOT_EVALUATED"}),
        "pep740_offline_attestations": report.get("pep740_offline_attestations", {"evaluated": False, "status": "ATTESTATION_NOT_EVALUATED"}),
        "cycles": [
            {
                "node_id": node_id,
                "note": "cycle encountered while computing subtree_integrity_digest; cycle marker was used to terminate traversal",
            }
            for node_id in sorted(digest_state.cycle_nodes)
        ],
        "not_claimed": list(BOM_NOT_CLAIMED),
    }
    bom["license_policy_screening"] = evaluate_license_policy(
        bom,
        load_license_policy(license_policy_path),
    )
    bom["entry_point_policy_screening"] = evaluate_entry_point_policy(
        bom,
        load_entry_point_policy(entry_point_policy_path),
    )
    bom["target_environment_screening"] = evaluate_target_environment(
        bom,
        load_target_environment(target_environment_path),
    )
    bom["lockfile_cross_check"] = evaluate_lockfile_cross_check(
        bom,
        load_lockfile_policy(lockfile_path),
    )
    bom["combined_policy_verdict"] = build_combined_policy_verdict(report, bom)
    return bom


class _DigestState:
    def __init__(
        self,
        nodes: Mapping[str, dict[str, Any]],
        provided_children: Mapping[str, list[str]],
        license_visibility: Mapping[str, dict[str, Any]],
    ) -> None:
        self.nodes = nodes
        self.provided_children = provided_children
        self.license_visibility = license_visibility
        self.cache: dict[str, str] = {}
        self.cycle_nodes: set[str] = set()

    def digest_for(self, node_id: str, stack: tuple[str, ...] = ()) -> str:
        if node_id in self.cache:
            return self.cache[node_id]
        if node_id in stack:
            self.cycle_nodes.update(stack[stack.index(node_id):])
            return _stable_digest({"cycle_ref": node_id})

        child_entries = []
        for child_id in self.provided_children.get(node_id, []):
            child = self.nodes[child_id]
            child_entries.append(
                {
                    "normalized_name": child.get("normalized_name"),
                    "version": child.get("version"),
                    "node_id": child_id,
                    "subtree_integrity_digest": self.digest_for(child_id, stack + (node_id,)),
                }
            )
        child_entries.sort(
            key=lambda item: (
                str(item.get("normalized_name") or ""),
                str(item.get("version") or ""),
                str(item.get("node_id") or ""),
            )
        )

        node = self.nodes[node_id]
        visibility = self.license_visibility.get(node_id, {})
        payload = {
            "digest_covers_fields": list(DIGEST_COVERS_FIELDS),
            "wheel_sha256": node.get("artifact_sha256"),
            "normalized_name": node.get("normalized_name"),
            "version": node.get("version"),
            "metadata_license": visibility.get("metadata_license"),
            "license_classifiers": sorted(visibility.get("license_classifiers", [])),
            "license_file_sha256_values": sorted(
                file.get("sha256") for file in visibility.get("license_files", []) if file.get("sha256")
            ),
            "sorted_child_subtree_integrity_digest_values": [
                child["subtree_integrity_digest"] for child in child_entries
            ],
        }
        digest = _stable_digest(payload)
        self.cache[node_id] = digest
        return digest


def _provided_children(edges: list[dict[str, Any]], nodes: Mapping[str, dict[str, Any]]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for edge in edges:
        parent = edge.get("from_node")
        child = edge.get("to_node")
        if (
            parent in nodes
            and child in nodes
            and nodes[parent].get("node_type") == "provided_artifact"
            and nodes[child].get("node_type") == "provided_artifact"
        ):
            children.setdefault(parent, []).append(child)
    return {key: sorted(set(value)) for key, value in children.items()}


def _provided_parents(children: Mapping[str, list[str]]) -> dict[str, list[str]]:
    parents: dict[str, list[str]] = {}
    for parent, child_ids in children.items():
        for child in child_ids:
            parents.setdefault(child, []).append(parent)
    return {key: sorted(set(value)) for key, value in parents.items()}


def _all_children(edges: list[dict[str, Any]]) -> dict[str, list[str]]:
    children: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("from_node") and edge.get("to_node"):
            children.setdefault(edge["from_node"], []).append(edge["to_node"])
    return {key: sorted(set(value)) for key, value in children.items()}


def _all_parents(edges: list[dict[str, Any]]) -> dict[str, list[str]]:
    parents: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("from_node") and edge.get("to_node"):
            parents.setdefault(edge["to_node"], []).append(edge["from_node"])
    return {key: sorted(set(value)) for key, value in parents.items()}


def _depths_over_provided_subgraph(
    roots: list[str],
    children: Mapping[str, list[str]],
    provided_ids: set[str],
) -> dict[str, int]:
    depths: dict[str, int] = {}
    queue: list[tuple[str, int]] = [(root, 0) for root in roots if root in provided_ids]
    while queue:
        node_id, depth = queue.pop(0)
        if node_id in depths and depths[node_id] <= depth:
            continue
        depths[node_id] = depth
        for child in children.get(node_id, []):
            queue.append((child, depth + 1))
    for node_id in provided_ids:
        depths.setdefault(node_id, 0)
    return depths


def _relationship_for_provided(
    node_id: str,
    *,
    roots: list[str],
    provided_children: Mapping[str, list[str]],
    provided_parents: Mapping[str, list[str]],
    depths: Mapping[str, int],
) -> str:
    if not provided_parents.get(node_id) and not provided_children.get(node_id):
        return "orphan"
    if node_id in roots or depths.get(node_id, 0) == 0:
        return "root"
    return "provided_transitive"


def _missing_depth(node_id: str, parents: Mapping[str, list[str]], depths: Mapping[str, int]) -> int | None:
    parent_depths = [depths[parent] for parent in parents.get(node_id, []) if parent in depths]
    if not parent_depths:
        return None
    return min(parent_depths) + 1


def _license_visibility(node: Mapping[str, Any]) -> dict[str, Any]:
    metadata = _wheel_metadata(Path(str(node.get("artifact_path")))) if node.get("artifact_path") else {}
    license_files = _license_files(Path(str(node.get("artifact_path")))) if node.get("artifact_path") else []
    return {
        "metadata_license": metadata.get("License"),
        "license_classifiers": [
            classifier
            for classifier in metadata.get_all("Classifier", [])
            if str(classifier).startswith("License ::")
        ] if hasattr(metadata, "get_all") else [],
        "license_file_present": bool(license_files),
        "license_files": license_files,
        "declared_only": True,
        "policy_evaluated": False,
    }


def _wheel_metadata(path: Path) -> Any:
    try:
        archive = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile):
        return Parser().parsestr("")
    with archive:
        metadata_names = sorted(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
        if not metadata_names:
            return Parser().parsestr("")
        text = archive.read(metadata_names[0]).decode("utf-8", errors="replace")
    return Parser().parsestr(text)


def _license_files(path: Path) -> list[dict[str, Any]]:
    try:
        archive = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile):
        return []
    records = []
    with archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if not _is_license_file(info.filename):
                continue
            data = archive.read(info.filename)
            records.append(
                {
                    "path": info.filename,
                    "sha256": sha256(data).hexdigest(),
                    "bytes": len(data),
                    "text_sample": data[:4096].decode("utf-8", errors="replace"),
                    "text_sample_truncated": len(data) > 4096,
                }
            )
    return sorted(records, key=lambda item: item["path"])


def _is_license_file(archive_path: str) -> bool:
    base = PurePosixPath(archive_path).name
    suffix = PurePosixPath(base).suffix.lower()
    if suffix in _BLOCKED_LICENSE_SUFFIXES:
        return False
    return bool(_LICENSE_NAME_RE.match(base))


def _embedded_sbom_visibility(path: Path) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    try:
        archive = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile):
        return _empty_embedded_sbom_visibility()
    with archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            if not _is_embedded_sbom_path(info.filename):
                continue
            data = archive.read(info.filename)
            records.append(
                {
                    "path": info.filename,
                    "sha256": sha256(data).hexdigest(),
                    "bytes": len(data),
                    "format_hint": _sbom_format_hint(info.filename),
                    "evidence_only": True,
                    "trusted_as_input": False,
                    "parsed": False,
                    "merged": False,
                }
            )
    records.sort(key=lambda item: item["path"])
    return {
        "embedded_sbom_file_present": bool(records),
        "embedded_sbom_files": records,
        "embedded_sbom_count": len(records),
        "evidence_only": True,
        "trusted_as_input": False,
        "parsed": False,
        "merged": False,
    }


def _empty_embedded_sbom_visibility() -> dict[str, Any]:
    return {
        "embedded_sbom_file_present": False,
        "embedded_sbom_files": [],
        "embedded_sbom_count": 0,
        "evidence_only": True,
        "trusted_as_input": False,
        "parsed": False,
        "merged": False,
    }


def _is_embedded_sbom_path(archive_path: str) -> bool:
    parts = PurePosixPath(archive_path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return False
    for index, part in enumerate(parts[:-2]):
        if part.endswith(".dist-info") and parts[index + 1] == "sboms":
            return True
    return False


def _sbom_format_hint(archive_path: str) -> str:
    name = PurePosixPath(archive_path).name.lower()
    for suffix, hint in sorted(_SBOM_FORMAT_HINTS.items(), key=lambda item: len(item[0]), reverse=True):
        if name.endswith(suffix):
            return hint
    return "unknown"


def _license_visibility_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    metadata_values = []
    classifiers = []
    files = []
    for artifact in artifacts:
        visibility = artifact.get("license_visibility", {})
        if visibility.get("metadata_license"):
            metadata_values.append(
                {
                    "node_id": artifact.get("node_id"),
                    "value": visibility.get("metadata_license"),
                }
            )
        for classifier in visibility.get("license_classifiers", []):
            classifiers.append({"node_id": artifact.get("node_id"), "value": classifier})
        for file in visibility.get("license_files", []):
            files.append({"node_id": artifact.get("node_id"), **file})
    return {
        "metadata_license_values": metadata_values,
        "license_classifiers": classifiers,
        "license_files_present": files,
        "policy_findings": "out_of_scope_for_v3_a",
    }


def _embedded_sbom_visibility_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    files = []
    for artifact in artifacts:
        visibility = artifact.get("embedded_sbom_visibility", {})
        for file in visibility.get("embedded_sbom_files", []) or []:
            files.append(
                {
                    "node_id": artifact.get("node_id"),
                    "name": artifact.get("name"),
                    "version": artifact.get("version"),
                    **file,
                }
            )
    return {
        "embedded_sbom_files_present": files,
        "embedded_sbom_count": len(files),
        "evidence_only": True,
        "trusted_as_input": False,
        "parsed": False,
        "merged": False,
        "policy_findings": "out_of_scope_for_bundle_025",
    }


def _entry_points_visibility_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for artifact in artifacts:
        visibility = artifact.get("entry_points_visibility", {})
        for entry in visibility.get("declared_entry_points", []):
            entries.append(
                {
                    "node_id": artifact.get("node_id"),
                    "name": artifact.get("name"),
                    "version": artifact.get("version"),
                    **entry,
                }
            )
    return {
        "declared_entry_points": entries,
        "declared_entry_point_count": len(entries),
        "policy_findings": "out_of_scope_without_explicit_v3_c_policy",
        "subtree_integrity_digest_coverage_changed": False,
    }


def _wheel_tag_visibility_summary(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    tags = []
    for artifact in artifacts:
        visibility = artifact.get("wheel_tag_visibility", {})
        if visibility.get("parsed"):
            tags.append(
                {
                    "node_id": artifact.get("node_id"),
                    "name": artifact.get("name"),
                    "version": artifact.get("version"),
                    "python_tag": visibility.get("python_tag"),
                    "abi_tag": visibility.get("abi_tag"),
                    "platform_tag": visibility.get("platform_tag"),
                }
            )
    return {
        "parsed_wheel_tags": tags,
        "parsed_wheel_tag_count": len(tags),
        "policy_findings": "out_of_scope_without_explicit_v3_d_target_environment",
        "subtree_integrity_digest_coverage_changed": False,
    }


def _record_verified(node: Mapping[str, Any]) -> bool:
    return node.get("review_verdict") != "CONTRADICTION_FOUND"


def _contradictions(node: Mapping[str, Any]) -> list[str]:
    if node.get("review_verdict") == "CONTRADICTION_FOUND":
        return list(node.get("reasons", []))
    return []


def _stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


def _tool_version() -> str:
    try:
        return importlib_metadata.version("spira-review")
    except importlib_metadata.PackageNotFoundError:
        return "source-tree"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
