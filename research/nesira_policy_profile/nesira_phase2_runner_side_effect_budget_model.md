# Nesira Phase 2 Runner Side-Effect Budget Model

## Status

```text
DOCUMENT_TYPE: RESEARCH -- RUNNER SIDE-EFFECT BUDGET MODEL
PHASE: PHASE_2_RUNNER_SIDE_EFFECT_BUDGET_GATE
SCOPE: MODEL_ONLY

AUTHORIZES:
side-effect budget vocabulary
side-effect accounting model
future candidate class budget requirements
future conformance expectations

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

This document defines how a later runner action class must account for side
effects before any implementation may be discussed. It does not authorize any
runner code or any real side effect.

## Core Lock

```text
AUTHORIZED_SIDE_EFFECT_BUDGET_NOW = 0
```

No action class receives a non-zero budget here.

The purpose of this model is to make any future non-zero side effect explicit,
bounded, class-specific, reversible or abortable where possible, and reviewable
before code exists.

## Core Invariant

```text
NO_FREE_SIDE_EFFECTS
```

Any operation that changes external state must be counted in the budget.

There are no implementation-detail exemptions for:

```text
audit writes
log writes
status markers
temporary files
lock files
cache writes
state checkpoints
network sends
rollback or abort requests
cleanup
retries
post-action verification writes
```

If a future runner needs one of these, the future action-class model must name
it as an explicit budgeted effect.

## Budget Vocabulary

Every future non-zero side-effect budget must use this vocabulary:

```text
effect_class
effect_count
declared_root
target_scope_digest
payload_schema_id
payload_max_bytes
idempotency_key
overwrite_policy
retry_policy
timeout_policy
rollback_or_abort_ref
post_effect_verification_boundary
audit_relation
secret_handling_rule
failure_semantics
```

Any budget that cannot fill these fields must stop with:

```text
SIDE_EFFECT_BUDGET_INCOMPLETE
```

## Allowed Future Effect Shapes

Only the following shapes may be modeled by later gates, and only for candidate
classes already named by the runner action class taxonomy.

```text
APPEND_ONE_BOUNDED_RECORD
  maximum effect_count: 1
  target: declared append-only audit sink
  overwrite_policy: append-only, no rewrite, no delete
  payload: non-secret, schema-bound, max bytes declared by class

CREATE_ONE_BOUNDED_MARKER
  maximum effect_count: 1
  target: declared output root + fixed schema-derived relative name
  overwrite_policy: create-only, no overwrite, no delete
  payload: non-secret, schema-bound, max bytes declared by class

MATERIALIZE_ONE_BOUNDED_REVIEW_PACKET
  maximum effect_count: 1 logical packet
  target: declared output root + fixed schema-derived relative name
  overwrite_policy: create-only, no overwrite, no executable content
  payload: non-secret, schema-bound, max bytes declared by class

SEND_ONE_TYPED_ABORT_OR_ROLLBACK_REQUEST
  maximum effect_count: 1
  target: declared channel root, not arbitrary URL or host input
  payload: typed schema, idempotency key, timeout, no command content
```

These are modeling shapes only. They do not authorize implementation.

## Forbidden Budget Shapes

The following are not budget shapes:

```text
run command
execute process
invoke tool
write arbitrary file
delete arbitrary file
mutate arbitrary path
open arbitrary network connection
send arbitrary HTTP request
cleanup as needed
retry until success
write logs as needed
best effort rollback
any path under workspace
any URL from user input
```

Any future design using one of these must stop with:

```text
RUNNER_ACTION_CLASS_INELIGIBLE
```

## Candidate Class Budget Ceilings

The current candidate classes remain unauthorized. If a later gate models them,
their maximum initial budgets are:

```text
AUDIT_RECORD_APPEND_ONLY
  ceiling: APPEND_ONE_BOUNDED_RECORD, effect_count = 1
  no marker, no packet, no network, no cleanup side effect unless separately
  budgeted by a later class-specific gate.

LOCAL_STATUS_MARKER_CREATE_ONLY
  ceiling: CREATE_ONE_BOUNDED_MARKER, effect_count = 1
  no overwrite, no delete, no directory cleanup, no command content.

MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY
  ceiling: MATERIALIZE_ONE_BOUNDED_REVIEW_PACKET, effect_count = 1 logical
  packet
  no executable instructions, no secrets, no runbook, no copy-paste commands.

ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY
  ceiling: SEND_ONE_TYPED_ABORT_OR_ROLLBACK_REQUEST, effect_count = 1
  no arbitrary endpoint, no retry storm, no implicit remediation.
```

Any future class-specific gate may choose a smaller budget, including zero. It
may not exceed these ceilings without:

```text
SCOPE_REVISION_REQUIRED
new side-effect budget model version
explicit rationale
adversarial review
human go/no-go owner approval
```

## Path Budget Rule

Future filesystem effects must be rooted and non-arbitrary.

Allowed future path shape:

```text
declared_root_id@version
fixed relative path from action-class schema
path digest included in human-go binding
no traversal
no absolute path from user input
no symlink-following ambiguity
create-only or append-only policy
maximum bytes
```

Forbidden:

```text
caller-supplied absolute path
caller-supplied relative path
path normalization as authorization
glob expansion
recursive write
recursive delete
overwrite by default
```

Path validation failure must fail closed before any side effect.

## Network Budget Rule

Future network effects must be channel-rooted and typed.

Allowed future network shape:

```text
declared_channel_root_id@version
fixed endpoint identity from the declared root
typed payload schema
idempotency key
timeout
single attempt unless retry is explicitly budgeted
```

Forbidden:

```text
arbitrary URL
arbitrary host
user-supplied endpoint
open-ended retry
network discovery
credential exfiltration path
```

Network validation failure must fail closed before any send.

## Attempt And Retry Accounting

Retries are side effects.

Default retry budget:

```text
retry_count = 0
```

Any future retry must be explicit:

```text
retry_count
retry_delay_policy
idempotency_key
max_elapsed_time
duplicate_effect_detection
```

If idempotency cannot be established, retry is not authorized.

## Partial Failure Semantics

Future runner designs must distinguish:

```text
NOT_ATTEMPTED
ATTEMPTED_NO_EFFECT_OBSERVED
EFFECT_APPLIED
EFFECT_PARTIALLY_APPLIED
EFFECT_STATUS_UNKNOWN
ROLLBACK_OR_ABORT_REQUESTED
ROLLBACK_OR_ABORT_UNAVAILABLE
```

Unknown effect status must never be reported as success.

If the system cannot tell whether an effect occurred, it must report:

```text
EFFECT_STATUS_UNKNOWN
```

and fail closed for any follow-on action.

## Audit Accounting Rule

Audit records are side effects, not free metadata.

A future action class may require:

```text
pre_effect_audit_record
post_effect_audit_record
failure_audit_record
```

Each required record must be budgeted explicitly. If audit is mandatory and the
budget does not include it, the model is incomplete.

Audit failure semantics must be defined before the action effect:

```text
if mandatory pre-effect audit fails -> no action effect
if post-effect audit fails after effect -> report partial failure, do not claim clean success
if audit status unknown -> effect status unknown unless independently verified
```

## Secret Handling

Side-effect payloads must be non-secret by default.

Forbidden unless a later secret-specific gate exists:

```text
secret values
tokens
private keys
passwords
credentials
environment dumps
filesystem snapshots
network captures
```

Redaction is not enough to make secret-bearing side effects authorized. A
secret-bearing side effect is a new scope class.

## Human-Go Binding

Any future non-zero budget must be bound into the human-go artifact by digest:

```text
side_effect_budget_digest
expected_side_effects_digest
target_scope_digest
rollback_or_abort_ref_digest
human_acknowledgement_text_digest
```

The human-readable acknowledgement text must name the side-effect class,
effect count, target scope, maximum payload size, retry policy, and rollback or
abort relation.

Approving an opaque side-effect hash is not sufficient.

## TCB Binding

Every future side-effect budget must preserve:

```text
EA-TCB-03
```

The trusted verifier must compare the human-approved side-effect budget and
target scope to the runner-intended budget and target scope for the actual
action class.

The runner must not compute and trust its own budget binding.

## Budget Verdict Vocabulary

Future class-specific budget evaluators must use:

```text
SIDE_EFFECT_BUDGET_SATISFIED_FOR_FUTURE_RUNNER_GATE
SIDE_EFFECT_BUDGET_NOT_AUTHORIZED
SIDE_EFFECT_BUDGET_NOT_EVALUATED
```

No verdict means that an effect occurred, may occur now, or is implemented.

The strongest verdict means only:

```text
the declared side-effect budget is internally consistent and narrow enough to
open a later class-specific runner discussion.
```

## Fail-Closed Mapping

```text
complete budget, concrete candidate class, declared roots, bounded count,
bounded payload, bound target scope, idempotency where needed, rollback/abort
relation, human-readable acknowledgement binding, and trusted verifier binding
  -> SIDE_EFFECT_BUDGET_SATISFIED_FOR_FUTURE_RUNNER_GATE

class not candidate or ineligible
  -> SIDE_EFFECT_BUDGET_NOT_AUTHORIZED

budget exceeds class ceiling
  -> SIDE_EFFECT_BUDGET_NOT_AUTHORIZED

arbitrary path, arbitrary URL, command content, secret-bearing payload, or
unbounded retry
  -> SIDE_EFFECT_BUDGET_NOT_AUTHORIZED

missing declared root, missing payload schema, missing target digest, missing
rollback/abort relation, missing clock, missing TCB binding, or malformed
budget artifact
  -> SIDE_EFFECT_BUDGET_NOT_EVALUATED
```

Both not-authorized and not-evaluated outcomes fail closed.

## Required Future Negative Cases

Every future side-effect budget implementation plan must require tests:

```text
1. missing side-effect budget -> not evaluated.
2. side-effect count exceeds ceiling -> not authorized.
3. class marked INELIGIBLE_ALWAYS -> not authorized.
4. permanently non-reclassifiable class -> not authorized.
5. arbitrary path input -> not authorized.
6. path traversal -> not authorized.
7. symlink ambiguity -> not evaluated.
8. arbitrary URL input -> not authorized.
9. retry requested without idempotency -> not authorized.
10. secret-bearing payload -> not authorized.
11. executable content in packet or audit -> not authorized.
12. mandatory audit missing from budget -> not evaluated.
13. mandatory pre-effect audit fails -> action not attempted.
14. effect status unknown -> no follow-on action.
15. human-readable text omits side-effect summary -> not evaluated.
16. human-go digest binds different side-effect budget -> not authorized.
17. trusted verifier compares prepared bundle only -> not authorized.
18. strongest budget verdict still emits ACTION_NOT_PERFORMED without later
    runner gate.
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later design:

```text
authorizes any non-zero side-effect budget without per-class runner gate
treats audit/log/temp/cache writes as free implementation details
permits arbitrary command, path, URL, or payload
permits unbounded cleanup or retry
permits secret-bearing side effects without a new secret-specific gate
omits human-readable side-effect acknowledgement
omits EA-TCB-03 binding to the runner-intended side-effect budget
reports unknown effect status as success
uses a budget verdict as permission to execute
changes public CLI or wheel behavior
changes version or release metadata
expands public claims
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_runner_side_effect_budget_model.md
research/nesira_policy_profile/nesira_phase2_runner_side_effect_budget_model_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation, or
network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this model is accepted, the next gate remains docs-only:

```text
nesira_phase2_runner_candidate_class_model
```

That future gate may select exactly one candidate class and model it under this
budget. It still must not authorize runner implementation or any side effect.
