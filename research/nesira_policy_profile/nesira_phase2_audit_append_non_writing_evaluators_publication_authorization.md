# Nesira Phase 2 Audit Append Non-Writing Evaluators Publication Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_NON_WRITING_EVALUATORS_PUBLICATION_GATE
VERSION: 0.7.4
RC_SOURCE_COMMIT: e95223ce453ec06c6912f5ebad686c3eabe4c6bb
RC_RECORD_COMMIT: 8b2896ddf01182739b24661ac0638613da37e518
WHEEL_SHA256: 479ff28a91adf8bb51d55320d2f723ac563d7b92c2a7c80c4a15a861bb96fd7e

AUTHORIZES:
publication-readiness preparation
production workflow release-notes update for 0.7.4 public text
TestPyPI staging after explicit GO #1
final pre-publication checks

DOES_NOT_AUTHORIZE_WITHOUT_SEPARATE_GO:
git tag creation or movement
PyPI upload
GitHub release publication
production workflow tag trigger
```

This gate opens publication readiness for the accepted `0.7.4` release
candidate. It does not itself authorize real publication.

## Candidate Lock

The candidate is locked to:

```text
version: 0.7.4
wheel: spira_trust-0.7.4-py3-none-any.whl
wheel_sha256: 479ff28a91adf8bb51d55320d2f723ac563d7b92c2a7c80c4a15a861bb96fd7e
```

Any wheel-producing source change, version change, dependency change, public
wheel allowlist change, or candidate SHA change requires a new RC.

## Authorized Changes

This publication-readiness gate may touch only:

```text
.github/workflows/pypi-production-publish.yml
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_publication_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_publication_authorization_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_publication_results.json
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_publication_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_publication_review_results.json
```

No wheel-producing source, pyproject metadata, tests, V1 package files, or
release-candidate evidence may be changed in this gate.

## Public Release Notes Requirement

The production workflow must generate public release notes that include:

```text
the accepted 0.7.1 conservative combined-verdict text
the accepted 0.7.3 dry-run library-module text
the accepted 0.7.4 non-writing evaluator library-module text
the release-evidence transparency ritual
```

The 0.7.4 text must state:

```text
public library modules only
non-writing evaluators only
no public CLI
runner/provider absent from the public wheel
execution_authorization_evaluator checks consistency and does not authorize execution
audit_append_evaluator checks preconditions and does not write
APPEND_APPLIED is not emitted by the exposed modules
APPEND_APPLIED remains a provider status report, not proof
EA-TCB-03 remains assumed, not proven
provider behavior remains outside the Lean-proven core
```

The notes must not claim:

```text
append performed
permission to act
operation readiness
action approval
runner or provider exposure
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
final pre-publication checks pass immediately before tag creation or movement
Snir explicitly issues GO #2
```

Real publication is performed only by tag creation or movement for `v0.7.4`.
That tag action triggers the production workflow and is irreversible in the
PyPI-version sense.

## Final Checks Before GO #2

Immediately before GO #2:

```text
HEAD is the intended tag target
wheel-producing source diff from e95223c is empty
rebuilt wheel SHA256 equals 479ff28a91adf8bb51d55320d2f723ac563d7b92c2a7c80c4a15a861bb96fd7e
version is 0.7.4
dependencies=[] remains
cryptography remains optional under nesira-assessment only
V1 SHA256SUMS remains 622/622
no existing PyPI 0.7.4 release
no existing GitHub v0.7.4 release
no existing v0.7.4 tag unless it is a known blocked attempt
production workflow notes contain the approved 0.7.4 public snippet
production workflow trigger and PyPI logic are unchanged
```

## Stop Conditions

Stop if:

```text
the wheel SHA changes
workflow triggers change
PyPI publish logic changes
public notes overclaim execution, append, authorization, or provider exposure
TestPyPI staging fails
final checks fail
Snir has not issued explicit GO #2
```
