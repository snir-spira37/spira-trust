from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


POLICY_SCHEMA = "SPIRA_LOCKFILE_CROSS_CHECK_V1"
POLICY_SCHEMA_VERSION = "1.1"
_SHA256_RE = re.compile(r"sha256[:=]([A-Fa-f0-9]{64})")


def load_lockfile_policy(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    lockfile_path = Path(path)
    text = lockfile_path.read_text(encoding="utf-8", errors="replace")
    kind = _detect_kind(lockfile_path, text)
    entries, unsupported = _parse_lockfile(lockfile_path, text, kind)
    return {
        "schema": POLICY_SCHEMA,
        "schema_version": POLICY_SCHEMA_VERSION,
        "path": str(lockfile_path.resolve()),
        "sha256": sha256(lockfile_path.read_bytes()).hexdigest(),
        "kind": kind,
        "entries": entries,
        "unsupported_entries": unsupported,
        "not_claimed": [
            "narrow local lockfile cross-check only",
            "not a dependency resolver",
            "not a full requirements.txt parser",
            "not a full poetry.lock parser",
            "not a full uv.lock parser",
            "not full PEP 508 support",
            "only compares local artifact bytes against lockfile package name/version/hash facts",
            "unsupported syntax becomes UNVERIFIED notes",
        ],
    }


def evaluate_lockfile_cross_check(bom: Mapping[str, Any], policy: Mapping[str, Any] | None) -> dict[str, Any]:
    if policy is None:
        return {
            "evaluated": False,
            "verdict": "LOCKFILE_NOT_PROVIDED",
            "findings": [],
            "not_claimed": ["no user-provided lockfile was supplied"],
        }

    artifacts = [
        artifact for artifact in bom.get("artifacts", [])
        if artifact.get("relationship") != "declared_missing" and artifact.get("sha256")
    ]
    by_name: dict[str, list[Mapping[str, Any]]] = {}
    for artifact in artifacts:
        by_name.setdefault(str(artifact.get("normalized_name")), []).append(artifact)

    entries = list(policy.get("entries", []))
    entry_names = {entry["normalized_name"] for entry in entries}
    findings: list[dict[str, Any]] = []
    entry_results: list[dict[str, Any]] = []

    for unsupported in policy.get("unsupported_entries", []):
        findings.append(
            {
                "severity": "NOTE",
                "kind": "LOCKFILE_UNSUPPORTED_ENTRY",
                "line": unsupported.get("line"),
                "raw": unsupported.get("raw"),
                "note": "lockfile line or block is outside the supported V4-B subset",
            }
        )

    for entry in entries:
        candidates = by_name.get(entry["normalized_name"], [])
        if not candidates:
            entry_results.append(_entry_result(entry, "LOCK_MISSING_ARTIFACT"))
            findings.append(
                {
                    "severity": "BLOCK",
                    "kind": "LOCKFILE_MISSING_LOCAL_WHEEL",
                    "name": entry["name"],
                    "normalized_name": entry["normalized_name"],
                    "expected_version": entry["version"],
                    "note": "lockfile declares a package but no local wheel was provided",
                }
            )
            continue
        version_matches = [artifact for artifact in candidates if artifact.get("version") == entry["version"]]
        if not version_matches:
            entry_results.append(
                _entry_result(
                    entry,
                    "LOCK_VERSION_MISMATCH",
                    provided_versions=sorted(str(artifact.get("version")) for artifact in candidates),
                )
            )
            findings.append(
                {
                    "severity": "BLOCK",
                    "kind": "LOCKFILE_VERSION_MISMATCH",
                    "name": entry["name"],
                    "normalized_name": entry["normalized_name"],
                    "expected_version": entry["version"],
                    "provided_versions": sorted(str(artifact.get("version")) for artifact in candidates),
                    "note": "local wheel version does not match the lockfile pin",
                }
            )
            continue
        expected_hashes = set(entry.get("sha256_hashes", []))
        hash_mismatched = False
        if expected_hashes:
            for artifact in version_matches:
                if artifact.get("sha256") not in expected_hashes:
                    hash_mismatched = True
                    entry_results.append(
                        _entry_result(
                            entry,
                            "LOCK_HASH_MISMATCH",
                            node_id=artifact.get("node_id"),
                            provided_sha256=artifact.get("sha256"),
                        )
                    )
                    findings.append(
                        {
                            "severity": "BLOCK",
                            "kind": "LOCKFILE_HASH_MISMATCH",
                            "name": entry["name"],
                            "normalized_name": entry["normalized_name"],
                            "version": entry["version"],
                            "expected_sha256": sorted(expected_hashes),
                            "provided_sha256": artifact.get("sha256"),
                            "node_id": artifact.get("node_id"),
                            "note": "lockfile hash and local wheel sha256 do not match",
                        }
                    )
        if not hash_mismatched:
            entry_results.extend(
                _entry_result(
                    entry,
                    "LOCK_MATCH",
                    node_id=artifact.get("node_id"),
                    provided_sha256=artifact.get("sha256"),
                    hash_checked=bool(expected_hashes),
                )
                for artifact in version_matches
            )

    for artifact in artifacts:
        if artifact.get("normalized_name") not in entry_names:
            findings.append(
                {
                    "severity": "WARN",
                    "kind": "LOCKFILE_EXTRA_LOCAL_WHEEL",
                    "name": artifact.get("name"),
                    "normalized_name": artifact.get("normalized_name"),
                    "version": artifact.get("version"),
                    "node_id": artifact.get("node_id"),
                    "note": "local wheel was provided but is absent from the lockfile",
                }
            )

    verdict = "LOCKFILE_CROSS_CHECK_PASS"
    if any(finding["severity"] == "BLOCK" for finding in findings):
        verdict = "LOCKFILE_CROSS_CHECK_BLOCK"
    elif any(finding["severity"] == "WARN" for finding in findings):
        verdict = "LOCKFILE_CROSS_CHECK_WARN"
    elif any(finding["severity"] == "NOTE" for finding in findings):
        verdict = "LOCKFILE_CROSS_CHECK_NOTES"

    return {
        "evaluated": True,
        "schema": str(policy.get("schema", POLICY_SCHEMA)),
        "schema_version": str(policy.get("schema_version", POLICY_SCHEMA_VERSION)),
        "lockfile_ref": {
            "path": policy.get("path"),
            "sha256": policy.get("sha256"),
            "kind": policy.get("kind"),
        },
        "entry_count": len(entries),
        "unsupported_entry_count": len(policy.get("unsupported_entries", [])),
        "verdict": verdict,
        "entry_results": entry_results,
        "status_counts": _status_counts(entry_results, findings),
        "findings": findings,
        "not_claimed": list(policy.get("not_claimed", [])),
    }


def _detect_kind(path: Path, text: str) -> str:
    name = path.name.lower()
    if name == "pipfile.lock":
        return "pipfile_lock"
    if name == "poetry.lock":
        return "poetry_lock"
    if name == "uv.lock":
        return "uv_lock"
    if "==" in text:
        return "pip_requirements_subset"
    return "unknown_text"


def _parse_lockfile(path: Path, text: str, kind: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if kind == "pipfile_lock":
        return _parse_pipfile_lock(text)
    if kind == "poetry_lock":
        return _parse_poetry_lock(text)
    if kind == "uv_lock":
        return _parse_uv_lock(text)
    return _parse_pip_requirements_subset(text)


def _parse_pip_requirements_subset(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    for line_no, raw in _logical_requirement_lines(text):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        body = stripped.split(" #", 1)[0].strip()
        match = re.match(r"^([A-Za-z0-9_.-]+)==([A-Za-z0-9_.!+-]+)(.*)$", body)
        if not match:
            unsupported.append({"line": line_no, "raw": raw})
            continue
        trailing = match.group(3).strip()
        hashes = _extract_sha256_hashes(trailing)
        trailing_without_hashes = _strip_supported_hash_tokens(trailing)
        if trailing_without_hashes:
            unsupported.append({"line": line_no, "raw": raw})
            continue
        entries.append(_entry(match.group(1), match.group(2), hashes, source_line=line_no))
    return entries, unsupported


def _parse_poetry_lock(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _parse_toml_package_blocks(text, kind="poetry.lock")


def _parse_uv_lock(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _parse_toml_package_blocks(text, kind="uv.lock")


def _parse_toml_package_blocks(text: str, *, kind: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_start = 0
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if stripped == "[[package]]":
            if current is not None:
                _finish_package_block(current, current_start, entries, unsupported, kind=kind)
            current = {"sha256_hashes": []}
            current_start = line_no
            continue
        if current is None or not stripped or stripped.startswith("#"):
            continue
        match = re.match(r"^(name|version)\s*=\s*\"([^\"]+)\"\s*$", stripped)
        if match:
            current[match.group(1)] = match.group(2)
        current["sha256_hashes"].extend(_extract_sha256_hashes(stripped))
    if current is not None:
        _finish_package_block(current, current_start, entries, unsupported, kind=kind)
    return entries, unsupported


def _finish_package_block(
    block: Mapping[str, Any],
    start_line: int,
    entries: list[dict[str, Any]],
    unsupported: list[dict[str, Any]],
    *,
    kind: str,
) -> None:
    name = block.get("name")
    version = block.get("version")
    if name and version:
        entries.append(_entry(str(name), str(version), list(block.get("sha256_hashes", [])), source_line=start_line))
    else:
        unsupported.append({"line": start_line, "raw": f"[[package]] missing name/version in {kind}"})


def _parse_pipfile_lock(text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entries: list[dict[str, Any]] = []
    unsupported: list[dict[str, Any]] = []
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], [{"line": exc.lineno, "raw": "invalid Pipfile.lock JSON"}]
    if not isinstance(payload, dict):
        return [], [{"line": None, "raw": "Pipfile.lock root is not a JSON object"}]
    for section in ("default", "develop"):
        packages = payload.get(section, {})
        if not isinstance(packages, dict):
            unsupported.append({"line": None, "raw": f"{section} section is not an object"})
            continue
        for name, info in packages.items():
            if not isinstance(info, dict):
                unsupported.append({"line": None, "raw": f"{name} entry is not an object"})
                continue
            version = str(info.get("version", ""))
            if version.startswith("=="):
                version = version[2:]
            if not version:
                unsupported.append({"line": None, "raw": f"{name} entry lacks pinned version"})
                continue
            hashes = [
                _normalize_sha256_text(str(item))
                for item in info.get("hashes", [])
                if isinstance(item, str) and _normalize_sha256_text(str(item))
            ]
            entries.append(_entry(str(name), version, hashes, source_line=None))
    return entries, unsupported


def _logical_requirement_lines(text: str) -> list[tuple[int, str]]:
    logical: list[tuple[int, str]] = []
    buffer = ""
    start_line: int | None = None
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.rstrip()
        if start_line is None:
            start_line = line_no
        if stripped.endswith("\\"):
            buffer += stripped[:-1].strip() + " "
            continue
        buffer += stripped.strip()
        logical.append((start_line, buffer))
        buffer = ""
        start_line = None
    if buffer:
        logical.append((start_line or 1, buffer))
    return logical


def _extract_sha256_hashes(text: str) -> list[str]:
    return [match.lower() for match in _SHA256_RE.findall(text)]


def _strip_supported_hash_tokens(text: str) -> str:
    without_equals = re.sub(r"--hash=sha256:[A-Fa-f0-9]{64}", "", text)
    without_space = re.sub(r"--hash\s+sha256:[A-Fa-f0-9]{64}", "", without_equals)
    return without_space.strip()


def _normalize_sha256_text(text: str) -> str | None:
    hashes = _extract_sha256_hashes(text)
    if hashes:
        return hashes[0]
    return None


def _entry_result(entry: Mapping[str, Any], status: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "status": status,
        "name": entry.get("name"),
        "normalized_name": entry.get("normalized_name"),
        "version": entry.get("version"),
        "source_line": entry.get("source_line"),
        "hash_declared": bool(entry.get("sha256_hashes")),
    }
    payload.update(extra)
    return payload


def _status_counts(entry_results: list[Mapping[str, Any]], findings: list[Mapping[str, Any]]) -> dict[str, int]:
    counts = {
        "LOCK_MATCH": 0,
        "LOCK_MISSING_ARTIFACT": 0,
        "LOCK_VERSION_MISMATCH": 0,
        "LOCK_HASH_MISMATCH": 0,
        "LOCK_EXTRA_ARTIFACT": 0,
        "LOCK_NOT_EVALUATED": 0,
    }
    for result in entry_results:
        status = str(result.get("status"))
        if status in counts:
            counts[status] += 1
    counts["LOCK_EXTRA_ARTIFACT"] = sum(1 for finding in findings if finding.get("kind") == "LOCKFILE_EXTRA_LOCAL_WHEEL")
    return counts


def _entry(name: str, version: str, hashes: list[str], *, source_line: int | None) -> dict[str, Any]:
    return {
        "name": name,
        "normalized_name": _normalize_pep503(name),
        "version": version,
        "sha256_hashes": [item.lower() for item in hashes],
        "source_line": source_line,
    }


def _normalize_pep503(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()
