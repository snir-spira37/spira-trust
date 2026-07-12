from __future__ import annotations

import base64
import csv
import io
import json
import re
import shutil
import unicodedata
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.parser import Parser
from hashlib import sha256
from pathlib import Path
from zipfile import ZipInfo
from typing import Any

from .governance_engine import build_manifest, hash_file, package_lock, verify_package


STRUCTURED = "structured"
FREE_TEXT = "free_text"
PROBE = "pre_registered_probe"

VERIFIED_RAW = "VERIFIED_RAW"
VERIFIED_RUNTIME = "VERIFIED_RUNTIME"
CLAIMED_NOT_RAW_VERIFIABLE = "CLAIMED_NOT_RAW_VERIFIABLE"
CONTRADICTION = "CONTRADICTION"
NEEDS_HUMAN_JUDGMENT = "NEEDS_HUMAN_JUDGMENT"

MAX_ARCHIVE_MEMBERS = 10_000
MAX_ARCHIVE_FILE_BYTES = 50 * 1024 * 1024
MAX_ARCHIVE_TOTAL_BYTES = 250 * 1024 * 1024


@dataclass(frozen=True)
class ArtifactView:
    artifact_type: str
    source_path: Path
    work_root: Path
    archive_path: Path | None
    extracted_root: Path
    metadata_path: str | None
    metadata_text: str | None
    pyproject_path: Path | None
    readme_files: list[Path]


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _sha_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _safe_package_token(value: str) -> str:
    token = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    return token or "ARTIFACT"


def _urlsafe_b64_sha256(data: bytes) -> str:
    return base64.urlsafe_b64encode(sha256(data).digest()).decode("ascii").rstrip("=")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _is_zip_symlink(info: ZipInfo) -> bool:
    return ((info.external_attr >> 16) & 0o170000) == 0o120000


def _safe_archive_target(root: Path, member_name: str) -> Path:
    normalized = member_name.replace("\\", "/")
    parts = [part for part in normalized.split("/") if part not in {"", "."}]
    if not parts or any(part == ".." for part in parts):
        raise ValueError(f"unsafe archive path: {member_name}")
    if normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        raise ValueError(f"unsafe archive path: {member_name}")
    target = (root / Path(*parts)).resolve()
    root_resolved = root.resolve()
    if target != root_resolved and root_resolved not in target.parents:
        raise ValueError(f"unsafe archive path: {member_name}")
    return target


def _safe_extract_archive(
    archive: zipfile.ZipFile,
    destination: Path,
    *,
    max_members: int = MAX_ARCHIVE_MEMBERS,
    max_file_bytes: int = MAX_ARCHIVE_FILE_BYTES,
    max_total_bytes: int = MAX_ARCHIVE_TOTAL_BYTES,
) -> dict[str, Any]:
    infos = archive.infolist()
    if len(infos) > max_members:
        raise ValueError(f"archive member count exceeds limit: {len(infos)} > {max_members}")

    total_bytes = 0
    extracted_files = 0
    for info in infos:
        if _is_zip_symlink(info):
            raise ValueError(f"unsafe archive symlink: {info.filename}")
        target = _safe_archive_target(destination, info.filename)
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if info.file_size > max_file_bytes:
            raise ValueError(f"archive member exceeds file size limit: {info.filename}")
        total_bytes += info.file_size
        if total_bytes > max_total_bytes:
            raise ValueError(f"archive extracted bytes exceed limit: {total_bytes} > {max_total_bytes}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info, "r") as source, target.open("wb") as dest:
            shutil.copyfileobj(source, dest)
        extracted_files += 1

    return {
        "members": len(infos),
        "files": extracted_files,
        "total_uncompressed_bytes": total_bytes,
        "max_members": max_members,
        "max_file_bytes": max_file_bytes,
        "max_total_bytes": max_total_bytes,
    }


def _extract_artifact(path: Path, work_root: Path) -> ArtifactView:
    if not path.exists():
        raise FileNotFoundError(path)
    extracted = work_root / "extracted"
    extracted.mkdir(parents=True, exist_ok=True)
    archive_copy: Path | None = None
    if path.is_dir():
        shutil.copytree(path, extracted, dirs_exist_ok=True)
        artifact_type = "folder"
    elif zipfile.is_zipfile(path):
        archive_copy = work_root / path.name
        shutil.copy2(path, archive_copy)
        with zipfile.ZipFile(path) as archive:
            _safe_extract_archive(archive, extracted)
        artifact_type = "wheel" if path.suffix == ".whl" else "zip"
    else:
        raise ValueError(f"unsupported artifact type: {path}")

    metadata_candidates = sorted(extracted.rglob("*.dist-info/METADATA"))
    metadata_file = metadata_candidates[0] if metadata_candidates else None
    pyproject = extracted / "pyproject.toml"
    readmes = sorted(
        p
        for p in extracted.rglob("*")
        if p.is_file() and p.name.lower() in {"readme", "readme.md", "readme.rst", "readme.txt"}
    )
    return ArtifactView(
        artifact_type=artifact_type,
        source_path=path,
        work_root=work_root,
        archive_path=archive_copy,
        extracted_root=extracted,
        metadata_path=str(metadata_file.relative_to(extracted).as_posix()) if metadata_file else None,
        metadata_text=_read_text(metadata_file) if metadata_file else None,
        pyproject_path=pyproject if pyproject.is_file() else None,
        readme_files=readmes,
    )


def _metadata_message(metadata_text: str | None):
    if not metadata_text:
        return None
    return Parser().parsestr(metadata_text)


def _metadata_values(message: Any, key: str) -> list[str]:
    if message is None:
        return []
    return list(message.get_all(key, []))


def _development_status_classifiers(classifiers: list[str]) -> list[str]:
    return [item for item in classifiers if item.startswith("Development Status ::")]


def _record_verify(view: ArtifactView) -> dict[str, Any] | None:
    if view.archive_path is None:
        return None
    with zipfile.ZipFile(view.archive_path) as archive:
        archive_names = [info.filename for info in archive.infolist() if not info.is_dir()]
        archive_name_set = set(archive_names)
        duplicate_archive_names = sorted({name for name in archive_names if archive_names.count(name) > 1})
        record_names = [name for name in archive_names if name.endswith(".dist-info/RECORD")]
        if not record_names:
            return None
        record_name = record_names[0]
        rows = list(csv.reader(io.StringIO(archive.read(record_name).decode("utf-8"))))
        mismatches = []
        missing_files = []
        unhashed_files = []
        malformed_rows = []
        checked = 0
        skipped_empty_hash = 0
        recorded_names = []
        for row in rows:
            if len(row) < 3:
                malformed_rows.append(row)
                continue
            filename, hash_spec, size_spec = row[0], row[1], row[2]
            recorded_names.append(filename)
            if filename not in archive_name_set:
                missing_files.append(filename)
                continue
            if not hash_spec:
                skipped_empty_hash += 1
                if filename != record_name:
                    unhashed_files.append(filename)
                continue
            data = archive.read(filename)
            checked += 1
            algo, _, expected = hash_spec.partition("=")
            actual = _urlsafe_b64_sha256(data) if algo == "sha256" else None
            if actual != expected or (size_spec and int(size_spec) != len(data)):
                mismatches.append({"file": filename, "expected_hash": hash_spec, "actual_sha256_b64": actual})
        recorded_name_set = set(recorded_names)
        undocumented_files = sorted(archive_name_set - recorded_name_set)
        non_ascii_paths = sorted(
            name for name in archive_name_set | recorded_name_set if any(ord(char) > 127 for char in name)
        )
        nfkc_collisions = _nfkc_path_collisions(archive_name_set | recorded_name_set)
        return {
            "record_file": record_name,
            "record_rows": len(rows),
            "archive_files": len(archive_name_set),
            "recorded_files": len(recorded_name_set),
            "checked_hashes": checked,
            "skipped_empty_hash": skipped_empty_hash,
            "record_entry_present": record_name in recorded_name_set,
            "missing_files": missing_files,
            "undocumented_files": undocumented_files,
            "unhashed_files": unhashed_files,
            "malformed_rows": malformed_rows,
            "duplicate_archive_names": duplicate_archive_names,
            "non_ascii_paths": non_ascii_paths,
            "nfkc_collisions": nfkc_collisions,
            "path_comparison": "strict_exact_unicode_string_no_confusable_folding",
            "mismatches": mismatches,
            "pass": (
                record_name in recorded_name_set
                and not missing_files
                and not undocumented_files
                and not unhashed_files
                and not malformed_rows
                and not duplicate_archive_names
                and not mismatches
            ),
        }


def _nfkc_path_collisions(names: set[str]) -> list[dict[str, Any]]:
    buckets: dict[str, list[str]] = {}
    for name in names:
        normalized = unicodedata.normalize("NFKC", name)
        buckets.setdefault(normalized, []).append(name)
    return [
        {"nfkc": normalized, "paths": sorted(paths)}
        for normalized, paths in sorted(buckets.items())
        if len(set(paths)) > 1
    ]


def _structured_claims(view: ArtifactView) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    message = _metadata_message(view.metadata_text)
    if view.artifact_type in {"zip", "folder"} and view.metadata_path is None and view.pyproject_path is None:
        claims.append(
            {
                "claim": "Artifact contains recognized Python package metadata",
                "source": STRUCTURED,
                "verdict": CONTRADICTION,
                "gap_type": "unsupported_package_structure",
                "evidence": {
                    "artifact_type": view.artifact_type,
                    "metadata_file": None,
                    "pyproject_file": None,
                    "boundary": "generic archives are not approved as trusted Python packages without recognized metadata",
                },
            }
        )
    if view.artifact_type == "wheel" and view.metadata_path is None:
        claims.append(
            {
                "claim": "Wheel METADATA file is present",
                "source": STRUCTURED,
                "verdict": CONTRADICTION,
                "gap_type": "wheel_metadata_missing",
                "evidence": {"metadata_file": None, "artifact_type": view.artifact_type},
            }
        )
    name = message.get("Name") if message is not None else None
    version = message.get("Version") if message is not None else None
    if name or version:
        claims.append(
            {
                "claim": "METADATA declares package identity",
                "source": STRUCTURED,
                "verdict": VERIFIED_RAW,
                "evidence": {"Name": name, "Version": version, "metadata_file": view.metadata_path},
            }
        )
    requires_dist = _metadata_values(message, "Requires-Dist")
    if message is not None:
        claims.append(
            {
                "claim": "METADATA Requires-Dist entries",
                "source": STRUCTURED,
                "verdict": VERIFIED_RAW,
                "evidence": {"Requires-Dist": requires_dist, "metadata_file": view.metadata_path},
            }
        )
    requires_python = message.get("Requires-Python") if message is not None else None
    if requires_python:
        claims.append(
            {
                "claim": "METADATA Requires-Python entry",
                "source": STRUCTURED,
                "verdict": VERIFIED_RAW,
                "evidence": {"Requires-Python": requires_python, "metadata_file": view.metadata_path},
            }
        )
    classifiers = _metadata_values(message, "Classifier")
    dev_status = _development_status_classifiers(classifiers)
    for classifier in dev_status:
        claims.append(
            {
                "claim": classifier,
                "source": STRUCTURED,
                "verdict": CLAIMED_NOT_RAW_VERIFIABLE,
                "gap_type": "metadata_classifier_not_raw_proof",
                "evidence": {"Classifier": classifier, "metadata_file": view.metadata_path},
            }
        )
    record = _record_verify(view)
    if record is None and view.artifact_type == "wheel":
        claims.append(
            {
                "claim": "Wheel RECORD file is present",
                "source": STRUCTURED,
                "verdict": CONTRADICTION,
                "gap_type": "wheel_record_missing",
                "evidence": {"record_file": None, "artifact_type": view.artifact_type},
            }
        )
    elif record is not None:
        claims.append(
            {
                "claim": "Wheel RECORD hashes match archive contents",
                "source": STRUCTURED,
                "verdict": VERIFIED_RAW if record["pass"] else CONTRADICTION,
                "evidence": record,
            }
        )
    return claims


def _free_text_surfaces(view: ArtifactView) -> list[dict[str, Any]]:
    surfaces = []
    if view.metadata_text:
        message = _metadata_message(view.metadata_text)
        payload = message.get_payload() if message is not None else ""
        if isinstance(payload, str) and payload.strip():
            surfaces.append(
                {
                    "source": FREE_TEXT,
                    "path": view.metadata_path,
                    "verdict": NEEDS_HUMAN_JUDGMENT,
                    "excerpt": payload[:4000],
                    "boundary": "free-text description surfaced, not auto-classified",
                }
            )
    for readme in view.readme_files:
        surfaces.append(
            {
                "source": FREE_TEXT,
                "path": readme.relative_to(view.extracted_root).as_posix(),
                "verdict": NEEDS_HUMAN_JUDGMENT,
                "excerpt": _read_text(readme)[:4000],
                "boundary": "README prose surfaced, not auto-classified",
            }
        )
    return surfaces


def _iniconfig_probe(view: ArtifactView) -> dict[str, Any] | None:
    message = _metadata_message(view.metadata_text)
    if message is None or message.get("Name") != "iniconfig" or message.get("Version") != "2.3.0":
        return None
    original_conditions = (
        "# content of example.ini\n"
        "[section1] # comment\n"
        "name1=value1  # comment\n"
        "name1b=value1,value2  # comment\n"
        "\n"
        "[section2]\n"
        "name2=\n"
        "    line1\n"
        "    line2\n"
    )
    expected = {
        "section_order": ["section1", "section2"],
        "name1_value": "value1",
        "name1b_split": ["value1", "value2"],
        "items_section1": [["name1", "value1"], ["name1b", "value1,value2"]],
    }
    return {
        "claim": "Pre-registered iniconfig Basic Example runtime behavior matches documented values",
        "source": PROBE,
        "verdict": CLAIMED_NOT_RAW_VERIFIABLE,
        "gap_type": "runtime_probe_disabled_no_foreign_code_execution",
        "evidence": {
            "pre_registered_probe": "iniconfig_2_3_0_basic_example_inline_comment",
            "runtime_probe_enabled": False,
            "runtime_probe_disabled_reason": "SPIRA trust v1 does not import or execute code from the artifact under review",
            "original_conditions": original_conditions,
            "expected": expected,
            "actual": None,
            "condition_gate": None,
            "not_claimed": [
                "does not verify iniconfig runtime behavior in static-only trust v1",
                "does not import the reviewed artifact to prove or disprove this claim",
                "does not preserve the prior runtime contradiction claim until sandboxed probes exist",
            ],
        },
    }


def _pre_registered_probes(view: ArtifactView) -> list[dict[str, Any]]:
    probe = _iniconfig_probe(view)
    return [probe] if probe else []


def _failure_report(
    *,
    source: Path,
    run_root: Path,
    output_root: Path,
    package: bool,
    error: Exception,
) -> dict[str, Any]:
    artifact_hash = hash_file(source) if source.is_file() else None
    manifest = {
        "verdict": "ARTIFACT_EXTRACTION_BLOCKED",
        "root": str(run_root.resolve()),
        "entries": [],
        "error_type": type(error).__name__,
        "error": str(error),
    }
    claims = [
        {
            "claim": "Artifact can be safely extracted for review",
            "source": STRUCTURED,
            "verdict": CONTRADICTION,
            "gap_type": "artifact_extraction_blocked",
            "evidence": {
                "error_type": type(error).__name__,
                "error": str(error),
                "safety_boundary": "unsafe or unsupported artifact is reported as BLOCK evidence, not traceback",
            },
        }
    ]
    report = {
        "name": "SPIRA_FOREIGN_ARTIFACT_REVIEW_CLI_001_RUN",
        "created_at_utc": _utc(),
        "artifact": {
            "path": str(source),
            "type": "blocked_before_extraction",
            "sha256": artifact_hash["sha256"] if artifact_hash else None,
            "bytes": artifact_hash["bytes"] if artifact_hash else None,
        },
        "discipline": {
            "structured_extraction_only": True,
            "free_text_auto_classification": False,
            "free_text_verdict": NEEDS_HUMAN_JUDGMENT,
            "condition_match_gate_for_contradictions": True,
            "unsafe_archive_errors_are_reported": True,
        },
        "manifest": manifest,
        "claims": claims,
        "free_text_surfaces": [],
        "verdict_counts": {CONTRADICTION: 1, NEEDS_HUMAN_JUDGMENT: 0},
        "overall_verdict": "CONTRADICTION_FOUND",
        "not_claimed": [
            "extracts structured metadata claims only",
            "surfaces free text for human judgment; does not auto-classify README prose",
            "does not claim complete claim extraction",
            "does not prove production readiness",
            "does not act as an AI auditor",
            "one artifact review only; not a general ecosystem claim",
            "does not close E",
            "unsafe or unsupported artifacts are blocked before extraction",
        ],
    }
    report_path = run_root / "foreign_artifact_review_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest_path = run_root / "artifact_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if package:
        package_result = package_lock(
            package_name=f"SPIRA_FOREIGN_ARTIFACT_REVIEW_CLI_001_{_safe_package_token(source.stem)}_BASELINE",
            payload_files=[report_path, manifest_path],
            output_dir=output_root,
            lock_metadata={
                "nature": "foreign artifact review CLI v1 blocked run",
                "artifact_path": str(source),
                "overall_verdict": report["overall_verdict"],
            },
            not_claimed=report["not_claimed"],
        )
        report["package_lock"] = package_result
        report["package_verify"] = verify_package(package_result["zip_path"], package_result["sidecar_path"])
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report


def review_artifact(artifact_path: str | Path, output_dir: str | Path, *, package: bool = True) -> dict[str, Any]:
    source = Path(artifact_path).resolve()
    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    run_root = output_root / f"review_{source.stem}"
    if run_root.exists():
        shutil.rmtree(run_root)
    run_root.mkdir(parents=True, exist_ok=True)
    try:
        view = _extract_artifact(source, run_root)
    except (ValueError, zipfile.BadZipFile, OSError) as exc:
        return _failure_report(source=source, run_root=run_root, output_root=output_root, package=package, error=exc)

    try:
        artifact_hash = hash_file(source) if source.is_file() else None
        manifest = build_manifest(view.extracted_root)
        structured_claims = _structured_claims(view)
        free_text = _free_text_surfaces(view)
        probe_claims = _pre_registered_probes(view)
    except (OSError, ValueError) as exc:
        return _failure_report(source=source, run_root=run_root, output_root=output_root, package=package, error=exc)
    claims = structured_claims + probe_claims
    verdict_counts: dict[str, int] = {}
    for claim in claims:
        verdict_counts[claim["verdict"]] = verdict_counts.get(claim["verdict"], 0) + 1
    verdict_counts[NEEDS_HUMAN_JUDGMENT] = len(free_text)
    report = {
        "name": "SPIRA_FOREIGN_ARTIFACT_REVIEW_CLI_001_RUN",
        "created_at_utc": _utc(),
        "artifact": {
            "path": str(source),
            "type": view.artifact_type,
            "sha256": artifact_hash["sha256"] if artifact_hash else None,
            "bytes": artifact_hash["bytes"] if artifact_hash else None,
        },
        "discipline": {
            "structured_extraction_only": True,
            "free_text_auto_classification": False,
            "free_text_verdict": NEEDS_HUMAN_JUDGMENT,
            "condition_match_gate_for_contradictions": True,
        },
        "manifest": manifest,
        "claims": claims,
        "free_text_surfaces": free_text,
        "verdict_counts": verdict_counts,
        "overall_verdict": "CONTRADICTION_FOUND" if verdict_counts.get(CONTRADICTION, 0) else "NO_CONTRADICTION_FOUND",
        "not_claimed": [
            "extracts structured metadata claims only",
            "surfaces free text for human judgment; does not auto-classify README prose",
            "does not claim complete claim extraction",
            "does not prove production readiness",
            "does not act as an AI auditor",
            "one artifact review only; not a general ecosystem claim",
            "does not close E",
        ],
    }
    report_path = run_root / "foreign_artifact_review_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest_path = run_root / "artifact_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if package:
        package_result = package_lock(
            package_name=f"SPIRA_FOREIGN_ARTIFACT_REVIEW_CLI_001_{_safe_package_token(source.stem)}_BASELINE",
            payload_files=[report_path, manifest_path],
            output_dir=output_root,
            lock_metadata={
                "nature": "foreign artifact review CLI v1 run",
                "artifact_path": str(source),
                "overall_verdict": report["overall_verdict"],
            },
            not_claimed=report["not_claimed"],
        )
        report["package_lock"] = package_result
        report["package_verify"] = verify_package(package_result["zip_path"], package_result["sidecar_path"])
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report
