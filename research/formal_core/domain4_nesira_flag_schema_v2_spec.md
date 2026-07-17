# SPIRA Domain 4 / Nesira Flag Schema V2 Specification

## Status

```text
DOCUMENT_TYPE: SPECIFICATION
SCHEMA_ID: SPIRA_NESIRA_DOMAIN4_FLAGS_V2
SCHEMA_VERSION: 2
FROZEN: true
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
FIXTURE_CHANGES: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document specifies the proof-grade V2 typed outcome interface for the
future Domain 4 / Nesira Formal Core. It is a specification only. It does not
implement Lean, Python, fixtures, tests, product integration, Phase 2 trust, or
release behavior.

## Design Boundary

V2 separates the proof core from reason-code fidelity:

```text
Proof core:
  uses outcome enums at action/status resolution.
  Splits causes only where accepted Phase 1 assigns a different status/action
  or where V2 -> V1 projection requires the distinction.

Reason-code fidelity:
  remains in traceability and future conformance harness artifacts.
  It may distinguish finer causes that share the same action/status.
```

Example:

```text
PATH_UNSAFE covers empty, absolute, UNC, drive-qualified, traversal, and empty
path-component failures because accepted Phase 1 maps all of them to INVALID /
STOP_BLOCKED through LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH.

The fine path reason is not part of the Lean proof-core enum.
```

## Immutable Schema Policy

```text
SPIRA_NESIRA_DOMAIN4_FLAGS_V2 is immutable.

Any change to an enum name, enum value, definition, applicability, V1
projection, derived_from source, or safety-critical classification requires a
new schema version.

V2 must not be edited in place after acceptance.
```

## Artifact Kinds

```text
Phase1ArtifactKind =
  SEVERANCE_AUTHORIZATION
  LEGACY_ISOLATION_RESULT
```

`SEVERANCE_AUTHORIZATION` evaluates structure, DSSE / in-toto payload shape,
context binding, and temporal binding. It does not perform evidence-root file
existence, path, symlink, duplicate, directory, or hash checks in Phase 1.

`LEGACY_ISOLATION_RESULT` evaluates structure, context/profile binding, evidence
manifest shape, evidence file existence, path safety, symlink/root containment,
file type, duplicate canonical paths, and SHA-256 evidence hashes.

## Execution Meta Stratum

`ExecutionMeta` is checked before per-artifact outcomes.

```text
ExecutionMeta =
  PARSED_OK
  INPUT_MALFORMED
  TOOL_ERROR
```

Definitions:

```text
PARSED_OK:
  the validator reached the per-check outcome layer.

INPUT_MALFORMED:
  byte input could not be decoded as UTF-8 JSON before artifact validation.
  Accepted Phase 1 maps this to RERUN_REQUIRED / RERUN_REQUIRED.

TOOL_ERROR:
  the validator itself failed unexpectedly, or a filesystem resolution operation
  raised a tool/runtime error. Accepted Phase 1 maps this to TOOL_ERROR /
  STOP_BLOCKED.
```

Guard:

```text
ordinary document-validation failure must not be classified as TOOL_ERROR.
```

derived_from:

```text
source/spira_core/nesira_policy_profile_validator.py:
  validate_severance_authorization_bytes
  validate_legacy_isolation_result_bytes
  validate_severance_authorization
  validate_legacy_isolation_result
  _validate_evidence_manifest
  _tool_error
```

## Tuple Shape

The V2 tuple is a named record, not a positional list:

```text
record NesiraDomain4FlagsV2:
  schema_id: "SPIRA_NESIRA_DOMAIN4_FLAGS_V2"
  schema_version: 2
  artifact_kind: Phase1ArtifactKind
  execution_meta: ExecutionMeta
  schema_outcome: SchemaOutcome
  evidence_presence_outcome: EvidencePresenceOutcome
  hash_outcome: HashOutcome
  path_outcome: PathOutcome
  symlink_outcome: SymlinkOutcome
  duplicate_outcome: DuplicateOutcome
  directory_evidence_outcome: DirectoryEvidenceOutcome
  context_outcome: ContextOutcome
  temporal_outcome: TemporalOutcome
```

If `execution_meta != PARSED_OK`, the decision table must stop at the execution
meta stratum. Per-check outcome values may be present only as inert
serialization placeholders in that case and must not override execution meta.

## Canonical Serialization

The canonical serialization of the V2 tuple is:

```text
UTF-8 JSON
object keys sorted lexicographically
enum values encoded as exact strings
no insignificant whitespace
no timestamps
no host paths
no environment metadata
no runtime duration
no provider/tool telemetry
```

The future conformance harness must compare canonical serialized tuples
byte-for-byte across repeated runs.

## Outcome Type: `SchemaOutcome`

```text
values:
  SCHEMA_OK
  SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION
  SCHEMA_STRUCTURAL_VIOLATION

applicability:
  SEVERANCE_AUTHORIZATION: applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  schema_valid = (schema_outcome == SCHEMA_OK)
```

Per-value definitions:

```text
SCHEMA_OK:
  The artifact passed accepted Phase 1 structural and schema/version checks
  required before semantic binding checks.
  maps_to_status: CONTINUE
  safety_critical: false
  derived_from:
    _validate_severance_authorization_core valid path before context checks
    _validate_legacy_isolation_result_core valid path before context checks

SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION:
  The artifact is malformed at the DSSE/payload/schema identity layer, or uses
  an unsupported Phase 1 schema/profile version, and accepted Phase 1 maps the
  cause to RERUN_REQUIRED.
  maps_to_status: RERUN_REQUIRED
  safety_critical: false
  derived_from:
    _validate_severance_authorization_core:
      NESIRA_PHASE1_MALFORMED_DSSE_ENVELOPE
      DSSE_PAYLOAD_TYPE_INVALID
      DSSE_PAYLOAD_MISSING
      DSSE_PAYLOAD_BASE64_INVALID
      DSSE_PAYLOAD_UTF8_INVALID
      DSSE_PAYLOAD_JSON_INVALID
      SEVERANCE_SCHEMA_VERSION_UNSUPPORTED
    _validate_legacy_isolation_result_core:
      LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED
      LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED

SCHEMA_STRUCTURAL_VIOLATION:
  The artifact reached a structural validation layer and violated required
  Phase 1 shape or field requirements that accepted Phase 1 maps to INVALID.
  maps_to_status: INVALID
  safety_critical: false
  derived_from:
    _validate_severance_statement_shape -> SEVERANCE_SCHEMA_INVALID
    _validate_legacy_isolation_result_core non-mapping result
    _validate_isolation_shape -> LEGACY_ISOLATION_RESULT_SCHEMA_INVALID
    _validate_evidence_manifest item shape -> LEGACY_ISOLATION_EVIDENCE_SCHEMA_INVALID
```

## Outcome Type: `EvidencePresenceOutcome`

```text
values:
  EVIDENCE_OK
  EVIDENCE_MISSING
  EVIDENCE_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  evidence_present = (outcome == EVIDENCE_OK OR outcome == EVIDENCE_NOT_APPLICABLE)
```

Per-value definitions:

```text
EVIDENCE_OK:
  Every evidence path that accepted Phase 1 is required to inspect exists before
  file-type and hash validation.
  maps_to_status: CONTINUE
  safety_critical: false
  derived_from:
    _validate_evidence_manifest path.exists() true path

EVIDENCE_MISSING:
  An applicable evidence file does not exist at the normalized in-root path.
  maps_to_status: NOT_EVALUATED
  safety_critical: false
  derived_from:
    _validate_evidence_manifest -> LEGACY_ISOLATION_EVIDENCE_FILE_MISSING

EVIDENCE_NOT_APPLICABLE:
  The artifact kind has no Phase 1 evidence-root file existence check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

## Outcome Type: `HashOutcome`

```text
values:
  HASH_OK
  HASH_MISMATCH
  HASH_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  hash_ok = (outcome == HASH_OK OR outcome == HASH_NOT_APPLICABLE)
```

Per-value definitions:

```text
HASH_OK:
  Every applicable evidence file's SHA-256 over the bytes read by accepted
  Phase 1 equals the declared digest.
  maps_to_status: CONTINUE
  safety_critical: true
  ledger_ids: NP-ADAPTER-05
  derived_from:
    _validate_evidence_manifest actual_hash == item["sha256"]

HASH_MISMATCH:
  At least one applicable evidence file's computed SHA-256 differs from the
  declared digest.
  maps_to_status: INVALID
  safety_critical: true
  ledger_ids: NP-ADAPTER-05
  derived_from:
    _validate_evidence_manifest -> LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH

HASH_NOT_APPLICABLE:
  The artifact kind has no Phase 1 evidence-root hash check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

## Outcome Type: `PathOutcome`

```text
values:
  PATH_OK
  PATH_UNSAFE
  PATH_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  path_safe = (outcome == PATH_OK OR outcome == PATH_NOT_APPLICABLE)
```

Per-value definitions:

```text
PATH_OK:
  Every applicable evidence path string passes accepted Phase 1 lexical path
  safety checks after separator normalization.
  maps_to_status: CONTINUE
  safety_critical: true
  ledger_ids: NP-ADAPTER-06
  derived_from:
    _normalize_evidence_path
    _unsafe_relative_path returns None

PATH_UNSAFE:
  An applicable evidence path is empty, absolute, UNC/network style,
  drive-qualified, contains traversal, or contains an empty path component.
  maps_to_status: INVALID
  safety_critical: true
  ledger_ids: NP-ADAPTER-06
  derived_from:
    _unsafe_relative_path -> LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH

PATH_NOT_APPLICABLE:
  The artifact kind has no Phase 1 evidence-root path safety check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

## Outcome Type: `SymlinkOutcome`

```text
values:
  SYMLINK_OK
  SYMLINK_ESCAPE
  SYMLINK_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  symlink_escape_absent = (outcome == SYMLINK_OK OR outcome == SYMLINK_NOT_APPLICABLE)
```

Per-value definitions:

```text
SYMLINK_OK:
  Every applicable evidence path resolves inside evidence_root and is not a
  symlink according to accepted Phase 1 checks.
  maps_to_status: CONTINUE
  safety_critical: true
  ledger_ids: NP-ADAPTER-04
  derived_from:
    _validate_evidence_manifest: _is_within(resolved, root) and not path.is_symlink()

SYMLINK_ESCAPE:
  An applicable evidence path resolves outside evidence_root or is a symlink.
  maps_to_status: INVALID
  safety_critical: true
  ledger_ids: NP-ADAPTER-04
  derived_from:
    _validate_evidence_manifest -> LEGACY_ISOLATION_SYMLINK_ESCAPE

SYMLINK_NOT_APPLICABLE:
  The artifact kind has no Phase 1 symlink/root containment check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

If `path.resolve()` raises `OSError`, accepted Phase 1 returns TOOL_ERROR. That
case belongs to `ExecutionMeta = TOOL_ERROR`, not to `SymlinkOutcome`.

## Outcome Type: `DuplicateOutcome`

```text
values:
  DUP_OK
  DUP_PRESENT
  DUP_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  duplicate_path_free = (outcome == DUP_OK OR outcome == DUP_NOT_APPLICABLE)
```

Per-value definitions:

```text
DUP_OK:
  No applicable evidence path resolves to a canonical in-root path already seen
  in the same evidence manifest.
  maps_to_status: CONTINUE
  safety_critical: true
  ledger_ids: NP-ADAPTER-06
  derived_from:
    _validate_evidence_manifest seen_paths non-duplicate path

DUP_PRESENT:
  Two or more applicable evidence entries resolve to the same canonical in-root
  path.
  maps_to_status: INVALID
  safety_critical: true
  ledger_ids: NP-ADAPTER-06
  derived_from:
    _validate_evidence_manifest -> LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH

DUP_NOT_APPLICABLE:
  The artifact kind has no Phase 1 duplicate evidence-path check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

## Outcome Type: `DirectoryEvidenceOutcome`

```text
values:
  DIR_OK
  DIR_AS_FILE
  DIR_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: not applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  directory_not_file_absent = (outcome == DIR_OK OR outcome == DIR_NOT_APPLICABLE)
```

Per-value definitions:

```text
DIR_OK:
  Every applicable evidence path that exists is a regular file before hash
  validation.
  maps_to_status: CONTINUE
  safety_critical: true
  ledger_ids: NP-ADAPTER-03
  derived_from:
    _validate_evidence_manifest path.is_file() true path

DIR_AS_FILE:
  An applicable evidence path exists but is not a regular file.
  maps_to_status: INVALID
  safety_critical: true
  ledger_ids: NP-ADAPTER-03
  derived_from:
    _validate_evidence_manifest -> LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE

DIR_NOT_APPLICABLE:
  The artifact kind has no Phase 1 regular-file evidence check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for SEVERANCE_AUTHORIZATION
```

## Outcome Type: `ContextOutcome`

```text
values:
  CONTEXT_OK
  CONTEXT_EXPECTED_MISSING
  CONTEXT_MISMATCH

applicability:
  SEVERANCE_AUTHORIZATION: applicable
  LEGACY_ISOLATION_RESULT: applicable

v1_projection:
  context_match = (outcome == CONTEXT_OK)
```

Per-value definitions:

```text
CONTEXT_OK:
  All accepted Phase 1 context fields that are required for the artifact_kind
  are present in expected/current context and match the artifact.
  maps_to_status: CONTINUE
  safety_critical: true
  derived_from:
    _missing_fields returns empty and _first_context_mismatch returns None

CONTEXT_EXPECTED_MISSING:
  Accepted Phase 1 expected/current context lacks one or more required fields.
  maps_to_status: NOT_EVALUATED
  safety_critical: true
  derived_from:
    _missing_fields -> SEVERANCE_EXPECTED_CONTEXT_MISSING
    _missing_fields -> LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING

CONTEXT_MISMATCH:
  Expected/current context is present but differs from artifact context, profile
  identity, or profile version according to accepted Phase 1.
  maps_to_status: RERUN_REQUIRED
  safety_critical: true
  derived_from:
    _first_context_mismatch -> SEVERANCE_<FIELD>_MISMATCH
    _first_context_mismatch -> LEGACY_ISOLATION_<FIELD>_MISMATCH
    profile_id mismatch -> LEGACY_ISOLATION_PROFILE_MISMATCH
```

`LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED` remains a schema/version outcome,
not a context outcome, because accepted Phase 1 labels it unsupported schema
version and maps it through `_rerun_isolation`.

## Outcome Type: `TemporalOutcome`

```text
values:
  TEMPORAL_OK
  TEMPORAL_VIOLATION
  TEMPORAL_NOT_APPLICABLE

applicability:
  SEVERANCE_AUTHORIZATION: applicable
  LEGACY_ISOLATION_RESULT: not applicable

v1_projection:
  temporal_binding_ok = (outcome == TEMPORAL_OK OR outcome == TEMPORAL_NOT_APPLICABLE)
```

Per-value definitions:

```text
TEMPORAL_OK:
  Accepted Phase 1 parsed issued_at and expires_at as aware UTC instants,
  issued_at is not in the future, and expires_at is after now_utc.
  maps_to_status: CONTINUE
  safety_critical: false
  derived_from:
    _validate_temporal_binding returns None

TEMPORAL_VIOLATION:
  Accepted Phase 1 could not parse temporal fields, the issued_at time is in
  the future, or the artifact is expired.
  maps_to_status: RERUN_REQUIRED
  safety_critical: false
  derived_from:
    _validate_temporal_binding -> SEVERANCE_TEMPORAL_BINDING_INVALID
    _validate_temporal_binding -> SEVERANCE_ISSUED_AT_IN_FUTURE
    _validate_temporal_binding -> SEVERANCE_EXPIRED

TEMPORAL_NOT_APPLICABLE:
  The artifact kind has no accepted Phase 1 temporal binding check.
  maps_to_status: IGNORED_BY_CONSULTED_SET
  safety_critical: false
  ledger_ids: NP-APPLIC-01
  derived_from:
    accepted artifact_kind split for LEGACY_ISOLATION_RESULT
```

## V1 Projection Summary

```text
schema_valid =
  schema_outcome == SCHEMA_OK

evidence_present =
  evidence_presence_outcome == EVIDENCE_OK
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
  duplicate_outcome == DUP_OK
  OR duplicate_outcome == DUP_NOT_APPLICABLE

directory_not_file_absent =
  directory_evidence_outcome == DIR_OK
  OR directory_evidence_outcome == DIR_NOT_APPLICABLE

context_match =
  context_outcome == CONTEXT_OK

temporal_binding_ok =
  temporal_outcome == TEMPORAL_OK
  OR temporal_outcome == TEMPORAL_NOT_APPLICABLE

evaluated =
  execution_meta == PARSED_OK
```

`*_NOT_APPLICABLE` values project to V1 `true` only to preserve accepted
`SPIRA_NESIRA_DOMAIN4_FLAGS_V1` claim-boundary semantics. They must always carry
`NP-APPLIC-01` and must never be read as "check performed."

## Minimality Invariant

V2 does not split outcomes by reason-code-only detail. A split belongs in V2
only if:

```text
accepted Phase 1 maps the causes to different validation_status values;
accepted Phase 1 maps the causes to different Phase1Action values;
the distinction is required for total V2 -> V1 projection; or
the distinction is required to preserve artifact_kind applicability.
```

All finer reason-code fidelity belongs to the traceability matrix and future
conformance harness, not to the Lean proof-core enum set.

## Not Authorized By This Specification

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
SPIRA_NESIRA_DOMAIN4_FLAGS_V2_SPECIFIED

OUTCOME_ENUMS_SPECIFIED
EXECUTION_META_STRATUM_SPECIFIED
NOT_APPLICABLE_ENUM_VALUES_SPECIFIED
V2_REFINES_V1_PROJECTION_SPECIFIED
ACTION_STATUS_RESOLUTION_SEPARATED_FROM_REASON_CODE_RESOLUTION
DECISION_TABLE_V2_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
