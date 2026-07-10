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


def _purl_type(purl: Any) -> str | None:
    if not isinstance(purl, str) or not purl.startswith("pkg:"):
        return None
    rest = purl[4:]
    return rest.split("/", 1)[0].lower() if "/" in rest else None


def _purl_name(purl: Any) -> str | None:
    if not isinstance(purl, str) or not purl.startswith("pkg:"):
        return None
    rest = purl[4:]
    if "/" not in rest:
        return None
    _, name_and_more = rest.split("/", 1)
    name = name_and_more.split("@", 1)[0].split("?", 1)[0]
    return urllib_unquote(name)


def urllib_unquote(value: str) -> str:
    # Avoid importing urllib for the common case while still handling PURL-escaped names.
    if "%" not in value:
        return value
    from urllib.parse import unquote

    return unquote(value)


def _versions_equivalent(left: Any, right: Any) -> bool:
    left_normalized = _normalize_version_subset(str(left))
    right_normalized = _normalize_version_subset(str(right))
    if left_normalized == right_normalized:
        return True
    left_parts = _numeric_release_parts(left_normalized)
    right_parts = _numeric_release_parts(right_normalized)
    if left_parts is None or right_parts is None:
        return False
    return _trim_trailing_zeroes(left_parts) == _trim_trailing_zeroes(right_parts)


def _normalize_version_subset(version: str) -> str:
    normalized = version.strip()
    if len(normalized) > 1 and normalized[0] in {"v", "V"}:
        normalized = normalized[1:]
    return normalized


def _numeric_release_parts(version: str) -> list[int] | None:
    if not re.fullmatch(r"\d+(?:\.\d+)*", version):
        return None
    return [int(part) for part in version.split(".")]


def _trim_trailing_zeroes(parts: list[int]) -> list[int]:
    trimmed = parts[:]
    while len(trimmed) > 1 and trimmed[-1] == 0:
        trimmed.pop()
    return trimmed


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
        record["status"] = "INVALID"
        record["findings"].append(f"embedded SBOM JSON is not parseable: {exc}")
        return record
    if not isinstance(payload, dict):
        record["status"] = "INVALID"
        record["findings"].append("embedded SBOM JSON root is not an object")
        return record
    if payload.get("bomFormat") != "CycloneDX":
        record["findings"].append("JSON SBOM is not CycloneDX; V1 records it as UNVERIFIED")
        return record
    record["standard"] = "CycloneDX"
    component = payload.get("metadata", {}).get("component") if isinstance(payload.get("metadata"), dict) else None
    if not isinstance(component, dict):
        record["component_scope"] = "UNKNOWN_COMPONENT_SCOPE"
        record["status"] = "UNVERIFIED"
        record["findings"].append("CycloneDX SBOM parseable; no metadata.component to compare with wheel metadata")
        return record
    declared_name = component.get("name")
    declared_version = component.get("version")
    declared_purl = component.get("purl")
    purl_type = _purl_type(declared_purl)
    record["component"] = {
        "name": declared_name,
        "version": declared_version,
        "purl": declared_purl,
        "purl_type": purl_type,
    }
    if purl_type and purl_type != "pypi":
        record["component_scope"] = "COMPONENT_SCOPE_NOT_WHEEL"
        record["status"] = "COMPONENT_SCOPE_NOT_WHEEL"
        record["findings"].append(f"metadata.component.purl is {purl_type!r}; V1 does not compare non-PyPI component SBOMs to wheel metadata")
        return record

    if purl_type == "pypi":
        record["component_scope"] = "PYPI_WHEEL_SCOPED"
        purl_name = _purl_name(declared_purl)
        if purl_name and _normalize_pep503(purl_name) != _normalize_pep503(package_name):
            record["status"] = "CONTRADICTION"
            record["findings"].append(f"metadata.component.purl name {purl_name!r} does not match wheel name {package_name!r}")
            return record
    elif declared_name and _normalize_pep503(str(declared_name)) == _normalize_pep503(package_name):
        record["component_scope"] = "PYPI_WHEEL_SCOPED_INFERRED"
    else:
        record["component_scope"] = "UNKNOWN_COMPONENT_SCOPE"
        record["status"] = "UNVERIFIED"
        if declared_name:
            record["findings"].append(
                f"metadata.component.name {declared_name!r} does not match wheel name {package_name!r}, and no purl identifies component scope"
            )
        else:
            record["findings"].append("metadata.component has no name or purl to identify wheel scope")
        return record

    mismatches = []
    if declared_name and _normalize_pep503(str(declared_name)) != _normalize_pep503(package_name):
        mismatches.append(f"metadata.component.name {declared_name!r} does not match wheel name {package_name!r}")
    if declared_version and version and not _versions_equivalent(declared_version, version):
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
    wheel_scoped = [item for item in results if item.get("component_scope") in {"PYPI_WHEEL_SCOPED", "PYPI_WHEEL_SCOPED_INFERRED"}]
    if error:
        status = "UNVERIFIED"
    elif any(status == "INVALID" for status in statuses):
        status = "INVALID"
    elif any(status == "CONTRADICTION" for status in statuses):
        status = "CONTRADICTION"
    elif wheel_scoped and all(item.get("status") == "VERIFIED_OK" for item in wheel_scoped):
        status = "VERIFIED_OK"
    elif results and not wheel_scoped and all(status == "COMPONENT_SCOPE_NOT_WHEEL" for status in statuses):
        status = "NO_WHEEL_SCOPED_SBOM"
    elif results:
        status = "UNVERIFIED"
    else:
        status = "NOT_EVALUATED"
    return {
        "schema": SBOM_CONSISTENCY_SCHEMA,
        "status": status,
        "evaluated": bool(results),
        "embedded_sbom_count": len(results),
        "wheel_scoped_sbom_count": len(wheel_scoped),
        "non_wheel_scoped_sbom_count": sum(1 for item in results if item.get("component_scope") == "COMPONENT_SCOPE_NOT_WHEEL"),
        "unknown_scope_sbom_count": sum(1 for item in results if item.get("component_scope") == "UNKNOWN_COMPONENT_SCOPE"),
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
