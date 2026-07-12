# Gate A Implementation Attempt Report

## Status

```text
GATE_A_IMPLEMENTATION_STOPPED
GATE_A_DOMAIN1_IDENTITY_REGRESSION_NOT_PASSED
GATE_A_MIGRATION_REQUIRED
CORE_CODE_UNCHANGED
DOMAIN_2_STILL_BLOCKED
```

## Authorization

This implementation attempt followed:

```text
research/domain_neutral_unification_core_gate_a_implementation_authorization.md
```

The authorization required:

```text
1,954 / 1,954 Domain 1 identity records match the accepted baseline

domain1_identity_baseline_root ==
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

Any unexpected identity change required:

```text
GATE_A_MIGRATION_REQUIRED
```

## Attempted Change

A minimal Gate A implementation was prototyped locally:

```text
generic proof assembly boundary
explicit subject input
prevalidated SPIRA_CLAIM_V1 claims
legacy Domain 1 wrapper
closed subject.type registry
```

The focused unit tests passed locally during the attempt:

```text
tests/test_unification_proof.py
10 passed
```

The code was not committed because the required Domain 1 identity regression did
not pass.

## Regression Smoke Result

The first corpus item was rerun against the accepted baseline:

```text
artifact_sha256:
880202ce5fa9b2f06189a10519b10137e7856bcc6ef62c8fae1630ecea0ef5a3

status:
MISMATCH
```

Mismatched fields:

```text
context_sha256
unification_id
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
```

Fields that remained stable in the smoke:

```text
canonical_claims_bytes_sha256
claims_merkle_root
canonical_decision_bytes_sha256
stop
recommended_agent_action
reason_codes
not_evaluated
worst_claim_status
```

## Root Cause

The mismatch was traced to the legacy Domain 1 context construction.

The current legacy context includes:

```text
decision_sha256
graph_report_sha256
command_fingerprint
```

On rerun, `decision_sha256` and `graph_report_sha256` changed even when claims
and the proof decision stayed stable. This changed:

```text
context_sha256
-> unification_id
-> compact reference hash
-> stable proof identity hash
```

This means the accepted Domain 1 baseline is valid as a committed before-image,
but strict rerun comparison through regenerated evidence files is not yet a
clean test of Gate A code alone.

## Gate Decision

Under the authorization rules, the result is:

```text
GATE_A_MIGRATION_REQUIRED
```

The implementation attempt was stopped before committing core code.

The baseline was not updated.

The canonicalization contract was not changed.

The 1,954 / 1,954 gate was not lowered.

## Current Repository State

```text
core code:
unchanged

Gate A implementation:
not merged

Domain 1 accepted baseline:
unchanged

Domain 2:
still blocked
```

## Required Next Step

Before Gate A implementation can be attempted again, the project needs a narrow
regression-methodology decision for legacy Domain 1 context drift:

```text
GATE_A_REGRESSION_METHOD_NEEDS_REVISION
```

That review must decide whether the Gate A identity regression should:

```text
1. require full regenerated legacy context identity, accepting that current
   evidence-file hash drift blocks Gate A; or

2. compare Gate A core assembly with the accepted baseline context held fixed,
   while separately reporting regenerated evidence-file context drift.
```

No code should resume until that regression method is reviewed and authorized.
