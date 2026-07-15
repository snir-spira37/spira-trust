# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_ACCEPTED
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO
PACKAGE_SAFETY_FORMALLY_PROVED_NO
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 1 raw adapter synthetic fixture conformance harness is accepted.

## Evidence

```json
{
  "counts": {
    "blocking_item_loss_count": 0,
    "contract_mismatch_count": 0,
    "evidence_proof_identity_loss_count": 0,
    "false_proceed_count": 0,
    "fixture_count": 33,
    "fixture_hash_mismatch_count": 0,
    "identity_hash_loss_count": 0,
    "not_claimed_loss_count": 0,
    "not_evaluated_loss_count": 0,
    "typed_evidence_mismatch_count": 0,
    "unification_id_loss_count": 0
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
    "identity_hash_loss_zero": true,
    "not_claimed_loss_zero": true,
    "not_evaluated_loss_zero": true,
    "typed_evidence_matches": true,
    "unification_id_loss_zero": true
  }
}
```

## Boundary

This review accepts conformance on the 33 synthetic Python artifact fixtures only. It does not claim formal proof of arbitrary raw wheel/ZIP parsing, RECORD parsing, SBOM parsing, package safety, dependency safety, malware absence, runtime behavior, filesystem behavior, or production release readiness.

## Next Step

```text
FORMAL_CORE_V1_ALL_DOMAIN_ADAPTER_ALIGNMENT_REVIEW_REQUIRED
```
