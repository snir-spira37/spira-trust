from __future__ import annotations

from pathlib import Path

from spira_core.nesira_domain4_v2_harness import run_harness


ROOT = Path(__file__).resolve().parents[1]


def test_domain4_nesira_harness_accepts_authorized_fixture_corpus():
    results = run_harness(ROOT, build_wheel=False)

    assert results["verdict"] == "DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED"
    assert results["layer1_core_agreement"]["core_agreement_disagreements"] == 0
    assert results["layer2_classification_faithfulness"]["safety_critical_values_without_mutation_pair"] == 0
    assert results["layer2_classification_faithfulness"]["mutation_pair_misses"] == 0
    assert results["layer3_phase1_reproduction"]["phase1_reproduction_divergences"] == 0
    assert results["two_run_semantic_diff"] == 0
