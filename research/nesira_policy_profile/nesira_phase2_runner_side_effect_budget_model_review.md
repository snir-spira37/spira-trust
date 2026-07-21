# Nesira Phase 2 Runner Side-Effect Budget Model Review

## Verdict

```text
NESIRA_PHASE2_RUNNER_SIDE_EFFECT_BUDGET_MODEL_ACCEPTED
```

## Scope Review

The gate is docs-only.

It authorizes:

```text
side-effect budget vocabulary
side-effect accounting model
future candidate class budget requirements
future conformance expectations
```

It does not authorize:

```text
runner implementation
subprocess execution
filesystem mutation
network execution
severance action
automatic remediation
CLI or wheel exposure change
version bump
release
public claim expansion
```

The model preserves:

```text
AUTHORIZED_SIDE_EFFECT_BUDGET_NOW = 0
```

No current side effect is authorized.

## Load-Bearing Checks

The model closes the main runner-frontier risk:

```text
NO_FREE_SIDE_EFFECTS
```

Audit writes, log writes, marker writes, temporary files, lock files, cache
writes, network sends, rollback requests, cleanup, and retries are all counted
as side effects. None can be hidden as implementation detail.

## Budget Shape Review

The allowed future shapes are narrow and concrete:

```text
APPEND_ONE_BOUNDED_RECORD
CREATE_ONE_BOUNDED_MARKER
MATERIALIZE_ONE_BOUNDED_REVIEW_PACKET
SEND_ONE_TYPED_ABORT_OR_ROLLBACK_REQUEST
```

They are modeling shapes only and do not authorize implementation.

The forbidden shapes block the dangerous class collapse:

```text
run command
execute process
write arbitrary file
delete arbitrary file
open arbitrary network connection
cleanup as needed
retry until success
write logs as needed
```

This keeps the runner from becoming a generic execution adapter.

## Candidate Ceiling Review

The four candidate classes remain unauthorized and receive only maximum future
ceilings:

```text
AUDIT_RECORD_APPEND_ONLY -> one bounded append
LOCAL_STATUS_MARKER_CREATE_ONLY -> one bounded create-only marker
MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY -> one bounded non-executable packet
ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY -> one typed rollback/abort request
```

The model explicitly allows a later class gate to choose a smaller budget,
including zero.

Increasing a ceiling requires:

```text
SCOPE_REVISION_REQUIRED
new side-effect budget model version
explicit rationale
adversarial review
human go/no-go owner approval
```

## Path And Network Review

The path rule blocks arbitrary path authority:

```text
declared root only
fixed schema-derived relative path
no traversal
no absolute path from user input
no glob expansion
no recursive write or delete
```

The network rule blocks arbitrary network authority:

```text
declared channel root only
fixed endpoint identity
typed payload
idempotency key
timeout
no user-supplied endpoint
```

Both rules fail closed before any side effect.

## Audit And Retry Review

The model correctly treats audit as a side effect, not free metadata.

It also treats retries as side effects:

```text
retry_count = 0
```

Any retry must be explicitly budgeted and idempotent. This prevents hidden
amplification of an apparently small action.

## Total Ceiling Review

The model now requires:

```text
NO_UNBOUNDED_TOTAL
```

The side-effect ceiling applies to the total budget, not only to the primary
effect. Supporting effects are counted too:

```text
audit records
status markers
temporary files
lock files
cache writes
checkpoint writes
post-effect verification writes
rollback or abort requests
retry attempts
```

The initial candidate ceilings are bounded:

```text
AUDIT_RECORD_APPEND_ONLY -> total_effect_count <= 1
LOCAL_STATUS_MARKER_CREATE_ONLY -> total_effect_count <= 4
MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY -> total_effect_count <= 4
ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY -> total_effect_count <= 4
```

The three audit records are a closed set for the initial candidate classes:

```text
pre_effect_audit_record
post_effect_audit_record
failure_audit_record
```

A future design cannot create a broad write channel by adding more audit,
logging, checkpoint, verification, or telemetry effects while claiming each one
is individually budgeted.

## Partial Failure Review

The model requires future runner designs to distinguish:

```text
NOT_ATTEMPTED
ATTEMPTED_NO_EFFECT_OBSERVED
EFFECT_APPLIED
EFFECT_PARTIALLY_APPLIED
EFFECT_STATUS_UNKNOWN
ROLLBACK_OR_ABORT_REQUESTED
ROLLBACK_OR_ABORT_UNAVAILABLE
```

Unknown effect status cannot be reported as success. This is the key
fail-closed condition once real side effects exist.

## Audit Terminal Anchor Review

The audit sink is correctly defined as the terminal accounting anchor. Audit
records are counted side effects, but they do not recursively require more
audit records for the audit write itself.

## Human And TCB Binding Review

The side-effect budget must be bound into human go by digest and explained in
human-readable acknowledgement text.

The model preserves:

```text
EA-TCB-03
```

The trusted verifier must compare the human-approved side-effect budget and
target scope to the runner-intended side-effect budget and target scope. The
runner cannot compute and trust its own binding.

## Verdict Boundary Review

The strongest budget verdict is:

```text
SIDE_EFFECT_BUDGET_SATISFIED_FOR_FUTURE_RUNNER_GATE
```

It means only that a later class-specific runner discussion may open. It does
not mean an effect occurred, may occur now, or has implementation authorization.

The model keeps:

```text
ACTION_NOT_PERFORMED
```

outside the budget verdict itself as the required boundary for future
non-executing evaluators and plans.

## Required Negative Cases Review

The conformance list covers the load-bearing failure modes:

```text
missing budget
ceiling exceeded
ineligible class
permanently non-reclassifiable class
arbitrary path or URL
path traversal
symlink ambiguity
retry without idempotency
secret-bearing payload
executable content
missing mandatory audit budget
unknown effect status
human text omission
human-go budget digest mismatch
prepared-bundle-only verifier
strongest budget verdict still not execution
```

This is sufficient for a later docs-only candidate class model.

## Boundary

The model is accepted as:

```text
MODEL_ONLY
zero side-effect budget now
future budget accounting only
no runner implementation
no subprocess
no filesystem mutation
no network execution
no release or public claim change
```

The next gate, if opened, must remain docs-only and select exactly one
candidate class for modeling under this budget.
