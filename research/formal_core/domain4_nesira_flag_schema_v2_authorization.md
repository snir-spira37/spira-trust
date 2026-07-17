# SPIRA Domain 4 / Nesira Flag Schema V2 Authorization

## Verdict

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_SPECIFICATION_AUTHORIZED
```

This authorization opens a narrow paper-only specification step for the
accepted Domain 4 / Nesira V2 flag-schema proposal. It authorizes writing the
V2 outcome-enum schema, the V2 decision table, and their traceability review.

It does not authorize Lean implementation, Lean proof scripts, Python changes,
fixture materialization, conformance-harness implementation, Phase 1 reopening,
Phase 2 implementation, product integration, public claims, or release work.

## Document Type

```text
DOCUMENT_TYPE: AUTHORIZATION
AUTHORIZES: V2 specification and V2 decision-table design only
PHASE: PHASE_2_RESEARCH
CODE: NOT_AUTHORIZED
LEAN: NOT_AUTHORIZED
PYTHON: NOT_AUTHORIZED
FIXTURES: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

## Prior Accepted Inputs

This authorization depends on the accepted V2 proposal and review:

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_PROPOSAL_ACCEPTED

proposal:
research/formal_core/domain4_nesira_flag_schema_v2_proposal.md

proposal review:
research/formal_core/domain4_nesira_flag_schema_v2_proposal_review.md
```

It also incorporates the scope-revision finding from:

```text
DOMAIN4_NESIRA_DECISION_TABLE_V1_NEEDS_REVISION
SCOPE_REVISION_REQUIRED
FLAGS_V1_INSUFFICIENT_FOR_EXACT_PHASE1_DECISION_TABLE

review:
research/formal_core/domain4_nesira_decision_table_v1_review.md
```

The accepted V1 artifacts remain frozen. V2 refines V1; it does not edit V1 in
place.

## Authorized Outputs

This authorization permits creating only the following paper artifacts under
`research/formal_core/`:

```text
research/formal_core/domain4_nesira_flag_schema_v2_spec.md
research/formal_core/domain4_nesira_flag_schema_v2.json
research/formal_core/domain4_nesira_flag_schema_v2_review.md
research/formal_core/domain4_nesira_decision_table_v2_spec.md
research/formal_core/domain4_nesira_decision_table_v2_review.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.json
```

No other file may be created or modified under this authorization. If another
artifact is required, this stage must stop and request a separate
authorization.

## Frozen Inputs

The following artifacts are frozen and must not be edited in this stage:

```text
SPIRA_NESIRA_DOMAIN4_FLAGS_V1
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
Domain4 / Nesira formal-core proposal and review
Domain4 / Nesira flag-schema V2 proposal and review
all accepted Nesira Phase 1 implementation, fixture, result, and reproduction artifacts
```

The V2 specification may reference and refine these artifacts, but it may not
silently alter their claims, statuses, or scope.

## Required V2 Invariants

The V2 specification and decision table must preserve all accepted V2 proposal
invariants:

```text
OUTCOME_ENUMS:
  every check whose cause changes accepted Phase 1 status/action must be a
  closed outcome enum, not a boolean.

EXECUTION_META_STRATUM:
  PARSED_OK, INPUT_MALFORMED, and TOOL_ERROR must be modeled before per-check
  outcomes.

DOCUMENT_FAILURE_NOT_TOOL_ERROR:
  ordinary document-validation failure must never be represented as TOOL_ERROR.
  TOOL_ERROR is reserved for validator/tool failure.

NOT_APPLICABLE_AS_ENUM:
  non-applicability must be represented by explicit enum values, not by an
  overloaded boolean true.

V2_REFINES_V1:
  every V1 boolean flag must be a total projection from V2 enum values.

MINIMAL_CAUSE_RESOLUTION:
  split enum values only where accepted Phase 1 assigns a different
  status/action or where the V2 -> V1 projection requires the distinction.

CONSULTED_SET_ARTIFACT_KIND_DISCIPLINE:
  artifact_kind branching and consulted-flag discipline must be preserved.

PHASE1ACTION_NO_PROCEED:
  the Phase 1 action type must still have no PROCEED constructor.

FIRST_MATCH_TOTAL:
  the V2 decision table must be deterministic and total over all legal V2
  tuples and execution meta states.

LEDGER_BACKED_REASON_CODES:
  every structural status, reason code, not_evaluated entry, and not_claimed
  entry must be backed either by accepted Phase 1 behavior or by a
  NOT_PROVEN_IN_LEAN ledger id.

SAFETY_CRITICAL_TAGGING:
  safety-critical status must be assigned to every enum value whose false
  classification could produce a false VALID or an unsafe weakening.
```

## Required Traceability

Every V2 enum value and every V2 decision-table row must carry an explicit
source:

```text
derived_from: <accepted Phase 1 file/function/branch/result that determines the behavior>
```

If accepted Phase 1 behavior does not determine an enum value, precedence rule,
status, action, or reason-code mapping, the specification or review must stop
with:

```text
SCOPE_REVISION_REQUIRED
```

This authorization does not permit filling gaps by judgment, taste, or inferred
future behavior. "Obvious" is not a source.

## Required Phase 1 Outcome Traceability Matrix

The V2 specification package must include a bidirectional traceability matrix
covering accepted Phase 1 behavior.

For every Phase 1 output shape that can be produced by the accepted validator:

```text
validation_status
recommended_agent_action
reason_code / reason_codes
not_evaluated
not_claimed
stop
```

the matrix must identify:

```text
the V2 execution meta state or enum tuple
the V2 decision-table row
the accepted Phase 1 source that produced the mapping
the V1 projection, when applicable
the NOT_PROVEN_IN_LEAN ledger ids, when applicable
```

The matrix must also prove the reverse direction:

```text
every V2 enum value and decision-table row is derived from accepted Phase 1
behavior or is explicitly blocked by SCOPE_REVISION_REQUIRED.
```

Acceptance requires:

```text
unmapped Phase 1 outcomes: 0
invented V2 outcomes: 0
decision rows without derived_from: 0
```

## Required V2 -> V1 Projection

The V2 schema must define a total projection from V2 to V1 for each accepted V1
boolean flag:

```text
schema_valid
evidence_present
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
context_match
temporal_binding_ok
evaluated
```

Each projection must state:

```text
V2 enum values that project to true
V2 enum values that project to false
why NOT_APPLICABLE values project as they do
which NP-APPLIC ledger entries prevent overclaim
```

The V2 review must reject the package if any V1 flag lacks a total projection.

## Required Decision-Table Properties

The V2 decision-table specification must define:

```text
execution-meta precedence
artifact_kind branching
consulted enum set per artifact_kind
first-match precedence
status projection
Phase1Action projection
stop value
reason-code precedence
blocking_items behavior
not_evaluated behavior
not_claimed behavior
simultaneous-failure determinism
total final case
```

The table must reproduce accepted Phase 1 semantics. It is not authorized to
invent new product behavior, broaden trust, or introduce any PROCEED-capable
path.

## Review Requirements

The V2 review must be adversarial. It must verify at least:

```text
1. Every required invariant in this authorization is satisfied.
2. Every enum value has a stable name, closed membership, and derived_from.
3. Every decision-table row has derived_from or SCOPE_REVISION_REQUIRED.
4. The Phase 1 outcome traceability matrix is complete in both directions.
5. V2 -> V1 projection is total for every V1 flag.
6. Minimality holds: no enum split exists if both branches always map to the
   same accepted Phase 1 status/action and are not needed for V1 projection.
7. Determinism and totality hold under execution meta states plus enum tuples.
8. No enum value, status, reason code, or positive claim asserts signature
   validity, signer authority, actual isolation execution, permission to sever,
   production readiness, or release readiness.
9. NOT_APPLICABLE values cannot be read as "check performed."
10. Ordinary document-validation failures cannot be classified as TOOL_ERROR.
```

## Not Authorized

This authorization does not authorize:

```text
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
version bump
tag
PyPI
```

## Required Review Outcomes

The V2 review must end in exactly one of:

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_ACCEPTED
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_NEEDS_REVISION
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_REJECTED
```

Even `ACCEPTED` does not authorize Lean implementation, proof scripts, Python
implementation, fixtures, conformance-harness implementation, Phase 2 work,
public claims, or release. It only permits a later, separate authorization
request.

## Status

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_SPECIFICATION_AUTHORIZED

OUTCOME_ENUM_SCHEMA_SPECIFICATION_AUTHORIZED
EXECUTION_META_STRATUM_SPECIFICATION_AUTHORIZED
NOT_APPLICABLE_ENUM_VALUES_REQUIRED
V2_REFINES_V1_INVARIANT_REQUIRED
MINIMAL_CAUSE_LEVEL_RESOLUTION_REQUIRED
DECISION_TABLE_V2_SPECIFICATION_AUTHORIZED
PHASE1_OUTCOME_TRACEABILITY_MATRIX_REQUIRED
DERIVED_FROM_REQUIRED_FOR_EVERY_ENUM_AND_TABLE_ROW
V2_REVIEW_REQUIRED

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
