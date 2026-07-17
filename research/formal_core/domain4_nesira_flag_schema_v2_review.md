# SPIRA Domain 4 / Nesira Flag Schema V2 Review

## Verdict

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_ACCEPTED
```

This review accepts the V2 flag-schema specification, machine-readable JSON,
and Phase 1 outcome traceability artifacts as the correct proof-grade input
schema for a future Domain 4 / Nesira decision-table specification.

It does not authorize the V2 decision table, Lean implementation, Lean proof
scripts, Python changes, fixtures, conformance-harness implementation, Phase 2
work, public claims, or release.

Reviewed artifacts:

```text
research/formal_core/domain4_nesira_flag_schema_v2_spec.md
research/formal_core/domain4_nesira_flag_schema_v2.json
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.json
```

## Review Findings

### 1. V1 Failure Mode Is Addressed

The V1 decision-table attempt failed because booleans lost cause-level
information needed to reproduce accepted Phase 1 status/action outcomes.

V2 fixes this by replacing overloaded booleans with closed outcome enums where
accepted Phase 1 distinguishes causes:

```text
schema outcome
context outcome
temporal outcome
evidence presence outcome
path/hash/symlink/duplicate/directory evidence outcomes
execution meta
```

### 2. Execution Meta Is Correctly Separated

`INPUT_MALFORMED` and `TOOL_ERROR` are modeled outside the artifact check layer.
The review accepts this separation.

The guard is explicit:

```text
ordinary document-validation failure must not be classified as TOOL_ERROR
```

### 3. N/A Is No Longer Overloaded Boolean True

Non-applicable checks are represented as explicit enum values:

```text
EVIDENCE_NOT_APPLICABLE
HASH_NOT_APPLICABLE
PATH_NOT_APPLICABLE
SYMLINK_NOT_APPLICABLE
DUP_NOT_APPLICABLE
DIR_NOT_APPLICABLE
TEMPORAL_NOT_APPLICABLE
```

These values project to V1 `true` only to preserve accepted V1 semantics and
carry `NP-APPLIC-01`. They cannot be read as "check performed."

### 4. Minimality Is Preserved

The schema does not split reason-code-only detail into proof-core enum values.
For example:

```text
PATH_UNSAFE covers empty, absolute, UNC, drive-qualified, traversal, and empty
component failures because accepted Phase 1 maps all of them to INVALID /
STOP_BLOCKED.
```

This keeps the future Lean core small while preserving reason-code fidelity in
traceability and the future harness.

### 5. V2 -> V1 Projection Is Total

Every V1 boolean has a total projection from V2:

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

The review accepts the projections, including explicit `*_NOT_APPLICABLE`
values guarded by `NP-APPLIC-01`.

### 6. Traceability Is Complete For Schema Stage

The traceability matrix maps accepted Phase 1 outcome families to V2 values and
maps every V2 value back to accepted Phase 1 source behavior.

Review counters:

```text
unmapped Phase 1 outcome families: 0
invented V2 enum values: 0
decision-table rows defined in this stage: 0
```

### 7. No Trust Or Release Claim Is Introduced

The V2 schema does not claim:

```text
signature validity
signer identity
signer authority
actual isolation execution
permission to sever
Phase 2 implementation
public product capability
release readiness
```

All such boundaries remain governed by the accepted
`SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1` ledger.

## Required Next Step

The next document should be:

```text
research/formal_core/domain4_nesira_decision_table_v2_spec.md
```

The V2 decision-table specification must consume the accepted V2 schema and
traceability matrix. It must define deterministic precedence and totality over
execution meta states, artifact_kind branches, and consulted outcome sets.

## Not Authorized

This review does not authorize:

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
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_ACCEPTED

OUTCOME_ENUM_SCHEMA_ACCEPTED
EXECUTION_META_STRATUM_ACCEPTED
NOT_APPLICABLE_ENUM_VALUES_ACCEPTED
V2_REFINES_V1_PROJECTION_ACCEPTED
PHASE1_OUTCOME_TRACEABILITY_ACCEPTED
ACTION_STATUS_RESOLUTION_SEPARATED_FROM_REASON_CODE_RESOLUTION

DECISION_TABLE_V2_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
