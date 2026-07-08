#!/usr/bin/env python3
"""Build the slim public spira-trust wheel.

This intentionally avoids setuptools package discovery. The public pilot wheel
is assembled from an explicit allowlist so internal workspace modules cannot
leak into the distribution by accident.
"""

from __future__ import annotations

import base64
import hashlib
import json
import shutil
import sys
import zipfile
from email.message import Message
from pathlib import Path


PROJECT = "spira-trust"
VERSION = "0.5.8"
DIST_INFO = f"spira_trust-{VERSION}.dist-info"
WHEEL_NAME = f"spira_trust-{VERSION}-py3-none-any.whl"
DETERMINISTIC_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

PUBLIC_FILES = [
    "spira_core/__init__.py",
    "spira_core/adapters.py",
    "spira_core/attestation_verify.py",
    "spira_core/bom.py",
    "spira_core/combined_verdict.py",
    "spira_core/contracts.py",
    "spira_core/core.py",
    "spira_core/cyclonedx_export.py",
    "spira_core/decision_report.py",
    "spira_core/drift.py",
    "spira_core/entry_points_policy.py",
    "spira_core/governance_engine.py",
    "spira_core/ledger.py",
    "spira_core/license_policy.py",
    "spira_core/lockfile_policy.py",
    "spira_core/policy_pack.py",
    "spira_core/range_parser.py",
    "spira_core/rebaseline.py",
    "spira_core/review.py",
    "spira_core/sbom_consistency.py",
    "spira_core/target_environment.py",
    "spira_core/trust.py",
    "spira_core/trust_cli.py",
    "spira_core/trust_graph.py",
    "spira_core/decision015/__init__.py",
    "spira_core/decision015/contract.py",
    "spira_core/decision015/core.py",
    "spira_core/decision015/service.py",
]

PUBLIC_DIRS = [
    "spira_core/vendored_stone015",
]

PUBLIC_DATA_FILES = [
    ("schemas/spira_decision_v1.json", "schemas/spira_decision_v1.json"),
]

BANNED_FRAGMENTS = (
    "spira_v10",
    "spira_unified",
    "spira_system_shell",
    "spira_omega_controller",
    "spira_stone2_launch_authority",
    "spira_core/server",
    "spira_core/stone2",
    "spira_core/system",
    "spira_core/unified",
    "spira_core/full_runtime",
)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    repo = Path.cwd()
    out_dir = Path(args[0]) if args else repo / "dist" / "_wheel_build_030_003_public"
    src_root = repo / "source"
    stage = out_dir / "stage"
    wheelhouse = out_dir / "wheelhouse"
    if stage.exists():
        shutil.rmtree(stage)
    if wheelhouse.exists():
        shutil.rmtree(wheelhouse)
    stage.mkdir(parents=True)
    wheelhouse.mkdir(parents=True)

    for rel in PUBLIC_FILES:
        src = src_root / rel
        if not src.is_file():
            raise FileNotFoundError(src)
        dst = stage / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    for rel in PUBLIC_DIRS:
        src = src_root / rel
        if not src.is_dir():
            raise FileNotFoundError(src)
        for path in src.rglob("*.py"):
            dst = stage / path.relative_to(src_root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)
    for src_rel, dst_rel in PUBLIC_DATA_FILES:
        src = repo / src_rel
        if not src.is_file():
            raise FileNotFoundError(src)
        dst = stage / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    _write_dist_info(stage)
    wheel_path = wheelhouse / WHEEL_NAME
    _write_wheel(stage, wheel_path)
    _assert_public_boundary(wheel_path)
    print(wheel_path)
    print(hashlib.sha256(wheel_path.read_bytes()).hexdigest())
    return 0


def _write_dist_info(stage: Path) -> None:
    repo = Path.cwd()
    dist = stage / DIST_INFO
    dist.mkdir(parents=True, exist_ok=True)
    msg = Message()
    msg["Metadata-Version"] = "2.1"
    msg["Name"] = PROJECT
    msg["Version"] = VERSION
    msg["Summary"] = "Offline verifier for Python wheel evidence before install."
    msg["Requires-Python"] = ">=3.10"
    msg["License"] = "Apache-2.0"
    msg["License-File"] = "LICENSE"
    msg["Description-Content-Type"] = "text/markdown"
    msg["Project-URL"] = "Homepage, https://github.com/snir-spira37/spira-trust"
    msg["Project-URL"] = "Repository, https://github.com/snir-spira37/spira-trust"
    msg["Project-URL"] = "Issues, https://github.com/snir-spira37/spira-trust/issues"
    msg["Project-URL"] = "Documentation, https://github.com/snir-spira37/spira-trust/tree/main/docs"
    readme = (repo / "README.md").read_text(encoding="utf-8")
    (dist / "METADATA").write_text(msg.as_string() + "\n" + readme, encoding="utf-8", newline="\n")
    license_path = repo / "LICENSE"
    if not license_path.is_file():
        raise FileNotFoundError(license_path)
    (dist / "LICENSE").write_text(license_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (dist / "WHEEL").write_text(
        "Wheel-Version: 1.0\n"
        "Generator: spira-public-wheel-builder\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n",
        encoding="utf-8",
        newline="\n",
    )
    (dist / "entry_points.txt").write_text(
        "[console_scripts]\n"
        "spira-trust = spira_core.trust_cli:main\n"
        "spira = spira_core.trust_cli:main\n",
        encoding="utf-8",
        newline="\n",
    )
    sbom_path = dist / "sboms" / "spira-trust.cdx.json"
    sbom_path.parent.mkdir(parents=True, exist_ok=True)
    sbom_path.write_text(
        json.dumps(_embedded_cyclonedx_sbom(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _embedded_cyclonedx_sbom() -> dict[str, object]:
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{hashlib.sha256(f'{PROJECT}:{VERSION}:embedded-sbom'.encode('utf-8')).hexdigest()[:32]}",
        "version": 1,
        "metadata": {
            "timestamp": "2026-07-08T00:00:00Z",
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "SPIRA public wheel builder",
                        "version": VERSION,
                    }
                ]
            },
            "component": {
                "type": "application",
                "name": PROJECT,
                "version": VERSION,
                "purl": f"pkg:pypi/{PROJECT}@{VERSION}",
            },
        },
        "components": [
            {
                "type": "library",
                "name": PROJECT,
                "version": VERSION,
                "purl": f"pkg:pypi/{PROJECT}@{VERSION}",
            }
        ],
        "properties": [
            {"name": "spira:embedded-sbom:claim", "value": "release artifact self-description"},
            {"name": "spira:not_claimed", "value": "embedded SBOM is checked for local consistency, not treated as authoritative trust evidence"},
        ],
    }


def _write_wheel(stage: Path, wheel_path: Path) -> None:
    files = sorted(
        (path for path in stage.rglob("*") if path.is_file() and path.name != "RECORD"),
        key=lambda path: path.relative_to(stage).as_posix(),
    )
    record_lines = []
    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_STORED) as zf:
        for path in files:
            rel = path.relative_to(stage).as_posix()
            data = _read_deterministic_payload(path)
            _write_zip_member(zf, rel, data)
            record_lines.append(f"{rel},{_record_hash(data)},{len(data)}")
        record_name = f"{DIST_INFO}/RECORD"
        record_lines.append(f"{record_name},,")
        _write_zip_member(zf, record_name, ("\n".join(record_lines) + "\n").encode("utf-8"))


def _read_deterministic_payload(path: Path) -> bytes:
    data = path.read_bytes()
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return data
    text = data.decode("utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def _write_zip_member(zf: zipfile.ZipFile, rel: str, data: bytes) -> None:
    info = zipfile.ZipInfo(rel, date_time=DETERMINISTIC_ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_STORED
    info.create_system = 3
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def _record_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _assert_public_boundary(wheel_path: Path) -> None:
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
    bad = [name for name in names if any(fragment in name for fragment in BANNED_FRAGMENTS)]
    if bad:
        raise RuntimeError("public wheel contains banned internal paths: " + ", ".join(bad))
    entry_points = [name for name in names if name.endswith("entry_points.txt")]
    if len(entry_points) != 1:
        raise RuntimeError("public wheel must contain one entry_points.txt")
    with zipfile.ZipFile(wheel_path) as zf:
        text = zf.read(entry_points[0]).decode("utf-8")
    allowed = {
        "[console_scripts]",
        "spira-trust = spira_core.trust_cli:main",
        "spira = spira_core.trust_cli:main",
    }
    actual = {line.strip() for line in text.splitlines() if line.strip()}
    if actual != allowed:
        raise RuntimeError(f"unexpected public entry points: {sorted(actual)}")


if __name__ == "__main__":
    raise SystemExit(main())
