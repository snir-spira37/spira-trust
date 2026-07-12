# Domain-Neutral Unification Core Interface Proposal V2

## Status

```text
GATE_A_DESIGN_ACCEPTANCE_ELIGIBLE
DESIGN_PROPOSAL_ONLY
IMPLEMENTATION_NOT_AUTHORIZED
CORE_CHANGE_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
GATE_B_EXCLUDED
DOMAIN_3_NOT_AUTHORIZED
```

This V2 proposal revises:

```text
research/domain_neutral_unification_core_interface_proposal.md
```

and addresses the review findings in:

```text
research/domain_neutral_unification_core_gate_a_review.md
```

This is not implementation authorization.

## Design Verdict

```text
GATE_A_DESIGN_ACCEPTANCE_ELIGIBLE
```

The design is eligible for acceptance because it makes the identity-preserving
choice explicit:

```text
Generic interface is additive.
Legacy Domain 1 serialization is immutable.
```

If implementation cannot preserve Domain 1 byte identity, the result becomes:

```text
GATE_A_MIGRATION_REQUIRED
```

and must not be described as a transparent refactor.

## V2 Decisions

V2 locks these choices:

```text
action enum: unchanged
claim statuses: unchanged
decision semantics version: unchanged
Merkle algorithm: unchanged
inclusion algorithm: unchanged
compact reference schema and bytes: unchanged for Domain 1
Domain 1 context construction: legacy path preserved exactly
Gate B: excluded
subject.type: explicit closed registry
```

The new generic interface is an additional entry path. It is not a rewrite of
the existing Domain 1 identity construction.

## Schema Decision

Gate A is proposed as:

```text
V1-additive for proof assembly API
```

because the existing `SPIRA_UNIFICATION_PROOF_V1` shape already contains a
subject object with a `type` field and does not cryptographically require that
the value be only `python_wheel` or `python_wheel_set`.

However, Domain 1 compatibility does not rely on reinterpreting V1.

For existing wheels:

```text
legacy builder path remains byte-identical
legacy subject.type values remain unchanged
legacy context_sha256 remains unchanged
legacy compact reference remains unchanged
```

For new domains:

```text
the generic assembler may emit SPIRA_UNIFICATION_PROOF_V1
only if it uses a registered subject.type and the unchanged proof primitives
```

If review later finds that V1 documentation is effectively wheel-only, the
status changes to:

```text
GATE_A_MIGRATION_REQUIRED
```

and the design must move to a versioned proof schema before code.

## Decision Semantics

The decision semantics version remains:

```text
SPIRA_DECISION_SEMANTICS_V2
```

Gate A does not change:

```text
stop semantics
recommended_agent_action semantics
reason_codes semantics
not_evaluated semantics
BLOCK semantics
```

If an implementation needs a new decision semantics version, this V2 proposal
is not accepted as written and becomes:

```text
GATE_A_MIGRATION_REQUIRED
```

## Subject Type Registry

`subject.type` is not free text.

Gate A V2 permits only this initial registry:

```text
python_wheel
python_wheel_set
pytest_test_run
pytest_test_evidence_set
```

Rules:

```text
unknown subject.type -> fail closed
aliases are not allowed
case normalization is not allowed
producer-specific subject.type strings are not allowed
```

Future subject types require an explicit registry update and review.

## Generic Proof Assembly Interface

The generic interface may accept:

```text
subject:
  type
  sha256

claims:
  list[SPIRA_CLAIM_V1]

context:
  context_sha256
  policy_sha256
  command_fingerprint
  tool_version
  decision_semantics_version

decision:
  verdict
  graph_verdict
  combined_verdict
  action_verdict
  stop
  recommended_agent_action
  reason_codes
  not_evaluated
```

For Gate A, `context_sha256` is an explicit input. The generic assembler must
not silently canonicalize a context object for Domain 1 compatibility.

New domains may define their own canonical context object later, but that is
outside the Domain 1 identity-preservation path.

## Domain 1 Legacy Identity Path

For existing Python-wheel evidence, the legacy path is immutable.

The following construction must remain byte-for-byte equivalent to the current
baseline:

```text
summary + decision
-> existing build_claims() output
-> existing canonical claim bytes
-> existing claims_merkle_root
-> existing context_sha256 construction
-> existing decision object construction
-> existing unification_id
-> existing compact reference
```

V2 does not authorize "cleaning up" the Domain 1 context object, renaming
fields, reordering fields in the decision object, or replacing existing
context hashing with a generic serializer.

The Domain 1 adapter may call the generic assembler only if it passes values
that preserve the exact existing outputs.

## Required Identity Equivalence

For every item in the frozen 1,954-wheel Domain 1 corpus, implementation must
prove:

```text
same canonical claims bytes
same claims_merkle_root
same context_sha256
same decision object canonical bytes
same unification_id
same compact reference bytes
same action
same reason_codes
same not_evaluated
same BLOCK behavior
```

The comparison is not merely semantic.

Where the current contract emits bytes, the comparison is byte-for-byte after
the same canonicalization rules used by the baseline.

## Baseline Identity Artifacts

The implementation plan must freeze these baseline artifacts before code:

```text
research/unification_proof_corpus/results/full_v1_public_results.json
research/unification_proof_corpus/report_v1.md
research/unification_proof_corpus/results/materialized_v1_2026-07-12.json
```

For each corpus item, the regression must compare at least:

```text
unification_proof.json canonical bytes, excluding created_at
agent_summary.json unification reference canonical bytes
claims_merkle_root
context_sha256
unification_id
decision object
action
reason_codes
not_evaluated
coverage.worst_claim_status
```

The Domain 1 history must remain explicit:

```text
first pass: 1,940 PASS + 14 TOOL_ERROR
closure retry on same frozen corpus: 14 / 14 PASS
final aggregate: 1,954 PASS
```

## Compact Reference Preservation

The compact reference remains unchanged:

```json
{
  "id": "...",
  "root": "...",
  "p": "unification_proof.json"
}
```

No field may be added, removed, renamed, or reordered in a way that changes
the canonical bytes for existing Domain 1 summaries.

For new domains, the same compact reference shape is used.

## Gate B Exclusion

Gate B remains excluded.

Gate A does not change:

```text
agent_status.py
agent_cache.py
rerun_planner.py
state directory layout
cache key semantics
status discovery semantics
rerun context field names
```

Those interfaces are still Domain 1 specific until a separate Gate B proposal
is reviewed and authorized.

Gate A may mention that a proof exists for a non-wheel subject. It may not
claim generic cache/status/rerun support.

## Design Acceptance Criteria

This proposal may be marked design-accepted only if review agrees that:

```text
1. Gate A is additive.
2. Domain 1 legacy serialization is immutable.
3. context_sha256 is preserved by explicit pass-through for Domain 1.
4. subject.type is governed by the closed registry.
5. action enum remains unchanged.
6. claim status enum remains unchanged.
7. decision semantics version remains unchanged.
8. compact reference remains unchanged.
9. Gate B remains excluded.
10. failure to preserve identity produces GATE_A_MIGRATION_REQUIRED.
```

Design acceptance still does not authorize code.

## Implementation Acceptance Criteria

If implementation is later explicitly authorized, it must pass:

```text
all existing unit tests
generic subject input tests
preconstructed claim input tests
subject.type registry tests
unknown subject.type fail-closed test
duplicate claim_id fail-closed test
unknown claim status fail-closed test
invalid subject hash fail-closed test
claim-order invariance test
inclusion proof verification and mutation rejection tests
Domain 1 frozen corpus identity regression
JSON validation
privacy/path/secret scan for public artifacts
```

The Domain 1 frozen corpus identity regression is mandatory.

If any Domain 1 identity differs unexpectedly:

```text
GATE_A_MIGRATION_REQUIRED
```

## Forbidden Shortcuts

```text
renaming test evidence as artifact_sha256
labeling test evidence as python_wheel
changing Domain 1 context hashing
canonicalizing Domain 1 context through a new serializer
changing compact reference shape
adding a test-specific action
adding a claim status
moving Gate B changes into Gate A
copying Merkle or unification assembly into a producer
dropping identity regression and checking only action equivalence
```

## Next Required Artifacts

If this design is accepted later, implementation still requires:

```text
1. frozen core manifest
2. Domain 1 identity regression plan
3. explicit owner authorization
4. explicit implementation authorization status
```

The required implementation authorization status is not present in this
document.

Until it exists in a separate committed authorization record:

```text
IMPLEMENTATION_NOT_AUTHORIZED
```

## Not Claimed

This V2 proposal does not claim:

```text
the code already implements a generic interface
Domain 2 can be implemented now
Gate B is solved
cache/status/rerun are domain-neutral
pytest evidence is safe to summarize
the proof is a safety proof
the proof is a signature
the proof is zero-knowledge
token savings
energy savings
```

## Final V2 Position

```text
Gate A design: acceptance-eligible
Gate A code: not authorized
Domain 1 identity: must remain byte-identical
Domain 2 producer: blocked
Gate B: excluded
```

The design is acceptable only as an identity-preserving additive interface.

If the implementation cannot preserve existing Domain 1 proof identities, the
correct next status is:

```text
GATE_A_MIGRATION_REQUIRED
```
