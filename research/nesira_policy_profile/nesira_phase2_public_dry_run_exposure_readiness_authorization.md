# Nesira Phase 2 Public Dry-Run Exposure Readiness Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLIC_DRY_RUN_EXPOSURE_READINESS_GATE
SCOPE: READINESS_PLANNING_AND_PUBLIC_TEXT_DRAFTING_ONLY

AUTHORIZES:
public dry-run exposure readiness package planning
public dry-run claim text drafting
release-candidate checklist drafting
rollback/support notes drafting

PUBLIC_WHEEL_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_CHANGE: NOT_AUTHORIZED
PYPROJECT_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
RUNNER_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
PUBLIC_CLAIM_USE: NOT_AUTHORIZED
```

This gate decides what would be required before the internal dry-run review
surface could be considered for public exposure.

It does not authorize any code, wheel, CLI, version, release, publication, or
execution change.

## Baseline

The accepted internal surface is:

```text
verdict: NESIRA_PHASE2_DRY_RUN_EXPOSURE_COLD_VERIFICATION_ACCEPTED
commit: 797c825dfeba16687918f58df63c359df275cf3c
targeted exposure pytest: 9 passed
full pytest: 387 passed
V1 SHA256SUMS: 622 OK / 0 FAILED
public wheel sha256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
dry_run_module_present_in_public_wheel: false
dry_run_tool_present_in_public_wheel: false
```

Public exposure would intentionally change that boundary, so it must be treated
as a new product surface, not as a routine continuation.

## Public Exposure Question

The readiness question is:

```text
Should the already verified non-executing dry-run artifact become a public
read-only surface?
```

It is not:

```text
Should SPIRA execute actions?
Should SPIRA authorize severance?
Should SPIRA provide a runner?
Should dry-run become permission to act?
```

## Mandatory Public Claim Boundary

Any future public dry-run claim may state only:

```text
SPIRA can emit a non-executing dry-run artifact that reports whether declared
preconditions are present for later human review.
```

It must also state:

```text
dry-run is not execution
dry-run is not action authorization
dry-run is not severance authorization
dry-run emits ACTION_NOT_PERFORMED even when preconditions are satisfied
separate execution authorization remains required
Nesira sufficient is not action authorization
action authority is not execution
```

Forbidden public wording:

```text
ready to run
safe to run
execution approved
permission granted
action authorized
severance authorized
automatic remediation
runner
executes
proves isolation happened
security guarantee
trust guarantee
certified
audited
third-party validated
endorsed
```

Any public text that a reasonable reader could interpret as execution,
permission to act, safety guarantee, certification, or runner behavior must stop
with:

```text
PUBLIC_DRY_RUN_CLAIM_SCOPE_REVISION_REQUIRED
```

## Public Surface Options

The readiness package must compare at least:

```text
Option A: no public exposure
  keep dry-run internal only

Option B: public library module only
  include evaluator in wheel, no console entry point

Option C: public read-only CLI subcommand/tool
  user can run dry-run review from installed package

Option D: public CLI + docs + release notes
  highest exposure in this family, still non-executing
```

The first public exposure should prefer the smallest surface that satisfies the
product need. Public CLI is higher risk than library exposure because exit code,
flags, help text, and examples can all be misread as action semantics.

## Required Release Candidate Consequences

Any actual public exposure later would require a new RC because it would change
the public wheel or public interface.

The RC gate must account for:

```text
version bump
wheel SHA change
public wheel allowlist update
pyproject/entry point decision
release notes review
public claim review
TestPyPI dry-run
post-install verification from built wheel
V1 manifest narrow refresh if a V1-pinned file changes
```

No release action is authorized by this readiness gate.

## Required Tests For A Later RC

A later RC must prove:

```text
1. installed public artifact emits dry-run JSON.
2. all outputs carry ACTION_NOT_PERFORMED.
3. strongest dry-run path still says not execution.
4. exit code means tool success only.
5. malformed input gives clean JSON error, no traceback.
6. no executable fields are emitted.
7. no subprocess/filesystem/network side effects occur.
8. base install dependency posture remains intentional.
9. public help text and docs stay inside claim boundary.
10. actual execution remains absent from wheel and CLI.
```

If public exposure requires a public CLI, the RC must also test:

```text
no --execute / --run / --apply / --remediate / --sever flags
no examples that can be copied as execution commands
exit code 0 for blocked/not-evaluated dry-runs when the tool succeeds
```

## Authorized Files

This gate may create only:

```text
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_readiness_authorization.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_readiness_authorization_review.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_claim_draft.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_readiness_plan.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_readiness_review.md
```

Any source, tests, pyproject, workflow, manifest, public wheel builder, version,
release, or publication change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Stop Conditions

Stop if readiness work:

```text
recommends public exposure without claim text review
collapses dry-run into authorization
uses dry-run as runner language
omits ACTION_NOT_PERFORMED from the public claim
requires code or release changes in this gate
```

## Next Step

If this authorization is accepted, draft the readiness plan and public claim
text. Implementation and release remain separate future gates.
