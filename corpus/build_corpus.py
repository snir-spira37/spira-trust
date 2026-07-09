#!/usr/bin/env python3
"""Build generated SPIRA conformance corpus artifacts."""

from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path


def record_hash(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return f"sha256={encoded}"


def record_row(path: str, data: bytes) -> list[str]:
    return [path, record_hash(data), str(len(data))]


def build_record_mismatch(out_dir: Path) -> Path:
    case_dir = out_dir / "record_mismatch"
    case_dir.mkdir(parents=True, exist_ok=True)

    wheel_name = "record_mismatch_pkg-1.0.0-py3-none-any.whl"
    wheel_path = case_dir / wheel_name

    package_path = "record_mismatch_pkg/__init__.py"
    dist_info = "record_mismatch_pkg-1.0.0.dist-info"

    clean_package = b'VALUE = "clean"\n'
    tampered_package = b'VALUE = "tampered"\n'

    files: dict[str, bytes] = {
        package_path: tampered_package,
        f"{dist_info}/METADATA": (
            b"Metadata-Version: 2.1\n"
            b"Name: record-mismatch-pkg\n"
            b"Version: 1.0.0\n"
        ),
        f"{dist_info}/WHEEL": (
            b"Wheel-Version: 1.0\n"
            b"Generator: spira-corpus\n"
            b"Root-Is-Purelib: true\n"
            b"Tag: py3-none-any\n"
        ),
    }

    rows: list[list[str]] = []

    # Intentional mismatch: RECORD stores the digest for clean_package,
    # while the wheel contains tampered_package.
    rows.append(record_row(package_path, clean_package))

    for path in sorted(p for p in files if p != package_path):
        rows.append(record_row(path, files[path]))

    rows.append([f"{dist_info}/RECORD", "", ""])

    record_buffer = io.StringIO()
    writer = csv.writer(record_buffer, lineterminator="\n")
    writer.writerows(rows)
    files[f"{dist_info}/RECORD"] = record_buffer.getvalue().encode("utf-8")

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.writestr(path, files[path])

    case = {
        "schema": "SPIRA_CONFORMANCE_CASE_V1",
        "case": "record_mismatch",
        "artifact": wheel_name,
        "expected": {
            "trust_verdict": "TRUST_BLOCK",
            "graph_verdict": "GRAPH_BLOCK",
            "finding_codes": ["RECORD_MISMATCH"],
        },
        "what_is_claimed": [
            "The wheel contains a RECORD digest that contradicts the local wheel bytes"
        ],
        "what_is_not_claimed": [
            "This does not simulate malware",
            "This does not test provenance",
            "This does not test dependency resolution",
            "This does not prove that all RECORD mismatch variants are detected",
        ],
    }
    (case_dir / "case.json").write_text(
        json.dumps(case, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    return wheel_path


def main() -> int:
    out_dir = Path("tmp/corpus")
    wheel = build_record_mismatch(out_dir)
    print(wheel.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
