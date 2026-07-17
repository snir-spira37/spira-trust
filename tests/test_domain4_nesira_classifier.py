from __future__ import annotations

from pathlib import Path

from spira_core.nesira_domain4_v2_classifier import classify_isolation_fixture
from spira_core.nesira_domain4_v2_harness import ISOLATION_CONTEXT, ISOLATION_PROFILE


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "tests" / "fixtures" / "nesira_policy_profile" / "isolation" / "evidence"


def test_hash_mismatch_does_not_project_to_context_mismatch():
    classification = classify_isolation_fixture(
        ROOT,
        "hash_mismatch",
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context=ISOLATION_CONTEXT,
    )

    assert classification.tuple["hash"] == "HASH_MISMATCH"
    assert classification.tuple["context"] == "CONTEXT_OK"
    assert classification.core_contract["status"] == "INVALID"
    assert classification.core_contract["action"] == "STOP_BLOCKED"


def test_context_mismatch_projects_only_for_context_reason_codes():
    classification = classify_isolation_fixture(
        ROOT,
        "valid_isolation_single_evidence",
        profile=ISOLATION_PROFILE,
        evidence_root=EVIDENCE,
        current_context={**ISOLATION_CONTEXT, "environment_id": "staging"},
    )

    assert classification.tuple["context"] == "CONTEXT_MISMATCH"
    assert classification.tuple["hash"] == "HASH_OK"
    assert classification.core_contract["status"] == "RERUN_REQUIRED"
    assert classification.core_contract["action"] == "RERUN_REQUIRED"
