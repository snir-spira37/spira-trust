# Nesira Phase 2 Audit Append Runner Scope Revision Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_RUNNER_SCOPE_REVISION_GATE
SCOPE: RUNNER_SCOPE_REVISION_DESIGN_ONLY

SELECTED_CLASS:
AUDIT_RECORD_APPEND_ONLY

AUTHORIZES:
audit append runner scope revision analysis
eligibility decision for a later class-specific implementation authorization
future implementation hard-stop requirements
future runner conformance expectations
future rollback/abort and audit semantics requirements

AUDIT_RECORD_APPEND_ONLY_STATUS: ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW: []
AUTHORIZED_SIDE_EFFECT_BUDGET_NOW: 0

AUDIT_APPEND_IMPLEMENTATION: NOT_AUTHORIZED
RUNNER_IMPLEMENTATION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_READ: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
AUDIT_SINK_OPEN: NOT_AUTHORIZED
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

This gate crosses only a planning boundary. It records that
`AUDIT_RECORD_APPEND_ONLY` is narrow enough to discuss in a later
implementation authorization. It does not authorize runner code or any append.

## Core Lock

```text
ELIGIBLE_FOR_IMPLEMENTATION_AUTHORIZATION_IS_NOT_AUTHORIZED_NOW
```

The following remain insufficient to append:

```text
AUDIT_APPEND_SATISFIED_FOR_FUTURE_RUNNER_GATE
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
human go
operator initiation
trusted verifier match
GRAPH_OK
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

Even together, they can only open a later implementation authorization
discussion.

## Why This Class Is Eligible

The selected class is eligible for a later implementation authorization because
it is:

```text
concrete
non-generic
append-only
bounded to one record
non-secret
schema-bound
rooted in a declared audit sink
not a command runner
not a target mutator
not a network sender
not a severance or remediation action
```

Eligibility does not mean permission to write.

## Exact Future Effect Envelope

A later implementation authorization may request at most:

```text
primary_effect: append one audit record
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
network_sends: 0
temporary_files: 0
lock_files: 0
cache_writes: 0
checkpoint_writes: 0
post_effect_verification_writes: 0
cleanup_effects: 0
```

The future implementation must not add:

```text
pre-effect audit record
post-effect audit record
failure audit record
status marker
temp file
lock file
cache write
verification write
fallback failure append
retry
cleanup
```

Any expansion of this envelope requires:

```text
SCOPE_REVISION_REQUIRED
new side-effect budget model version
new candidate class model version
adversarial review
human go/no-go owner approval
```

## Required Preconditions For Later Implementation Gate

A later implementation authorization must require all of:

```text
AUDIT_RECORD_APPEND_ONLY class model accepted
audit append non-executing evaluator accepted
execution authorization evaluator accepted
authenticated external human go
operator initiation distinct from human go unless policy explicitly allows
trusted verifier compares runner-intended append context under EA-TCB-03
declared audit sink root
schema-bound non-secret payload
idempotency key
rollback or abort reference
side-effect budget digest
human-readable acknowledgement of the exact side effect
```

Missing any prerequisite must prevent runner invocation.

## Runner / Trusted Verifier Separation

The future runner must not be the trusted verifier.

The trusted verifier must bind:

```text
class_id
audit sink root id and version
audit schema id
payload digest
target scope digest
side-effect budget digest
idempotency key
operator identity or role
human-go artifact digest
```

The runner must receive a verifier-approved, runner-intended context. It must
not construct that context and then trust its own digest.

If the future design cannot prove this separation at the architecture level,
it must stop with:

```text
RUNNER_TCB_SCOPE_REVISION_REQUIRED
```

## Sink Boundary

There is no default sink.

Forbidden sink selection:

```text
current working directory
repository root
environment variable
user-supplied path
system log
network endpoint
target artifact path
```

A later implementation authorization must define a declared audit sink root
contract before code may open anything.

The future runner must not accept arbitrary path input. It may receive only:

```text
AUDIT_SINK_ROOT_ID@version
fixed sink-relative append target from the sink root contract
payload bytes already validated against schema
idempotency key
```

## No Probe Rule

The future runner must not perform unbudgeted probes.

Forbidden unless separately budgeted:

```text
path existence check
directory listing
symlink inspection
stat before append
read-back verification
lock acquisition
temp-file write
permission probe
network reachability probe
```

If the append cannot proceed without a probe, the class model is incomplete and
the implementation gate must stop.

## Failure Semantics

A later implementation must distinguish:

```text
NOT_ATTEMPTED
APPEND_ATTEMPTED
APPEND_APPLIED
APPEND_STATUS_UNKNOWN
APPEND_NOT_AUTHORIZED
APPEND_NOT_EVALUATED
```

Unknown append status must not be reported as success.

Because `total_effect_count=1`, failure handling must not write a fallback
failure audit record. It must return an in-memory failure artifact only.

Any follow-on action after unknown status must stop.

## Public Claim Boundary

Before public exposure of any runner behavior, public text must not say:

```text
safe to execute
approved to run
audit append proves action happened
append proves safety
runner verified safety
automatic remediation
severance authorized
filesystem verified
audit sink certified
```

Allowed pre-implementation language is limited to:

```text
audit append runner scope revision opened
AUDIT_RECORD_APPEND_ONLY eligible for separate implementation authorization
runner implementation still not authorized
append not performed
```

## Required Future Conformance

Any future implementation authorization must require negative tests:

```text
1. no human go -> no append.
2. no operator initiation -> no append.
3. no trusted verifier match -> no append.
4. runner verifies its own context -> no append.
5. missing audit sink root -> no append.
6. default sink attempt -> no append.
7. user-supplied path -> rejected before append.
8. path traversal -> rejected before append.
9. network target -> rejected before append.
10. command or executable payload -> rejected before append.
11. secret-bearing payload -> rejected before append.
12. total_effect_count > 1 -> no append.
13. retry_count > 0 -> no append.
14. unbudgeted probe requested -> no append.
15. fallback failure audit write requested -> no append.
16. append status unknown -> report unknown, no success, no follow-on action.
17. any negative case -> zero side effects.
18. positive case, if separately authorized -> exactly one append and no other
    effects.
```

The positive case remains forbidden until a later implementation authorization
explicitly permits code and test fixtures capable of observing one bounded
append.

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later proposal:

```text
implements runner code in this gate
opens an audit sink in this gate
adds filesystem read or mutation in this gate
moves AUDIT_RECORD_APPEND_ONLY to AUTHORIZED_NOW without implementation authorization
uses generic command, generic path, or generic network abstraction
uses any public assessment or dry-run result as permission to append
turns human go into automatic append trigger
omits operator initiation
collapses runner and trusted verifier
omits declared audit sink root
omits total_effect_count=1
permits retry or supporting writes
writes a fallback failure audit record
reports unknown append status as success
changes public CLI or wheel behavior
changes version or release metadata
expands public claims
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_audit_append_runner_scope_revision_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_scope_revision_authorization_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem read or mutation,
audit sink access, or network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this scope revision is accepted, the next gate is still not implementation
by default.

A future gate may draft:

```text
nesira_phase2_audit_append_runner_implementation_authorization
```

That future authorization must decide whether to permit code that can append
exactly one bounded audit record under the envelope above.
