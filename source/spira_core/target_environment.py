from __future__ import annotations

import json
import re
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


POLICY_SCHEMA = "SPIRA_TARGET_ENVIRONMENT_V1"
POLICY_SCHEMA_VERSION = "1.0"
WHEEL_TAG_DIGEST_COVERS_FIELDS = [
    "python_tag",
    "abi_tag",
    "platform_tag",
]


def parse_wheel_tags(path: str | Path) -> dict[str, Any]:
    filename = Path(path).name
    stem = filename[:-4] if filename.endswith(".whl") else Path(path).stem
    parts = stem.rsplit("-", 3)
    if len(parts) != 4:
        return {
            "parsed": False,
            "filename": filename,
            "python_tag": None,
            "abi_tag": None,
            "platform_tag": None,
            "parse_error": "wheel filename does not contain python/abi/platform tag triplet",
            "wheel_tags_digest": _stable_digest({"parsed": False, "filename": filename}),
            "wheel_tags_digest_covers_fields": list(WHEEL_TAG_DIGEST_COVERS_FIELDS),
            "declared_only": True,
            "policy_evaluated": False,
        }
    _, python_tag, abi_tag, platform_tag = parts
    return {
        "parsed": True,
        "filename": filename,
        "python_tag": python_tag,
        "abi_tag": abi_tag,
        "platform_tag": platform_tag,
        "parse_error": None,
        "wheel_tags_digest": _stable_digest(
            {
                "wheel_tags_digest_covers_fields": list(WHEEL_TAG_DIGEST_COVERS_FIELDS),
                "python_tag": python_tag,
                "abi_tag": abi_tag,
                "platform_tag": platform_tag,
            }
        ),
        "wheel_tags_digest_covers_fields": list(WHEEL_TAG_DIGEST_COVERS_FIELDS),
        "declared_only": True,
        "policy_evaluated": False,
    }


def load_target_environment(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    target_path = Path(path)
    payload = json.loads(target_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("target environment policy must be a JSON object")
    schema = payload.get("schema", POLICY_SCHEMA)
    if schema != POLICY_SCHEMA:
        raise ValueError(f"unsupported target environment schema: {schema}")
    return {
        "schema": POLICY_SCHEMA,
        "schema_version": str(payload.get("schema_version", POLICY_SCHEMA_VERSION)),
        "path": str(target_path.resolve()),
        "sha256": sha256(target_path.read_bytes()).hexdigest(),
        "python_tag": _required_text(payload, "python_tag"),
        "abi_tag": _required_text(payload, "abi_tag"),
        "platform_tag": _required_text(payload, "platform_tag"),
        "strict_target": bool(payload.get("strict_target", False)),
        "block_on_mismatch": bool(payload.get("block_on_mismatch", False)),
        "not_claimed": [
            "target environment screening is wheel filename tag relevance only",
            "target environment screening is not full packaging.tags compatibility",
            "target environment screening does not guarantee installability",
        ],
    }


def evaluate_target_environment(bom: Mapping[str, Any], target: Mapping[str, Any] | None) -> dict[str, Any]:
    if target is None:
        return {
            "evaluated": False,
            "verdict": "TARGET_ENVIRONMENT_NOT_PROVIDED",
            "findings": [],
            "not_claimed": ["no user-provided target environment file was supplied"],
        }

    findings = []
    for artifact in bom.get("artifacts", []):
        if artifact.get("relationship") == "declared_missing":
            continue
        visibility = artifact.get("wheel_tag_visibility", {})
        if not visibility.get("parsed"):
            findings.append(_finding("UNVERIFIED", artifact, "wheel_tags", None, None, "wheel tag triplet could not be parsed"))
            continue
        components = [
            ("python_tag", visibility.get("python_tag"), target.get("python_tag")),
            ("abi_tag", visibility.get("abi_tag"), target.get("abi_tag")),
            ("platform_tag", visibility.get("platform_tag"), target.get("platform_tag")),
        ]
        for field, value, expected in components:
            result = _component_match(field, str(value), str(expected))
            if result["status"] == "MATCH":
                continue
            severity = "NOTE"
            if target.get("block_on_mismatch"):
                severity = "BLOCK"
            elif target.get("strict_target"):
                severity = "WARN"
            findings.append(_finding(severity, artifact, field, value, expected, result["note"]))

    verdict = "TARGET_ENVIRONMENT_PASS"
    if any(finding["severity"] == "BLOCK" for finding in findings):
        verdict = "TARGET_ENVIRONMENT_BLOCK"
    elif any(finding["severity"] == "WARN" for finding in findings):
        verdict = "TARGET_ENVIRONMENT_WARN"
    elif findings:
        verdict = "TARGET_ENVIRONMENT_NOTES"

    return {
        "evaluated": True,
        "schema": str(target.get("schema", POLICY_SCHEMA)),
        "schema_version": str(target.get("schema_version", POLICY_SCHEMA_VERSION)),
        "target_ref": {
            "path": target.get("path"),
            "sha256": target.get("sha256"),
        },
        "target": {
            "python_tag": target.get("python_tag"),
            "abi_tag": target.get("abi_tag"),
            "platform_tag": target.get("platform_tag"),
            "strict_target": bool(target.get("strict_target")),
            "block_on_mismatch": bool(target.get("block_on_mismatch")),
        },
        "verdict": verdict,
        "findings": findings,
        "not_claimed": list(target.get("not_claimed", [])),
    }


def _component_match(field: str, value: str, expected: str) -> dict[str, str]:
    if field == "abi_tag" and value == "none":
        return {"status": "MATCH", "note": "abi tag none is universal"}
    if field == "platform_tag" and value == "any":
        return {"status": "MATCH", "note": "platform tag any is universal"}
    if field == "python_tag" and _python_universal_for_target(value, expected):
        return {"status": "MATCH", "note": "python tag is broad Python 3 compatible tag"}
    if value == expected:
        return {"status": "MATCH", "note": "exact tag match"}
    return {
        "status": "UNVERIFIED",
        "note": "tag is not exact target match and narrow parser does not model compatibility hierarchy",
    }


def _python_universal_for_target(value: str, expected: str) -> bool:
    return value == "py3" and expected.startswith("cp3")


def _finding(
    severity: str,
    artifact: Mapping[str, Any],
    field: str,
    observed: Any,
    expected: Any,
    note: str,
) -> dict[str, Any]:
    return {
        "severity": severity,
        "node_id": artifact.get("node_id"),
        "name": artifact.get("name"),
        "version": artifact.get("version"),
        "relationship": artifact.get("relationship"),
        "field": field,
        "observed": observed,
        "expected": expected,
        "note": note,
    }


def _required_text(payload: Mapping[str, Any], field: str) -> str:
    value = str(payload.get(field, "")).strip()
    if not value:
        raise ValueError(f"target environment requires {field}")
    if not re.match(r"^[A-Za-z0-9_\\.]+$", value):
        raise ValueError(f"target environment {field} contains unsupported characters")
    return value


def _stable_digest(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()
