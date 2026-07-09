from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from corpus.build_corpus import build_record_mismatch


REPO_ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = REPO_ROOT / "tools" / "run_previous_version_gate.py"


def _load_helper():
    spec = importlib.util.spec_from_file_location("run_previous_version_gate", HELPER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


gate = _load_helper()


def _trust(verdict: str | None = "TRUST_OK_WITH_NOTES", exit_code: int = 0) -> dict[str, object]:
    return {
        "exit_code": exit_code,
        "verdict": verdict,
        "finding_codes": [],
        "schema_readable": verdict is not None,
    }


def _graph(verdict: str | None = "GRAPH_OK_WITH_NOTES", exit_code: int = 0, codes: list[str] | None = None) -> dict[str, object]:
    return {
        "exit_code": exit_code,
        "verdict": verdict,
        "finding_codes": codes or [],
        "schema_readable": verdict is not None,
    }


def _no_declaration() -> dict[str, object]:
    return {"declaration_path": None, "declaration_valid": False, "matched": False, "validation_errors": []}


def _valid_declaration() -> dict[str, object]:
    return {
        "declaration_path": "release/expected_previous_block.json",
        "declaration_valid": True,
        "matched": False,
        "validation_errors": [],
        "declaration": {
            "expected_previous_verdict": "GRAPH_BLOCK",
            "expected_finding_codes": ["RECORD_MISMATCH"],
        },
    }


def _invalid_declaration() -> dict[str, object]:
    return {
        "declaration_path": "release/expected_previous_block.json",
        "declaration_valid": False,
        "matched": False,
        "validation_errors": ["candidate_version does not match release candidate"],
        "declaration": {
            "expected_previous_verdict": "GRAPH_BLOCK",
            "expected_finding_codes": ["RECORD_MISMATCH"],
        },
    }


def test_no_declaration_previous_pass_allows_publish() -> None:
    result = gate._decide_gate(_trust(), _graph(), _no_declaration())

    assert result["status"] == "PASS"
    assert result["publish_allowed"] is True


def test_no_declaration_previous_block_denies_publish() -> None:
    result = gate._decide_gate(_trust(), _graph("GRAPH_BLOCK", 1, ["RECORD_MISMATCH"]), _no_declaration())

    assert result["status"] == "PREVIOUS_VERSION_BLOCK"
    assert result["publish_allowed"] is False


def test_valid_declaration_observed_block_is_documented_previous_block() -> None:
    expected = _valid_declaration()

    result = gate._decide_gate(_trust(), _graph("GRAPH_BLOCK", 1, ["RECORD_MISMATCH"]), expected)

    assert result["status"] == "DOCUMENTED_PREVIOUS_BLOCK"
    assert result["publish_allowed"] is True
    assert expected["matched"] is True


def test_valid_declaration_without_observed_block_fails_as_residue() -> None:
    result = gate._decide_gate(_trust(), _graph(), _valid_declaration())

    assert result["status"] == "EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED"
    assert result["publish_allowed"] is False


def test_invalid_declaration_fails_even_when_previous_blocks() -> None:
    result = gate._decide_gate(
        _trust(),
        _graph("GRAPH_BLOCK", 1, ["RECORD_MISMATCH"]),
        _invalid_declaration(),
    )

    assert result["status"] == "EXPECTED_PREVIOUS_BLOCK_INVALID"
    assert result["publish_allowed"] is False


def test_declaration_cannot_launder_missing_verdict() -> None:
    result = gate._decide_gate(_trust(None, 1), _graph("GRAPH_BLOCK", 1, ["RECORD_MISMATCH"]), _valid_declaration())

    assert result["status"] == "PREVIOUS_VERSION_SCHEMA_UNREADABLE"
    assert result["publish_allowed"] is False


def test_nonblocking_verdict_with_abnormal_runtime_is_run_error() -> None:
    result = gate._decide_gate(_trust("TRUST_OK_WITH_NOTES", 5), _graph(), _no_declaration())

    assert result["status"] == "PREVIOUS_VERSION_RUN_ERROR"
    assert result["publish_allowed"] is False


def test_expected_block_notes_must_contain_mechanical_terms(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    Path("release").mkdir()
    notes = Path("release/notes.md")
    notes.write_text(
        "previous version blocked 0.6.0 0.6.1 RECORD_MISMATCH DOCUMENTED_PREVIOUS_BLOCK\n",
        encoding="utf-8",
    )
    declaration_path = Path("release/expected_previous_block.json")
    declaration_path.write_text(
        json.dumps(
            {
                "schema": "SPIRA_EXPECTED_PREVIOUS_BLOCK_V1",
                "candidate_version": "0.6.1",
                "previous_version": "0.6.0",
                "expected_previous_verdict": "GRAPH_BLOCK",
                "expected_finding_codes": ["RECORD_MISMATCH"],
                "release_notes_path": "release/notes.md",
                "release_notes_required_terms": ["previous version blocked"],
                "why_expected": "test fixture",
            }
        ),
        encoding="utf-8",
    )

    state = gate._read_expected_block_state(declaration_path, "0.6.1", "0.6.0")

    assert state["declaration_valid"] is True

    notes.write_text("previous version blocked 0.6.0 RECORD_MISMATCH DOCUMENTED_PREVIOUS_BLOCK\n", encoding="utf-8")
    stale = gate._read_expected_block_state(declaration_path, "0.6.1", "0.6.0")

    assert stale["declaration_valid"] is False
    assert "release notes missing mechanical term: 0.6.1" in stale["validation_errors"]


def test_previous_selection_uses_pep440_version_ordering() -> None:
    pypi_json = {
        "releases": {
            "0.6.9": [_wheel("spira_trust-0.6.9-py3-none-any.whl")],
            "0.6.10": [_wheel("spira_trust-0.6.10-py3-none-any.whl")],
            "0.6.11": [_wheel("spira_trust-0.6.11-py3-none-any.whl", yanked=True)],
        }
    }

    previous = gate._select_previous_distribution(
        pypi_json,
        candidate_version="0.6.11",
        override_version=None,
        first_public_release=False,
    )

    assert previous.version == "0.6.10"


def test_generated_record_mismatch_corpus_blocks(tmp_path: Path) -> None:
    wheel = build_record_mismatch(tmp_path / "corpus")
    output = tmp_path / "graph"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "source")

    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "spira_core.trust_cli",
            "graph",
            str(wheel),
            "--output-dir",
            str(output),
            "--format",
            "json",
        ],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
    )

    assert run.returncode == 1
    decision = json.loads((output / "spira-decision.json").read_text(encoding="utf-8"))
    assert decision["decision"]["verdict"] == "GRAPH_BLOCK"


def _wheel(filename: str, *, yanked: bool = False) -> dict[str, object]:
    return {
        "filename": filename,
        "packagetype": "bdist_wheel",
        "yanked": yanked,
        "url": f"https://example.invalid/{filename}",
        "digests": {"sha256": "0" * 64},
        "size": 1,
        "upload_time_iso_8601": "2026-07-09T00:00:00Z",
    }
