# Nesira Phase 2 Audit Append Runner Implementation Authorization Review

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_RUNNER_IMPLEMENTATION_AUTHORIZATION_ACCEPTED
```

## Scope Review

This is the first gate that may authorize code with a non-zero side-effect
budget, and it is correctly limited to one class:

```text
AUDIT_RECORD_APPEND_ONLY
```

It does not authorize public exposure, CLI changes, version bump, release,
generic runner behavior, network execution, severance, or remediation.

## Taxonomy Review

The authorization requires runner taxonomy V3:

```text
AUDIT_RECORD_APPEND_ONLY_STATUS: AUTHORIZED_NOW
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW: [AUDIT_RECORD_APPEND_ONLY]
```

This keeps taxonomy as the source of truth. The authorization does not create a
side status outside the taxonomy.

## Effect Envelope Review

The envelope is exact:

```text
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
```

The implementation may perform exactly one effect on the positive path:

```text
append_one(record_payload, idempotency_key)
```

through a declared audit sink append capability.

No direct filesystem path handling is authorized by the runner.

## Sink Capability Review

The runner does not receive arbitrary paths. It receives a declared sink
capability already bound by human go and trusted verifier evidence.

The capability must not expose path, open, read, arbitrary write, delete,
overwrite, list, stat, endpoint, or command operations.

The authorization now also requires the runner to compare the supplied
`append_capability_root_digest` against the human-go and trusted-verifier
approved digest before the single append call. A missing or mismatched digest
must return `AUDIT_APPEND_NOT_AUTHORIZED` with zero attempted and applied
effects.

This closes capability-substitution at the call site without claiming that the
object behind the capability is proven honest; capability correctness remains an
explicit assumption.

This is the safest shape for the first real effect: the runner can request one
typed append without becoming a filesystem adapter.

## No Probe Review

The no-probe rule remains load-bearing.

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

Any need for a probe means the model is incomplete.

## Failure Review

Failure handling is in-memory only.

Because `total_effect_count=1`, the runner cannot write:

```text
failure audit record
fallback audit record
error log
temporary diagnostic file
checkpoint
cleanup marker
```

Unknown append status is not success.

## Conformance Review

The required 24 cases cover:

```text
all precondition failures -> zero append calls
all path/network/command/secret attempts -> zero append calls
append capability root digest mismatch -> zero append calls
budget expansion -> zero append calls
retry request -> zero append calls
unbudgeted probe request -> zero append calls
fallback failure write request -> zero append calls
unknown append status -> not success
positive path -> exactly one append call and no other effects
append capability called at most once
public wheel exclusion remains true
```

## Boundary

The authorization is accepted as:

```text
CLASS_SPECIFIC_RUNNER_IMPLEMENTATION_AUTHORIZATION
one declared audit append capability call only
private implementation only
no public exposure
no release
no generic runner
```

The next implementation may write only the private audit append runner and its
tests under this envelope.
