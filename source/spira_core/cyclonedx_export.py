from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Mapping


CYCLONEDX_SUPPORTED_SPEC = "1.6"
SPIRA_CDX_NOT_CLAIMED = [
    "CycloneDX export is generated from SPIRA evidence BOM only",
    "does not add vulnerability intelligence",
    "does not add malware detection",
    "does not add license legal analysis",
    "does not add provenance verification",
    "does not mutate wheels or embed SBOMs into wheels",
    "embedded SBOM files are recorded as evidence only, not trusted or merged",
    "does not resolve dependencies",
    "does not access the network",
    "does not change graph, trust, drift, or policy verdict logic",
    "declared missing dependencies are recorded as properties, not invented components",
    "absolute local paths are omitted unless include_local_paths is enabled",
]


def build_cyclonedx_bom(
    spira_bom: Mapping[str, Any],
    *,
    include_local_paths: bool = False,
    spec_version: str = CYCLONEDX_SUPPORTED_SPEC,
) -> dict[str, Any]:
    if spec_version != CYCLONEDX_SUPPORTED_SPEC:
        raise ValueError(f"unsupported CycloneDX spec version: {spec_version}")
    artifacts = [artifact for artifact in spira_bom.get("artifacts", []) if artifact.get("sha256")]
    component_refs = {_node_id(artifact): _bom_ref(artifact) for artifact in artifacts}
    root_ref = _root_ref(spira_bom, artifacts)
    components = [
        _component(artifact, component_refs[_node_id(artifact)], include_local_paths=include_local_paths)
        for artifact in artifacts
    ]
    dependencies = [{"ref": root_ref, "dependsOn": _root_depends_on(spira_bom, artifacts, component_refs)}]
    for artifact in artifacts:
        dependencies.append(_dependency_entry(artifact, component_refs))
    payload = {
        "bomFormat": "CycloneDX",
        "specVersion": spec_version,
        "serialNumber": f"urn:uuid:{_deterministic_uuid(spira_bom)}",
        "version": 1,
        "metadata": {
            "timestamp": _timestamp(spira_bom),
            "lifecycles": [{"phase": "post-build"}],
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "SPIRA Trust CLI",
                        "version": str(spira_bom.get("generated_by", {}).get("tool_version") or "0.1.0"),
                    }
                ]
            },
            "component": {
                "type": "application",
                "bom-ref": root_ref,
                "name": "SPIRA Trust local wheel set",
            },
            "properties": [
                {"name": "spira:analysis:model", "value": "local evidence gate"},
                {
                    "name": "spira:analysis:execution",
                    "value": "no network, no resolver, no install, no code execution",
                },
                {"name": "spira:source:schema", "value": str(spira_bom.get("schema"))},
                {"name": "spira:source:schema_version", "value": str(spira_bom.get("schema_version"))},
            ],
        },
        "components": components,
        "dependencies": dependencies,
        "properties": _top_level_properties(spira_bom),
    }
    return payload


def write_cyclonedx_bom(
    spira_bom: Mapping[str, Any],
    output_path: str | Path,
    *,
    include_local_paths: bool = False,
    spec_version: str = CYCLONEDX_SUPPORTED_SPEC,
) -> dict[str, Any]:
    payload = build_cyclonedx_bom(
        spira_bom,
        include_local_paths=include_local_paths,
        spec_version=spec_version,
    )
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return payload


def _component(artifact: Mapping[str, Any], bom_ref: str, *, include_local_paths: bool) -> dict[str, Any]:
    component: dict[str, Any] = {
        "type": "library",
        "bom-ref": bom_ref,
        "name": str(artifact.get("name") or artifact.get("normalized_name") or "unknown"),
        "version": str(artifact.get("version") or "0"),
        "purl": _purl(artifact),
        "hashes": [{"alg": "SHA-256", "content": str(artifact.get("sha256"))}],
        "properties": _component_properties(artifact, include_local_paths=include_local_paths),
    }
    licenses = _licenses(artifact)
    if licenses:
        component["licenses"] = licenses
    return component


def _component_properties(artifact: Mapping[str, Any], *, include_local_paths: bool) -> list[dict[str, str]]:
    integrity = artifact.get("integrity", {})
    wheel_tags = artifact.get("wheel_tag_visibility", {})
    embedded_sboms = artifact.get("embedded_sbom_visibility", {})
    props = [
        {"name": "spira:artifact:filename", "value": _filename(artifact.get("path"))},
        {"name": "spira:artifact:sha256", "value": str(artifact.get("sha256"))},
        {"name": "spira:artifact:record_verified", "value": _bool(integrity.get("record_verified"))},
        {"name": "spira:trust:status", "value": str(artifact.get("trust_status"))},
        {"name": "spira:review:verdict", "value": str(artifact.get("review_verdict"))},
        {"name": "spira:graph:status", "value": str(artifact.get("graph_status"))},
        {"name": "spira:graph:node_id", "value": str(artifact.get("node_id"))},
        {"name": "spira:graph:relationship", "value": str(artifact.get("relationship"))},
        {"name": "spira:evidence:subtree_integrity_digest", "value": str(integrity.get("subtree_integrity_digest"))},
    ]
    if wheel_tags.get("parsed"):
        props.extend(
            [
                {"name": "spira:wheel:python_tag", "value": str(wheel_tags.get("python_tag"))},
                {"name": "spira:wheel:abi_tag", "value": str(wheel_tags.get("abi_tag"))},
                {"name": "spira:wheel:platform_tag", "value": str(wheel_tags.get("platform_tag"))},
            ]
        )
    for child in artifact.get("children", []) or []:
        if _is_missing_node_id(child):
            props.append({"name": "spira:declared_missing_requirement", "value": _missing_requirement_name(child)})
    props.append({"name": "spira:embedded_sbom:count", "value": str(embedded_sboms.get("embedded_sbom_count") or 0)})
    for sbom in embedded_sboms.get("embedded_sbom_files", []) or []:
        props.append(
            {
                "name": "spira:embedded_sbom:entry",
                "value": _compact_json(
                    {
                        "path": sbom.get("path"),
                        "sha256": sbom.get("sha256"),
                        "bytes": sbom.get("bytes"),
                        "format_hint": sbom.get("format_hint"),
                        "evidence_only": True,
                        "trusted_as_input": False,
                    }
                ),
            }
        )
    if include_local_paths:
        props.append({"name": "spira:artifact:absolute_path", "value": str(artifact.get("path"))})
    return _drop_empty_properties(props)


def _dependency_entry(artifact: Mapping[str, Any], component_refs: Mapping[str, str]) -> dict[str, Any]:
    depends_on = []
    for child_id in artifact.get("children", []) or []:
        if child_id in component_refs:
            depends_on.append(component_refs[child_id])
    return {"ref": _bom_ref(artifact), "dependsOn": sorted(depends_on)}


def _licenses(artifact: Mapping[str, Any]) -> list[dict[str, Any]]:
    visibility = artifact.get("license_visibility", {})
    licenses = []
    metadata_license = visibility.get("metadata_license")
    if metadata_license:
        licenses.append({"license": {"name": str(metadata_license)}})
    for classifier in visibility.get("license_classifiers", []) or []:
        licenses.append({"license": {"name": str(classifier)}})
    return licenses


def _top_level_properties(spira_bom: Mapping[str, Any]) -> list[dict[str, str]]:
    combined = spira_bom.get("combined_policy_verdict", {})
    license_visibility = spira_bom.get("license_visibility", {})
    embedded_sbom_visibility = spira_bom.get("embedded_sbom_visibility", {})
    pep770 = spira_bom.get("pep770_sbom_consistency", {}) or {}
    pep740 = spira_bom.get("pep740_offline_attestations", {}) or {}
    trust_root = pep740.get("trust_root") or {}
    missing_count = sum(
        1
        for artifact in spira_bom.get("artifacts", []) or []
        for child in artifact.get("children", []) or []
        if _is_missing_node_id(child)
    )
    return _drop_empty_properties(
        [
            {"name": "spira:export:type", "value": "evidence-backed-cyclonedx"},
            {"name": "spira:not_claimed", "value": "does not add vulnerability intelligence, malware detection, legal analysis, provenance verification, resolver behavior, network access, or code execution"},
            {"name": "spira:graph:verdict", "value": str(spira_bom.get("source_graph", {}).get("verdict"))},
            {"name": "spira:policy:combined_verdict", "value": str(combined.get("combined_verdict"))},
            {"name": "spira:policy:winning_status", "value": str(combined.get("winning_status"))},
            {"name": "spira:graph:declared_missing_artifacts", "value": str(missing_count)},
            {"name": "spira:license:file_count", "value": str(len(license_visibility.get("license_files_present", []) or []))},
            {"name": "spira:embedded_sbom:file_count", "value": str(embedded_sbom_visibility.get("embedded_sbom_count") or 0)},
            {"name": "spira:pep770:status", "value": str(pep770.get("status"))},
            {"name": "spira:pep770:evaluated", "value": _bool(pep770.get("evaluated"))},
            {"name": "spira:pep740:status", "value": str(pep740.get("status"))},
            {"name": "spira:pep740:evaluated", "value": _bool(pep740.get("attestation_path"))},
            {"name": "spira:attestation:identity_evaluated", "value": _bool(pep740.get("identity_evaluated"))},
            {"name": "spira:attestation:trust_root_sha256", "value": str(trust_root.get("sha256"))},
            {"name": "spira:attestation:trust_root_pinned", "value": _bool(trust_root.get("pinned"))},
        ]
    )


def _root_depends_on(
    spira_bom: Mapping[str, Any],
    artifacts: list[Mapping[str, Any]],
    component_refs: Mapping[str, str],
) -> list[str]:
    root_ids = {str(root) for root in spira_bom.get("roots", []) or []}
    return sorted(
        component_refs[_node_id(artifact)]
        for artifact in artifacts
        if _node_id(artifact) in root_ids and _node_id(artifact) in component_refs
    )


def _root_ref(spira_bom: Mapping[str, Any], artifacts: list[Mapping[str, Any]]) -> str:
    digest_source = json.dumps(
        {
            "schema": spira_bom.get("schema"),
            "artifacts": sorted((artifact.get("normalized_name"), artifact.get("version"), artifact.get("sha256")) for artifact in artifacts),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return f"spira:local-wheel-set:{uuid.uuid5(uuid.NAMESPACE_URL, digest_source).hex}"


def _deterministic_uuid(spira_bom: Mapping[str, Any]) -> uuid.UUID:
    source = json.dumps(
        {
            "schema": spira_bom.get("schema"),
            "artifacts": [
                (artifact.get("normalized_name"), artifact.get("version"), artifact.get("sha256"))
                for artifact in spira_bom.get("artifacts", [])
                if artifact.get("sha256")
            ],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return uuid.uuid5(uuid.NAMESPACE_URL, source)


def _bom_ref(artifact: Mapping[str, Any]) -> str:
    name = str(artifact.get("normalized_name") or artifact.get("name") or "unknown")
    version = str(artifact.get("version") or "0")
    sha = str(artifact.get("sha256") or "no-sha")
    return f"spira:pypi/{name}@{version}:sha256:{sha}"


def _purl(artifact: Mapping[str, Any]) -> str:
    name = str(artifact.get("normalized_name") or artifact.get("name") or "unknown")
    version = str(artifact.get("version") or "0")
    return f"pkg:pypi/{name}@{version}"


def _node_id(artifact: Mapping[str, Any]) -> str:
    return str(artifact.get("node_id"))


def _is_missing_node_id(value: Any) -> bool:
    return str(value).startswith("missing::")


def _missing_requirement_name(value: Any) -> str:
    text = str(value)
    if _is_missing_node_id(text):
        return text.removeprefix("missing::")
    return text


def _timestamp(spira_bom: Mapping[str, Any]) -> str:
    value = spira_bom.get("created_at_utc")
    if isinstance(value, str) and value:
        return value
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _filename(path: Any) -> str:
    if not path:
        return ""
    text = str(path)
    if "\\" in text:
        return PureWindowsPath(text).name
    return Path(text).name


def _bool(value: Any) -> str:
    return "true" if bool(value) else "false"


def _compact_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _drop_empty_properties(properties: list[dict[str, str]]) -> list[dict[str, str]]:
    return [item for item in properties if item.get("value") not in {"", "None", None}]
