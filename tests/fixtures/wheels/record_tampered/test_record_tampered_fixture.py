"""Acceptance tests for the tampered-RECORD empirical fixture.

Unit tier: SPIRA verdicts only. pip/uv empirical measurements live in the
integration/smoke tier (see installer_record_behavior.md) so this test has no
dependency on installer availability.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

FIXTURES = Path(__file__).parent
REPO_ROOT = FIXTURES.parents[3]
SOURCE_ROOT = REPO_ROOT / "source"
TAMPERED = FIXTURES / "record_tampered-1.0.0-py3-none-any.whl"
CLEAN = FIXTURES / "record_tampered_clean-1.0.0-py3-none-any.whl"


def run_spira_trust(*args):
    env = dict(os.environ)
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(SOURCE_ROOT) if not existing else str(SOURCE_ROOT) + os.pathsep + existing
    return subprocess.run(
        [sys.executable, "-m", "spira_core.trust_cli", *args],
        capture_output=True,
        text=True,
        env=env,
    )


def ensure_fixtures():
    if not TAMPERED.exists() or not CLEAN.exists():
        subprocess.run(
            [sys.executable, str(FIXTURES / "build_record_tampered_fixture.py"), str(FIXTURES)],
            check=True,
        )


def test_fixture_wheels_match_pinned_hashes():
    ensure_fixtures()
    import hashlib
    expected = json.loads((FIXTURES / "expected.json").read_text())
    assert hashlib.sha256(TAMPERED.read_bytes()).hexdigest() == expected["tampered_wheel"]["sha256"]
    assert hashlib.sha256(CLEAN.read_bytes()).hexdigest() == expected["clean_wheel"]["sha256"]


def test_spira_blocks_record_tampered_wheel(tmp_path):
    ensure_fixtures()
    result = run_spira_trust("trust", str(TAMPERED), "--output-dir", str(tmp_path))

    assert result.returncode == 1, result.stdout + result.stderr
    combined = result.stdout + result.stderr
    assert "TRUST_BLOCK" in combined
    assert "record_tampered/__init__.py" in combined  # exact evidence surfaced

    report = tmp_path / "artifact_trust_report.json"
    assert report.exists()


def test_spira_passes_clean_control_wheel(tmp_path):
    ensure_fixtures()
    result = run_spira_trust("trust", str(CLEAN), "--output-dir", str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "TRUST_OK" in (result.stdout + result.stderr)
