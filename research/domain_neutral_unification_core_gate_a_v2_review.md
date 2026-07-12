# Domain-Neutral Unification Core Gate A V2 Review

## Status

```text
GATE_A_NEEDS_REVISION
DESIGN_REVIEW_ONLY
IMPLEMENTATION_NOT_AUTHORIZED
BASELINE_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

This is a cold design review of:

```text
research/domain_neutral_unification_core_interface_proposal_v2.md
```

No code, baseline materialization, producer work, corpus work, or oracle
population is authorized by this review.

## Verdict

```text
GATE_A_NEEDS_REVISION
```

V2 correctly defines the identity-preservation contract, but it does not yet
require the frozen per-item identity evidence needed to test that contract.

The central finding:

```text
The identity-preservation contract is precise,
but the frozen per-item identity evidence required to test it does not yet
exist as a committed artifact.
```

## What V2 Solved

V2 made the correct conservative design choices:

```text
action enum unchanged
claim statuses unchanged
decision semantics version unchanged
Merkle algorithm unchanged
inclusion algorithm unchanged
compact reference unchanged
Domain 1 legacy context construction preserved exactly
Gate B excluded
subject.type governed by a closed registry
```

It also correctly states:

```text
Generic interface is additive.
Legacy Domain 1 serialization is immutable.
```

Those choices are accepted by this review as the right direction.

## Blocking Gap

V2 lists these as baseline artifacts:

```text
research/unification_proof_corpus/results/full_v1_public_results.json
research/unification_proof_corpus/report_v1.md
research/unification_proof_corpus/results/materialized_v1_2026-07-12.json
```

Those artifacts are not sufficient by themselves to prove future byte-for-byte
identity preservation for every corpus item.

The public aggregate results do not necessarily contain the per-wheel canonical
claim bytes hash, context hash, decision bytes hash, proof bytes hash, and
compact reference bytes hash required to distinguish:

```text
identity preserved
```

from:

```text
action preserved, but proof/context identity changed
```

Because V2's core claim is identity preservation, the missing per-item identity
baseline is a design-blocking issue, not a small operational detail.

## Required V2 Revision

V2 must require a committed baseline artifact before any Gate A implementation:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

This artifact must be generated from the frozen pre-change core and reviewed
before any Gate A code change.

Required top-level metadata:

```text
schema
schema_version
baseline_commit
tool_version
decision_semantics_version
unification_proof_schema
unification_reference_schema
corpus_manifest_sha256
corpus_size: 1954
generation_timestamp
volatile_fields_excluded
canonicalization_contract
domain1_identity_baseline_root
```

Required per-wheel fields:

```text
artifact_sha256
canonical_claims_bytes_sha256
claims_merkle_root
context_sha256
canonical_decision_bytes_sha256
unification_id
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
recommended_agent_action
stop
reason_codes
not_evaluated
worst_claim_status
```

## Proof Bytes Rule

If `unification_proof.json` contains volatile fields such as `created_at`, the
baseline must lock one comparison rule before any implementation run:

```text
hash canonical proof excluding declared volatile fields
```

or:

```text
hash stable proof identity projection
```

The chosen rule must be recorded in `canonicalization_contract`.

The rule may not be changed after Gate A implementation results are observed.

## Compact Reference Rule

The compact reference must be hashed as exact canonical bytes, not merely as
decoded fields.

This is required to catch changes in:

```text
field names
field presence
serialization
canonical ordering
path value
```

For Domain 1, V2 claims the compact reference is immutable. The baseline must
make that claim testable.

## Corpus Identity Root

The baseline must include:

```text
domain1_identity_baseline_root
```

computed from all 1,954 per-wheel identity records after sorting by
`artifact_sha256`.

This allows the project to prove:

```text
same 1,954 per-item identities
-> same corpus identity root
```

without relying only on aggregate `PASS: 1954`.

## Required Process Revision

The next process should be:

```text
1. Amend V2 to require the per-item identity baseline artifact.
2. Commit a separate authorization for baseline materialization only.
3. Generate the baseline with the frozen pre-change core.
4. Commit and review the baseline artifact.
5. Run a second V2 design review.
6. Only then decide whether Gate A can become GATE_A_DESIGN_ACCEPTED.
```

Baseline materialization is not Gate A implementation, but it is still a
research action that must be authorized explicitly:

```text
DOMAIN_1_IDENTITY_BASELINE_MATERIALIZATION_AUTHORIZED
```

Until that authorization exists:

```text
BASELINE_MATERIALIZATION_NOT_AUTHORIZED
```

## Why Accepted-With-Precondition Is Not Enough

The missing baseline is the evidence required to test V2's central promise:

```text
Domain 1 identity preserved byte-for-byte
```

Therefore this review does not use:

```text
GATE_A_DESIGN_ACCEPTED_WITH_PRECONDITION
```

The correct result is:

```text
GATE_A_NEEDS_REVISION
```

because the design must include the baseline requirement directly.

## Not Authorized

This review does not authorize:

```text
core code changes
Gate A implementation
baseline materialization
producer implementation
oracle population
corpus materialization
Gate B work
Domain 3
release claims
token, CPU, energy, or CO2 claims
```

## Next Artifact

The next artifact, if continuing, is an amendment to V2:

```text
research/domain_neutral_unification_core_interface_proposal_v2.md
```

or a versioned successor:

```text
research/domain_neutral_unification_core_interface_proposal_v3.md
```

The amendment must add the Domain 1 identity baseline requirement before any
baseline materialization or implementation work begins.
