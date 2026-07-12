# Gate A Implementation Retry Report

## Status

```text
GATE_A_IMPLEMENTATION_RETRY_COMPLETE
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_PASS
LEGACY_REGENERATION_AUDIT_COMPLETE
DOMAIN_2_STILL_BLOCKED
GATE_B_NOT_AUTHORIZED
```

## Implementation Scope

The retry implemented only the authorized Gate A scope:

```text
minimal generic proof assembler
legacy Domain 1 wrapper
isolated assembly regression runner
legacy regeneration audit runner/report
focused Gate A tests
```

No Domain 2 producer, pytest adapter, oracle population, Gate B behavior, or
release/version/tag work was implemented.

## Regression Artifact

```text
research/unification_proof_corpus/results/gate_a_retry_regression_v1.json
```

Accepted baseline root:

```text
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

## Isolated Assembly Regression

Final status:

```text
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_PASS
```

Summary:

```text
expected_count: 1,954
compared_count: 1,954
isolated_identity_match_count: 1,954
isolated_identity_mismatch_count: 0
unique_artifact_hashes: 1,954

isolated_identity_root:
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c

isolated_identity_root_matches_baseline:
true
```

The isolated regression used regenerated claims and decision objects only after
verifying that their canonical hashes matched the accepted baseline. It then
assembled proofs with the frozen baseline `context_sha256`, so the check tested
the Gate A assembler boundary directly rather than report-byte regeneration.

## Legacy Regeneration Audit

Legacy regeneration audit was completed for all 1,954 records.

Summary:

```text
legacy_drift_count: 1,954
legacy_claim_drift_count: 0
legacy_decision_drift_count: 0
legacy_action_drift_count: 0
```

Observed legacy drift fields:

```text
context_sha256: 1,954
unification_id: 1,954
compact_reference_bytes_sha256: 1,954
canonical_proof_bytes_sha256: 1,954
```

This preserves the finding from the first implementation attempt: full
end-to-end regeneration changes legacy context-derived identity fields because
the legacy context binds regenerated report bytes. It does not change claims,
decision, or action semantics in this run.

## Tests

Focused Gate A/unification tests:

```text
tests/test_unification_proof.py
10 passed
```

Full suite:

```text
78 passed
```

## What Changed

Gate A adds a domain-neutral proof assembly boundary that can accept:

```text
explicit subject
prevalidated SPIRA_CLAIM_V1 claims
context roots
decision/action object
```

The existing Domain 1 path remains a wrapper that builds the same Domain 1
claims, context, and decision, then calls the assembler.

## What Did Not Change

```text
action enum
claim status enum
SPIRA_DECISION_SEMANTICS_V2
Merkle algorithm
inclusion-proof algorithm
compact reference format
legacy Domain 1 context construction
status/cache/rerun behavior
baseline artifact
baseline root
```

## Not Claimed

This result does not claim:

```text
Domain 2 producer is authorized
pytest adapter exists
Gate B is authorized
legacy report-byte regeneration is stable
the proof is a safety proof
SBOM correctness is proven
release/version/tag/PyPI is authorized
```

## Verdict

```text
GATE_A_IMPLEMENTATION_ACCEPTABLE_WITH_LEGACY_DRIFT_NOTES
```

Gate A passed the required isolated assembly regression over 1,954 / 1,954
records. Legacy end-to-end regeneration drift remains real and is reported
separately.

Domain 2 remains blocked until a separate authorization is committed.
