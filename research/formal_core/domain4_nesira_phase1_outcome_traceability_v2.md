# SPIRA Domain 4 / Nesira Phase 1 Outcome Traceability V2

## Status

```text
DOCUMENT_TYPE: TRACEABILITY_MATRIX
TRACEABILITY_ID: SPIRA_NESIRA_DOMAIN4_PHASE1_OUTCOME_TRACEABILITY_V2
SCHEMA_ID: SPIRA_NESIRA_DOMAIN4_FLAGS_V2
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This matrix links accepted Nesira Phase 1 validator behavior to V2 execution
meta states and outcome enums. Its purpose is to prevent invented enum values
and prevent missing Phase 1 outcomes.

It is not a decision table. The V2 decision-table specification remains a
separate next step.

## Traceability Rules

```text
Direction 1: completeness
  every accepted Phase 1 output family must map to a V2 execution meta state
  or outcome enum.

Direction 2: no invention
  every V2 execution meta value and outcome enum value must map back to an
  accepted Phase 1 source.
```

Acceptance targets:

```text
unmapped Phase 1 outcome families: 0
invented V2 enum values: 0
decision-table rows defined here: 0
```

## Status / Action Projection From Accepted Phase 1

```text
VALID            -> REPORT_NOT_EVALUATED
INVALID          -> STOP_BLOCKED
NOT_EVALUATED    -> REPORT_NOT_EVALUATED
RERUN_REQUIRED   -> RERUN_REQUIRED
TOOL_ERROR       -> STOP_BLOCKED
```

derived_from:

```text
source/spira_core/nesira_policy_profile_validator.py::_action_for_status
source/spira_core/nesira_policy_profile_validator.py::_result
```

`PROCEED` is not an accepted Phase 1 action. `_result` raises if an attempted
Phase 1 result action is `PROCEED`.

## Direction 1: Phase 1 Outcome Families -> V2

### Global Execution Meta Outcomes

| Phase 1 source | Status | Action | V2 mapping | Notes |
| --- | --- | --- | --- | --- |
| malformed UTF-8/JSON bytes in `validate_severance_authorization_bytes` | RERUN_REQUIRED | RERUN_REQUIRED | ExecutionMeta.INPUT_MALFORMED | before per-check outcomes |
| malformed UTF-8/JSON bytes in `validate_legacy_isolation_result_bytes` | RERUN_REQUIRED | RERUN_REQUIRED | ExecutionMeta.INPUT_MALFORMED | before per-check outcomes |
| exception caught by `validate_severance_authorization` | TOOL_ERROR | STOP_BLOCKED | ExecutionMeta.TOOL_ERROR | validator failure, not document failure |
| exception caught by `validate_legacy_isolation_result` | TOOL_ERROR | STOP_BLOCKED | ExecutionMeta.TOOL_ERROR | validator failure, not document failure |
| `path.resolve()` OSError in `_validate_evidence_manifest` | TOOL_ERROR | STOP_BLOCKED | ExecutionMeta.TOOL_ERROR | filesystem resolution failure |

### Severance Authorization Outcomes

| Phase 1 reason/source | Status | Action | V2 mapping | Reason-code layer |
| --- | --- | --- | --- | --- |
| `NESIRA_PHASE1_MALFORMED_DSSE_ENVELOPE` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `DSSE_PAYLOAD_TYPE_INVALID` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `DSSE_PAYLOAD_MISSING` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `DSSE_PAYLOAD_BASE64_INVALID` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `DSSE_PAYLOAD_UTF8_INVALID` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `DSSE_PAYLOAD_JSON_INVALID` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `SEVERANCE_SCHEMA_VERSION_UNSUPPORTED` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `SEVERANCE_SCHEMA_INVALID` | INVALID | STOP_BLOCKED | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION | exact reason preserved outside core enum |
| `SEVERANCE_EXPECTED_CONTEXT_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | ContextOutcome.CONTEXT_EXPECTED_MISSING | exact missing fields preserved outside core enum |
| `SEVERANCE_<FIELD>_MISMATCH` | RERUN_REQUIRED | RERUN_REQUIRED | ContextOutcome.CONTEXT_MISMATCH | exact field preserved outside core enum |
| `SEVERANCE_TEMPORAL_BINDING_INVALID` | RERUN_REQUIRED | RERUN_REQUIRED | TemporalOutcome.TEMPORAL_VIOLATION | exact temporal reason preserved outside core enum |
| `SEVERANCE_ISSUED_AT_IN_FUTURE` | RERUN_REQUIRED | RERUN_REQUIRED | TemporalOutcome.TEMPORAL_VIOLATION | exact temporal reason preserved outside core enum |
| `SEVERANCE_EXPIRED` | RERUN_REQUIRED | RERUN_REQUIRED | TemporalOutcome.TEMPORAL_VIOLATION | exact temporal reason preserved outside core enum |
| valid severance structure/binding | VALID | REPORT_NOT_EVALUATED | SCHEMA_OK + CONTEXT_OK + TEMPORAL_OK + evidence/hash/path/symlink/duplicate/directory NOT_APPLICABLE | trust still not evaluated |

### Legacy Isolation Result Outcomes

| Phase 1 reason/source | Status | Action | V2 mapping | Reason-code layer |
| --- | --- | --- | --- | --- |
| non-mapping result | INVALID | STOP_BLOCKED | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION | `LEGACY_ISOLATION_RESULT_SCHEMA_INVALID` |
| `LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | exact reason preserved outside core enum |
| `_validate_isolation_shape` violation | INVALID | STOP_BLOCKED | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION | `LEGACY_ISOLATION_RESULT_SCHEMA_INVALID` |
| `LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED` | RERUN_REQUIRED | RERUN_REQUIRED | SchemaOutcome.SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | profile version is treated as unsupported schema/profile version |
| evidence manifest item malformed | INVALID | STOP_BLOCKED | SchemaOutcome.SCHEMA_STRUCTURAL_VIOLATION | `LEGACY_ISOLATION_EVIDENCE_SCHEMA_INVALID` |
| `LEGACY_ISOLATION_<FIELD>_MISMATCH` | RERUN_REQUIRED | RERUN_REQUIRED | ContextOutcome.CONTEXT_MISMATCH | exact field preserved outside core enum |
| `LEGACY_ISOLATION_PROFILE_MISMATCH` | RERUN_REQUIRED | RERUN_REQUIRED | ContextOutcome.CONTEXT_MISMATCH | exact reason preserved outside core enum |
| `LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | ContextOutcome.CONTEXT_EXPECTED_MISSING | missing fields preserved outside core enum |
| `LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH` | INVALID | STOP_BLOCKED | PathOutcome.PATH_UNSAFE | unsafe path subtype remains reason-code layer |
| `LEGACY_ISOLATION_EVIDENCE_FILE_MISSING` | NOT_EVALUATED | REPORT_NOT_EVALUATED | EvidencePresenceOutcome.EVIDENCE_MISSING | missing path preserved in details |
| `LEGACY_ISOLATION_SYMLINK_ESCAPE` | INVALID | STOP_BLOCKED | SymlinkOutcome.SYMLINK_ESCAPE | path preserved in details |
| `LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE` | INVALID | STOP_BLOCKED | DirectoryEvidenceOutcome.DIR_AS_FILE | path preserved in details |
| `LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH` | INVALID | STOP_BLOCKED | DuplicateOutcome.DUP_PRESENT | canonical path preserved in details |
| `LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH` | INVALID | STOP_BLOCKED | HashOutcome.HASH_MISMATCH | expected/actual hash preserved in details |
| valid isolation structure/evidence | VALID | REPORT_NOT_EVALUATED | SCHEMA_OK + CONTEXT_OK + EVIDENCE_OK + PATH_OK + SYMLINK_OK + DIR_OK + DUP_OK + HASH_OK + TEMPORAL_NOT_APPLICABLE | isolation trust still not evaluated |

## Direction 2: V2 Values -> Phase 1 Source

| V2 value | Phase 1 source | Status/action |
| --- | --- | --- |
| ExecutionMeta.PARSED_OK | validators reached core per-check path | continue |
| ExecutionMeta.INPUT_MALFORMED | `validate_*_bytes` JSON decode failure | RERUN_REQUIRED / RERUN_REQUIRED |
| ExecutionMeta.TOOL_ERROR | wrapper exception or path resolution OSError -> `_tool_error` | TOOL_ERROR / STOP_BLOCKED |
| SCHEMA_OK | accepted structural/schema path before binding checks | continue |
| SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION | DSSE/payload/schema/profile version rerun branches | RERUN_REQUIRED / RERUN_REQUIRED |
| SCHEMA_STRUCTURAL_VIOLATION | severance/isolation/evidence structural invalid branches | INVALID / STOP_BLOCKED |
| EVIDENCE_OK | `_validate_evidence_manifest` existing file path | continue |
| EVIDENCE_MISSING | `LEGACY_ISOLATION_EVIDENCE_FILE_MISSING` | NOT_EVALUATED / REPORT_NOT_EVALUATED |
| EVIDENCE_NOT_APPLICABLE | severance has no evidence-root file check | ignored by consulted set |
| HASH_OK | computed SHA-256 equals declared digest | continue |
| HASH_MISMATCH | `LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH` | INVALID / STOP_BLOCKED |
| HASH_NOT_APPLICABLE | severance has no evidence-root hash check | ignored by consulted set |
| PATH_OK | `_unsafe_relative_path` returns None | continue |
| PATH_UNSAFE | `LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH` | INVALID / STOP_BLOCKED |
| PATH_NOT_APPLICABLE | severance has no evidence-root path check | ignored by consulted set |
| SYMLINK_OK | resolved path is within root and not symlink | continue |
| SYMLINK_ESCAPE | `LEGACY_ISOLATION_SYMLINK_ESCAPE` | INVALID / STOP_BLOCKED |
| SYMLINK_NOT_APPLICABLE | severance has no symlink/root containment check | ignored by consulted set |
| DUP_OK | canonical path not already seen | continue |
| DUP_PRESENT | `LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH` | INVALID / STOP_BLOCKED |
| DUP_NOT_APPLICABLE | severance has no duplicate evidence-path check | ignored by consulted set |
| DIR_OK | evidence path is regular file | continue |
| DIR_AS_FILE | `LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE` | INVALID / STOP_BLOCKED |
| DIR_NOT_APPLICABLE | severance has no regular-file evidence check | ignored by consulted set |
| CONTEXT_OK | `_missing_fields` empty and `_first_context_mismatch` none | continue |
| CONTEXT_EXPECTED_MISSING | `*_EXPECTED_CONTEXT_MISSING` | NOT_EVALUATED / REPORT_NOT_EVALUATED |
| CONTEXT_MISMATCH | `*_<FIELD>_MISMATCH` or profile mismatch | RERUN_REQUIRED / RERUN_REQUIRED |
| TEMPORAL_OK | `_validate_temporal_binding` returns None | continue |
| TEMPORAL_VIOLATION | temporal parse/future/expired rerun branches | RERUN_REQUIRED / RERUN_REQUIRED |
| TEMPORAL_NOT_APPLICABLE | isolation has no temporal binding check | ignored by consulted set |

## Reason-Code Resolution Boundary

The V2 proof-core enums intentionally do not encode reason-code-only subtypes
when accepted Phase 1 maps them to the same status/action.

Examples:

```text
PATH_UNSAFE covers empty path, absolute path, UNC/network path,
drive-qualified path, traversal, and empty path component.

TEMPORAL_VIOLATION covers malformed temporal binding, issued_at in future, and
expired artifact.

SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION covers several DSSE/payload/schema
rerun causes.
```

The exact Phase 1 reason code and details remain obligations for the future
conformance harness and recorded traceability, not for the minimal Lean
proof-core enum set.

## Status

```text
SPIRA_NESIRA_DOMAIN4_PHASE1_OUTCOME_TRACEABILITY_V2_SPECIFIED

PHASE1_TO_V2_COMPLETENESS_SPECIFIED
V2_TO_PHASE1_NO_INVENTION_SPECIFIED
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
