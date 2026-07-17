# SPIRA Domain 4 / Nesira Decision Table V2 Review

## Verdict

```text
DOMAIN4_NESIRA_DECISION_TABLE_V2_ACCEPTED
```

This review accepts the V2 decision-table specification as the correct
action/status ordering over the accepted Domain 4 / Nesira V2 outcome schema.

It does not authorize Lean implementation, Lean proof scripts, Python changes,
fixtures, conformance-harness implementation, Phase 2 work, public claims, or
release.

Reviewed artifact:

```text
research/formal_core/domain4_nesira_decision_table_v2_spec.md
```

## Review Findings

### 1. The Table Does Not Invent Statuses

The accepted V2 schema already assigns status meaning to enum outcomes. The
decision table correctly limits itself to:

```text
execution-meta precedence
artifact_kind branching
consulted outcome sets
dependency-derived first-match order
status -> action projection
```

This avoids repeating the V1 failure mode.

### 2. Execution Meta Is First

The review accepts Stratum 0:

```text
TOOL_ERROR       -> TOOL_ERROR     -> STOP_BLOCKED
INPUT_MALFORMED -> RERUN_REQUIRED -> RERUN_REQUIRED
PARSED_OK        -> Stratum 1
```

The guard remains explicit:

```text
ordinary document-validation failure must not be classified as TOOL_ERROR
```

### 3. Artifact Branching And Consulted Sets Are Correct

The severance branch consumes only:

```text
schema_outcome
context_outcome
temporal_outcome
```

The isolation branch consumes:

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

`*_NOT_APPLICABLE` values are skipped by construction and cannot be interpreted
as checks performed. This preserves `NP-APPLIC-01`.

### 4. Dependency Order Is Derived From Accepted Phase 1

The evidence order is accepted:

```text
path safety
-> file existence
-> symlink/root containment
-> regular-file classification
-> duplicate canonical path
-> hash equality
```

This matches the accepted validator dependency path. In particular:

```text
EVIDENCE_MISSING precedes HASH_MISMATCH
```

because accepted Phase 1 cannot hash a missing file.

### 5. Severity Is Preserved Without Violating Dependencies

The table preserves non-permissive status/action outcomes:

```text
INVALID        -> STOP_BLOCKED
RERUN_REQUIRED -> RERUN_REQUIRED
NOT_EVALUATED  -> REPORT_NOT_EVALUATED
TOOL_ERROR     -> STOP_BLOCKED
VALID          -> REPORT_NOT_EVALUATED
```

Where a later invalid check depends on an earlier missing prerequisite, the
dependency order correctly wins because the later check cannot be evaluated.
This is not a safety weakening.

### 6. Totality Is Accepted

The table is total over legal V2 tuples:

```text
ExecutionMeta x Phase1ArtifactKind x legal V2 outcome tuples
```

Each artifact branch ends in an explicit otherwise row producing structural
Phase 1 `VALID` and `REPORT_NOT_EVALUATED`, not `PROCEED`.

### 7. Reason-Code Layer Remains Separate

The review accepts the separation:

```text
Lean proof-core table:
  action/status resolution

traceability and future harness:
  exact reason-code and details fidelity
```

This keeps the proof core minimal while preserving the obligation to reproduce
accepted Phase 1 reason codes in the future harness.

### 8. No Trust Or Release Claim Is Introduced

The table does not claim:

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
research/formal_core/domain4_nesira_conformance_harness_v2_spec.md
```

The harness specification must define how future Python adapter outputs will be
checked against the accepted V2 schema and decision table, including mutation
pairs for every safety-critical enum value and exact reason-code fidelity
outside the Lean proof core.

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
DOMAIN4_NESIRA_DECISION_TABLE_V2_ACCEPTED

EXECUTION_META_PRECEDENCE_ACCEPTED
ARTIFACT_KIND_BRANCHING_ACCEPTED
CONSULTED_SET_DISCIPLINE_ACCEPTED
DEPENDENCY_ORDER_ACCEPTED
FIRST_MATCH_TOTAL_TABLE_ACCEPTED
PHASE1ACTION_NO_PROCEED_PRESERVED
REASON_CODE_RESOLUTION_LEFT_TO_TRACEABILITY_AND_HARNESS

CONFORMANCE_HARNESS_SPECIFICATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
