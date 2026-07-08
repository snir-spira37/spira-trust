#!/usr/bin/env python3
"""Build the tampered-RECORD empirical fixture.

Creates two wheels:
  record_tampered-1.0.0-py3-none-any.whl        (RECORD mismatch, one byte changed)
  record_tampered_clean-1.0.0-py3-none-any.whl  (control, fully consistent)

The tampered wheel is a structurally valid ZIP whose RECORD no longer matches
the physical bytes of record_tampered/__init__.py. RECORD is intentionally
NOT updated after the mutation.
"""

import base64
import hashlib
import json
import sys
import zipfile
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
OUT.mkdir(parents=True, exist_ok=True)

NAME = "record_tampered"
VERSION = "1.0.0"
ORIG_INIT = b'"""record_tampered fixture package."""\nVALUE = 1\n'
# One-byte mutation: VALUE = 1 -> VALUE = 2
TAMPERED_INIT = ORIG_INIT.replace(b"VALUE = 1", b"VALUE = 2")
assert len(TAMPERED_INIT) == len(ORIG_INIT)

METADATA = (
    "Metadata-Version: 2.1\n"
    f"Name: {NAME}\n"
    f"Version: {VERSION}\n"
    "Summary: Empirical fixture: internal byte changed without updating RECORD.\n"
).encode()

WHEEL_META = (
    "Wheel-Version: 1.0\n"
    "Generator: spira-fixture-builder\n"
    "Root-Is-Purelib: true\n"
    "Tag: py3-none-any\n"
).encode()


def urlsafe_b64_sha256(data: bytes) -> str:
    digest = hashlib.sha256(data).digest()
    return "sha256=" + base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def build_wheel(path: Path, init_bytes_for_record: bytes, init_bytes_written: bytes) -> str:
    """Build a wheel where RECORD is computed over init_bytes_for_record but the
    archive physically contains init_bytes_written. Identical args = clean wheel."""
    dist_info = f"{NAME}-{VERSION}.dist-info"
    files = {
        f"{NAME}/__init__.py": (init_bytes_for_record, init_bytes_written),
        f"{dist_info}/METADATA": (METADATA, METADATA),
        f"{dist_info}/WHEEL": (WHEEL_META, WHEEL_META),
    }
    record_lines = []
    for arcname, (record_bytes, _written) in files.items():
        record_lines.append(
            f"{arcname},{urlsafe_b64_sha256(record_bytes)},{len(record_bytes)}"
        )
    record_lines.append(f"{dist_info}/RECORD,,")
    record = ("\n".join(record_lines) + "\n").encode()

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for arcname, (_record_bytes, written) in files.items():
            zf.writestr(arcname, written)
        zf.writestr(f"{dist_info}/RECORD", record)

    # Sanity: still a valid ZIP.
    with zipfile.ZipFile(path) as zf:
        assert zf.testzip() is None, "fixture wheel is not a valid ZIP"
    return hashlib.sha256(path.read_bytes()).hexdigest()


clean = OUT / f"{NAME}_clean-{VERSION}-py3-none-any.whl"
tampered = OUT / f"{NAME}-{VERSION}-py3-none-any.whl"

clean_sha = build_wheel(clean, ORIG_INIT, ORIG_INIT)
tampered_sha = build_wheel(tampered, ORIG_INIT, TAMPERED_INIT)

expected = {
    "fixture": "record_tampered",
    "mutation": "one byte in record_tampered/__init__.py (VALUE = 1 -> VALUE = 2), RECORD not updated",
    "clean_wheel": {"file": clean.name, "sha256": clean_sha, "expected_spira_verdict_prefix": "TRUST_OK"},
    "tampered_wheel": {"file": tampered.name, "sha256": tampered_sha, "expected_spira_verdict": "TRUST_BLOCK", "expected_exit_code": 1},
}
(OUT / "expected.json").write_text(json.dumps(expected, indent=2))
print(json.dumps(expected, indent=2))
