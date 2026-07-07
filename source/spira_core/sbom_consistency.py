from __future__ import annotations

import json
import re
import zipfile
from hashlib import sha256
from pathlib import PurePosixPath
from typing import Any


SBOM_CONSISTENCY_SCHEMA = "SPIRA_PEP770_SBOM_CONSISTENCY_V1"


def _normalize_pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def evaluate_embedded_sbom_consistency(wheel_path: str, *, package_name: str, version: str | None) -> dict[str, Any]:
    """Evaluate a narrow PEP 770 consistency subset for embedded SBOM files.

    PEP 770 treats SBOM documents as opaque. This checker therefore only
    validates the standard location, JSON parseability for JSON SBOMs, and
    top-level CycloneDX component name/version consistency when those fields
    are present. It does not merge or trust SBOM contents.
    """

    results: list[dict[str, Any]] = []
    try:
        archive = zipfile.ZipFile(wheel_path)
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        return _summary(results, error=str(exc))
    with archive:
        for info in archive.infolist():
            if info.is_dir() or not _is_embedded_sbom_path(info.filename):
                continue
            data = archive.read(info.filename)
            results.append(_evaluate_one(info.filename, data, package_name=package_name, version=version))
    return _summary(results)


def _evaluate_one(path: str, data: bytes, *, package_name: str, version: str | None) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema": SBOM_CONSISTENCY_SCHEMA,
        "path": path,
        "sha256": sha256(data).hexdigest(),
        "bytes": len(data),
        "status": "UNVERIFIED",
        "findings": [],
        "format": _format_hint(path),
        "not_claimed": [
            "does not validate full SBOM schema",
            "does not trust, merge, or replace SPIRA evidence with embedded SBOM contents",
            "does not perform vulnerability, license, or legal analysis",
        ],
    }
    if record["format"] != "json":
        record["findings"].append("unsupported SBOM format for V1 consistency parser")
        return record
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        record["status"] = "CONTRADICTION"
        record["findings"].append(f"embedded SBOM JSON is not parseable: {exc}")
        return record
    if not isinstance(payload, dict):
        record["status"] = "CONTRADICTION"
        record["findings"].append("embedded SBOM JSON root is not an object")
        return record
    if payload.get("bomFormat") != "CycloneDX":
        record["findings"].append("JSON SBOM is not CycloneDX; V1 records it as UNVERIFIED")
        return record
    record["standard"] = "CycloneDX"
    component = payload.get("metadata", {}).get("component") if isinstance(payload.get("metadata"), dict) else None
    if not isinstance(component, dict):
        record["status"] = "VERIFIED_OK"
        record["findings"].append("CycloneDX SBOM parseable; no metadata.component to compare")
        return record
    declared_name = component.get("name")
    declared_version = component.get("version")
    mismatches = []
    if declared_name and _normalize_pep503(str(declared_name)) != _normalize_pep503(package_name):
        mismatches.append(f"metadata.component.name {declared_name!r} does not match wheel name {package_name!r}")
    if declared_version and version and str(declared_version) != str(version):
        mismatches.append(f"metadata.component.version {declared_version!r} does not match wheel version {version!r}")
    if mismatches:
        record["status"] = "CONTRADICTION"
        record["findings"].extend(mismatches)
    else:
        record["status"] = "VERIFIED_OK"
        record["findings"].append("CycloneDX metadata.component is consistent with wheel metadata")
    return record


def _summary(results: list[dict[str, Any]], *, error: str | None = None) -> dict[str, Any]:
    statuses = [item.get("status") for item in results]
    if error:
        status = "UNVERIFIED"
    elif any(status == "CONTRADICTION" for status in statuses):
        status = "CONTRADICTION"
    elif results and all(status == "VERIFIED_OK" for status in statuses):
        status = "VERIFIED_OK"
    elif results:
        status = "UNVERIFIED"
    else:
        status = "NOT_EVALUATED"
    return {
        "schema": SBOM_CONSISTENCY_SCHEMA,
        "status": status,
        "evaluated": bool(results),
        "embedded_sbom_count": len(results),
        "results": results,
        "error": error,
        "not_claimed": [
            "PEP 770 SBOM consistency is a narrow local evidence check",
            "does not validate full SBOM schemas",
            "does not treat SBOM contents as authoritative package truth",
        ],
    }


def _is_embedded_sbom_path(archive_path: str) -> bool:
    parts = PurePosixPath(archive_path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return False
    for index, part in enumerate(parts[:-2]):
        if part.endswith(".dist-info") and parts[index + 1] == "sboms":
            return True
    return False


def _format_hint(path: str) -> str:
    lowered = PurePosixPath(path).name.lower()
    if lowered.endswith(".json"):
        return "json"
    if lowered.endswith(".xml"):
        return "xml"
    if lowered.endswith(".spdx"):
        return "spdx"
    return "unknown"
