from __future__ import annotations

import json
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_dry_run_runner as dry_run


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "run_nesira_phase2_dry_run_review.py"
EVALUATOR = ROOT / "source" / "spira_core" / "nesira_phase2_dry_run_runner.py"


def test_internal_tool_emits_artifact_for_valid_input(tmp_path):
    request = tmp_path / "request.json"
    request.write_text(json.dumps(_request(_combined_ok(), _nesira_sufficient(), _authority_sufficient())), encoding="utf-8")

    result = _run_tool(request)
    artifact = json.loads(result.stdout)

    assert result.returncode == 0
    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_SATISFIED
    assert artifact["action_not_performed"] is True
    assert dry_run.ACTION_NOT_PERFORMED in artifact["markers"]


def test_exit_code_zero_for_blocked_and_not_evaluated_dry_runs(tmp_path):
    blocked = tmp_path / "blocked.json"
    blocked.write_text(json.dumps(_request(_combined_ok(), _nesira_sufficient(), None)), encoding="utf-8")
    not_evaluated = tmp_path / "not_evaluated.json"
    not_evaluated.write_text(
        json.dumps(_request(_combined_ok(), _nesira_not_evaluated(), _authority_not_evaluated())),
        encoding="utf-8",
    )

    blocked_result = _run_tool(blocked)
    not_evaluated_result = _run_tool(not_evaluated)

    assert blocked_result.returncode == 0
    assert json.loads(blocked_result.stdout)["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert not_evaluated_result.returncode == 0
    assert json.loads(not_evaluated_result.stdout)["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_NOT_EVALUATED


def test_malformed_input_returns_clean_json_error(tmp_path):
    request = tmp_path / "bad.json"
    request.write_text("{", encoding="utf-8")

    result = _run_tool(request)
    error = json.loads(result.stderr)

    assert result.returncode == 2
    assert error["schema"] == "NESIRA_PHASE2_DRY_RUN_REVIEW_TOOL_ERROR_V1"
    assert error["error"] == "request file is not valid JSON"
    assert "Traceback" not in result.stderr
    assert str(tmp_path) not in result.stderr


def test_output_contains_mandatory_markers_and_no_executable_fields(tmp_path):
    request = tmp_path / "request.json"
    request.write_text(json.dumps(_request(_combined_ok(), _nesira_sufficient(), _authority_sufficient())), encoding="utf-8")

    result = _run_tool(request)
    artifact = json.loads(result.stdout)

    assert set(dry_run.MANDATORY_MARKERS).issubset(set(artifact["markers"]))
    assert _forbidden_output_hits(artifact) == []


def test_output_file_matches_stdout_when_requested(tmp_path):
    request = tmp_path / "request.json"
    output = tmp_path / "artifact.json"
    request.write_text(json.dumps(_request(_combined_ok(), _nesira_sufficient(), _authority_sufficient())), encoding="utf-8")

    result = _run_tool(request, output)

    assert result.returncode == 0
    assert output.read_text(encoding="utf-8") == result.stdout


def test_public_wheel_excludes_dry_run_evaluator_and_exposure_tool(tmp_path):
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert "spira_core/nesira_phase2_dry_run_runner.py" not in names
    assert all("run_nesira_phase2_dry_run_review" not in name for name in names)
    assert "dry-run" not in metadata.lower()
    assert "dry_run" not in metadata.lower()


def test_pyproject_entry_points_are_unchanged():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"] == {
        "spira-trust": "spira_core.trust_cli:main",
        "spira": "spira_core.trust_cli:main",
    }
    assert "dry" not in json.dumps(pyproject["project"]["scripts"]).lower()


def test_evaluator_source_side_effect_scan_remains_zero():
    text = EVALUATOR.read_text(encoding="utf-8")
    forbidden = [
        "import subprocess",
        "import socket",
        "import requests",
        "import urllib",
        "import http",
        "import shutil",
        "import tempfile",
        "import os",
        "os.system",
        "os.popen",
        "Path.write_text",
        "Path.write_bytes",
    ]

    assert [item for item in forbidden if item in text] == []


def test_v1_sha256sums_remain_consistent():
    ok = 0
    failed = []
    sums = ROOT / "research" / "formal_core" / "external_reproduction_package" / "SHA256SUMS"
    for line in sums.read_text(encoding="utf-8").splitlines():
        expected, rel = line.split(maxsplit=1)
        path = ROOT / rel.lstrip("*")
        if path.read_bytes():
            import hashlib

            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            actual = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        if actual == expected:
            ok += 1
        else:
            failed.append(rel)

    assert ok == 622
    assert failed == []


def _run_tool(request: Path, output: Path | None = None) -> subprocess.CompletedProcess[str]:
    args = [sys.executable, str(TOOL), str(request)]
    if output is not None:
        args.extend(["--output", str(output)])
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def _request(combined: dict[str, object], nesira: dict[str, object] | None, authority: dict[str, object] | None) -> dict[str, object]:
    return {
        "expected_context": _context(),
        "combined_verdict": combined,
        "nesira_assessment": nesira,
        "action_authority_result": authority,
    }


def _context() -> dict[str, object]:
    return {
        "action_class": "review-only-transition",
        "subject_context": "subject:artifact-set-1",
        "environment_context": "env:staging",
        "action_authority_root_id": "action-root-main",
    }


def _combined_ok() -> dict[str, object]:
    return {"combined_verdict": "GRAPH_OK", "winning_status": "OK", "not_evaluated_layers": []}


def _nesira_sufficient() -> dict[str, object]:
    return {
        "verdict": dry_run.NESIRA_VERDICT_SUFFICIENT,
        "assumptions": ["PT-CRYPTO-01", "PT-ISOLATION-01", "PT-META-01"],
        "per_domain_breakdown": {"isolation": dry_run.NESIRA_VERDICT_SUFFICIENT},
    }


def _nesira_not_evaluated() -> dict[str, object]:
    value = _nesira_sufficient()
    value["verdict"] = dry_run.NESIRA_VERDICT_NOT_EVALUATED
    return value


def _authority_sufficient() -> dict[str, object]:
    return {
        "verdict": dry_run.ACTION_AUTHORITY_SUFFICIENT,
        "action_authority_root_id": "action-root-main",
        "authorized_action_class": "review-only-transition",
        "authorized_subject_context": "subject:artifact-set-1",
        "authorized_environment_context": "env:staging",
        "rollback_or_abort_ref": "rollback:manual-abort-record",
        "assumptions": ["PA-AUTHORITY-01", "PA-CLOCK-01", "PA-META-01"],
    }


def _authority_not_evaluated() -> dict[str, object]:
    value = _authority_sufficient()
    value["verdict"] = dry_run.ACTION_NOT_EVALUATED
    return value


def _forbidden_output_hits(value: Any) -> list[str]:
    hits: list[str] = []
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if str(key).lower() in dry_run.FORBIDDEN_EXECUTABLE_KEYS:
                    hits.append(str(key))
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(hits)
