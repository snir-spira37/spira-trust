# SPIRA Domain 4 / Nesira Decision Table V1 Specification

## Status

```text
DOCUMENT_TYPE: SPECIFICATION_ATTEMPT
SPEC_ID: SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V1
SPEC_STATUS: SCOPE_REVISION_REQUIRED
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
FIXTURE_CHANGES: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document attempts to specify the Domain 4 / Nesira decision table from the
accepted Phase 1 behavior. It does not authorize implementation. During this
specification pass, the existing `SPIRA_NESIRA_DOMAIN4_FLAGS_V1` tuple was found
to be too coarse to reproduce the accepted Phase 1 status/action behavior
exactly. Therefore the correct result of this specification attempt is:

```text
SCOPE_REVISION_REQUIRED
```

## Required Function Shape

The intended future core shape remains:

```text
NesiraCore : ArtifactKind -> FlagsV1 -> Policy -> MachineContract
```

The intended future machine contract shape remains:

```text
validation_status : Phase1ValidationStatus
action            : Phase1Action
stop              : Bool
reason_codes      : closed enum / structural-or-ledger mapped set
not_claimed       : ledger-id set
not_evaluated     : ledger-id set
evidence_refs     : list
proof_refs        : list
```

The Phase 1 action type must not contain `PROCEED`.

## Phase1Action

The Phase 1 action codomain remains:

```text
Phase1Action =
  STOP_BLOCKED
  REPORT_NOT_EVALUATED
  RERUN_REQUIRED
```

There is no `PROCEED` constructor.

## Status Projection Required by Existing Phase 1

The existing Phase 1 Python validator projects status to action as follows:

```text
VALID         -> REPORT_NOT_EVALUATED
INVALID       -> STOP_BLOCKED
NOT_EVALUATED -> REPORT_NOT_EVALUATED
RERUN_REQUIRED -> RERUN_REQUIRED
TOOL_ERROR    -> STOP_BLOCKED
```

Derived from:

```text
source/spira_core/nesira_policy_profile_validator.py::_action_for_status
```

This mapping is proof-ready and can be formalized later. The blocker is not this
status-to-action projection. The blocker is deriving the correct status from
the current `FlagsV1` tuple.

## Consulted Flag Sets

The table must enforce `NP-APPLIC-01` by construction. A flag that is not
applicable for an artifact kind must not be consumed as a successful check.

```text
consulted(SEVERANCE_AUTHORIZATION) =
  schema_valid
  context_match
  temporal_binding_ok
  evaluated

consulted(LEGACY_ISOLATION_RESULT) =
  schema_valid
  context_match
  evidence_present
  path_safe
  symlink_escape_absent
  duplicate_path_free
  directory_not_file_absent
  hash_ok
  evaluated
```

The following flags are N/A for `SEVERANCE_AUTHORIZATION` in V1 and must not be
read by the severance branch:

```text
evidence_present
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
```

The following flag is N/A for `LEGACY_ISOLATION_RESULT` in V1 and must not be
read by the isolation branch:

```text
temporal_binding_ok
```

## Candidate First-Match Structure

A future accepted decision table should be a total ordered first-match chain:

```text
for artifact_kind:
  consult only consulted(artifact_kind)
  return first matching rule
  final else covers all remaining tuples
```

This structure is accepted as the right proof shape:

```text
first-match-wins -> deterministic
final else -> total
named flags -> no positional ambiguity
artifact_kind branch -> NP-APPLIC-01 enforced by construction
```

However, the current flag schema does not provide enough information to write an
exact first-match chain that matches Phase 1.

## Code-Derived Phase 1 Precedence

### Severance Authorization

The existing severance validator evaluates approximately:

```text
1. envelope is not mapping / malformed DSSE / payload type invalid
   -> RERUN_REQUIRED

2. DSSE payload JSON invalid
   -> RERUN_REQUIRED

3. severance statement shape invalid
   -> INVALID

4. severance schema_version unsupported
   -> RERUN_REQUIRED

5. expected context missing
   -> NOT_EVALUATED

6. context mismatch
   -> RERUN_REQUIRED

7. temporal binding invalid / expired
   -> RERUN_REQUIRED

8. otherwise
   -> VALID -> REPORT_NOT_EVALUATED
```

Derived from:

```text
source/spira_core/nesira_policy_profile_validator.py::_validate_severance_authorization_core
source/spira_core/nesira_policy_profile_validator.py::_not_evaluated_severance
source/spira_core/nesira_policy_profile_validator.py::_rerun_severance
source/spira_core/nesira_policy_profile_validator.py::_invalid_severance
```

### Legacy Isolation Result

The existing isolation validator evaluates approximately:

```text
1. result is not mapping
   -> INVALID

2. schema identity / schema_version unsupported
   -> RERUN_REQUIRED

3. isolation shape invalid
   -> INVALID

4. context mismatch
   -> RERUN_REQUIRED

5. profile mismatch / unsupported profile version
   -> RERUN_REQUIRED

6. expected context missing
   -> NOT_EVALUATED

7. evidence item schema invalid
   -> INVALID

8. unsafe path
   -> INVALID

9. evidence file missing
   -> NOT_EVALUATED

10. symlink escape
    -> INVALID

11. not regular file
    -> INVALID

12. duplicate canonical evidence path
    -> INVALID

13. hash mismatch
    -> INVALID

14. otherwise
    -> VALID -> REPORT_NOT_EVALUATED
```

Derived from:

```text
source/spira_core/nesira_policy_profile_validator.py::_validate_legacy_isolation_result_core
source/spira_core/nesira_policy_profile_validator.py::_validate_evidence_manifest
source/spira_core/nesira_policy_profile_validator.py::_not_evaluated_isolation
source/spira_core/nesira_policy_profile_validator.py::_rerun_isolation
source/spira_core/nesira_policy_profile_validator.py::_invalid_isolation
```

## Scope Revision Findings

### Finding 1: `schema_valid = false` Is Too Coarse

`SPIRA_NESIRA_DOMAIN4_FLAGS_V1` currently has one `schema_valid` flag. Existing
Phase 1 maps different schema/parse/version failures to different statuses:

```text
malformed JSON / malformed DSSE          -> RERUN_REQUIRED
unsupported schema_version               -> RERUN_REQUIRED
statement / result shape schema invalid  -> INVALID
```

These cases can collapse to the same tuple:

```text
schema_valid = false
```

but require different statuses. Therefore an exact decision table cannot be
derived from `FlagsV1` alone.

### Finding 2: Missing Context and Context Mismatch Are Not Distinguishable

Existing Phase 1 distinguishes:

```text
expected/current context missing -> NOT_EVALUATED
context mismatch                 -> RERUN_REQUIRED
```

`context_match` alone cannot represent this distinction. A tuple with
`context_match = false` does not say whether the problem is absence of expected
context or mismatch against supplied context.

### Finding 3: `evaluated = false` Is Too Coarse

The flag schema says `evaluated = false` can represent malformed input paths and
internal tool-error paths. Existing Phase 1 treats these differently:

```text
malformed JSON / malformed DSSE -> RERUN_REQUIRED
internal tool error             -> TOOL_ERROR -> STOP_BLOCKED
```

Without an additional discriminator, a total table cannot match both behaviors.

### Finding 4: Exact Reason-Code Enumeration Requires Cause Discriminants

A closed reason-code enum cannot be mapped exactly from the current flags
because multiple Phase 1 reason codes share the same coarse boolean state.

Examples:

```text
SEVERANCE_SCHEMA_INVALID
SEVERANCE_SCHEMA_VERSION_UNSUPPORTED
DSSE_PAYLOAD_JSON_INVALID
LEGACY_ISOLATION_RESULT_SCHEMA_INVALID
LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED
```

The future table must not invent a reason code when Phase 1 has a more precise
cause.

## Rejected Shortcut

The following shortcut is rejected:

```text
schema_valid = false -> INVALID
```

It would incorrectly classify unsupported versions and malformed decode paths
that Phase 1 returns as `RERUN_REQUIRED`.

The following shortcut is also rejected:

```text
schema_valid = false -> RERUN_REQUIRED
```

It would incorrectly classify structural schema violations that Phase 1 returns
as `INVALID`.

## Safety-Only Table Is Insufficient

A coarse safety-only table could prove:

```text
no PROCEED
fail closed for obvious unsafe flags
```

but it would not formalize Phase 1 as implemented. The accepted Domain 4 goal is
not merely "some safe table"; it is formalizing the accepted Phase 1 decision
behavior. Therefore a safety-only table is not accepted as V1.

## Required Scope Revision

Before `SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V1` can be accepted, one of the
following must be authorized:

```text
Option A:
Create SPIRA_NESIRA_DOMAIN4_FLAGS_V2 with cause-level discriminants.

Option B:
Explicitly narrow Domain4 V1 to a safety-only abstraction and document that it
does not reproduce Phase 1 status/reason-code behavior exactly.
```

Option A is recommended because the established research path says:

```text
formalize existing Phase 1 behavior, do not invent a new table
```

## Candidate Additional Discriminants for V2

A future V2 proposal should consider cause-level fields such as:

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

The final V2 set must be reviewed separately. This document does not authorize
or freeze V2.

## Status

```text
SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V1_SCOPE_REVISION_REQUIRED

DECISION_TABLE_V1_NOT_ACCEPTED
FLAGS_V1_INSUFFICIENT_FOR_EXACT_PHASE1_STATUS_TABLE
NO_LEAN_IMPLEMENTATION_AUTHORIZED
NO_PYTHON_CHANGES_AUTHORIZED
NO_FIXTURE_CHANGES_AUTHORIZED
NO_PHASE1_REOPEN_AUTHORIZED
NO_PHASE2_IMPLEMENTATION_AUTHORIZED
NO_PUBLIC_CLAIM_AUTHORIZED
NO_RELEASE_AUTHORIZED
```

