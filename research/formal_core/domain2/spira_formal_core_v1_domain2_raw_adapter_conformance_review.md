# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_ACCEPTED
RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO
PRODUCTION_ADAPTER_UNCHANGED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 2 raw adapter synthetic fixture conformance harness is accepted.

## Evidence

```json
{
  "counts": {
    "blocking_item_loss_count": 0,
    "contract_mismatch_count": 0,
    "evidence_proof_identity_loss_count": 0,
    "false_proceed_count": 0,
    "fixture_count": 26,
    "fixture_hash_mismatch_count": 0,
    "not_claimed_loss_count": 0,
    "not_evaluated_loss_count": 0,
    "typed_evidence_mismatch_count": 0
  },
  "gates": {
    "blocking_item_loss_zero": true,
    "evidence_proof_identity_loss_zero": true,
    "false_proceed_zero": true,
    "fixture_count": true,
    "fixture_hashes_match": true,
    "focused_tests_pass": true,
    "formal_core_contracts_match": true,
    "full_pytest_pass": true,
    "not_claimed_loss_zero": true,
    "not_evaluated_loss_zero": true,
    "typed_evidence_matches": true
  }
}
```

## Boundary

This review accepts conformance on the 26 synthetic fixtures only. It does not claim formal proof of arbitrary pytest/JUnit parsing, runtime behavior, filesystem behavior, or production release readiness.

## Next Step

```text
DOMAIN_2_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZATION_REQUIRED
```
