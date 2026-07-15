# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO
TERRAFORM_EXECUTION_FORMALLY_PROVED_NO
PRODUCTION_ADAPTER_UNCHANGED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 3 raw adapter synthetic fixture conformance harness is accepted.

## Evidence

```json
{
  "counts": {
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
  },
  "gates": {
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
}
```

## Boundary

This review accepts conformance on the 31 synthetic Terraform Plan fixtures only. It does not claim formal proof of arbitrary raw Terraform Plan JSON parsing, Terraform execution, provider behavior, cloud state, cost, security, compliance, apply success, filesystem behavior, or production release readiness.

## Next Step

```text
DOMAIN_3_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZATION_REQUIRED
```
