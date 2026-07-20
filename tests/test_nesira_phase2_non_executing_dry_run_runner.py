from __future__ import annotations

import ast
import zipfile
from pathlib import Path
from typing import Any

from spira_core import nesira_phase2_dry_run_runner as dry_run


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source" / "spira_core" / "nesira_phase2_dry_run_runner.py"


def test_nesira_sufficient_without_action_authority_is_blocked():
    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), None)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "ACTION_AUTHORITY_MISSING" in artifact["blocking_reasons"]
    assert dry_run.ACTION_NOT_PERFORMED in artifact["markers"]


def test_sufficient_authority_still_does_not_perform_action():
    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), _authority_sufficient())

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_SATISFIED
    assert artifact["action_not_performed"] is True
    assert artifact["execution_authorization_required"] is True
    assert dry_run.ACTION_NOT_PERFORMED in artifact["markers"]
    assert "action not performed" in artifact["precondition_summary"]


def test_combined_graph_ok_without_action_authority_is_blocked():
    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), None, None)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "ACTION_AUTHORITY_MISSING" in artifact["blocking_reasons"]
    assert "NESIRA_ASSESSMENT_MISSING" in artifact["not_evaluated_reasons"]


def test_action_authority_sufficient_with_combined_block_is_blocked():
    artifact = dry_run.evaluate_dry_run(_context(), _combined_block(), _nesira_sufficient(), _authority_sufficient())

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "COMBINED_VERDICT_BLOCK" in artifact["blocking_reasons"]
    assert dry_run.ACTION_NOT_PERFORMED in artifact["markers"]


def test_action_authority_context_mismatch_is_blocked():
    authority = _authority_sufficient()
    authority["authorized_subject_context"] = "subject:other"

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), authority)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "ACTION_AUTHORITY_CONTEXT_MISMATCH" in artifact["blocking_reasons"]


def test_action_authority_rollback_missing_is_blocked():
    authority = _authority_sufficient()
    authority["rollback_or_abort_ref"] = ""

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), authority)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "ACTION_AUTHORITY_ROLLBACK_OR_ABORT_MISSING" in artifact["blocking_reasons"]


def test_action_authority_not_evaluated_is_not_evaluated():
    authority = _authority_sufficient()
    authority["verdict"] = dry_run.ACTION_NOT_EVALUATED

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), authority)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_NOT_EVALUATED
    assert "ACTION_AUTHORITY_NOT_EVALUATED" in artifact["not_evaluated_reasons"]


def test_action_authority_not_authorized_is_blocked():
    authority = _authority_sufficient()
    authority["verdict"] = dry_run.ACTION_NOT_AUTHORIZED

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), authority)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "ACTION_NOT_AUTHORIZED" in artifact["blocking_reasons"]


def test_nesira_insufficient_is_blocked():
    assessment = _nesira_sufficient()
    assessment["verdict"] = dry_run.NESIRA_VERDICT_INSUFFICIENT

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), assessment, _authority_sufficient())

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "NESIRA_TRUST_INSUFFICIENT" in artifact["blocking_reasons"]


def test_nesira_not_evaluated_is_not_evaluated():
    assessment = _nesira_sufficient()
    assessment["verdict"] = dry_run.NESIRA_VERDICT_NOT_EVALUATED

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), assessment, _authority_sufficient())

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_NOT_EVALUATED
    assert "NESIRA_TRUST_NOT_EVALUATED" in artifact["not_evaluated_reasons"]


def test_malformed_or_action_looking_inputs_fail_closed():
    assessment = _nesira_sufficient()
    assessment["command"] = "do not serialize commands"
    authority = _authority_sufficient()
    authority["network_targets"] = ["example.invalid"]

    artifact = dry_run.evaluate_dry_run(_context(), _combined_ok(), assessment, authority)

    assert artifact["dry_run_verdict"] == dry_run.DRY_RUN_VERDICT_BLOCKED
    assert "NESIRA_ASSESSMENT_ACTION_LOOKING" in artifact["blocking_reasons"]
    assert "ACTION_AUTHORITY_ACTION_LOOKING" in artifact["blocking_reasons"]


def test_all_output_paths_carry_mandatory_markers():
    artifacts = [
        dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), _authority_sufficient()),
        dry_run.evaluate_dry_run(_context(), _combined_block(), _nesira_sufficient(), _authority_sufficient()),
        dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_not_evaluated(), _authority_not_evaluated()),
        dry_run.evaluate_dry_run({}, {}, None, None),
    ]

    for artifact in artifacts:
        assert set(dry_run.MANDATORY_MARKERS).issubset(set(artifact["markers"]))
        assert artifact["action_not_performed"] is True
        assert artifact["execution_authorization_required"] is True


def test_output_contains_no_executable_key():
    artifacts = [
        dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_sufficient(), _authority_sufficient()),
        dry_run.evaluate_dry_run(_context(), _combined_block(), _nesira_sufficient(), _authority_sufficient()),
        dry_run.evaluate_dry_run(_context(), _combined_ok(), _nesira_not_evaluated(), _authority_not_evaluated()),
    ]

    for artifact in artifacts:
        assert _forbidden_output_hits(artifact) == []


def test_static_source_scan_finds_no_side_effect_imports_or_calls():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    forbidden_import_roots = {"subprocess", "socket", "requests", "urllib", "http", "shutil", "tempfile", "os"}
    imported = set()
    calls = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in {"open", "os.system", "os.popen", "Path.write_text", "Path.write_bytes"}:
                calls.append(name)

    assert imported.isdisjoint(forbidden_import_roots)
    assert calls == []


def test_public_wheel_behavior_unchanged_dry_run_module_not_exposed(tmp_path):
    import subprocess
    import sys

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
        entry_points_name = next(name for name in names if name.endswith(".dist-info/entry_points.txt"))
        entry_points = zf.read(entry_points_name).decode("utf-8")

    assert "spira_core/nesira_phase2_dry_run_runner.py" not in names
    assert "spira-trust = spira_core.trust_cli:main" in entry_points
    assert "spira = spira_core.trust_cli:main" in entry_points
    assert "dry-run" not in metadata.lower()


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


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _context() -> dict[str, object]:
    return {
        "action_class": "review-only-transition",
        "subject_context": "subject:artifact-set-1",
        "environment_context": "env:staging",
        "action_authority_root_id": "action-root-main",
    }


def _combined_ok() -> dict[str, object]:
    return {
        "combined_verdict": "GRAPH_OK",
        "winning_status": "OK",
        "not_evaluated_layers": [],
    }


def _combined_block() -> dict[str, object]:
    return {
        "combined_verdict": "GRAPH_BLOCK",
        "winning_status": "BLOCK",
        "not_evaluated_layers": [],
    }


def _nesira_sufficient() -> dict[str, object]:
    return {
        "verdict": dry_run.NESIRA_VERDICT_SUFFICIENT,
        "assumptions": ["PT-CRYPTO-01", "PT-ISOLATION-01", "PT-META-01"],
        "per_domain_breakdown": {"isolation": dry_run.NESIRA_VERDICT_SUFFICIENT},
    }


def _nesira_not_evaluated() -> dict[str, object]:
    assessment = _nesira_sufficient()
    assessment["verdict"] = dry_run.NESIRA_VERDICT_NOT_EVALUATED
    return assessment


def _authority_sufficient() -> dict[str, object]:
    return {
        "verdict": dry_run.ACTION_AUTHORITY_SUFFICIENT,
        "action_authority_root_id": "action-root-main",
        "authorized_action_class": "review-only-transition",
        "authorized_subject_context": "subject:artifact-set-1",
        "authorized_environment_context": "env:staging",
        "rollback_or_abort_ref": "rollback:manual-abort-record",
        "assumptions": [
            "PA-AUTHORITY-01",
            "PA-CLOCK-01",
            "PA-META-01",
            "PA-REVOKE-01",
            "PA-ROLLBACK-01",
        ],
    }


def _authority_not_evaluated() -> dict[str, object]:
    authority = _authority_sufficient()
    authority["verdict"] = dry_run.ACTION_NOT_EVALUATED
    return authority
