# Nesira Phase 2 Audit Append Documentation-Only Exposure Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_DOCUMENTATION_ONLY_EXPOSURE_GATE
SCOPE: PUBLIC_DOCUMENTATION_ONLY

SELECTED_OPTION:
Option B: public documentation only

AUTHORIZES:
one public documentation page describing the private audit append boundary
documentation-only review

SOURCE_CHANGE: NOT_AUTHORIZED
TEST_CHANGE: NOT_AUTHORIZED
PYPROJECT_CHANGE: NOT_AUTHORIZED
README_CHANGE: NOT_AUTHORIZED
PUBLIC_WHEEL_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
WORKFLOW_CHANGE: NOT_AUTHORIZED
RUNTIME_EXPOSURE: NOT_AUTHORIZED
SECOND_SIDE_EFFECT_CLASS: NOT_AUTHORIZED
GENERIC_RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
```

This gate selects the documentation-only path from the accepted readiness plan.
It may add one public-facing documentation page under `docs/`. It does not
authorize changing the package, wheel, CLI, README, release notes, or runtime
surface.

## Baseline

```text
public package: spira-trust 0.7.3
public wheel sha256: 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
private milestone: NESIRA_PHASE2_PRIVATE_AUDIT_APPEND_CHAIN_COMPLETE_PRIVATE_ONLY
private milestone commit: a77ace464dc79214b23468a1d5d981360d6d8517
```

The public wheel still excludes:

```text
audit append runner
audit append capability provider
execution authorization evaluator
action authority evaluator
```

## Authorized Public Documentation

This gate may add only:

```text
docs/audit_append_boundary.md
```

The page may describe:

```text
the private audit append milestone
the completed private chain
the class-specific AUDIT_RECORD_APPEND_ONLY envelope
the public 0.7.3 boundary
the provider and runner boundaries
the CAP-* and EA-* assumption boundaries
what remains not authorized
```

The page must state that the documentation is not a release announcement and
does not expose runtime code.

## Claim Boundary

The documentation may state only:

```text
SPIRA has a private, opt-in, class-specific AUDIT_RECORD_APPEND_ONLY chain that
can attempt one bounded audit append through a declared capability provider
under recorded assumptions.
```

It must also state:

```text
the public 0.7.3 wheel does not include the runner or provider
APPEND_APPLIED is a provider status report, not proof
provider behavior is outside the Lean-proven composition core
CAP-* assumptions remain NOT_PROVEN
EA-TCB-03 remains assumed, not proven
no generic runner, arbitrary path, severance, or remediation is authorized
```

Forbidden wording:

```text
safe to write
safe to run
execution approved
permission granted by Nesira
append truth proven
durability proven
idempotency proven
sink legitimacy proven
provider proven by Lean
secure filesystem runner
generic runner
arbitrary path support
automatic remediation
severance authorized
certified
audited
endorsed
third-party validated
security guarantee
trust guarantee
```

Any wording that a reasonable reader could interpret as runtime exposure,
permission to act, proof of append truth, or release approval must stop with:

```text
DOCUMENTATION_ONLY_CLAIM_SCOPE_REVISION_REQUIRED
```

## Authorized Files

This gate may touch only:

```text
docs/audit_append_boundary.md
research/nesira_policy_profile/nesira_phase2_audit_append_documentation_only_exposure_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_documentation_only_exposure_review.md
```

Do not update `README.md` in this gate. `README.md` is the wheel long
description source and changing it would change future wheel metadata.

Any other file change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Required Verification

Before acceptance:

```text
git diff is limited to the authorized files
git diff --check passes
public text contains APPEND_APPLIED is not proof
public text contains provider outside Lean-proven core
public text states 0.7.3 public wheel does not include runner/provider
public text contains no forbidden wording outside boundary sections
README.md remains unchanged
pyproject.toml remains unchanged
tools/build_spira_trust_public.py remains unchanged
```

## Stop Conditions

Stop if the documentation:

```text
claims the public wheel exposes audit append runtime
claims APPEND_APPLIED proves a durable append
claims provider behavior is formally proven
links documentation-only exposure to release approval
adds install or CLI instructions for audit append
```

## Next Step

If accepted, add the documentation page and review it. Runtime exposure,
release-candidate preparation, release, and publication remain separate gates.
