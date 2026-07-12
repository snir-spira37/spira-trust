# Domain-Neutral Unification Core Interface Proposal

## Status

```text
ARCHITECTURAL_PROPOSAL_ONLY
CORE_CHANGE_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

This proposal follows the `CORE_CHANGE_REQUIRED` result in:

```text
research/test_build_failure_contract_core_compatibility.md
```

It proposes a minimal interface change for review. It does not authorize code.

## Problem Statement

The compatibility audit found:

```text
Mathematical / cryptographic primitives: DOMAIN-NEUTRAL ENOUGH
Proof assembly contract: DOMAIN-1 SPECIFIC
Agent state interfaces: DOMAIN-1 SPECIFIC
```

The current implementation can validate claims, build a claims Merkle root,
produce inclusion proofs, and compute tagged identities over canonical inputs.

However, the current proof assembler accepts only the Python-wheel-shaped
summary/decision path:

```text
agent_summary + graph decision layers
-> build_claims()
-> python_wheel / python_wheel_set subject
-> unification proof
```

That is not a domain-neutral input interface.

Using `artifact_sha256` for pytest evidence would bind bytes but falsely label
the subject as a Python wheel. Calling lower-level Merkle primitives directly
from a producer would duplicate proof assembly outside the core.

Both are disallowed.

## Goal

Create, if later authorized, one generic proof-assembly input boundary:

```text
explicit subject
+ prevalidated SPIRA_CLAIM_V1 claims
+ explicit context binding
+ existing decision/action contract
-> existing claims root
-> existing unification identity
-> existing inclusion proofs
```

The goal is interface generalization, not new semantics.

## Non-Goals

This proposal does not authorize or propose:

```text
new action enum values
new claim status values
pytest parsing in core
test/build producer implementation
general CI-log summarization
Domain 3
orchestrator
SPIRA OS
new safety claim
new token, CPU, energy, or CO2 claim
```

## Design Split

The proposal is split into two gates.

### Proposal Gate A - Generic Proof Assembly

Gate A is the minimal core-interface change.

It would introduce an explicit proof assembly boundary that accepts:

```text
subject:
  type
  sha256

claims:
  list[SPIRA_CLAIM_V1]

context:
  policy_sha256
  context_sha256 or canonical context object
  command_fingerprint
  tool_version
  decision_semantics_version

decision:
  verdict/action_verdict
  stop
  recommended_agent_action
  reason_codes
  not_evaluated
```

It must preserve:

```text
STATUS_RANK
AGENT_ACTIONS
DECISION_SEMANTICS_VERSION unless explicitly versioned
claims Merkle algorithm
inclusion proof algorithm
tagged unification-id construction
not_evaluated visibility
BLOCK semantics
```

The existing Python-wheel flow would become a Domain 1 adapter over the generic
assembler. It may still build wheel claims from graph decision layers, but the
final proof assembly must pass through the same generic boundary used by future
domains.

### Proposal Gate B - Generic State / Cache / Rerun Context

Gate B is separate.

The audit showed that `status`, `cache`, and `rerun_planner` are also
artifact/wheel-oriented:

```text
status discovers *.whl
cache rejects non-.whl paths
rerun planner requires artifact_sha256 and wheel-shaped context fields
```

Gate B may propose domain-neutral state and exact-context reuse later, but it
must not be bundled silently into Gate A.

Possible Gate B direction:

```text
subject_sha256 instead of artifact_sha256
subject_type
context_fingerprint
domain_context fields
generic changed-subject detection
domain-specific adapters for discovery
```

Gate B requires separate tests, separate migration notes, and separate
acceptance criteria.

If Gate A is clean and Gate B is not, Gate A may still be valuable as a proof
assembly improvement. Gate B must not turn the change into an uncontrolled
state/cache refactor.

## Required Gate A Compatibility Contract

Gate A can be accepted only if all of the following are proven:

```text
1. Non-wheel subject types can be represented without false labeling.
2. Preconstructed claims can be passed into the core assembler.
3. Duplicate claim IDs still fail closed.
4. Unknown claim statuses still fail closed.
5. Missing or invalid subject SHA still fails closed.
6. Claims root is stable under claim order.
7. Inclusion proofs verify and reject mutation.
8. Action enum is unchanged.
9. Claim status enum is unchanged.
10. Existing Domain 1 output remains identity-equivalent.
```

Identity-equivalent means more than "tests pass".

For the frozen Domain 1 corpus:

```text
same action
same decision object
same claims_merkle_root
same unification_id
same compact reference
same not_evaluated preservation
same BLOCK preservation
```

The corpus baseline is:

```text
research/unification_proof_corpus/results/full_v1_public_results.json
research/unification_proof_corpus/report_v1.md
```

The Domain 1 history must remain explicit:

```text
first pass: 1,940 PASS + 14 TOOL_ERROR
closure retry on same frozen corpus: 14 / 14 PASS
final aggregate: 1,954 PASS
```

## Versioning Decision Required Before Code

Before implementation, an accepted design must decide whether the generic
assembler is:

```text
schema-compatible additive API
```

or:

```text
new proof schema / semantics version
```

No silent widening is allowed.

At minimum, the design review must answer:

```text
Does SPIRA_UNIFICATION_PROOF_V1 allow non-wheel subject.type values?
Does the context object need a new schema version?
Does the agent-facing compact reference change?
Does existing Domain 1 unification_id remain byte-identical?
```

If Domain 1 identities change, the result is not a transparent refactor. It
requires explicit migration notes and release review.

## Forbidden Shortcuts

The following do not satisfy this proposal:

```text
renaming pytest evidence to artifact_sha256
labeling test evidence as python_wheel
building a parallel proof assembler inside a pytest producer
copying Merkle code into a producer
adding pytest-specific branches to the generic core
adding a test-specific action
adding a new claim status without contract review
weakening Domain 1 tests to make the refactor pass
dropping unification_id identity checks and keeping only action checks
```

## Frozen File Manifest Required Before Implementation

Before any core code change, create:

```text
research/domain_neutral_unification_core/frozen_core_manifest.json
```

It must include:

```text
baseline commit
core file paths
SHA-256 of each frozen file
current proof schema
current reference schema
current decision semantics version
current action enum
current claim status enum
current Domain 1 corpus result files
baseline test commands
```

The minimum frozen files are:

```text
source/spira_core/unification_proof.py
source/spira_core/combined_verdict.py
source/spira_core/agent_summary.py
source/spira_core/agent_status.py
source/spira_core/agent_cache.py
source/spira_core/rerun_planner.py
docs/unification_proof.md
docs/agent_action_contract.md
research/unification_proof_corpus/report_v1.md
research/test_build_failure_contract_core_compatibility.md
```

Gate A may modify only files authorized by the accepted implementation plan.
Gate B files must remain unchanged unless Gate B is explicitly authorized.

## Required Regression Plan

Any Gate A implementation proposal must include:

```text
unit tests for generic subject input
unit tests for preconstructed claims
unit tests for non-wheel subject type preservation
unit tests for duplicate claim_id rejection
unit tests for unknown status rejection
unit tests for invalid subject hash rejection
unit tests for claim-order stability
unit tests for inclusion proof verification and mutation rejection
Domain 1 wheel-flow regression
Domain 1 frozen corpus identity regression
JSON/schema validation
privacy/path/secret scan for new public artifacts
```

The Domain 1 frozen corpus identity regression is mandatory if any code path
that generates `unification_id` changes.

## Acceptance Criteria For Gate A

Gate A may be marked accepted only if:

```text
generic proof assembly exists in the core
Domain 1 wheel flow calls the generic assembly path
Domain 2 sample claims can enter without false wheel labeling
all existing tests pass
Domain 1 identity regression passes
no action enum change occurred
no claim status enum change occurred
no pytest parsing exists in core
not_claimed boundaries remain unchanged
```

If any item fails:

```text
CORE_INTERFACE_PROPOSAL_FAIL
```

## Stop Conditions

Stop before implementation or merge if:

```text
Domain 1 unification identities change unexpectedly
generic subject type requires broad schema rewrite
state/cache/rerun changes become necessary for Gate A
pytest-specific logic enters the core
producer implementation starts before core interface acceptance
test evidence must be mislabeled to pass
the proposal cannot preserve closed action/status enums
```

A stop is a valid outcome.

## Authorization Chain

Current status:

```text
PROPOSAL_RECORDED
IMPLEMENTATION_NOT_AUTHORIZED
```

The next possible status, after review only, is one of:

```text
GATE_A_DESIGN_ACCEPTED
GATE_A_REJECTED
GATE_A_NEEDS_REVISION
```

No status in this document authorizes code.

Domain 2 producer work remains blocked until, at minimum:

```text
Gate A accepted or explicitly deemed unnecessary by review
Core compatibility re-audit passes
frozen core manifest exists
oracle schema is locked
corpus is frozen
owner explicitly authorizes producer implementation
```

## Not Claimed

This proposal does not claim:

```text
the current core is already domain-neutral
Domain 2 can be implemented now
pytest results can be safely summarized
the proof is a safety proof
the proof is a signature
the proof is zero-knowledge
cache/rerun are domain-neutral
token savings
energy savings
```

## Summary

The audit result should not be patched around.

The correct architectural move is:

```text
make proof assembly generic at the core boundary
keep domain producers outside the core
preserve Domain 1 identity exactly
keep Gate B state/cache/rerun generalization separate
authorize no producer until compatibility is proven again
```
