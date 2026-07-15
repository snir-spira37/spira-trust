# SPIRA Formal Core V1 Domain 2 Production Adapter Alignment Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED
```

Gates:

```json
{
  "blocking_item_loss_zero": true,
  "false_proceed_zero": true,
  "focused_tests_pass": true,
  "full_pytest_pass": true,
  "not_claimed_loss_zero": true,
  "not_evaluated_loss_zero": true,
  "production_adapter_source_unchanged": true,
  "production_case_count": true,
  "production_case_pass_count": true,
  "production_domain2_conformance_accepted": true,
  "production_mutation_pairs_pass": true,
  "synthetic_fixture_contracts_match": true,
  "synthetic_fixture_count": true,
  "synthetic_fixture_typed_evidence_matches": true
}
```

Production conformance:

```json
{
  "blocking_to_proceed_cases": [],
  "case_count": 38,
  "case_fail_count": 0,
  "case_pass_count": 38,
  "mismatch_count": 0,
  "mutation_pair_checks": {
    "checks": [
      {
        "mutated_case_id": "synthetic_single_assertion_failure",
        "passed": true,
        "source_case_id": "synthetic_clean_success"
      },
      {
        "mutated_case_id": "synthetic_multiple_failures",
        "passed": true,
        "source_case_id": "synthetic_single_assertion_failure"
      },
      {
        "mutated_case_id": "synthetic_long_traceback",
        "passed": true,
        "source_case_id": "synthetic_single_assertion_failure"
      },
      {
        "mutated_case_id": "synthetic_linux_paths",
        "passed": true,
        "source_case_id": "synthetic_windows_paths"
      },
      {
        "mutated_case_id": "synthetic_injection_proceed",
        "passed": true,
        "source_case_id": "synthetic_single_assertion_failure"
      },
      {
        "mutated_case_id": "synthetic_non_derivable_rerun",
        "passed": true,
        "source_case_id": "synthetic_derivable_rerun"
      }
    ],
    "failed": 0,
    "passed": 6,
    "total": 6
  },
  "not_evaluated_to_proceed_cases": [],
  "report_with_notes_case_count": 2,
  "status": "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED"
}
```

Synthetic fixtures:

```json
{
  "blocking_item_loss_count": 0,
  "contract_mismatch_count": 0,
  "evidence_proof_identity_loss_count": 0,
  "false_proceed_count": 0,
  "fixture_count": 26,
  "fixture_hash_mismatch_count": 0,
  "not_claimed_loss_count": 0,
  "not_evaluated_loss_count": 0,
  "typed_evidence_mismatch_count": 0
}
```
