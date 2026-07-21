# Nesira Phase 2 Runner Candidate Class Model

## Status

```text
DOCUMENT_TYPE: RESEARCH -- RUNNER CANDIDATE CLASS MODEL
PHASE: PHASE_2_RUNNER_CANDIDATE_CLASS_MODEL_GATE
SCOPE: MODEL_ONLY

SELECTED_CLASS:
AUDIT_RECORD_APPEND_ONLY

AUTHORIZES:
one candidate action-class model
class-specific side-effect budget specification
future conformance expectations

AUTHORIZED_NOW: []
RUNNER_IMPLEMENTATION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
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

This document models exactly one future candidate action class:

```text
AUDIT_RECORD_APPEND_ONLY
```

It does not authorize runner code or any real append.

## Core Lock

```text
AUDIT_RECORD_APPEND_ONLY remains CANDIDATE_FOR_FUTURE_MODEL_ONLY.
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW remains [].
AUTHORIZED_SIDE_EFFECT_BUDGET_NOW remains 0.
```

The class is modeled so a later gate can review the smallest possible real
side effect before code exists.

## Class Definition

```text
class_id: AUDIT_RECORD_APPEND_ONLY
class_version: 1
effect_shape: APPEND_ONE_BOUNDED_RECORD
effect_count: 1
total_effect_count: 1
retry_count: 0
```

Purpose:

```text
append one bounded, non-secret, schema-bound audit record to a declared
append-only audit sink.
```

Non-goals:

```text
execute a command
mutate a target artifact
create or modify a status marker
materialize a review packet
send a network request
delete, overwrite, rename, move, chmod, or cleanup files
record secrets
prove that a target action was safe
prove that an effect happened in the real world
authorize severance or remediation
```

## Declared Roots

A future implementation must receive an explicit root:

```text
AUDIT_SINK_ROOT_ID@version
```

The root must define:

```text
sink identity
append-only semantics
schema registry reference
maximum record size
idempotency semantics
clock source
failure reporting boundary
```

There is no default audit sink.

The following are forbidden:

```text
current working directory as sink
repository root as sink
user-supplied path as sink
environment variable as implicit sink
system log as default sink
network endpoint as default sink
```

Missing or ambiguous audit sink root:

```text
AUDIT_APPEND_NOT_EVALUATED
```

## Allowed Inputs

A future evaluator or runner gate may consume only caller-supplied fields:

```text
action_id
action_class
subject_context_digest
environment_context_digest
target_scope_digest
combined_verdict_digest
action_authority_digest
dry_run_artifact_digest
execution_authorization_digest
human_go_digest
side_effect_budget_digest
audit_sink_root_id
audit_schema_id
audit_record_payload
idempotency_key
issued_at
```

The action, subject, target, sink, and payload schema must not be learned from
the target artifact under action.

## Audit Record Payload

The payload must be declarative and non-executable.

Minimum allowed payload fields:

```text
schema_id
schema_version
record_id
action_id
action_class
subject_context_digest
environment_context_digest
target_scope_digest
combined_verdict_digest
action_authority_digest
dry_run_artifact_digest
execution_authorization_digest
human_go_digest
side_effect_budget_digest
result_marker
assumptions_carried
created_at
idempotency_key
```

Allowed `result_marker` values:

```text
ACTION_NOT_PERFORMED
AUDIT_APPEND_CONSIDERED_FOR_FUTURE_RUNNER_GATE
AUDIT_APPEND_NOT_AUTHORIZED
AUDIT_APPEND_NOT_EVALUATED
```

The payload must not contain:

```text
command
command_line
script
shell
powershell
bash
python -m
subprocess_args
runbook
copy_paste_steps
write_paths
delete_paths
network_targets
secret
token
password
private_key
credential
environment_dump
filesystem_snapshot
```

## Side-Effect Budget

The complete class budget is:

```text
primary_effect: append one audit record
supporting_effects: none
effect_count: 1
total_effect_count: 1
retry_count: 0
temporary_files: 0
lock_files: 0
cache_writes: 0
checkpoint_writes: 0
post_effect_verification_writes: 0
network_sends: 0
cleanup_effects: 0
```

No pre-effect, post-effect, or failure audit record is added for this class.
The audit append is the terminal accounting anchor.

If the append cannot be attempted or its result cannot be known, the future
runner must return an in-memory status only. It must not write an additional
failure audit record unless a later model version explicitly budgets it.

## Path Boundary

The future implementation must not accept arbitrary path input.

Allowed path shape:

```text
AUDIT_SINK_ROOT_ID@version
fixed sink-relative append target from the audit sink root
target_scope_digest bound in human go
no traversal
no absolute caller path
no glob
no recursive write
no overwrite
```

Any direct caller-supplied path produces:

```text
AUDIT_APPEND_NOT_AUTHORIZED
```

If the sink root cannot resolve an unambiguous append target:

```text
AUDIT_APPEND_NOT_EVALUATED
```

## Network Boundary

This class is filesystem/local-sink only unless a later model version changes
the class under `SCOPE_REVISION_REQUIRED`.

Network sends are not part of the budget:

```text
network_sends: 0
```

Any URL, host, endpoint, or network channel input produces:

```text
AUDIT_APPEND_NOT_AUTHORIZED
```

## Retry And Idempotency

Retries are not authorized:

```text
retry_count: 0
```

The payload still must include an idempotency key so a future sink can detect
duplicate attempts outside SPIRA.

Missing idempotency key:

```text
AUDIT_APPEND_NOT_EVALUATED
```

Any requested retry:

```text
AUDIT_APPEND_NOT_AUTHORIZED
```

## Rollback Or Abort Relation

Append-only audit records are not rolled back by default.

The future authorization must bind:

```text
rollback_or_abort_ref_digest
```

The reference may state:

```text
append is immutable; correction requires a later compensating audit record
```

That compensating record is not authorized by this class model.

Missing rollback or abort reference:

```text
AUDIT_APPEND_NOT_EVALUATED
```

## Human-Go Binding

The human-go artifact must bind:

```text
authorized_action_class = AUDIT_RECORD_APPEND_ONLY
side_effect_budget_digest
expected_side_effects_digest
target_scope_digest
audit_sink_root_id
audit_schema_id
idempotency_key
human_acknowledgement_text_digest
```

The human-readable acknowledgement text must say, in ordinary language:

```text
one non-secret audit record may be appended to the declared audit sink.
No command, target mutation, network send, remediation, severance, retry, or
additional write is authorized by this approval.
```

Approving only opaque digests is not sufficient.

## TCB Binding

The future trusted verifier must preserve:

```text
EA-TCB-03
```

It must compare the human-approved side-effect budget to the runner-intended
append budget for the actual action class:

```text
class_id
total_effect_count
audit_sink_root_id
audit_schema_id
target_scope_digest
payload_digest
idempotency_key
```

The runner must not compute and trust its own budget binding.

## Verdict Vocabulary

Future non-executing class evaluators must use:

```text
AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE
AUDIT_APPEND_NOT_AUTHORIZED
AUDIT_APPEND_NOT_EVALUATED
```

No verdict means that an append occurred, may occur now, or is implemented.

The strongest verdict means only:

```text
the declared AUDIT_RECORD_APPEND_ONLY budget and context are internally
consistent enough to open a later runner implementation discussion.
```

It must still carry:

```text
ACTION_NOT_PERFORMED
```

until a separate runner implementation gate is authorized.

## Fail-Closed Mapping

```text
declared audit sink root, schema-bound non-secret payload, total_effect_count=1,
retry_count=0, no executable fields, no arbitrary path, no network target,
human-go binding, trusted verifier binding, rollback/abort relation, and
idempotency key present
  -> AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE

class not AUDIT_RECORD_APPEND_ONLY
  -> AUDIT_APPEND_NOT_AUTHORIZED

ineligible or permanently non-reclassifiable class
  -> AUDIT_APPEND_NOT_AUTHORIZED

total_effect_count > 1
  -> AUDIT_APPEND_NOT_AUTHORIZED

retry_count > 0
  -> AUDIT_APPEND_NOT_AUTHORIZED

arbitrary path, URL, command content, executable content, or secret-bearing
payload
  -> AUDIT_APPEND_NOT_AUTHORIZED

missing audit sink root, missing schema, missing idempotency key, missing
rollback/abort reference, missing human-go budget binding, missing trusted
verifier binding, or malformed budget artifact
  -> AUDIT_APPEND_NOT_EVALUATED
```

Both not-authorized and not-evaluated outcomes fail closed.

## Required Future Conformance

Any future implementation plan must require tests:

```text
1. strongest valid model path -> AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE
   and ACTION_NOT_PERFORMED.
2. missing audit sink root -> AUDIT_APPEND_NOT_EVALUATED.
3. user-supplied absolute path -> AUDIT_APPEND_NOT_AUTHORIZED.
4. path traversal -> AUDIT_APPEND_NOT_AUTHORIZED.
5. network target supplied -> AUDIT_APPEND_NOT_AUTHORIZED.
6. command field in payload -> AUDIT_APPEND_NOT_AUTHORIZED.
7. secret-bearing payload -> AUDIT_APPEND_NOT_AUTHORIZED.
8. total_effect_count=2 -> AUDIT_APPEND_NOT_AUTHORIZED.
9. retry_count=1 -> AUDIT_APPEND_NOT_AUTHORIZED.
10. missing idempotency key -> AUDIT_APPEND_NOT_EVALUATED.
11. missing human-readable side-effect acknowledgement -> AUDIT_APPEND_NOT_EVALUATED.
12. human-go digest binds different side-effect budget -> AUDIT_APPEND_NOT_AUTHORIZED.
13. trusted verifier compares prepared bundle only -> AUDIT_APPEND_NOT_AUTHORIZED.
14. rollback/abort reference missing -> AUDIT_APPEND_NOT_EVALUATED.
15. append status unknown -> EFFECT_STATUS_UNKNOWN and no follow-on action.
16. strongest verdict still performs no append without later runner gate.
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later design:

```text
moves AUDIT_RECORD_APPEND_ONLY to AUTHORIZED_NOW without separate runner gate
implements append behavior in this gate
adds any write beyond total_effect_count=1
adds pre/post/failure audit records for this class without a new model version
permits arbitrary path or URL input
permits command or executable content in the payload
permits secret-bearing payload
permits retry
omits idempotency key
omits rollback or abort relation
omits human-readable side-effect acknowledgement
omits EA-TCB-03 binding
reports unknown append status as success
changes public CLI or wheel behavior
changes version or release metadata
expands public claims
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_runner_candidate_class_model.md
research/nesira_policy_profile/nesira_phase2_runner_candidate_class_model_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation,
network execution, or non-research artifact change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this model is accepted, the next gate is still not runner implementation.

A future gate may draft:

```text
nesira_phase2_audit_append_non_executing_evaluator_authorization
```

That future evaluator may check model consistency in memory only. It must not
append an audit record or perform any side effect.
