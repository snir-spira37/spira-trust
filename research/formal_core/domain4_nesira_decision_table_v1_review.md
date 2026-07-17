# SPIRA Domain 4 / Nesira Decision Table V1 Review

## Verdict

```text
DOMAIN4_NESIRA_DECISION_TABLE_V1_NEEDS_REVISION
SCOPE_REVISION_REQUIRED
```

This review rejects acceptance of the current Decision Table V1 specification
attempt as an exact formalization of accepted Phase 1 behavior. The review does
not authorize Lean implementation, Python implementation, fixtures, tests, Phase
2 work, public claims, or release work.

Reviewed artifact:

```text
research/formal_core/domain4_nesira_decision_table_v1_spec.md
```

## Summary

The correct proof shape is clear:

```text
artifact_kind branch
consulted flag set
ordered first-match chain
final else for totality
Phase1Action without PROCEED
status -> action projection
ledger-backed reason/not_evaluated/not_claimed fields
```

However, the accepted `SPIRA_NESIRA_DOMAIN4_FLAGS_V1` tuple is too coarse to
derive the exact Phase 1 status and reason-code table. The table cannot be
accepted without either a V2 flag schema or an explicitly narrowed safety-only
scope.

## Review Findings

### 1. No Invented Table Is Allowed

The review confirms the governing principle:

```text
formalize existing Phase 1 behavior
do not design a new product table
```

The spec correctly refuses to invent a table where Phase 1 behavior is not
determined by the current flags.

### 2. `schema_valid` Is Not Enough

Existing Phase 1 distinguishes:

```text
malformed decode / unsupported version -> RERUN_REQUIRED
structural shape violation             -> INVALID
```

The current flag tuple can represent both only as:

```text
schema_valid = false
```

Therefore the table cannot exactly recover the Phase 1 status.

### 3. `context_match` Is Not Enough

Existing Phase 1 distinguishes:

```text
expected/current context missing -> NOT_EVALUATED
context mismatch                 -> RERUN_REQUIRED
```

The current flag tuple cannot distinguish those causes. A decision table that
maps `context_match = false` to either outcome would misclassify one accepted
Phase 1 path.

### 4. `evaluated` Is Not Enough

Existing Phase 1 has both malformed input paths and internal tool-error paths.
They do not project to the same status/action:

```text
malformed input -> RERUN_REQUIRED
tool error      -> TOOL_ERROR -> STOP_BLOCKED
```

The current `evaluated` flag does not carry enough information to reproduce that
distinction.

### 5. NP-APPLIC-01 Is Correctly Enforced by the Proposed Shape

The reviewed spec correctly proposes consulted sets:

```text
SEVERANCE_AUTHORIZATION:
  do not consume evidence/path/hash flags

LEGACY_ISOLATION_RESULT:
  consume evidence/path/hash flags
```

This is the correct way to enforce `NP-APPLIC-01`. The problem is not
applicability. The problem is insufficient cause-level granularity for exact
status and reason-code projection.

### 6. Phase1Action Without PROCEED Remains Accepted

The review preserves:

```text
Phase1Action has no PROCEED constructor.
```

This part is ready for a future proof once the decision table input is precise
enough.

## Required Revision Path

The review recommends:

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V2_PROPOSAL_REQUIRED
```

The V2 proposal should add cause-level discriminants sufficient to derive the
accepted Phase 1 table exactly. Candidate discriminants include:

```text
decode_ok
supported_version
shape_valid
expected_context_present
context_match
temporal_binding_ok
tool_error_absent
evidence_manifest_shape_valid
```

The final V2 design must be separately authorized and reviewed. This review does
not authorize V2 implementation or any Python/Lean changes.

## Alternative Path

A safety-only abstraction may be proposed instead:

```text
DOMAIN4_NESIRA_SAFETY_ONLY_DECISION_ABSTRACTION_PROPOSAL
```

That path would need to state clearly that it proves only a safety abstraction
and does not reproduce Phase 1 status/reason-code behavior exactly. This review
does not recommend that path as the primary route.

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
DOMAIN4_NESIRA_DECISION_TABLE_V1_NEEDS_REVISION
SCOPE_REVISION_REQUIRED

FLAGS_V1_INSUFFICIENT_FOR_EXACT_PHASE1_DECISION_TABLE
FLAG_SCHEMA_V2_PROPOSAL_REQUIRED

NP_APPLIC_01_CONSULTED_SET_APPROACH_ACCEPTED
PHASE1ACTION_WITHOUT_PROCEED_ACCEPTED
FIRST_MATCH_TOTAL_TABLE_SHAPE_ACCEPTED

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

