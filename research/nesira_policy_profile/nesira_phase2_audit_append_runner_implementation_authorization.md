# Nesira Phase 2 Audit Append Runner Implementation Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_RUNNER_IMPLEMENTATION_GATE
SCOPE: CLASS_SPECIFIC_RUNNER_IMPLEMENTATION_AUTHORIZATION

SELECTED_CLASS:
AUDIT_RECORD_APPEND_ONLY

AUTHORIZES:
private audit append runner implementation for exactly one class
one declared sink append capability call on the positive path
local conformance fixtures capable of observing one bounded append
local tests proving zero side effects for all negative cases
implementation report and review
runner taxonomy V3 update for this exact class

AUDIT_RECORD_APPEND_ONLY_STATUS: AUTHORIZED_NOW
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW: [AUDIT_RECORD_APPEND_ONLY]
AUTHORIZED_SIDE_EFFECT_BUDGET_NOW:
  AUDIT_RECORD_APPEND_ONLY:
    effect_count: 1
    total_effect_count: 1
    retry_count: 0
    supporting_effects: none

RUNNER_IMPLEMENTATION: AUTHORIZED_FOR_AUDIT_RECORD_APPEND_ONLY_ONLY
AUDIT_APPEND_IMPLEMENTATION: AUTHORIZED_FOR_ONE_DECLARED_SINK_APPEND_ONLY
FILESYSTEM_READ: NOT_AUTHORIZED
FILESYSTEM_PATH_RESOLUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: AUTHORIZED_ONLY_THROUGH_DECLARED_AUDIT_SINK_APPEND_CAPABILITY
AUDIT_SINK_OPEN_BY_RUNNER: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
CLI_FLAG_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE_CHANGE: NOT_AUTHORIZED
COMBINED_VERDICT_BEHAVIOR_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```

This is the first authorization that may permit code with a non-zero
side-effect budget. The authorization is limited to one private runner for
`AUDIT_RECORD_APPEND_ONLY`. It does not authorize public exposure or release.

## Core Lock

```text
ONE_DECLARED_AUDIT_APPEND_IS_THE_ONLY_AUTHORIZED_EFFECT
```

The only authorized effect is:

```text
call the declared audit sink append capability exactly once with one
schema-bound, non-secret audit record.
```

The runner must not:

```text
open a path
resolve a path
check path existence
list a directory
stat a file
inspect symlinks
write a fallback failure record
retry
create temp files
create lock files
write cache
write checkpoints
perform read-back verification
send network traffic
spawn subprocesses
execute commands
mutate the target artifact
```

## Sink Capability Boundary

The runner must not accept filesystem paths.

The runner may receive only an already-declared audit sink capability whose
identity was bound by the trusted verifier and human-go artifact:

```text
audit_sink_root_id@version
append_capability_ref
append_capability_root_digest
```

Before the runner may call the capability, it must compare the supplied
capability identity against the human-approved and trusted-verifier-approved
identity:

```text
runner_supplied.append_capability_root_digest
  == human_go_authorized.append_capability_root_digest
  == trusted_verifier_approved.append_capability_root_digest
```

If any value is missing or mismatched, the runner must return:

```text
AUDIT_APPEND_NOT_AUTHORIZED
effect_count_attempted=0
effect_count_applied=0
```

This is an in-memory digest comparison. It does not prove the capability object
is honest, append-only, durable, or backed by the declared root; those remain
explicit assumptions.

The runner may invoke exactly one method shape:

```text
append_one(record_payload, idempotency_key)
```

The capability must not expose:

```text
path
open
read
write arbitrary bytes
delete
overwrite
list
stat
network endpoint
command execution
```

The correctness, append-only behavior, durability, and root legitimacy of the
provided sink capability remain assumptions outside SPIRA. The runner does not
prove them.

## Preconditions

Before the append capability may be called, the runner must require:

```text
audit append non-executing evaluator verdict:
  AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE

execution authorization evaluator verdict:
  EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE

operator initiation:
  present, caller-supplied, bound to the same action id and operator identity

trusted verifier:
  independent and matched to runner-intended append budget under EA-TCB-03
  binds the append capability root digest that the runner must compare before
  the append call

human-go artifact:
  authenticated externally, non-self-authorized, fresh, not revoked, digest-bound
  binds the same append capability root digest

side-effect budget:
  effect_count=1
  total_effect_count=1
  retry_count=0
  supporting_effects=none

payload:
  schema-bound
  non-secret
  non-executable
  bounded size
  idempotency key present

rollback/abort relation:
  present and bound, even if it states immutable append correction requires a
  later compensating record that is not authorized here
```

Any missing prerequisite prevents the append capability call.

## Authorized Output

The runner may return a structured artifact with:

```text
schema_id
schema_version
action_class
action_id
verdict
effect_status
effect_count_attempted
effect_count_applied
total_effect_count
idempotency_key
audit_sink_root_ref
append_capability_ref
assumptions
conditional_on_roots
precondition_breakdown
blocking_reasons
not_evaluated_reasons
evidence_refs
```

Allowed verdicts:

```text
AUDIT_APPEND_APPLIED
AUDIT_APPEND_NOT_AUTHORIZED
AUDIT_APPEND_NOT_EVALUATED
AUDIT_APPEND_STATUS_UNKNOWN
```

Allowed effect statuses:

```text
NOT_ATTEMPTED
APPEND_ATTEMPTED
APPEND_APPLIED
APPEND_STATUS_UNKNOWN
```

The artifact must not include command, path, runbook, arbitrary write target, or
network target fields.

## Attempt Semantics

The runner must decide before the append call whether all preconditions are
satisfied.

If any blocking or not-evaluated reason exists:

```text
effect_count_attempted = 0
effect_count_applied = 0
effect_status = NOT_ATTEMPTED
```

and the append capability is not called.

If all preconditions are satisfied, the runner may call the declared append
capability once.

After the call:

```text
capability reports applied
  -> AUDIT_APPEND_APPLIED

capability reports unknown or raises an append-status exception
  -> AUDIT_APPEND_STATUS_UNKNOWN

capability reports not authorized or malformed response
  -> AUDIT_APPEND_STATUS_UNKNOWN
```

Unknown status is not success and must not permit follow-on action.

## No Probe Rule

The runner must not perform probes before append.

The implementation must not call:

```text
exists
is_file
stat
read
read_text
read_bytes
iterdir
glob
resolve
absolute
samefile
open
```

The runner may only validate supplied in-memory fields and then either call the
declared append capability once or return without side effects.

## Failure Semantics

Failure handling is in-memory only.

The runner must not write:

```text
failure audit record
fallback audit record
error log
temporary diagnostic file
checkpoint
cleanup marker
```

Because `total_effect_count=1`, no secondary write is authorized after any
failure or unknown status.

## Required Conformance

Implementation must prove:

```text
1. no human go -> no append call.
2. no operator initiation -> no append call.
3. no trusted verifier match -> no append call.
4. runner self-verification evidence -> no append call.
5. missing audit sink root -> no append call.
6. default sink attempt -> no append call.
7. user-supplied path -> rejected before append.
8. path traversal -> rejected before append.
9. network target -> rejected before append.
10. command or executable payload -> rejected before append.
11. secret-bearing payload -> rejected before append.
12. total_effect_count > 1 -> no append call.
13. retry_count > 0 -> no append call.
14. unbudgeted probe request -> no append call.
15. fallback failure audit write request -> no append call.
16. append status unknown -> AUDIT_APPEND_STATUS_UNKNOWN, no success, no follow-on action.
17. every negative case -> zero side effects.
18. positive case -> exactly one append call and no other effects.
19. append capability called at most once.
20. runner source contains no subprocess, socket, requests, urllib, pathlib, os path, or direct open.
21. runner output contains no path, command, runbook, or network target field.
22. public wheel exclusion remains true.
23. two-run equality for negative cases.
24. append capability root digest mismatch -> no append call.
```

Positive tests may use a local test double append capability to observe exactly
one bounded append call. They must not require public exposure or real user
files.

## Assumption Carrying

Every result must carry assumptions, including:

```text
EA-TCB-03
EA-META-01
EA-META-02
```

Any applied result must also carry assumptions for:

```text
declared audit sink root legitimacy
append capability correctness
append-only semantics
idempotency enforcement
operator initiation authenticity
human-go root legitimacy
trusted clock
revocation freshness
rollback or abort reference
```

These are assumptions, not proofs.

## Public Boundary

This authorization does not expose runner behavior publicly.

No release note, README, PyPI metadata, CLI help, or public claim may say:

```text
safe to execute
approved to run
audit append proves action happened
append proves safety
runner verified filesystem
audit sink certified
automatic remediation
severance authorized
```

Allowed internal language:

```text
private audit append runner implemented for one declared sink append capability
exactly one append call on positive path
zero append calls on negative paths
public exposure not authorized
```

## Authorized Files

This gate may edit only:

```text
source/spira_core/nesira_phase2_audit_append_runner.py
tests/test_nesira_phase2_audit_append_runner.py
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_authorization_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_report.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_results.json
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_implementation_review_results.json
research/nesira_policy_profile/nesira_phase2_runner_action_class_taxonomy.md
research/nesira_policy_profile/nesira_phase2_runner_action_class_taxonomy_review.md
```

Any workflow, pyproject, manifest, version, release, tag, public claim, CLI,
public wheel metadata, combined-verdict behavior, generic runner, subprocess,
direct filesystem path handling, direct sink open, network execution, severance,
or automatic remediation change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

If V1-pinned files are touched unexpectedly, stop before refreshing any
manifest.

## Required Verification

Before acceptance:

```text
24 conformance cases pass
positive path exactly one append capability call
all negative paths zero append capability calls
append capability root digest mismatch -> zero append capability calls
source scan: no subprocess/socket/requests/urllib/http/pathlib/direct open
source scan: no path resolution or existence checks
output scan: no command/path/runbook/network fields
no fallback failure write
two-run equality for negative cases
full pytest
V1 SHA256SUMS remains 622/622 if unchanged
public wheel behavior unchanged
```

## Next Step

If this authorization is accepted, the next step may implement only the private
`AUDIT_RECORD_APPEND_ONLY` runner under this envelope.

Public exposure, CLI exposure, release, generic runner behavior, network
actions, severance, remediation, and any second side effect remain blocked.
