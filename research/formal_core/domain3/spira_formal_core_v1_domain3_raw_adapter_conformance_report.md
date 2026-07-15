# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
```

Summary:

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

Gates:

```json
{
  "blocking_item_loss_zero": true,
  "contracts_match": true,
  "evidence_proof_identity_loss_zero": true,
  "false_proceed_zero": true,
  "fixture_count": true,
  "fixture_hashes_match": true,
  "focused_tests_pass": true,
  "full_pytest_pass": true,
  "not_claimed_loss_zero": true,
  "not_evaluated_loss_zero": true,
  "replace_path_loss_zero": true,
  "resource_action_loss_zero": true,
  "sensitive_path_loss_zero": true,
  "typed_evidence_matches": true,
  "unknown_path_loss_zero": true
}
```

This is a synthetic fixture conformance harness. It does not prove arbitrary raw Terraform Plan JSON parsing or Terraform execution.
