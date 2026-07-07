from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Sequence


class GovernanceError(ValueError):
    """Raised when a governance primitive would create an invalid artifact."""


@dataclass(frozen=True)
class HashRecord:
    file: str
    sha256: str
    bytes: int

    def as_dict(self) -> dict[str, Any]:
        return {"file": self.file, "sha256": self.sha256, "bytes": self.bytes}


def hash_file(path: str | Path) -> dict[str, Any]:
    """Return SHA256 and byte count for a file."""
    target = Path(path)
    digest = sha256()
    size = 0
    with target.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"file": str(target), "sha256": digest.hexdigest(), "bytes": size}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def _relative_record(root: Path, path: Path) -> HashRecord:
    hashed = hash_file(path)
    return HashRecord(
        file=path.relative_to(root).as_posix(),
        sha256=hashed["sha256"],
        bytes=hashed["bytes"],
    )


def build_manifest(root: str | Path, *, exclude: Iterable[str] = ("manifest.json",)) -> dict[str, Any]:
    """Build a deterministic manifest for files under root.

    The manifest intentionally excludes itself by default. This is the
    self-reference rule learned from the delivery packages.
    """
    root_path = Path(root)
    excluded = set(exclude)
    if not root_path.is_dir():
        raise GovernanceError(f"manifest root is not a directory: {root_path}")

    entries = []
    for path in sorted(root_path.rglob("*")):
        if not path.is_file():
            continue
        if path.name in excluded:
            continue
        entries.append(_relative_record(root_path, path).as_dict())

    return {
        "manifest_scope": "package files excluding manifest.json",
        "entry_count": len(entries),
        "entries": entries,
    }


def _zip_folder(folder: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(folder.parent).as_posix())


def package_lock(
    *,
    package_name: str,
    payload_files: Iterable[str | Path],
    output_dir: str | Path,
    lock_metadata: dict[str, Any],
    not_claimed: Iterable[str],
) -> dict[str, Any]:
    """Create a minimal SPIRA-style lock package.

    This primitive is intentionally narrow: it packages explicit files, writes
    not_claimed, writes a lock json, writes a manifest, creates a zip, creates
    an external sidecar, and verifies the result. It does not update an index.
    """
    boundaries = [str(item) for item in not_claimed if str(item).strip()]
    if not boundaries:
        raise GovernanceError("package_lock requires at least one not_claimed boundary")

    output_root = Path(output_dir)
    package_dir = output_root / package_name
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)

    source_paths = [Path(source) for source in payload_files]
    basenames = [source_path.name for source_path in source_paths]
    duplicate_basenames = sorted({name for name in basenames if basenames.count(name) > 1})
    if duplicate_basenames:
        raise GovernanceError(f"duplicate payload basenames are not allowed: {', '.join(duplicate_basenames)}")

    copied_payloads = []
    for source_path in source_paths:
        if not source_path.is_file():
            raise GovernanceError(f"payload file is missing: {source_path}")
        target = package_dir / source_path.name
        shutil.copy2(source_path, target)
        copied_payloads.append(target.name)

    lock_payload = dict(lock_metadata)
    lock_payload.setdefault("name", f"{package_name}_LOCK")
    lock_payload["payload_files"] = copied_payloads
    lock_payload["not_claimed"] = boundaries
    _write_json(package_dir / f"{package_name}_LOCK.json", lock_payload)
    _write_text(package_dir / "not_claimed.txt", "\n".join(boundaries) + "\n")

    manifest = build_manifest(package_dir)
    manifest["name"] = package_name
    _write_json(package_dir / "manifest.json", manifest)

    zip_path = output_root / f"{package_name}.zip"
    _zip_folder(package_dir, zip_path)
    zip_hash = hash_file(zip_path)["sha256"]
    sidecar_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    _write_text(sidecar_path, f"{zip_hash}  {zip_path.name}\n")

    verify = verify_package(zip_path, sidecar_path)
    post_lock_path = zip_path.with_suffix("").with_suffix(".POST_LOCK_VERIFY.json")
    _write_json(post_lock_path, verify)
    return {
        "package_dir": str(package_dir),
        "zip_path": str(zip_path),
        "zip_sha256": zip_hash,
        "sidecar_path": str(sidecar_path),
        "post_lock_verify_path": str(post_lock_path),
        "post_lock_pass": verify["post_lock_pass"],
    }


def _read_sidecar(sidecar_path: Path) -> str | None:
    if not sidecar_path.exists():
        return None
    parts = sidecar_path.read_text(encoding="utf-8").strip().split()
    return parts[0] if parts else None


def verify_package(zip_path: str | Path, sidecar_path: str | Path | None = None) -> dict[str, Any]:
    """Verify a SPIRA-style package zip against sidecar, manifest, and boundaries."""
    archive_path = Path(zip_path)
    sidecar = Path(sidecar_path) if sidecar_path is not None else archive_path.with_suffix(archive_path.suffix + ".sha256")
    archive_hash = hash_file(archive_path)["sha256"]
    sidecar_hash = _read_sidecar(sidecar)

    manifest_candidates: list[str] = []
    missing_entries: list[str] = []
    mismatched_entries: list[dict[str, str]] = []
    entry_count = 0
    not_claimed_present = False
    not_claimed_boundary_count = 0
    not_claimed_path: str | None = None

    with zipfile.ZipFile(archive_path) as archive:
        names = set(archive.namelist())
        manifest_candidates = [name for name in names if name.endswith("/manifest.json")]
        if len(manifest_candidates) != 1:
            return {
                "post_lock_pass": False,
                "zip_sha256": archive_hash,
                "sidecar_matches_zip": sidecar_hash == archive_hash,
                "manifest_found": len(manifest_candidates) == 1,
                "manifest_candidates": sorted(manifest_candidates),
                "missing_entries": [],
                "mismatched_entries": [],
                "not_claimed_present": False,
                "not_claimed_boundary_count": 0,
                "not_claimed_path": None,
            }
        manifest_name = manifest_candidates[0]
        package_prefix = manifest_name.rsplit("/", 1)[0] + "/"
        manifest = json.loads(archive.read(manifest_name).decode("utf-8"))
        for entry in manifest.get("entries", []):
            entry_count += 1
            archive_name = package_prefix + entry["file"]
            if archive_name not in names:
                missing_entries.append(entry["file"])
                continue
            data = archive.read(archive_name)
            digest = sha256(data).hexdigest()
            if digest != entry["sha256"] or len(data) != entry["bytes"]:
                mismatched_entries.append(
                    {
                        "file": entry["file"],
                        "expected_sha256": entry["sha256"],
                        "actual_sha256": digest,
                    }
                )
        claimed_boundary_name = package_prefix + "not_claimed.txt"
        if claimed_boundary_name in names:
            not_claimed_path = claimed_boundary_name
            not_claimed_text = archive.read(claimed_boundary_name).decode("utf-8")
            boundary_check = check_not_claimed(not_claimed_text)
            not_claimed_present = bool(boundary_check["pass"])
            not_claimed_boundary_count = int(boundary_check["boundary_count"])

    pass_status = (
        sidecar_hash == archive_hash
        and len(manifest_candidates) == 1
        and not missing_entries
        and not mismatched_entries
        and not_claimed_present
    )
    return {
        "post_lock_pass": pass_status,
        "zip_sha256": archive_hash,
        "sidecar_matches_zip": sidecar_hash == archive_hash,
        "manifest_found": len(manifest_candidates) == 1,
        "manifest_candidates": sorted(manifest_candidates),
        "entry_count": entry_count,
        "missing_entries": missing_entries,
        "mismatched_entries": mismatched_entries,
        "not_claimed_present": not_claimed_present,
        "not_claimed_boundary_count": not_claimed_boundary_count,
        "not_claimed_path": not_claimed_path,
    }


def verify_runtime_manifest(
    runtime_root: str | Path,
    manifest_path: str | Path,
    *,
    required_files: Iterable[str] = (),
) -> dict[str, Any]:
    """Verify a live runtime directory against an expected manifest.

    This is the launch gate between the governance engine and a runnable
    artifact. It verifies files on disk before a caller may start the runtime;
    it does not start the runtime by itself.
    """
    root_path = Path(runtime_root)
    manifest_file = Path(manifest_path)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    missing_entries: list[str] = []
    mismatched_entries: list[dict[str, str]] = []
    verified_entries: list[dict[str, Any]] = []

    if not root_path.is_dir():
        raise GovernanceError(f"runtime root is not a directory: {root_path}")

    entries = manifest.get("entries", [])
    expected_files = {entry["file"] for entry in entries}
    for required in required_files:
        if required not in expected_files:
            missing_entries.append(required)

    for entry in entries:
        relative_file = entry["file"]
        target = root_path / relative_file
        if not target.is_file():
            missing_entries.append(relative_file)
            continue
        actual = hash_file(target)
        if actual["sha256"] != entry["sha256"] or actual["bytes"] != entry["bytes"]:
            mismatched_entries.append(
                {
                    "file": relative_file,
                    "expected_sha256": entry["sha256"],
                    "actual_sha256": actual["sha256"],
                    "expected_bytes": str(entry["bytes"]),
                    "actual_bytes": str(actual["bytes"]),
                }
            )
            continue
        verified_entries.append(
            {
                "file": relative_file,
                "sha256": actual["sha256"],
                "bytes": actual["bytes"],
            }
        )

    pass_status = not missing_entries and not mismatched_entries
    return {
        "pass": pass_status,
        "runtime_root": str(root_path),
        "manifest_path": str(manifest_file),
        "manifest_sha256": hash_file(manifest_file)["sha256"],
        "entry_count": len(entries),
        "verified_count": len(verified_entries),
        "missing_entries": sorted(set(missing_entries)),
        "mismatched_entries": mismatched_entries,
        "required_files": list(required_files),
        "verified_entries": verified_entries,
    }


def verified_launch_attestation(
    runtime_root: str | Path,
    manifest_path: str | Path,
    *,
    required_files: Iterable[str] = (),
    launch_command: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Return an attestation for a runtime that passed governance verification."""
    verification = verify_runtime_manifest(runtime_root, manifest_path, required_files=required_files)
    if not verification["pass"]:
        raise GovernanceError("verified launch refused runtime with manifest mismatch")
    return {
        "verified_launch_allowed": True,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "verification": verification,
        "launch_command": list(launch_command) if launch_command is not None else None,
        "not_claimed": [
            "does not prove production readiness",
            "does not prove runtime behavior beyond manifest identity",
            "does not modify 015 decision logic",
        ],
    }


def launch_verified_runtime(
    runtime_root: str | Path,
    manifest_path: str | Path,
    *,
    required_files: Iterable[str] = (),
    command: Sequence[str],
    timeout_seconds: float | None = None,
    attestation_filename: str = ".spira_launch_attestation.json",
) -> dict[str, Any]:
    """Verify a runtime directory, then execute a command in that directory.

    The command is not started when verification fails. This is the operational
    launch gate; callers may pass a short-lived harness command or a long-lived
    server command.
    """
    if not command:
        raise GovernanceError("launch_verified_runtime requires a command")
    attestation = verified_launch_attestation(
        runtime_root,
        manifest_path,
        required_files=required_files,
        launch_command=command,
    )
    runtime_path = Path(runtime_root)
    attestation_path = runtime_path / attestation_filename
    _write_json(attestation_path, attestation)
    child_env = dict(os.environ)
    child_env["SPIRA_LAUNCH_ATTESTATION_PATH"] = str(attestation_path)
    completed = subprocess.run(
        list(command),
        cwd=runtime_path,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        env=child_env,
    )
    return {
        "verified_launch_allowed": True,
        "command_started_after_verification": True,
        "attestation": attestation,
        "attestation_path": str(attestation_path),
        "command": list(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def verify_references(references: Sequence[dict[str, Any]], *, root: str | Path = ".") -> dict[str, Any]:
    """Resolve path+sha references from disk and compare full SHA256 values."""
    root_path = Path(root)
    resolved: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    mismatches: list[dict[str, str]] = []

    for item in references:
        label = str(item.get("label", item.get("path", "<unlabeled>")))
        raw_path = item.get("path")
        expected = str(item.get("sha256", "")).lower()
        if not raw_path or not expected:
            missing.append({"label": label, "path": str(raw_path), "reason": "missing path or sha256"})
            continue
        target = Path(raw_path)
        if not target.is_absolute():
            target = root_path / target
        if not target.exists() or not target.is_file():
            missing.append({"label": label, "path": str(raw_path), "reason": "file not found"})
            continue
        actual = hash_file(target)["sha256"]
        if actual != expected:
            mismatches.append(
                {
                    "label": label,
                    "path": str(raw_path),
                    "expected_sha256": expected,
                    "actual_sha256": actual,
                }
            )
            continue
        resolved.append({"label": label, "path": str(raw_path), "sha256": actual})

    return {
        "all_resolved": not missing and not mismatches,
        "resolved_count": len(resolved),
        "missing_count": len(missing),
        "mismatch_count": len(mismatches),
        "resolved": resolved,
        "missing": missing,
        "mismatches": mismatches,
    }


def _boundary_lines(value: str | Path | Iterable[str]) -> list[str]:
    if isinstance(value, Path):
        raw = value.read_text(encoding="utf-8")
        lines = raw.splitlines()
    elif isinstance(value, str):
        possible_path = Path(value)
        if "\n" not in value and possible_path.exists() and possible_path.is_file():
            lines = possible_path.read_text(encoding="utf-8").splitlines()
        else:
            lines = value.splitlines()
    else:
        lines = [str(item) for item in value]
    return [line.strip() for line in lines if line.strip()]


def check_not_claimed(
    current: str | Path | Iterable[str],
    *,
    prior: str | Path | Iterable[str] | None = None,
) -> dict[str, Any]:
    """Check not_claimed presence and simple correction-overlay superset.

    A correction overlay is valid only if every prior boundary is still present.
    This exact-line rule is deliberately conservative; wording changes should be
    represented as a new explicit boundary, not silent weakening.
    """
    current_lines = _boundary_lines(current)
    present = bool(current_lines)
    result: dict[str, Any] = {
        "present": present,
        "boundary_count": len(current_lines),
        "boundaries": current_lines,
        "superset_checked": prior is not None,
    }
    if prior is None:
        result.update(
            {
                "superset_holds": None,
                "removed_or_weakened": [],
                "pass": present,
            }
        )
        return result

    prior_lines = _boundary_lines(prior)
    current_set = set(current_lines)
    removed = [line for line in prior_lines if line not in current_set]
    result.update(
        {
            "prior_boundary_count": len(prior_lines),
            "superset_holds": present and not removed,
            "removed_or_weakened": removed,
            "pass": present and not removed,
        }
    )
    return result


def _load_json_input(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return json.loads(Path(value).read_text(encoding="utf-8"))


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _json_input_identity(value: str | Path | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return {}
    path = Path(value)
    identity = {"path": str(path)}
    if path.exists() and path.is_file():
        identity["sha256"] = hash_file(path)["sha256"]
    return identity


def _registered_gate(gate_id: str) -> dict[str, str]:
    normalized = gate_id.lower().replace("_", "-")
    package_gate_root = Path(__file__).resolve().parent
    repo_gate_root = _project_root() / "tools"
    registry = {
        "permanent-field-preservation": (
            "PERMANENT_FIELD_PRESERVATION_GATE_001",
            repo_gate_root / "permanent_field_preservation_gate.py",
            package_gate_root / "permanent_field_preservation_gate.py",
        ),
        "permanent-field-preservation-gate-001": (
            "PERMANENT_FIELD_PRESERVATION_GATE_001",
            repo_gate_root / "permanent_field_preservation_gate.py",
            package_gate_root / "permanent_field_preservation_gate.py",
        ),
        "contradiction-condition-match": (
            "CONTRADICTION_CONDITION_MATCH_GATE_001",
            repo_gate_root / "condition_match_gate.py",
            package_gate_root / "condition_match_gate.py",
        ),
        "contradiction-condition-match-gate-001": (
            "CONTRADICTION_CONDITION_MATCH_GATE_001",
            repo_gate_root / "condition_match_gate.py",
            package_gate_root / "condition_match_gate.py",
        ),
    }
    if normalized not in registry:
        raise GovernanceError(f"unsupported gate: {gate_id}")
    gate_name, *candidates = registry[normalized]
    module_path = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
    if not module_path.is_file():
        raise GovernanceError(f"registered gate module is missing: {module_path}")
    return {
        "gate": gate_name,
        "module_path": str(module_path),
        "module_sha256": hash_file(module_path)["sha256"],
    }


def _json_arg_to_file(value: str | Path | dict[str, Any], temp_dir: Path, name: str) -> Path:
    if isinstance(value, dict):
        path = temp_dir / name
        _write_json(path, value)
        return path
    return Path(value)


def run_gate(
    gate_id: str,
    *,
    previous: str | Path | dict[str, Any],
    candidate: str | Path | dict[str, Any],
) -> dict[str, Any]:
    """Run a registered governance gate.

    The first registered gate is permanent-field preservation. The engine binds
    the gate to a module path and module SHA, then executes that module instead
    of silently reimplementing the gate inside this function.
    """
    gate = _registered_gate(gate_id)
    with tempfile.TemporaryDirectory() as temp:
        temp_dir = Path(temp)
        previous_path = _json_arg_to_file(previous, temp_dir, "previous.json")
        candidate_path = _json_arg_to_file(candidate, temp_dir, "candidate.json")
        out_path = temp_dir / "gate_report.json"
        completed = subprocess.run(
            [
                sys.executable,
                gate["module_path"],
                "--previous",
                str(previous_path),
                "--candidate",
                str(candidate_path),
                "--out",
                str(out_path),
            ],
            capture_output=True,
            text=True,
        )
        if completed.returncode not in (0, 2) or not out_path.exists():
            raise GovernanceError(
                "registered gate execution failed: "
                f"returncode={completed.returncode}; stderr={completed.stderr.strip()}"
            )
        report = json.loads(out_path.read_text(encoding="utf-8"))
    report["execution_mode"] = "registered_module_subprocess"
    report["gate_module_path"] = gate["module_path"]
    report["gate_module_sha256"] = gate["module_sha256"]
    report["gate_execution_returncode"] = completed.returncode
    return report


def append_index(
    previous_index: str | Path | dict[str, Any],
    new_references: Sequence[dict[str, Any]],
    *,
    root: str | Path = ".",
    version: str | None = None,
) -> dict[str, Any]:
    """Append references to an index document after verifying every reference.

    This command deliberately produces an index document, not a lock package.
    Packaging the result remains a separate package-lock operation.
    """
    previous = _load_json_input(previous_index)
    previous_identity = _json_input_identity(previous_index)
    previous_refs = list(previous.get("references", []))
    combined = previous_refs + list(new_references)
    reference_report = verify_references(combined, root=root)
    if not reference_report["all_resolved"]:
        raise GovernanceError("append-index refused unresolved or mismatched references")

    prior_version = str(previous.get("version", "0"))
    next_version = version
    if next_version is None:
        try:
            next_version = f"{int(prior_version) + 1:03d}"
        except ValueError:
            next_version = prior_version + "+1"

    supersedes = {
        "name": previous.get("name"),
        "version": previous.get("version"),
    }
    if previous_identity:
        supersedes.update(previous_identity)

    return {
        "name": f"SPIRA_MASTER_INDEX_{next_version}",
        "version": next_version,
        "supersedes": supersedes,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "nature": "full pointer index",
        "adds": [ref.get("label", ref.get("path")) for ref in new_references],
        "reference_count": len(combined),
        "all_references_resolved": True,
        "reference_mismatches": [],
        "references": combined,
    }
