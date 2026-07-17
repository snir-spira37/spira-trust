# SPIRA Domain 4 / Nesira Flag Schema V2 Proposal

## Status

```text
DOCUMENT_TYPE: RESEARCH_PROPOSAL
PROPOSAL_ID: SPIRA_NESIRA_DOMAIN4_FLAG_SCHEMA_V2_PROPOSAL
IMPLEMENTATION: NOT_AUTHORIZED
V2_SPECIFICATION: NOT_AUTHORIZED_IN_THIS_DOCUMENT
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
FIXTURE_CHANGES: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This proposal responds to:

```text
DOMAIN4_NESIRA_DECISION_TABLE_V1_NEEDS_REVISION
SCOPE_REVISION_REQUIRED
FLAGS_V1_INSUFFICIENT_FOR_EXACT_PHASE1_DECISION_TABLE
```

It proposes a proof-grade V2 flag schema. It does not implement or freeze V2.

## Diagnosis

`SPIRA_NESIRA_DOMAIN4_FLAGS_V1` is valid for claim-boundary hygiene, but it is
too coarse to reproduce the exact accepted Phase 1 decision table. V1 booleans
answer:

```text
did this check pass?
```

Accepted Phase 1 sometimes decides based on:

```text
why did this check fail?
```

Different causes can produce different statuses and actions. Therefore a
proof-grade schema must carry cause-level outcomes, not only booleans.

## Design Principle

```text
Use closed outcome enums.

Split a V1 boolean into multiple V2 enum values only where accepted Phase 1
assigns different statuses/actions to different causes.

Do not add enum values that Phase 1 does not distinguish.
```

V2 must be:

```text
no coarser than Phase 1
no finer than Phase 1
```

## Stratum 0: Validator Execution Meta-State

Some outcomes are not properties of the artifact. They are properties of the
validator execution path. V2 must model this separately.

```text
ExecutionMeta =
  PARSED_OK
  INPUT_MALFORMED
  TOOL_ERROR
```

Meaning:

```text
PARSED_OK:
  the validator reached the per-check outcome layer

INPUT_MALFORMED:
  the input could not be parsed/decoded enough to enter the per-check layer
  according to accepted Phase 1 behavior

TOOL_ERROR:
  the validator itself failed unexpectedly; this must not be used for ordinary
  document-validation failures
```

Required guard:

```text
Document-validation failure must not be classified as TOOL_ERROR.
TOOL_ERROR is reserved for validator/tool failure.
```

## Stratum 1: Per-Check Outcome Enums

V2 should replace ambiguous booleans with closed enums where Phase 1 requires
cause-level discrimination.

### Schema Outcome

Candidate enum:

```text
SchemaOutcome =
  SCHEMA_OK
  SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION
  SCHEMA_STRUCTURAL_VIOLATION
```

Intended mapping:

```text
SCHEMA_OK -> continue
SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION -> RERUN_REQUIRED
SCHEMA_STRUCTURAL_VIOLATION -> INVALID
```

This refines V1:

```text
schema_valid = (schema_outcome == SCHEMA_OK)
```

The final V2 spec must derive the exact membership of each enum value from
accepted Phase 1 code and fixtures.

### Context Outcome

Candidate enum:

```text
ContextOutcome =
  CONTEXT_OK
  CONTEXT_EXPECTED_MISSING
  CONTEXT_MISMATCH
```

Intended mapping:

```text
CONTEXT_OK -> continue
CONTEXT_EXPECTED_MISSING -> NOT_EVALUATED
CONTEXT_MISMATCH -> RERUN_REQUIRED
```

This refines V1:

```text
context_match = (context_outcome == CONTEXT_OK)
```

### Temporal Outcome

Candidate enum:

```text
TemporalOutcome =
  TEMPORAL_OK
  TEMPORAL_NOT_APPLICABLE
  TEMPORAL_INVALID_OR_EXPIRED
```

Intended mapping:

```text
TEMPORAL_OK -> continue
TEMPORAL_NOT_APPLICABLE -> ignored under artifact_kind branch
TEMPORAL_INVALID_OR_EXPIRED -> RERUN_REQUIRED
```

This refines V1:

```text
temporal_binding_ok =
  temporal_outcome == TEMPORAL_OK
  OR temporal_outcome == TEMPORAL_NOT_APPLICABLE
```

### Evidence Presence Outcome

Candidate enum:

```text
EvidencePresenceOutcome =
  EVIDENCE_PRESENT
  EVIDENCE_NOT_APPLICABLE
  EVIDENCE_MISSING
```

Intended mapping:

```text
EVIDENCE_PRESENT -> continue
EVIDENCE_NOT_APPLICABLE -> ignored under artifact_kind branch
EVIDENCE_MISSING -> NOT_EVALUATED
```

This refines V1:

```text
evidence_present =
  evidence_presence_outcome == EVIDENCE_PRESENT
  OR evidence_presence_outcome == EVIDENCE_NOT_APPLICABLE
```

### Evidence Hash Outcome

Candidate enum:

```text
HashOutcome =
  HASH_OK
  HASH_NOT_APPLICABLE
  HASH_MISMATCH
```

Intended mapping:

```text
HASH_OK -> continue
HASH_NOT_APPLICABLE -> ignored under artifact_kind branch
HASH_MISMATCH -> INVALID
```

This refines V1:

```text
hash_ok =
  hash_outcome == HASH_OK
  OR hash_outcome == HASH_NOT_APPLICABLE
```

Unlike V1, `HASH_NOT_APPLICABLE` cannot be misread as a performed hash check.

### Path Outcome

Candidate enum:

```text
PathOutcome =
  PATH_OK
  PATH_NOT_APPLICABLE
  PATH_UNSAFE
```

Intended mapping:

```text
PATH_OK -> continue
PATH_NOT_APPLICABLE -> ignored under artifact_kind branch
PATH_UNSAFE -> INVALID
```

This refines V1:

```text
path_safe =
  path_outcome == PATH_OK
  OR path_outcome == PATH_NOT_APPLICABLE
```

### Symlink Outcome

Candidate enum:

```text
SymlinkOutcome =
  SYMLINK_OK
  SYMLINK_NOT_APPLICABLE
  SYMLINK_ESCAPE
```

Intended mapping:

```text
SYMLINK_OK -> continue
SYMLINK_NOT_APPLICABLE -> ignored under artifact_kind branch
SYMLINK_ESCAPE -> INVALID
```

This refines V1:

```text
symlink_escape_absent =
  symlink_outcome == SYMLINK_OK
  OR symlink_outcome == SYMLINK_NOT_APPLICABLE
```

### Duplicate Path Outcome

Candidate enum:

```text
DuplicatePathOutcome =
  DUPLICATE_PATH_FREE
  DUPLICATE_PATH_NOT_APPLICABLE
  DUPLICATE_PATH_PRESENT
```

Intended mapping:

```text
DUPLICATE_PATH_FREE -> continue
DUPLICATE_PATH_NOT_APPLICABLE -> ignored under artifact_kind branch
DUPLICATE_PATH_PRESENT -> INVALID
```

This refines V1:

```text
duplicate_path_free =
  duplicate_path_outcome == DUPLICATE_PATH_FREE
  OR duplicate_path_outcome == DUPLICATE_PATH_NOT_APPLICABLE
```

### Regular File Outcome

Candidate enum:

```text
RegularFileOutcome =
  REGULAR_FILE_OK
  REGULAR_FILE_NOT_APPLICABLE
  DIRECTORY_OR_NON_REGULAR_FILE
```

Intended mapping:

```text
REGULAR_FILE_OK -> continue
REGULAR_FILE_NOT_APPLICABLE -> ignored under artifact_kind branch
DIRECTORY_OR_NON_REGULAR_FILE -> INVALID
```

This refines V1:

```text
directory_not_file_absent =
  regular_file_outcome == REGULAR_FILE_OK
  OR regular_file_outcome == REGULAR_FILE_NOT_APPLICABLE
```

## Artifact Kind Branching

V2 keeps the accepted `artifact_kind` branching discipline:

```text
SEVERANCE_AUTHORIZATION:
  consumes schema_outcome
  consumes context_outcome
  consumes temporal_outcome
  does not consume evidence/path/hash/symlink/duplicate/regular-file outcomes

LEGACY_ISOLATION_RESULT:
  consumes schema_outcome
  consumes context_outcome
  consumes evidence_presence_outcome
  consumes path_outcome
  consumes symlink_outcome
  consumes duplicate_path_outcome
  consumes regular_file_outcome
  consumes hash_outcome
  does not consume temporal_outcome
```

The N/A cases become explicit enum values rather than `true` booleans.

This strengthens:

```text
NP-APPLIC-01
```

from a ledger guard to a type-level distinction.

## V2 Refines V1

V2 must project cleanly onto the accepted V1 schema:

```text
schema_valid =
  schema_outcome == SCHEMA_OK

context_match =
  context_outcome == CONTEXT_OK

temporal_binding_ok =
  temporal_outcome == TEMPORAL_OK
  OR temporal_outcome == TEMPORAL_NOT_APPLICABLE

evidence_present =
  evidence_presence_outcome == EVIDENCE_PRESENT
  OR evidence_presence_outcome == EVIDENCE_NOT_APPLICABLE

hash_ok =
  hash_outcome == HASH_OK
  OR hash_outcome == HASH_NOT_APPLICABLE

path_safe =
  path_outcome == PATH_OK
  OR path_outcome == PATH_NOT_APPLICABLE

symlink_escape_absent =
  symlink_outcome == SYMLINK_OK
  OR symlink_outcome == SYMLINK_NOT_APPLICABLE

duplicate_path_free =
  duplicate_path_outcome == DUPLICATE_PATH_FREE
  OR duplicate_path_outcome == DUPLICATE_PATH_NOT_APPLICABLE

directory_not_file_absent =
  regular_file_outcome == REGULAR_FILE_OK
  OR regular_file_outcome == REGULAR_FILE_NOT_APPLICABLE

evaluated =
  execution_meta == PARSED_OK
```

Therefore:

```text
V1 remains frozen and valid for claim-boundary hygiene.
V2 is a proof-grade refinement for exact Phase 1 decision-table work.
```

## What V2 Preserves from V1

```text
artifact_kind branching
consulted-set discipline
Phase1Action without PROCEED
first-match total table shape
safety-critical tagging
NOT_PROVEN ledger and NP-APPLIC-01
mutation-pair requirement for safety-critical adapter claims
canonical serialization requirement
```

## Minimality Rule

The V2 spec must reject over-modeling.

```text
If Phase 1 maps two causes to the same status/action and does not require
separate reason-code identity for the formal decision table, V2 should not split
them.
```

If Phase 1 maps two causes to different statuses/actions, V2 must not collapse
them.

## Review Requirements for V2 Spec

A future V2 specification review must check:

```text
1. every enum value corresponds to a cause Phase 1 actually distinguishes
2. no enum value is invented for a cause Phase 1 does not distinguish
3. every enum is closed and total
4. every parse/check outcome maps to exactly one enum value
5. document-validation failures cannot be classified as TOOL_ERROR
6. V2 -> V1 refinement holds for every V1 flag
7. N/A is represented as explicit enum value where applicable
8. no enum value encodes trust/signature/execution claims
9. first-match determinism and totality remain possible over V2
```

## Recommended Next Step

If this proposal is accepted, the next step is:

```text
research/formal_core/domain4_nesira_flag_schema_v2_authorization.md
```

That authorization should permit only:

```text
V2 flag schema specification
V2 decision-table specification
V2 review
```

It should still block:

```text
Lean implementation
proof scripts
Python code changes
fixtures
fixture materialization
conformance harness implementation
Phase 2 implementation
public claims
release
```

## Status

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_PROPOSED

OUTCOME_ENUMS_PROPOSED
EXECUTION_META_STRATUM_PROPOSED
NOT_APPLICABLE_ENUM_VALUES_PROPOSED
V2_REFINES_V1_INVARIANT_PROPOSED
MINIMAL_CAUSE_LEVEL_RESOLUTION_PROPOSED

V2_SPECIFICATION_NOT_AUTHORIZED
LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

