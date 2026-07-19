# Nesira Phase 2 Publication Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLICATION_GATE
SCOPE: PUBLICATION_OF_ACCEPTED_READ_ONLY_RELEASE_CANDIDATE

AUTHORIZES_CONDITIONALLY:
FINAL_PRE_PUBLICATION_CHECKS
TESTPYPI_DRY_RUN_FOR_V0_7_0
GIT_TAG_CREATION_FOR_V0_7_0
GITHUB_RELEASE_DRAFT_FOR_V0_7_0
GITHUB_RELEASE_PUBLICATION_FOR_V0_7_0
PYPI_UPLOAD_FOR_V0_7_0_REQUIRES_SECOND_GO
PUBLIC_RELEASE_NOTES_USE
PUBLIC_CLAIM_USE_WITH_ACCEPTED_BOUNDARY

COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
VERSION_CHANGE: NOT_AUTHORIZED
SCOPE_EXPANSION: NOT_AUTHORIZED
```

This document opens the publication gate for the accepted `spira-trust` 0.7.0
release candidate only.

It does not authorize changing the candidate. It authorizes publication only if
the exact accepted candidate is still intact and the final pre-publication
checks pass immediately before publication.

## Accepted Candidate

```text
release_candidate_review_commit:
c3221efbebdedefac1c3b587820df83a0aeafd4b

candidate_code_commit:
cdceab25292e7d4522865df09f9695468990b3f9

version:
0.7.0

wheel:
spira_trust-0.7.0-py3-none-any.whl

wheel_sha256:
956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5

accepted_verdict:
NESIRA_PHASE2_RELEASE_CANDIDATE_ACCEPTED
```

The publication must use this candidate only. Any changed source, rebuilt wheel
with a different SHA256, changed release notes, changed claim text, changed
version, or changed dependency posture must stop with:

```text
PUBLICATION_CANDIDATE_CHANGED_REQUIRES_NEW_RC
```

## Publication Boundary

The public claim remains:

```text
SPIRA includes an opt-in Nesira Phase 2 read-only assessment surface in the
public wheel. The surface checks declared trust evidence against declared trust
roots and composes the result through a verified fail-closed composition core,
conditional on the declared trust roots and recorded NOT_PROVEN assumptions.
It emits an assessment artifact only.
```

The mandatory boundary remains:

```text
assessment-only
not execution
not severance authorization
not permission to proceed
not proof that isolation happened
not proof that trust roots are absolutely legitimate
not combined verdict integration
not runner behavior
not independent certification
not audit
not endorsement
not third-party validation
not security guarantee
not trust guarantee
```

Release notes, GitHub release text, PyPI description, announcements, and any
public-facing text must not exceed this boundary.

Any wording that a reasonable reader could interpret as execution, permission
to proceed, severance authorization, isolation truth, absolute root legitimacy,
combined verdict integration, runner behavior, certification, audit,
endorsement, third-party validation, or a security/trust guarantee must stop
with:

```text
PUBLIC_CLAIM_SCOPE_REVISION_REQUIRED
```

## Required Final Pre-Publication Checks

Immediately before any upload, tag, GitHub release, or announcement, the
publisher must verify:

```text
HEAD or publication source is the accepted candidate/review state
candidate version is 0.7.0
candidate wheel filename is spira_trust-0.7.0-py3-none-any.whl
candidate wheel SHA256 equals 956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5
full pytest passes
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results still have 0 Phase2 scope hits
dependencies=[]
cryptography appears only under optional extra nesira-assessment
no unconditional cryptography Requires-Dist
production workflow release notes generation includes the approved Nesira public snippet and preserves the release-evidence ritual
rollback plan hash matches accepted RC evidence
no combined verdict integration change
no runner/severance action change
no existing v0.7.0 tag already points elsewhere
no existing PyPI 0.7.0 release already exists
```

If any check fails, publication must stop.

## Publication Staging

Publication must be staged so that the least reversible action happens last.

The required order is:

```text
1. final pre-publication checks
2. GO #1 from Snir for reversible/publication-preview actions
3. TestPyPI dry-run upload/install check
4. git tag v0.7.0
5. GitHub release draft creation
6. inspect the GitHub draft and attached artifact
7. GO #2 from Snir for real PyPI upload
8. upload the exact accepted wheel artifact to PyPI
9. publish or finalize the GitHub release
10. record publication evidence
```

PyPI upload is the least reversible step. It requires a second explicit human
go/no-go after the TestPyPI dry-run and GitHub draft inspection.

Existing repository automation must not collapse GO #1 into GO #2. If any
workflow publishes to real PyPI or publishes a GitHub release on tag push, tag
push is not a reversible GO #1 action in that repository state.

In that case, staging must stop with:

```text
TAG_PUSH_WOULD_TRIGGER_REAL_PUBLICATION_REQUIRES_WORKFLOW_REVISION
```

If TestPyPI cannot be used, the publisher must record why and stop with:

```text
TESTPYPI_DRY_RUN_NOT_EVALUATED_REQUIRES_HUMAN_DECISION
```

## Authorized Publication Actions

If and only if all final pre-publication checks pass and GO #1 is given, this
gate authorizes:

```text
upload the exact accepted wheel artifact to TestPyPI
install/check the TestPyPI artifact in an isolated environment
prepare git tag v0.7.0 locally or as a draft plan
create a GitHub release draft v0.7.0 using the accepted release notes
attach the exact accepted wheel artifact to the GitHub draft
```

Only after GO #2 is given, this gate authorizes:

```text
push tag v0.7.0 if that push triggers real publication automation
upload the exact accepted wheel artifact to real PyPI
publish or finalize the GitHub release
record publication evidence after the upload/release
```

The publication order must be recorded. If the operator chooses to publish only
GitHub or only PyPI, the non-performed publication surface must be recorded as
`NOT_PERFORMED`.

## Still Forbidden

This publication gate does not authorize:

```text
changing source code
changing version after acceptance
changing wheel content
changing release notes beyond the accepted boundary
combined verdict integration
runner implementation
severance action
claiming independent certification
claiming audit
claiming endorsement
claiming third-party validation
claiming security or trust guarantee
```

## Required Publication Record

After any publication action, a record must be written:

```text
research/nesira_policy_profile/nesira_phase2_publication_record.md
research/nesira_policy_profile/nesira_phase2_publication_record.json
```

The record must include:

```text
tag name and tag target SHA
GitHub release URL or NOT_PERFORMED
PyPI project/version URL or NOT_PERFORMED
uploaded wheel filename
uploaded wheel SHA256
release notes SHA256
claim text SHA256
timestamp
operator
final pre-publication check results
rollback plan reference
blocked surfaces still blocked
```

If publication is not performed after this authorization, the record may state:

```text
PUBLICATION_NOT_PERFORMED
```

## Required Verdicts

The publication record must return one of:

```text
NESIRA_PHASE2_PUBLICATION_COMPLETED
NESIRA_PHASE2_PUBLICATION_PARTIAL
NESIRA_PHASE2_PUBLICATION_NOT_PERFORMED
NESIRA_PHASE2_PUBLICATION_BLOCKED
NESIRA_PHASE2_PUBLICATION_REJECTED
```

## Human Go/No-Go

This authorization requires explicit human go/no-go before any actual external
publication command is executed.

It requires two separate human decisions:

```text
GO_1_PREVIEW_PUBLICATION_STAGING:
  permits TestPyPI dry-run, local tag preparation, and GitHub release draft
  creation only if repository automation cannot publish real PyPI from that
  action

GO_2_REAL_PYPI_UPLOAD:
  permits tag push that triggers real publication, real PyPI upload, and final
  GitHub release publication
```

GO #2 must not be inferred from GO #1.

The go/no-go owner is:

```text
Snir
```
