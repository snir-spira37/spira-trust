# Domain-Neutral Unification Core Interface Proposal V3

## Status

```text
GATE_A_DESIGN_ACCEPTANCE_ELIGIBLE
DESIGN_PROPOSAL_ONLY
BASELINE_MATERIALIZATION_NOT_YET_AUTHORIZED
IMPLEMENTATION_NOT_AUTHORIZED
CORE_CHANGE_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
GATE_B_EXCLUDED
DOMAIN_3_NOT_AUTHORIZED
```

This V3 proposal supersedes:

```text
research/domain_neutral_unification_core_interface_proposal_v2.md
```

It addresses the blocking finding in:

```text
research/domain_neutral_unification_core_gate_a_v2_review.md
```

V3 is still a design proposal only. It does not authorize code or baseline
materialization.

## Inherited V2 Contract

V3 inherits the V2 identity-preservation contract:

```text
Generic interface is additive.
Legacy Domain 1 serialization is immutable.
```

The following remain unchanged:

```text
action enum
claim statuses
decision semantics version: SPIRA_DECISION_SEMANTICS_V2
Merkle algorithm
inclusion algorithm
compact reference schema and bytes
Domain 1 context construction
Gate B exclusion
subject.type closed registry
```

The allowed initial `subject.type` registry remains:

```text
python_wheel
python_wheel_set
pytest_test_run
pytest_test_evidence_set
```

Unknown subject types fail closed. Aliases, case normalization, and
producer-specific subject type strings are not allowed.

## New V3 Requirement

No Gate A implementation may begin until a committed, reviewed, per-wheel
Domain 1 identity baseline exists.

The required artifact is:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

This artifact must be generated from the frozen pre-change core.

It must be committed and reviewed before any Gate A code change.

## Baseline Artifact Schema

The baseline artifact must include top-level metadata:

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

It must include exactly 1,954 per-wheel identity records unless the
materialization process stops with `DOMAIN_1_IDENTITY_BASELINE_NOT_MATERIALIZABLE`.

Each per-wheel record must include:

```text
artifact_sha256
canonical_claims_bytes_sha256
claims_merkle_root
context_sha256
canonical_decision_bytes_sha256
unification_id
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
stop
recommended_agent_action
reason_codes
not_evaluated
worst_claim_status
```

## Canonicalization Contract

The baseline must lock the comparison rules before Gate A implementation.

For proof bytes, the artifact must use exactly one declared rule:

```text
hash canonical proof excluding declared volatile fields
```

or:

```text
hash stable proof identity projection
```

The selected rule must be recorded in `canonicalization_contract`.

The rule may not be changed after Gate A implementation results are observed.

The compact reference must be hashed as canonical bytes, not as decoded fields.
This catches changes in:

```text
field names
field presence
serialization
canonical ordering
path value
```

## Corpus Identity Root

The baseline must include:

```text
domain1_identity_baseline_root
```

It is computed from all per-wheel identity records after sorting by
`artifact_sha256`.

This makes the corpus-level identity claim testable:

```text
same 1,954 per-item identities
-> same domain1_identity_baseline_root
```

## Required Identity Preservation

Gate A implementation, if later authorized, must preserve for all 1,954 Domain
1 records:

```text
same canonical claims bytes
same claims_merkle_root
same context_sha256
same canonical decision bytes
same unification_id
same compact reference bytes
same canonical proof bytes under the declared volatile-field rule
same stop
same recommended_agent_action
same reason_codes
same not_evaluated
same worst_claim_status
same domain1_identity_baseline_root
```

If any required identity changes unexpectedly:

```text
GATE_A_MIGRATION_REQUIRED
```

and the work must not be described as a transparent refactor.

## Authorization Separation

V3 committed does not authorize baseline generation.

Baseline generated does not mean Gate A design accepted.

Gate A design accepted does not authorize implementation.

The only possible next authorization after V3 is a separate committed record:

```text
DOMAIN_1_IDENTITY_BASELINE_MATERIALIZATION_AUTHORIZED
```

That authorization may allow only:

```text
read the frozen Domain 1 corpus
run the existing frozen core without modification
extract hashes and identities
write domain1_identity_baseline_v1.json
validate the baseline artifact
document the result
```

It must not allow:

```text
core refactor
generic assembler implementation
Domain 2 producer
oracle population
new corpus selection
Gate B work
Domain 3 work
```

## Baseline Stop Condition

If the required identity data cannot be reconstructed for all 1,954 corpus
items from the frozen pre-change material:

```text
DOMAIN_1_IDENTITY_BASELINE_NOT_MATERIALIZABLE
```

In that state:

```text
do not infer missing identities
do not replace corpus cases
do not lower the required record count
do not begin Gate A implementation
return to methodology review
```

## Process After V3

The required sequence is:

```text
1. Commit V3.
2. Commit separate baseline-materialization authorization.
3. Generate baseline from frozen pre-change core.
4. Commit baseline artifact.
5. Review baseline artifact.
6. Run final Gate A design review.
7. Only then decide whether GATE_A_DESIGN_ACCEPTED is justified.
```

No step implies the next one.

## Design Acceptance Criteria

Gate A design may be accepted only after:

```text
V3 is committed
domain1_identity_baseline_v1.json is committed
baseline artifact review passes
the baseline contains 1,954 records
domain1_identity_baseline_root is present
canonicalization_contract is frozen
volatile_fields_excluded is explicit
no implementation has begun
```

Until then:

```text
GATE_A_DESIGN_ACCEPTANCE_ELIGIBLE
```

but not:

```text
GATE_A_DESIGN_ACCEPTED
```

## Not Authorized

This V3 proposal does not authorize:

```text
baseline materialization
core code changes
Gate A implementation
producer implementation
oracle population
corpus materialization
Gate B work
Domain 3
release claims
token, CPU, energy, or CO2 claims
```

## Final V3 Position

```text
Gate A design: acceptance-eligible
Gate A implementation: not authorized
Baseline materialization: not yet authorized
Domain 1 identity evidence: required before acceptance
Domain 2 producer: blocked
Gate B: excluded
```

V3 defines what must be preserved and what evidence must exist before the
design can be accepted.
