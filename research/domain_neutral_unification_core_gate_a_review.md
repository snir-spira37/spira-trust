# Domain-Neutral Unification Core Gate A Review

## Status

```text
GATE_A_NEEDS_REVISION
DESIGN_REVIEW_ONLY
IMPLEMENTATION_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

This is a cold design review of:

```text
research/domain_neutral_unification_core_interface_proposal.md
```

It does not review code, because no Gate A code is authorized.

## Reviewed Baseline

```text
proposal_commit: 4f1dad5af21a1a6b467ce81ae98a21fab56d4728
proposal_status: ARCHITECTURAL_PROPOSAL_ONLY
compatibility_audit: research/test_build_failure_contract_core_compatibility.md
compatibility_result: CORE_CHANGE_REQUIRED
```

## Verdict

```text
GATE_A_NEEDS_REVISION
```

The proposed direction is architecturally sound:

```text
explicit subject
+ prevalidated claims
+ explicit context binding
+ existing decision/action contract
-> generic proof assembly
```

However, the design is not yet precise enough to accept. It leaves several
identity-critical choices unresolved, and those choices are exactly where a
"same action but different proof identity" regression could hide.

The next artifact should be a revised proposal, not implementation.

## Review Criteria

### 1. Minimality

```text
Result: PASS_WITH_CLARIFICATION_REQUIRED
```

Gate A is correctly scoped to proof assembly rather than pytest parsing,
producer work, or broad orchestration.

The minimal target is valid:

```text
accept subject
accept claims
accept context
accept decision
reuse existing proof primitives
```

Clarification required:

```text
The proposal must distinguish design acceptance from implementation acceptance.
```

The current proposal includes an "Acceptance Criteria For Gate A" section that
requires a generic proof assembler to exist. That is an implementation
acceptance condition, not a design-review condition.

Revision required:

```text
split "Design Acceptance Criteria" from "Implementation Acceptance Criteria"
```

### 2. Separation

```text
Result: PASS
```

The proposal correctly separates:

```text
Gate A: generic proof assembly
Gate B: generic status/cache/rerun context
```

It explicitly states that Gate B must not be bundled silently into Gate A.

This is the strongest part of the proposal. It prevents a small interface
change from turning into an uncontrolled state/cache/rerun refactor.

### 3. Contract Preservation

```text
Result: NEEDS_REVISION
```

The proposal correctly says that the following must be preserved:

```text
action enum
claim status enum
claims Merkle algorithm
inclusion proof algorithm
not_evaluated visibility
BLOCK semantics
```

But it leaves two contract questions unresolved:

```text
Does SPIRA_UNIFICATION_PROOF_V1 explicitly allow non-wheel subject.type values?
Does Gate A require a new schema version or remain additive under V1?
```

The proposal names those questions, but does not answer them. Gate A design
cannot be accepted until the design selects one path.

Revision required:

```text
Declare whether Gate A is V1-additive or introduces a versioned proof schema.
Declare whether decision semantics version remains byte-for-byte unchanged.
Declare whether any agent-facing reference field changes.
```

The preferred design-review target is:

```text
no action enum change
no claim status change
no decision semantics change
no Merkle/inclusion algorithm change
no compact reference shape change
```

If any of those change, the proposal must say so explicitly and move out of
"minimal interface" territory.

### 4. Domain 1 Identity Preservation

```text
Result: NEEDS_REVISION
```

The proposal correctly requires identity equivalence over the frozen 1,954
wheel corpus:

```text
same decision object
same claims_merkle_root
same unification_id
same compact reference
same action / reasons / NOT_EVALUATED / BLOCK
```

The central unresolved risk is context canonicalization.

The proposed Gate A input allows:

```text
context_sha256 or canonical context object
```

That `or` is too loose for a byte-for-byte identity-preservation design. If the
Domain 1 adapter passes a precomputed `context_sha256`, identity may be
preserved. If it passes a canonical context object and the new generic
assembler serializes it even slightly differently, the action may remain the
same while `unification_id` changes.

Revision required:

```text
Specify exactly how Domain 1 context_sha256 is preserved.
Specify whether the generic assembler accepts precomputed context_sha256,
canonicalizes context itself, or supports both under separate modes.
For Domain 1 compatibility, define the exact byte-equivalence path.
```

Design acceptance requires a concrete statement such as:

```text
Domain 1 compatibility mode passes the existing context_sha256 unchanged.
Generic context canonicalization is allowed only for new domains or under a
versioned identity change.
```

Without that, "same action" could pass while proof identity silently changes.

### 5. Domain Neutrality

```text
Result: PASS_WITH_CLARIFICATION_REQUIRED
```

The proposal correctly forbids:

```text
pytest parsing in core
false python_wheel labeling
parallel proof assembler inside producer
test-specific action values
```

The domain-neutral direction is sound.

Clarification required:

```text
The subject type vocabulary must be governed.
```

Gate A should not allow arbitrary free-text subject types without a versioned
contract or registry rule. Otherwise two producers may use different strings
for the same concept and create non-comparable proof identities.

Revision required:

```text
Define subject.type validation policy:
  closed enum,
  namespaced string convention,
  or documented registry.
```

The review does not require choosing a large registry. A minimal namespaced
rule is enough, for example:

```text
python_wheel
python_wheel_set
pytest_test_run
pytest_test_evidence_set
```

But the rule must be explicit before design acceptance.

## Central Risk

The central risk is not action preservation.

It is identity drift:

```text
same action
same claims
slightly different context serialization
-> different unification_id
```

That would make the refactor semantically successful but historically
incompatible with Domain 1 evidence memory.

Therefore, a future Gate A implementation plan must treat byte-for-byte
identity preservation as a first-class test target, not as a side effect of
ordinary unit tests.

## Required Revisions

The proposal needs these revisions before design acceptance:

```text
1. Split design acceptance from implementation acceptance.
2. Decide V1-additive versus versioned proof schema.
3. Decide whether decision semantics version remains unchanged.
4. Specify exact Domain 1 context_sha256 preservation path.
5. Define subject.type validation or registry policy.
6. State whether compact unification reference shape remains unchanged.
7. Define the exact baseline artifacts for byte-for-byte identity comparison.
```

## What Already Looks Correct

The proposal should keep:

```text
Gate A / Gate B separation
no producer authorization
no pytest code in core
no action enum expansion
no claim status expansion
no direct use of Merkle primitives from producers as a substitute for core assembly
Domain 1 frozen corpus identity regression requirement
explicit not_claimed boundaries
```

## Not Authorized

This review does not authorize:

```text
core code changes
producer implementation
oracle population
corpus materialization
Gate B work
Domain 3
release claims
token, CPU, energy, or CO2 claims
```

## Next Step

The next artifact, if continuing, is:

```text
research/domain_neutral_unification_core_interface_proposal_v2.md
```

It should address only the required revisions above.

No implementation may begin from this review.
