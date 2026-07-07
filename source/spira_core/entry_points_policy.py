from __future__ import annotations

import configparser
import json
import zipfile
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


POLICY_SCHEMA = "SPIRA_ENTRY_POINT_POLICY_V1"
POLICY_SCHEMA_VERSION = "1.0"
MATCH_MODE = "exact_command_name"
ENTRY_POINT_DIGEST_COVERS_FIELDS = [
    "entry_point_section",
    "declared_command_name",
    "target",
]
ENTRY_POINT_SECTIONS = ("console_scripts", "gui_scripts")


def extract_entry_points(path: str | Path) -> dict[str, Any]:
    wheel_path = Path(path)
    try:
        archive = zipfile.ZipFile(wheel_path)
    except (FileNotFoundError, zipfile.BadZipFile):
        return _empty_visibility()

    with archive:
        names = sorted(name for name in archive.namelist() if name.endswith(".dist-info/entry_points.txt"))
        if not names:
            return _empty_visibility()
        raw = archive.read(names[0]).decode("utf-8", errors="replace")

    parser = configparser.ConfigParser(interpolation=None)
    parser.optionxform = str
    try:
        parser.read_string(raw)
    except configparser.Error:
        digest = _stable_digest({"parse_error": True, "raw_sha256": sha256(raw.encode("utf-8")).hexdigest()})
        return {
            "entry_points_file_present": True,
            "entry_points_path": names[0],
            "declared_entry_points": [],
            "parse_error": "entry_points.txt could not be parsed as INI",
            "entry_points_digest": digest,
            "entry_points_digest_covers_fields": list(ENTRY_POINT_DIGEST_COVERS_FIELDS),
            "declared_only": True,
            "policy_evaluated": False,
        }

    entries = []
    for section in ENTRY_POINT_SECTIONS:
        if not parser.has_section(section):
            continue
        for command_name, target in parser.items(section):
            entries.append(
                {
                    "section": section,
                    "declared_command_name": command_name.strip(),
                    "raw_command_name": command_name,
                    "target": str(target).strip(),
                }
            )
    entries.sort(key=lambda item: (item["section"], item["declared_command_name"], item["target"]))
    digest = _stable_digest(
        {
            "entry_points_digest_covers_fields": list(ENTRY_POINT_DIGEST_COVERS_FIELDS),
            "declared_entry_points": [
                {
                    "entry_point_section": item["section"],
                    "declared_command_name": item["declared_command_name"],
                    "target": item["target"],
                }
                for item in entries
            ],
        }
    )
    return {
        "entry_points_file_present": True,
        "entry_points_path": names[0],
        "declared_entry_points": entries,
        "parse_error": None,
        "entry_points_digest": digest,
        "entry_points_digest_covers_fields": list(ENTRY_POINT_DIGEST_COVERS_FIELDS),
        "declared_only": True,
        "policy_evaluated": False,
    }


def load_entry_point_policy(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    policy_path = Path(path)
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("entry point policy must be a JSON object")
    schema = payload.get("schema", POLICY_SCHEMA)
    if schema != POLICY_SCHEMA:
        raise ValueError(f"unsupported entry point policy schema: {schema}")
    match_mode = payload.get("match_mode", MATCH_MODE)
    if match_mode != MATCH_MODE:
        raise ValueError(f"unsupported entry point policy match_mode: {match_mode}")
    return {
        "schema": POLICY_SCHEMA,
        "schema_version": str(payload.get("schema_version", POLICY_SCHEMA_VERSION)),
        "path": str(policy_path.resolve()),
        "sha256": sha256(policy_path.read_bytes()).hexdigest(),
        "match_mode": MATCH_MODE,
        "case_insensitive": bool(payload.get("case_insensitive", True)),
        "blocked_command_names": _terms(payload.get("blocked_command_names", [])),
        "warn_command_names": _terms(payload.get("warn_command_names", [])),
        "not_claimed": [
            "policy matches declared entry point command names only",
            "policy is not runtime PATH hijacking detection",
            "policy does not fold executable-name variants",
        ],
    }


def evaluate_entry_point_policy(bom: Mapping[str, Any], policy: Mapping[str, Any] | None) -> dict[str, Any]:
    if policy is None:
        return {
            "evaluated": False,
            "verdict": "ENTRY_POINT_POLICY_NOT_PROVIDED",
            "findings": [],
            "not_claimed": ["no user-provided entry point policy file was supplied"],
        }

    findings = []
    case_insensitive = bool(policy.get("case_insensitive", True))
    for artifact in bom.get("artifacts", []):
        if artifact.get("relationship") == "declared_missing":
            continue
        visibility = artifact.get("entry_points_visibility", {})
        for entry in visibility.get("declared_entry_points", []):
            command = str(entry.get("declared_command_name", ""))
            for severity, names in (
                ("BLOCK", policy.get("blocked_command_names", [])),
                ("WARN", policy.get("warn_command_names", [])),
            ):
                for name in names:
                    if _matches(command, str(name), case_insensitive=case_insensitive):
                        findings.append(
                            {
                                "severity": severity,
                                "node_id": artifact.get("node_id"),
                                "name": artifact.get("name"),
                                "version": artifact.get("version"),
                                "relationship": artifact.get("relationship"),
                                "declared_command_name": command,
                                "policy_command_name": str(name),
                                "section": entry.get("section"),
                                "target": entry.get("target"),
                                "match_mode": MATCH_MODE,
                                "case_insensitive": case_insensitive,
                                "note": "matched explicit user-provided entry point policy command name",
                            }
                        )

    verdict = "ENTRY_POINT_POLICY_PASS"
    if any(finding["severity"] == "BLOCK" for finding in findings):
        verdict = "ENTRY_POINT_POLICY_BLOCK"
    elif any(finding["severity"] == "WARN" for finding in findings):
        verdict = "ENTRY_POINT_POLICY_WARN"

    return {
        "evaluated": True,
        "schema": str(policy.get("schema", POLICY_SCHEMA)),
        "schema_version": str(policy.get("schema_version", POLICY_SCHEMA_VERSION)),
        "policy_ref": {
            "path": policy.get("path"),
            "sha256": policy.get("sha256"),
        },
        "match_mode": MATCH_MODE,
        "case_insensitive": case_insensitive,
        "blocked_command_names_count": len(policy.get("blocked_command_names", [])),
        "warn_command_names_count": len(policy.get("warn_command_names", [])),
        "verdict": verdict,
        "findings": findings,
        "not_claimed": list(policy.get("not_claimed", [])),
    }


def _empty_visibility() -> dict[str, Any]:
    return {
        "entry_points_file_present": False,
        "entry_points_path": None,
        "declared_entry_points": [],
        "parse_error": None,
        "entry_points_digest": _stable_digest(
            {
                "entry_points_digest_covers_fields": list(ENTRY_POINT_DIGEST_COVERS_FIELDS),
                "declared_entry_points": [],
            }
        ),
        "entry_points_digest_covers_fields": list(ENTRY_POINT_DIGEST_COVERS_FIELDS),
        "declared_only": True,
        "policy_evaluated": False,
    }


def _matches(command: str, policy_name: str, *, case_insensitive: bool) -> bool:
    if case_insensitive:
        return command.casefold() == policy_name.casefold()
    return command == policy_name


def _terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("entry point policy terms must be lists")
    terms = []
    for item in value:
        text = str(item).strip()
        if text:
            terms.append(text)
    return terms


def _stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()
