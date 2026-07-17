# SPIRA Domain 4 / Nesira Decision Table V2 Specification

## Status

```text
DOCUMENT_TYPE: SPECIFICATION
TABLE_ID: SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V2
INPUT_SCHEMA: SPIRA_NESIRA_DOMAIN4_FLAGS_V2
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
FIXTURE_CHANGES: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document specifies the future Domain 4 / Nesira Formal Core decision table
over the accepted V2 flag schema. It is a paper specification only.

The table does not invent statuses. V2 outcome values already carry
`maps_to_status`. The table only defines deterministic evaluation order,
artifact_kind consultation, and action projection.

## Inputs

```text
NesiraCoreV2:
  artifact_kind: Phase1ArtifactKind
  execution_meta: ExecutionMeta
  outcome_tuple: NesiraDomain4FlagsV2
  policy: Phase1 policy / version context
  -> Phase1MachineContract
```

This decision table consumes:

```text
research/formal_core/domain4_nesira_flag_schema_v2_spec.md
research/formal_core/domain4_nesira_flag_schema_v2.json
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.json
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.md
```

## Phase 1 Action Type

```text
Phase1Action =
  STOP_BLOCKED
  REPORT_NOT_EVALUATED
  RERUN_REQUIRED
```

`PROCEED` is not representable in this action type.

If a future stage needs a `PROCEED`-capable action type, that belongs to a
separately authorized Phase 2 trust layer. It is not part of this table.

## Status To Action Projection

Accepted Phase 1 projects statuses to actions as follows:

```text
VALID          -> REPORT_NOT_EVALUATED
INVALID        -> STOP_BLOCKED
NOT_EVALUATED  -> REPORT_NOT_EVALUATED
RERUN_REQUIRED -> RERUN_REQUIRED
TOOL_ERROR     -> STOP_BLOCKED
```

derived_from:

```text
source/spira_core/nesira_policy_profile_validator.py::_action_for_status
source/spira_core/nesira_policy_profile_validator.py::_result
```

`VALID` remains structural-only Phase 1 validity. It still does not authorize
severance, trust a signer, trust isolation execution, or permit an agent to
proceed.

## Reason-Code Boundary

The decision table resolves action/status. It does not encode every fine
reason-code subtype in the Lean proof-core enum ordering.

Reason-code fidelity is preserved by:

```text
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
future conformance harness artifacts
accepted Phase 1 validator outputs
```

Examples:

```text
PATH_UNSAFE covers empty path, absolute path, UNC/network path,
drive-qualified path, traversal, and empty path component.

TEMPORAL_VIOLATION covers malformed temporal binding, future issued_at, and
expired artifact.
```

These subtypes share the same action/status in accepted Phase 1 and therefore
do not split the proof-core decision table.

## Stratum 0: Execution Meta

Stratum 0 is evaluated before any artifact outcome.

| Row | Condition | Status | Action | derived_from |
| --- | --- | --- | --- | --- |
| M1 | `execution_meta = TOOL_ERROR` | TOOL_ERROR | STOP_BLOCKED | `_tool_error`; wrapper exception handlers; `_validate_evidence_manifest` OSError path |
| M2 | `execution_meta = INPUT_MALFORMED` | RERUN_REQUIRED | RERUN_REQUIRED | `validate_severance_authorization_bytes`; `validate_legacy_isolation_result_bytes` malformed JSON branch |
| M3 | `execution_meta = PARSED_OK` | continue | continue | validator reached per-check outcome layer |

Guard:

```text
ordinary document-validation failure must not be classified as TOOL_ERROR.
```

This guard is required by:

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_ACCEPTED
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
```

## Stratum 1: Artifact Branching

After `execution_meta = PARSED_OK`, the table branches by:

```text
artifact_kind =
  SEVERANCE_AUTHORIZATION
  LEGACY_ISOLATION_RESULT
```

Each branch consumes only the V2 outcomes applicable to that artifact kind.
`*_NOT_APPLICABLE` values are skipped by construction and must never be read as
"check performed."

## Branch A: SEVERANCE_AUTHORIZATION

Consulted outcome set:

```text
schema_outcome
context_outcome
temporal_outcome
```

Non-consulted outcome values:

```text
evidence_presence_outcome = EVIDENCE_NOT_APPLICABLE
hash_outcome = HASH_NOT_APPLICABLE
path_outcome = PATH_NOT_APPLICABLE
symlink_outcome = SYMLINK_NOT_APPLICABLE
duplicate_outcome = DUP_NOT_APPLICABLE
directory_evidence_outcome = DIR_NOT_APPLICABLE
```

These non-consulted values must carry `NP-APPLIC-01`.

First-match table:

| Row | Condition | Status | Action | derived_from |
| --- | --- | --- | --- | --- |
| S1 | `schema_outcome = SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION` | RERUN_REQUIRED | RERUN_REQUIRED | malformed DSSE envelope / payload / unsupported severance schema branches |
| S2 | `schema_outcome = SCHEMA_STRUCTURAL_VIOLATION` | INVALID | STOP_BLOCKED | `_validate_severance_statement_shape` -> `SEVERANCE_SCHEMA_INVALID` |
| S3 | `context_outcome = CONTEXT_EXPECTED_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | `_missing_fields` -> `SEVERANCE_EXPECTED_CONTEXT_MISSING` |
| S4 | `context_outcome = CONTEXT_MISMATCH` | RERUN_REQUIRED | RERUN_REQUIRED | `_first_context_mismatch` -> `SEVERANCE_<FIELD>_MISMATCH` |
| S5 | `temporal_outcome = TEMPORAL_VIOLATION` | RERUN_REQUIRED | RERUN_REQUIRED | `_validate_temporal_binding` invalid/future/expired branches |
| S6 | otherwise all consulted values are OK | VALID | REPORT_NOT_EVALUATED | valid severance structure/binding result |

S1 and S2 are mutually exclusive values of one closed enum. Their relative order
does not create a semantic choice; both are listed before context/temporal
checks because accepted Phase 1 reaches context only after schema/payload
handling.

## Branch B: LEGACY_ISOLATION_RESULT

Consulted outcome set:

```text
schema_outcome
context_outcome
evidence_presence_outcome
path_outcome
symlink_outcome
directory_evidence_outcome
duplicate_outcome
hash_outcome
```

Non-consulted outcome values:

```text
temporal_outcome = TEMPORAL_NOT_APPLICABLE
```

This non-consulted value must carry `NP-APPLIC-01`.

First-match table:

| Row | Condition | Status | Action | derived_from |
| --- | --- | --- | --- | --- |
| I1 | `schema_outcome = SCHEMA_STRUCTURAL_VIOLATION` | INVALID | STOP_BLOCKED | non-mapping result; `_validate_isolation_shape`; malformed evidence manifest item |
| I2 | `schema_outcome = SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION` | RERUN_REQUIRED | RERUN_REQUIRED | unsupported isolation schema/profile version branches |
| I3 | `context_outcome = CONTEXT_MISMATCH` | RERUN_REQUIRED | RERUN_REQUIRED | `_first_context_mismatch`; profile mismatch |
| I4 | `context_outcome = CONTEXT_EXPECTED_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | `_missing_fields` -> `LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING` |
| I5 | `path_outcome = PATH_UNSAFE` | INVALID | STOP_BLOCKED | `_unsafe_relative_path` -> `LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH` |
| I6 | `evidence_presence_outcome = EVIDENCE_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | `path.exists()` false -> `LEGACY_ISOLATION_EVIDENCE_FILE_MISSING` |
| I7 | `symlink_outcome = SYMLINK_ESCAPE` | INVALID | STOP_BLOCKED | `_is_within` false or `path.is_symlink()` -> `LEGACY_ISOLATION_SYMLINK_ESCAPE` |
| I8 | `directory_evidence_outcome = DIR_AS_FILE` | INVALID | STOP_BLOCKED | `not path.is_file()` -> `LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE` |
| I9 | `duplicate_outcome = DUP_PRESENT` | INVALID | STOP_BLOCKED | duplicate canonical path -> `LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH` |
| I10 | `hash_outcome = HASH_MISMATCH` | INVALID | STOP_BLOCKED | computed hash differs -> `LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH` |
| I11 | otherwise all consulted values are OK | VALID | REPORT_NOT_EVALUATED | valid isolation structure/evidence result |

The evidence order is dependency-derived from accepted Phase 1:

```text
path safety
-> file existence
-> resolve / symlink containment
-> regular-file classification
-> duplicate canonical path
-> hash equality
```

In particular, `EVIDENCE_MISSING` precedes symlink, directory, duplicate, and
hash checks because accepted Phase 1 cannot resolve, classify, de-duplicate, or
hash a missing file. `HASH_MISMATCH` is last because accepted Phase 1 reads
bytes only after all earlier evidence checks pass.

## Dependency DAG

The table is a topological ordering of the accepted Phase 1 dependency graph:

```text
execution meta
  -> schema/payload/profile structure
    -> context/profile binding
      -> temporal binding              (SEVERANCE_AUTHORIZATION only)
      -> path lexical safety           (LEGACY_ISOLATION_RESULT only)
        -> evidence existence
          -> symlink/root containment
            -> regular-file check
              -> duplicate canonical path check
                -> hash equality
```

The future review must reject any reordered table that consumes an outcome
before its accepted Phase 1 prerequisites can be evaluated.

## Severity Precedence

Within the dependency graph, accepted Phase 1 severity is preserved:

```text
TOOL_ERROR       -> STOP_BLOCKED
INVALID          -> STOP_BLOCKED
RERUN_REQUIRED   -> RERUN_REQUIRED
NOT_EVALUATED    -> REPORT_NOT_EVALUATED
VALID            -> REPORT_NOT_EVALUATED
```

Dependency order may make `NOT_EVALUATED` precede a later `INVALID` check when
the later check cannot be evaluated without the missing prerequisite. The key
case is:

```text
EVIDENCE_MISSING precedes HASH_MISMATCH
```

This is not a weakening. It reflects the accepted Phase 1 fact that a missing
file cannot be hashed.

If a future artifact exposes a true dependency/severity conflict not determined
by accepted Phase 1, the correct result is:

```text
SCOPE_REVISION_REQUIRED
```

## Totality

The table is total over:

```text
ExecutionMeta x Phase1ArtifactKind x legal V2 outcome tuples
```

Totality is achieved by:

```text
Stratum 0:
  TOOL_ERROR
  INPUT_MALFORMED
  PARSED_OK

Stratum 1:
  artifact_kind-specific first-match rows
  final otherwise row per artifact_kind
```

Unexpected enum values, missing enum values, or unsupported artifact_kind values
are outside legal V2 tuples and belong to input/schema validation before this
core. They are not permissive defaults.

## Proof-Readiness Theorem Targets

The future Lean proof package may use this table to state theorem families such
as:

```text
tool_error_stops:
  execution_meta = TOOL_ERROR -> action = STOP_BLOCKED

input_malformed_rerun:
  execution_meta = INPUT_MALFORMED -> action = RERUN_REQUIRED

schema_structural_violation_not_valid:
  schema_outcome = SCHEMA_STRUCTURAL_VIOLATION -> action = STOP_BLOCKED

hash_mismatch_not_valid:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> hash_outcome = HASH_MISMATCH
  -> action = STOP_BLOCKED

unsafe_path_not_valid:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> path_outcome = PATH_UNSAFE
  -> action = STOP_BLOCKED

missing_evidence_not_evaluated:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> evidence_presence_outcome = EVIDENCE_MISSING
  -> action = REPORT_NOT_EVALUATED

context_expected_missing_not_evaluated:
  context_outcome = CONTEXT_EXPECTED_MISSING
  -> action = REPORT_NOT_EVALUATED

phase1_no_proceed:
  action is never PROCEED because PROCEED is not in Phase1Action

core_deterministic:
  same artifact_kind, execution_meta, outcome tuple, and policy
  -> same machine contract
```

These are theorem targets only. This document does not authorize Lean
definitions or proofs.

## Not Claimed

This table does not prove or claim:

```text
JSON parsing correctness
DSSE decoding correctness
filesystem correctness
symlink resolution correctness
SHA-256 computed over the correct bytes
signature validity
signer identity
signer authority
actual isolation execution
permission to sever
public product capability
release readiness
```

These remain governed by:

```text
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
```

## Not Authorized

This specification does not authorize:

```text
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
conformance harness implementation
decision-table implementation
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
SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V2_SPECIFIED

EXECUTION_META_PRECEDENCE_SPECIFIED
ARTIFACT_KIND_BRANCHING_SPECIFIED
CONSULTED_SET_DISCIPLINE_SPECIFIED
DEPENDENCY_ORDER_SPECIFIED
FIRST_MATCH_TOTAL_TABLE_SPECIFIED
PHASE1ACTION_NO_PROCEED_PRESERVED
REASON_CODE_RESOLUTION_LEFT_TO_TRACEABILITY_AND_HARNESS

CONFORMANCE_HARNESS_SPECIFICATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
