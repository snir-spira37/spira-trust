# Nesira Phase 2 Public Dry-Run Exposure Publication Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLIC_DRY_RUN_EXPOSURE_PUBLICATION_GATE
VERSION: 0.7.3
RC_SOURCE_COMMIT: PENDING_COMMIT
RC_RECORD_COMMIT: PENDING_COMMIT
WHEEL_SHA256: 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5

AUTHORIZES:
publication-readiness preparation
production workflow release-notes update for 0.7.3 public text
TestPyPI staging after explicit GO #1
final pre-publication checks

DOES_NOT_AUTHORIZE_WITHOUT_SEPARATE_GO:
git tag creation or movement
PyPI upload
GitHub release publication
production workflow tag trigger
```

This gate opens publication readiness for the accepted `0.7.3` release
candidate. It does not itself authorize real publication.

## Candidate Lock

The candidate is locked to:

```text
version: 0.7.3
wheel: spira_trust-0.7.3-py3-none-any.whl
wheel_sha256: 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
```

Any wheel-producing source change, version change, dependency change, public
wheel allowlist change, or candidate SHA change requires a new RC.

## Authorized Changes

This publication-readiness gate may touch only:

```text
.github/workflows/pypi-production-publish.yml
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_publication_authorization.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_publication_authorization_review.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_publication_results.json
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_publication_review.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_publication_review_results.json
```

No wheel-producing source, pyproject metadata, tests, V1 package files, or
release-candidate evidence may be changed in this gate.

## Public Release Notes Requirement

The production workflow must generate public release notes that include:

```text
the accepted 0.7.1 conservative combined-verdict text
the accepted 0.7.3 dry-run library-module text
the release-evidence transparency ritual
```

The 0.7.3 text must state:

```text
public library module only
no new public CLI
no new pyproject console entry point
ACTION_NOT_PERFORMED is always carried
separate execution authorization remains required
dry-run is not action execution
dry-run is not action authorization
reproduction is not certification
```

The notes must not claim:

```text
permission to act
operation readiness
action approval
automatic remediation
security guarantee
certification
audit
endorsement
third-party validation
```

## Workflow Safety

Only the release-notes generation block may change.

The following must remain unchanged:

```text
workflow triggers
PyPI publish step
GitHub release publish step
tag-version guard
wheel build step
TestPyPI workflow
```

## GO Boundaries

GO #1 may authorize TestPyPI staging only.

GO #2 may authorize real publication only after:

```text
TestPyPI staging passes
final pre-publication checks pass immediately before tag movement
Snir explicitly issues GO #2
```

Real publication is performed only by tag movement or tag creation for
`v0.7.3`. That tag action triggers the production workflow and is irreversible
in the PyPI-version sense.

## Final Checks Before GO #2

Immediately before GO #2:

```text
HEAD is the intended tag target
wheel-producing source diff from RC source is empty
rebuilt wheel SHA256 equals 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
version is 0.7.3
dependencies=[] remains
cryptography remains optional under nesira-assessment only
V1 SHA256SUMS remains 622/622
no existing PyPI 0.7.3 release
no existing GitHub v0.7.3 release
no existing v0.7.3 tag unless it is a known blocked attempt
production workflow notes contain the approved 0.7.3 public snippet
production workflow trigger and PyPI logic are unchanged
```

## Stop Conditions

Stop if:

```text
the wheel SHA changes
workflow triggers change
PyPI publish logic changes
public notes overclaim execution or authorization
TestPyPI staging fails
final checks fail
Snir has not issued explicit GO #2
```
