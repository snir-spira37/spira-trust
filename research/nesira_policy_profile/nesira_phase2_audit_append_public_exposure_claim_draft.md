# Nesira Phase 2 Audit Append Public Exposure Claim Draft

## Status

```text
DOCUMENT_TYPE: PUBLIC CLAIM DRAFT
PUBLICATION: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_WHEEL_CHANGE: NOT_AUTHORIZED
```

This draft is for review only. It must not be used publicly without a separate
publication authorization.

## Proposed Public Claim

SPIRA has a private, opt-in, class-specific `AUDIT_RECORD_APPEND_ONLY` chain
that evaluates declared preconditions for one bounded audit append and can
delegate the append attempt to a declared capability provider under recorded
assumptions.

If this chain is ever exposed publicly, it remains limited to the
`AUDIT_RECORD_APPEND_ONLY` class. It is not a generic runner, not arbitrary
filesystem access, not network execution, not severance, and not automatic
remediation.

`APPEND_APPLIED` is a provider status report. It is not proof that the append is
durable, that the sink root is legitimate, that idempotency is truly enforced,
or that the provider behavior is covered by SPIRA's Lean-proven composition
core. Provider behavior and sink properties remain conditional on recorded
`CAP-*` assumptions, including `CAP-TCB-01` and `CAP-IDEMPOTENCY-02`.

## Short Form

SPIRA's private audit-append chain is class-specific and opt-in. It can attempt
one bounded audit append only through a declared capability provider, under
recorded assumptions. `APPEND_APPLIED` is a status report, not proof of durable
append truth, provider correctness, or sink legitimacy.

## Boundary

This claim does not mean:

```text
safe to write
safe to run
execution approved
permission granted by Nesira
generic runner
arbitrary path support
secure filesystem runner
append truth proven
durability proven
idempotency proven
sink legitimacy proven
provider proven by Lean
severance authorized
automatic remediation
security guarantee
trust guarantee
independent certification
audit
endorsement
third-party validation
```

## Evidence Statement

External or cold reproduction, if later performed for a public release
candidate, would mean only that the recorded checks and package behavior were
reproduced. It would not mean independent certification, audit, endorsement,
third-party validation, or a security or trust guarantee.

## Required Public Wording

Any future release notes, README text, PyPI description, GitHub release text, or
announcement must preserve:

```text
opt-in only
AUDIT_RECORD_APPEND_ONLY only
not a generic runner
not arbitrary filesystem access
APPEND_APPLIED is a provider status report only
provider behavior is outside the Lean-proven composition core
CAP-* assumptions remain NOT_PROVEN
EA-TCB-03 remains assumed, not proven
no severance
no automatic remediation
```

## Option-Specific Clauses

If only non-writing evaluators are exposed publicly, public text must also
state:

```text
the public surface evaluates consistency only and does not write
runner and provider code remain absent from the public wheel
```

If the runner is exposed publicly without the provider, public text must also
state:

```text
SPIRA does not provide a filesystem-capable provider in this release
any supplied capability is outside SPIRA's proof boundary
```

If the runner and declared provider are exposed publicly, public text must also
state:

```text
the provider can attempt one append only through a declared sink binding
the provider performs no retry, fallback write, probe, or readback
native durable idempotency is required before APPEND_APPLIED may be reported
```

## Stop Condition

Stop if any public wording can be reasonably read as:

```text
APPEND_APPLIED proves the append happened durably
SPIRA proves provider correctness
Nesira authorizes action
the user can run arbitrary filesystem actions
the release is certified, audited, endorsed, or guaranteed
```
