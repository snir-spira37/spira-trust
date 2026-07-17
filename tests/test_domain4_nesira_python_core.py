from __future__ import annotations

from pathlib import Path

from spira_core.nesira_domain4_v2_core import (
    EXPECTED_CORE_SPACE_SIZE,
    compare_python_to_lean_dump,
    python_core,
)


ROOT = Path(__file__).resolve().parents[1]


def test_python_core_rejects_proceed_by_construction():
    contract = python_core(
        "LEGACY_ISOLATION_RESULT",
        "PARSED_OK",
        {
            "schema": "SCHEMA_OK",
            "evidence": "EVIDENCE_OK",
            "hash": "HASH_OK",
            "path": "PATH_OK",
            "symlink": "SYMLINK_OK",
            "duplicate": "DUP_OK",
            "directory": "DIR_OK",
            "context": "CONTEXT_OK",
            "temporal": "TEMPORAL_NOT_APPLICABLE",
        },
    )

    assert contract == {
        "status": "VALID_STRUCTURAL_ONLY",
        "action": "REPORT_NOT_EVALUATED",
        "stop": True,
    }
    assert contract["action"] != "PROCEED"


def test_python_core_exhaustively_agrees_with_lean_dump():
    results = compare_python_to_lean_dump(ROOT)

    assert results["core_agreement_total_tuples"] == EXPECTED_CORE_SPACE_SIZE
    assert results["python_record_count"] == EXPECTED_CORE_SPACE_SIZE
    assert results["lean_record_count"] == EXPECTED_CORE_SPACE_SIZE
    assert results["core_agreement_disagreements"] == 0
