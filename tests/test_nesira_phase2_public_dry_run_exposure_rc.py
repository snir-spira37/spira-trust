from __future__ import annotations

import json
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.7.4"
DRY_RUN_MODULE = "spira_core/nesira_phase2_dry_run_runner.py"
INTERNAL_TOOL = "tools/run_nesira_phase2_dry_run_review.py"


def test_public_dry_run_rc_wheel_contains_library_module_only(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    names, metadata, entry_points = _wheel_payload(wheel_path)

    assert wheel_path.name == f"spira_trust-{VERSION}-py3-none-any.whl"
    assert f"Version: {VERSION}" in metadata
    assert DRY_RUN_MODULE in names
    assert INTERNAL_TOOL not in names
    assert all(not name.startswith("tests/") for name in names)
    assert all(not name.startswith("research/") for name in names)
    assert all("_harness.py" not in name for name in names)
    assert "spira-trust = spira_core.trust_cli:main" in entry_points
    assert "spira = spira_core.trust_cli:main" in entry_points
    assert "dry" not in entry_points.lower()
    assert "runner" not in metadata.lower()
    assert "executes" not in metadata.lower()


def test_public_dry_run_rc_installed_wheel_evaluates_without_execution_fields(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    python = _install_wheel_in_venv(tmp_path, wheel_path)

    code = r"""
import json
from spira_core import nesira_phase2_dry_run_runner as dry_run

context = {
    "action_class": "review-only-transition",
    "subject_context": "subject:artifact-set-1",
    "environment_context": "env:staging",
    "action_authority_root_id": "action-root-main",
}
combined = {
    "combined_verdict": "GRAPH_OK",
    "winning_status": "OK",
    "not_evaluated_layers": [],
}
nesira = {
    "verdict": dry_run.NESIRA_VERDICT_SUFFICIENT,
    "assumptions": ["PT-CRYPTO-01", "PT-ISOLATION-01", "PT-META-01"],
    "per_domain_breakdown": {"isolation": dry_run.NESIRA_VERDICT_SUFFICIENT},
}
authority = {
    "verdict": dry_run.ACTION_AUTHORITY_SUFFICIENT,
    "action_authority_root_id": "action-root-main",
    "authorized_action_class": "review-only-transition",
    "authorized_subject_context": "subject:artifact-set-1",
    "authorized_environment_context": "env:staging",
    "rollback_or_abort_ref": "rollback:manual-abort-record",
    "assumptions": ["PA-AUTHORITY-01", "PA-CLOCK-01", "PA-META-01"],
}
artifact = dry_run.evaluate_dry_run(context, combined, nesira, authority)
print(json.dumps(artifact, sort_keys=True))
"""
    result = subprocess.run([python, "-c", code], text=True, capture_output=True, check=True)
    artifact = json.loads(result.stdout)

    assert artifact["dry_run_verdict"] == "DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION"
    assert artifact["action_not_performed"] is True
    assert artifact["execution_authorization_required"] is True
    assert "ACTION_NOT_PERFORMED" in artifact["markers"]
    assert _forbidden_output_hits(artifact) == []


def test_public_dry_run_rc_preserves_dependency_and_entry_point_posture():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == VERSION
    assert pyproject["project"]["dependencies"] == []
    assert pyproject["project"]["optional-dependencies"] == {
        "nesira-assessment": ["cryptography==49.0.0"],
    }
    assert pyproject["project"]["scripts"] == {
        "spira-trust": "spira_core.trust_cli:main",
        "spira": "spira_core.trust_cli:main",
    }
    assert "spira_core.nesira_phase2_dry_run_runner" in pyproject["tool"]["spira"]["public-wheel"]["package_allowlist"]


def _build_public_wheel(tmp_path: Path) -> Path:
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.splitlines()[0])


def _wheel_payload(wheel_path: Path) -> tuple[list[str], str, str]:
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
        metadata = zf.read(metadata_name).decode("utf-8")
        entry_points = zf.read(entry_points_name).decode("utf-8")
    return names, metadata, entry_points


def _install_wheel_in_venv(tmp_path: Path, wheel_path: Path) -> str:
    venv = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True, text=True, capture_output=True)
    python = venv / "Scripts" / "python.exe"
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel_path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return str(python)


def _forbidden_output_hits(value: Any) -> list[str]:
    forbidden = {
        "apply",
        "bash",
        "command",
        "command_line",
        "copy_paste_steps",
        "cwd",
        "environment_variables",
        "execute",
        "network_targets",
        "powershell",
        "python -m",
        "remediate",
        "runbook",
        "script",
        "sever",
        "shell",
        "subprocess_args",
        "write_paths",
    }
    hits: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if str(key).lower() in forbidden:
                    hits.append(str(key))
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(hits)
