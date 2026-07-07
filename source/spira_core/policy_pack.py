from __future__ import annotations

import json
import os
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping


POLICY_PACK_SCHEMA = "SPIRA_POLICY_PACK_V1"
POLICY_PACK_SCHEMA_VERSION = "1.0"


class PolicyPackError(ValueError):
    pass


class PolicyPackUntrustedError(PolicyPackError):
    pass


def resolve_policy_inputs(
    *,
    output_dir: str | Path,
    policy_pack_path: str | Path | None = None,
    policy_sha256: str | None = None,
    license_policy_path: str | Path | None = None,
    entry_point_policy_path: str | Path | None = None,
    target_environment_path: str | Path | None = None,
    lockfile_path: str | Path | None = None,
) -> dict[str, Any]:
    env_policy_pack = _env_nonempty("SPIRA_POLICY_PACK")
    env_policy_sha = _env_nonempty("SPIRA_POLICY_SHA256")
    pack_path = Path(env_policy_pack or policy_pack_path) if (env_policy_pack or policy_pack_path) else None
    expected_pack_sha = env_policy_sha or policy_sha256
    pack_payload: dict[str, Any] | None = None
    pack_sha: str | None = None
    pack_trust = "NOT_PROVIDED"
    if pack_path is not None:
        if not pack_path.is_file():
            raise PolicyPackUntrustedError(f"policy pack file does not exist: {pack_path}")
        pack_sha = _hash_file(pack_path)
        if expected_pack_sha is not None and pack_sha.lower() != expected_pack_sha.lower():
            raise PolicyPackUntrustedError("policy pack sha256 pin mismatch")
        pack_trust = "PINNED_MATCH" if expected_pack_sha else "UNPINNED"
        pack_payload = _load_pack(pack_path)
        if expected_pack_sha is not None and _pack_has_path_reference(pack_payload):
            raise PolicyPackUntrustedError("pinned policy pack must be self-contained; path references are forbidden")

    effective_dir = Path(output_dir) / "effective_policy_inputs"
    effective_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = TemporaryDirectory(prefix="spira_policy_pack_")
    temp_root = Path(temp_dir.name)

    license_result = _resolve_layer(
        layer="license_policy",
        pack_payload=pack_payload,
        explicit_path=_env_nonempty("SPIRA_LICENSE_POLICY") or license_policy_path,
        temp_root=temp_root,
        inline_writer=_write_license_inline,
    )
    entry_result = _resolve_layer(
        layer="entry_point_policy",
        pack_payload=pack_payload,
        explicit_path=_env_nonempty("SPIRA_ENTRY_POINT_POLICY") or entry_point_policy_path,
        temp_root=temp_root,
        inline_writer=_write_entry_inline,
    )
    target_result = _resolve_layer(
        layer="target_environment",
        pack_payload=pack_payload,
        explicit_path=_env_nonempty("SPIRA_TARGET_ENVIRONMENT") or target_environment_path,
        temp_root=temp_root,
        inline_writer=_write_target_inline,
    )
    lockfile_result = _resolve_layer(
        layer="lockfile",
        pack_payload=pack_payload,
        explicit_path=_env_nonempty("SPIRA_LOCKFILE") or lockfile_path,
        temp_root=temp_root,
        inline_writer=_write_lockfile_inline,
    )

    effective_policy = {
        "schema": "SPIRA_EFFECTIVE_POLICY_V1",
        "schema_version": "1.0",
        "policy_pack": {
            "path": str(pack_path.resolve()) if pack_path else None,
            "sha256": pack_sha,
            "expected_sha256": expected_pack_sha,
            "trust": pack_trust,
            "source": "env" if env_policy_pack else ("flag" if policy_pack_path else "not_provided"),
        },
        "precedence": "env > explicit CLI flag > policy pack > default",
        "layers": [
            license_result["effective"],
            entry_result["effective"],
            target_result["effective"],
            lockfile_result["effective"],
        ],
        "not_claimed": [
            "effective policy records policy inputs only; it is not a verdict",
            "missing policy pack sections remain NOT_EVALUATED",
            "pinned policy packs must be self-contained; external path references are rejected",
        ],
    }
    effective_policy_path = effective_dir / "effective_policy.json"
    effective_policy_path.write_text(json.dumps(effective_policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {
        "license_policy_path": license_result["path"],
        "entry_point_policy_path": entry_result["path"],
        "target_environment_path": target_result["path"],
        "lockfile_path": lockfile_result["path"],
        "effective_policy_path": effective_policy_path,
        "effective_policy": effective_policy,
        "_tempdir": temp_dir,
    }


def write_policy_refusal(
    output_dir: str | Path,
    *,
    policy_pack_path: str | Path | None,
    expected_sha256: str | None,
    reason: str,
) -> dict[str, Any]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    actual = _hash_file(Path(policy_pack_path)) if policy_pack_path and Path(policy_pack_path).is_file() else None
    report = {
        "schema": "SPIRA_POLICY_REFUSAL_REPORT_V1",
        "schema_version": "1.0",
        "verdict": "POLICY_UNTRUSTED",
        "exit_code": 5,
        "reason": reason,
        "policy_pack": {
            "path": str(Path(policy_pack_path).resolve()) if policy_pack_path else None,
            "actual_sha256": actual,
            "expected_sha256": expected_sha256,
        },
        "not_claimed": [
            "policy refusal occurs before graph scan",
            "no package trust verdict was computed",
        ],
    }
    path = output / "policy_refusal_report.json"
    report["summary_text"] = (
        "SPIRA Policy Refusal\n"
        "====================\n"
        "[POLICY_UNTRUSTED] policy pack could not be trusted; graph was not scanned\n\n"
        f"Reason: {reason}\n"
    )
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["report_path"] = str(path.resolve())
    return report


def _resolve_layer(
    *,
    layer: str,
    pack_payload: Mapping[str, Any] | None,
    explicit_path: str | Path | None,
    temp_root: Path,
    inline_writer,
) -> dict[str, Any]:
    if explicit_path is not None:
        path = Path(explicit_path)
        return {
            "path": path,
            "effective": _effective(layer, True, "env_or_flag", path=path),
        }
    if pack_payload is None or layer not in pack_payload:
        return {
            "path": None,
            "effective": _effective(layer, False, "not_provided"),
        }
    section = pack_payload.get(layer)
    if not isinstance(section, Mapping):
        return {
            "path": None,
            "effective": _effective(layer, False, "not_provided", note="pack section is not an object"),
        }
    if section.get("path"):
        path = Path(str(section["path"]))
        return {
            "path": path,
            "effective": _effective(layer, True, "pack_path", path=path),
        }
    path = inline_writer(temp_root, section)
    return {
        "path": path,
        "effective": _effective(layer, True, "pack_inline", path=path, value=section),
    }


def _effective(
    layer: str,
    evaluated: bool,
    source: str,
    *,
    path: Path | None = None,
    value: Mapping[str, Any] | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    payload = {
        "layer": layer,
        "evaluated": evaluated,
        "source": source,
        "path": str(path.resolve()) if path else None,
        "source_hash": _hash_file(path) if path and path.exists() else None,
        "value": value,
    }
    if note:
        payload["note"] = note
    return payload


def _load_pack(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PolicyPackError("policy pack must be a JSON object")
    schema = payload.get("schema", POLICY_PACK_SCHEMA)
    if schema != POLICY_PACK_SCHEMA:
        raise PolicyPackError(f"unsupported policy pack schema: {schema}")
    return payload


def _pack_has_path_reference(payload: Mapping[str, Any]) -> bool:
    for layer in ("license_policy", "entry_point_policy", "target_environment", "lockfile"):
        section = payload.get(layer)
        if isinstance(section, Mapping) and section.get("path"):
            return True
    return False


def _write_license_inline(root: Path, section: Mapping[str, Any]) -> Path:
    path = root / "license_policy.json"
    payload = {
        "schema": "SPIRA_LICENSE_POLICY_V1",
        "schema_version": str(section.get("schema_version", "1.0")),
        "match_mode": section.get("match_mode", "case_insensitive_substring"),
        "blocked_terms": section.get("blocked_terms", []),
        "warn_terms": section.get("warn_terms", []),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_entry_inline(root: Path, section: Mapping[str, Any]) -> Path:
    path = root / "entry_point_policy.json"
    payload = {
        "schema": "SPIRA_ENTRY_POINT_POLICY_V1",
        "schema_version": str(section.get("schema_version", "1.0")),
        "match_mode": section.get("match_mode", "exact_command_name"),
        "case_insensitive": bool(section.get("case_insensitive", True)),
        "blocked_command_names": section.get("blocked_command_names", []),
        "warn_command_names": section.get("warn_command_names", []),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_target_inline(root: Path, section: Mapping[str, Any]) -> Path:
    path = root / "target_environment.json"
    payload = {
        "schema": "SPIRA_TARGET_ENVIRONMENT_V1",
        "schema_version": str(section.get("schema_version", "1.0")),
        "python_tag": section.get("python_tag"),
        "abi_tag": section.get("abi_tag"),
        "platform_tag": section.get("platform_tag"),
        "strict_target": bool(section.get("strict_target", False)),
        "block_on_mismatch": bool(section.get("block_on_mismatch", False)),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_lockfile_inline(root: Path, section: Mapping[str, Any]) -> Path:
    path = root / "requirements.txt"
    lines = []
    for entry in section.get("entries", []):
        if not isinstance(entry, Mapping):
            continue
        line = f"{entry.get('name')}=={entry.get('version')}"
        for hash_value in entry.get("sha256_hashes", []):
            line += f" --hash=sha256:{hash_value}"
        lines.append(line)
    if section.get("requirements"):
        lines.extend(str(item) for item in section.get("requirements", []))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _env_nonempty(name: str) -> str | None:
    value = os.environ.get(name)
    return value if value else None


def _hash_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
