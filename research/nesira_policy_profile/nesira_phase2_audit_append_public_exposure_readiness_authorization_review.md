# Nesira Phase 2 Audit Append Public Exposure Readiness Authorization Review

## Status

```text
DOCUMENT_TYPE: REVIEW
REVIEWED_DOCUMENT:
nesira_phase2_audit_append_public_exposure_readiness_authorization.md

VERDICT:
NESIRA_PHASE2_AUDIT_APPEND_PUBLIC_EXPOSURE_READINESS_AUTHORIZATION_ACCEPTED
```

## Scope Check

The authorization is docs-only.

It does not authorize:

```text
source changes
test changes
pyproject changes
public wheel changes
workflow changes
version bump
release
GitHub release
PyPI upload
public CLI
public runtime exposure
second side-effect class
generic runner
severance
automatic remediation
```

This matches the private milestone boundary: exposure of the runner/provider
chain is a new decision class and starts from `SCOPE_REVISION_REQUIRED`.

## Boundary Review

The authorization preserves the load-bearing distinctions:

```text
assessment is not action authorization
combined verdict is not execution
dry-run is not execution
execution authorization is not execution
runner/provider exposure is not release
APPEND_APPLIED is not append proof
provider behavior is not Lean-proven
```

The public exposure question is framed correctly: whether the private
`AUDIT_RECORD_APPEND_ONLY` chain should ever become an opt-in public product
surface. It explicitly rejects generic runner, arbitrary path, severance,
remediation, and durability-proof readings.

## Exposure Ladder

The option ladder is appropriately risk-ordered:

```text
no public exposure
public documentation only
public non-writing evaluator library only
public runner library without provider
public runner plus declared provider library
public CLI
```

The document does not pick a release path. It requires the smallest future
surface that satisfies the product need and separates CLI exposure into its own
future gate.

## Provider Boundary

The provider boundary is the most important part of this authorization.

It keeps the future public API constrained to declared sink bindings and opaque
capability identity. It rejects:

```text
raw path exposure to the runner
generic filesystem writer behavior
path/open/read/write/stat/exists/resolve/list/delete exposure
fallback writes
retry
probe-before-append behavior
```

The document also carries the two provider honesty constraints that must not be
lost in public text:

```text
CAP-TCB-01:
  provider behavior is outside the Lean-proven SPIRA composition core

CAP-IDEMPOTENCY-02:
  idempotency durability remains an assumption, not a proof
```

## Claim Review

The claim allowlist is narrow and conditional. It allows only a statement that
SPIRA may contain an opt-in, class-specific `AUDIT_RECORD_APPEND_ONLY` path
that can evaluate and, through a declared capability provider, attempt one
bounded append under recorded assumptions.

The forbidden wording covers the dangerous overclaims:

```text
safe to write
execution approved
action authorized by Nesira
append truth proven
durability proven
idempotency proven
provider proven by Lean
generic runner
arbitrary path support
security or trust guarantee
certification/audit/endorsement
```

The reasonable-reader catch-all is present, so the boundary is not limited to a
literal blocklist.

## Required Future RC Checks

The required future RC checks target the right failure modes:

```text
wheel allowlist exactness
runner source scan
provider source scan
installed-wheel negative cases with zero records
installed-wheel positive case with at most one record
native idempotency guard before write
capability digest mismatch blocks append
CAP-* assumption carriage
release notes claim review
no second side-effect class
```

This is the correct level for a future exposure gate. It does not perform those
checks now because no wheel or source change is authorized by this readiness
gate.

## Finding

No blocking finding.

## Acceptance

```text
NESIRA_PHASE2_AUDIT_APPEND_PUBLIC_EXPOSURE_READINESS_AUTHORIZATION_ACCEPTED
```

The authorization is ready to open only the next docs artifacts:

```text
readiness plan
public claim draft
readiness review
```

Implementation, RC, release, publication, and CLI exposure remain blocked.
