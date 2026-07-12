# Domain-Neutral Unification Core Gate A Implementation Authorization

## Status

```text
GATE_A_IMPLEMENTATION_AUTHORIZED
DOMAIN_1_IDENTITY_REGRESSION_REQUIRED
DOMAIN_2_STILL_BLOCKED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
research/domain_neutral_unification_core_interface_proposal_v3.md
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
research/domain1_identity_baseline_review.md
research/domain_neutral_unification_core_gate_a_final_review.md
```

Accepted Domain 1 baseline root:

```text
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

Accepted Domain 1 baseline size:

```text
1,954 records
```

## Authorized Scope

This document authorizes only the minimal code changes required to implement
Gate A:

```text
explicit subject {type, sha256}
prevalidated SPIRA_CLAIM_V1 list
generic proof assembly boundary
legacy Domain 1 wrapper using the unchanged legacy path
Domain 1 identity regression against the accepted baseline
```

The implementation may introduce a small domain-neutral proof assembly entry
point only if the existing Domain 1 path continues to produce the accepted
baseline identity.

The existing Python wheel flow must remain the source of truth for Domain 1.
Any generic interface is additive.

## Allowed Files

Implementation may touch only files needed for Gate A and its regression:

```text
source/spira_core/unification_proof.py
tests/test_unification_proof.py
research/unification_proof_corpus/materialize_identity_baseline.py
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
research/unification_proof_corpus/*identity*regression*.py
research/*gate_a*implementation*.md
```

If a needed change falls outside this list, implementation must stop and the
authorization must be revised before the file is changed.

## Explicitly Forbidden Changes

The implementation must not change:

```text
action enum
claim status enum
SPIRA_DECISION_SEMANTICS_V2
Merkle algorithm
inclusion-proof algorithm
compact reference format
legacy Domain 1 context serialization
Gate B status/cache/rerun behavior
pytest or Domain 2 logic
Domain 2 producer
Domain 2 corpus
oracle population
release/version/tag/PyPI behavior
```

No pytest-specific logic may enter the unification core.

No producer-specific extraction logic may enter the unification core.

No Domain 2 files may be created under this authorization.

## Required Regression Gates

Before Gate A implementation can be accepted, all of the following must pass:

```text
1,954 / 1,954 Domain 1 identity records match the accepted baseline

domain1_identity_baseline_root ==
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c

canonical claims hashes unchanged
claims_merkle_root unchanged
legacy context_sha256 unchanged
canonical decision bytes unchanged
unification_id unchanged
compact reference bytes unchanged
stable proof identity unchanged
stop unchanged
recommended_agent_action unchanged
reason_codes unchanged
not_evaluated unchanged
worst_claim_status unchanged
BLOCK semantics unchanged
NOT_EVALUATED semantics unchanged

full pytest suite passes
```

The regression comparison must use:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

as the immutable before-image.

## Stop Conditions

Any unexpected Domain 1 identity change is a stop condition:

```text
GATE_A_MIGRATION_REQUIRED
```

In that state:

```text
do not update the baseline to match the new output
do not change canonicalization after observing results
do not lower the required 1,954 / 1,954 match gate
do not present the change as a transparent refactor
do not proceed to Domain 2
```

If a migration is truly desired, it requires a separate migration proposal,
separate versioning decision, and separate owner authorization.

## Regression Artifact Requirement

The implementation must produce or update a regression artifact documenting:

```text
Gate A implementation commit
baseline root used
record count compared
identity match count
identity mismatch count
domain1_identity_baseline_root recomputation
pytest result
final status
```

The only acceptable successful final status is:

```text
GATE_A_DOMAIN1_IDENTITY_REGRESSION_PASS
```

Any mismatch must produce:

```text
GATE_A_MIGRATION_REQUIRED
```

## Domain 2 Boundary

Domain 2 remains blocked after this authorization.

This authorization does not permit:

```text
pytest producer implementation
pytest oracle population
pytest corpus materialization
test/build failure contract execution
Domain 2 validation claims
```

Domain 2 may be reconsidered only after:

```text
Gate A implementation is complete
Domain 1 identity regression passes 1,954 / 1,954
Gate A implementation review accepts the result
```

## Verdict

```text
GATE_A_IMPLEMENTATION_AUTHORIZED
DOMAIN_1_IDENTITY_REGRESSION_REQUIRED
DOMAIN_2_STILL_BLOCKED
```

This authorization permits the first Gate A implementation work under the
bounded scope above. It does not authorize Domain 2 or Gate B.
