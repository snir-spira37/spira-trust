# SPIRA Domain 4 / Nesira Flag Schema V2 Proposal Review

## Verdict

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_PROPOSAL_ACCEPTED
```

This review accepts the V2 proposal as the correct response to the V1 decision
table scope revision. It does not authorize V2 specification, Lean
implementation, Python implementation, fixtures, tests, Phase 2 work, public
claims, or release.

Reviewed artifact:

```text
research/formal_core/domain4_nesira_flag_schema_v2_proposal.md
```

## Why V2 Is Needed

The V1 decision-table attempt found:

```text
V1 booleans lose cause information.
Accepted Phase 1 sometimes branches on cause.
```

The V2 proposal correctly addresses this by replacing ambiguous booleans with
closed outcome enums where Phase 1 distinguishes causes.

## Review Findings

### 1. Outcome Enums Are the Right Shape

The proposal correctly shifts from:

```text
check passed? -> Bool
```

to:

```text
what outcome did this check produce? -> closed enum
```

This is the right representation for exact Phase 1 status/action formalization.

### 2. Minimality Rule Is Accepted

The proposal does not blindly add detail. It states:

```text
split only where accepted Phase 1 assigns different statuses/actions
```

This prevents over-modeling and keeps V2 proof-grade without becoming a
parallel product design.

### 3. Execution Meta-Stratum Is Required

The review accepts:

```text
ExecutionMeta =
  PARSED_OK
  INPUT_MALFORMED
  TOOL_ERROR
```

This fixes the category error in V1 where malformed input and validator tool
failure were both compressed into `evaluated = false`.

The guard is accepted:

```text
ordinary document-validation failure must not become TOOL_ERROR
```

### 4. N/A as Explicit Enum Value Is Required

The review accepts the proposal to represent non-applicability explicitly:

```text
HASH_NOT_APPLICABLE
PATH_NOT_APPLICABLE
TEMPORAL_NOT_APPLICABLE
...
```

This strengthens `NP-APPLIC-01`. Future consumers cannot confuse "not
applicable" with "check performed and passed."

### 5. V2 Refines V1

The review accepts the V2 -> V1 refinement invariant:

```text
each V1 boolean is a projection from V2 enums
```

This preserves the already accepted V1 claim-boundary work while allowing V2 to
serve as the proof-grade schema.

### 6. Existing Accepted Structures Are Preserved

The proposal preserves:

```text
artifact_kind branching
consulted-set discipline
Phase1Action without PROCEED
first-match total table shape
safety-critical tagging
NOT_PROVEN ledger
mutation-pair requirement
canonical serialization requirement
```

This continuity is accepted.

## Required Next Step

The next document should be:

```text
research/formal_core/domain4_nesira_flag_schema_v2_authorization.md
```

It should authorize:

```text
V2 flag schema specification
V2 decision-table specification
V2 review
```

It should not authorize:

```text
Lean implementation
proof scripts
Python changes
fixtures
fixture materialization
conformance harness implementation
Phase 2 implementation
public claims
release
```

## Not Authorized

This review does not authorize:

```text
V2 specification
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
conformance harness implementation
Phase 1 reopening
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
combined verdict integration
CLI or wheel exposure
public capability claims
release
```

## Status

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_PROPOSAL_ACCEPTED

OUTCOME_ENUMS_ACCEPTED
EXECUTION_META_STRATUM_ACCEPTED
NOT_APPLICABLE_ENUM_VALUES_ACCEPTED
V2_REFINES_V1_INVARIANT_ACCEPTED
MINIMAL_CAUSE_LEVEL_RESOLUTION_ACCEPTED

DOMAIN4_NESIRA_FLAG_SCHEMA_V2_AUTHORIZATION_REQUIRED_NEXT

V2_SPECIFICATION_NOT_AUTHORIZED
LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

