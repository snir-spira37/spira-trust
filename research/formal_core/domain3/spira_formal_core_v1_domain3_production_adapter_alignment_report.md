# SPIRA Formal Core V1 Domain 3 Production Adapter Alignment Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED
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
  "production_domain3_conformance_accepted": true,
  "production_mutation_pairs_pass": true,
  "replace_path_loss_zero": true,
  "resource_action_loss_zero": true,
  "sensitive_path_loss_zero": true,
  "synthetic_fixture_contracts_match": true,
  "synthetic_fixture_count": true,
  "synthetic_fixture_typed_evidence_matches": true,
  "unknown_path_loss_zero": true,
  "validator_pass": true
}
```

Production conformance:

```json
{
  "action_distribution": {
    "PROCEED": 8,
    "REPORT_NOT_EVALUATED": 2,
    "RERUN_REQUIRED": 1,
    "STOP_BLOCKED": 29
  },
  "blocking_to_proceed_cases": [],
  "case_count": 40,
  "case_fail_count": 0,
  "case_pass_count": 40,
  "malformed_to_proceed_cases": [],
  "mismatch_count": 0,
  "mutation_pair_checks": {
    "failed": 0,
    "passed": 10,
    "total": 10
  },
  "not_evaluated_to_proceed_cases": [],
  "sensitive_value_leak_cases": [],
  "status": "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED"
}
```

Synthetic fixtures:

```json
{
  "blocking_item_loss_count": 0,
  "contract_mismatch_count": 0,
  "evidence_proof_identity_loss_count": 0,
  "false_proceed_count": 0,
  "fixture_count": 31,
  "fixture_hash_mismatch_count": 0,
  "not_claimed_loss_count": 0,
  "not_evaluated_loss_count": 0,
  "replace_path_loss_count": 0,
  "resource_action_loss_count": 0,
  "sensitive_path_loss_count": 0,
  "typed_evidence_mismatch_count": 0,
  "unknown_path_loss_count": 0
}
```
