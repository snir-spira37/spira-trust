# Nesira Phase 2 Combined Verdict Publication Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLICATION_GATE
SCOPE: PUBLICATION_OF_ACCEPTED_COMBINED_VERDICT_RELEASE_CANDIDATE

AUTHORIZES_CONDITIONALLY:
FINAL_PRE_PUBLICATION_CHECKS
TESTPYPI_DRY_RUN_FOR_V0_7_1
GIT_TAG_CREATION_FOR_V0_7_1
GITHUB_RELEASE_DRAFT_FOR_V0_7_1
GITHUB_RELEASE_PUBLICATION_FOR_V0_7_1
PYPI_UPLOAD_FOR_V0_7_1_REQUIRES_SECOND_GO
PUBLIC_RELEASE_NOTES_USE
PUBLIC_CLAIM_USE_WITH_ACCEPTED_BOUNDARY

RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
VERSION_CHANGE: NOT_AUTHORIZED
SCOPE_EXPANSION: NOT_AUTHORIZED
```

This document opens the publication gate for the accepted `spira-trust` 0.7.1
release candidate only.

It does not authorize changing the candidate. It authorizes publication only if
the exact accepted candidate is still intact and the final pre-publication
checks pass immediately before publication.

## Accepted Candidate

```text
release_candidate_source_commit:
954c400

release_candidate_review_commit:
abfa4b5

version:
0.7.1

wheel:
spira_trust-0.7.1-py3-none-any.whl

wheel_sha256:
297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664

accepted_verdict:
NESIRA_PHASE2_COMBINED_VERDICT_RELEASE_CANDIDATE_ACCEPTED
```

The publication must use this candidate only. Any changed source, rebuilt wheel
with a different SHA256, changed release notes, changed claim text, changed
version, or changed dependency posture must stop with:

```text
PUBLICATION_CANDIDATE_CHANGED_REQUIRES_NEW_RC
```

## Publication Boundary

The public claim is:

```text
SPIRA includes the accepted Nesira Phase 2 combined verdict integration as an
explicit opt-in conservative policy layer. Existing default behavior is
unchanged. Nesira sufficient contributes only OK and cannot upgrade another
layer's BLOCK, WARN, NOTE, or NOT_EVALUATED result. Nesira insufficient
contributes BLOCK, and not-evaluated remains not sufficient. Malformed,
action-looking, marker-mismatched, or caveat-missing Nesira artifacts fail
closed.
```

The mandatory boundary remains:

```text
assessment composition only
not execution
not severance authorization
not permission to proceed
not runner behavior
not automatic remediation
not proof that isolation happened
not proof that trust roots are absolutely legitimate
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
to proceed, severance authorization, automatic remediation, isolation truth,
absolute root legitimacy, runner behavior, certification, audit, endorsement,
third-party validation, or a security/trust guarantee must stop with:

```text
PUBLIC_CLAIM_SCOPE_REVISION_REQUIRED
```

## Required Final Pre-Publication Checks

Immediately before any upload, tag, GitHub release, or announcement, the
publisher must verify:

```text
HEAD or publication source is the accepted candidate/review state
candidate version is 0.7.1
candidate wheel filename is spira_trust-0.7.1-py3-none-any.whl
candidate wheel SHA256 equals 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
full pytest passes
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results still have 0 Phase2/Nesira scope hits
dependencies=[]
cryptography appears only under optional extra nesira-assessment
no unconditional cryptography Requires-Dist
production workflow release notes generation includes the approved 0.7.1 combined verdict public snippet and preserves the release-evidence ritual
rollback plan hash matches accepted RC evidence
no runner/severance/automatic-remediation action change
existing v0.7.1 tag is absent
no existing PyPI 0.7.1 release already exists
no existing GitHub release v0.7.1 already exists
```

If any check fails, publication must stop.

## Publication Staging

Publication must be staged so that the least reversible action happens last.

Repository automation publishes to real PyPI when a `v*` tag is pushed. For
this repository state, tag push is a GO #2 action.

The required order is:

```text
1. final pre-publication checks
2. GO #1 from Snir for reversible/publication-preview actions
3. TestPyPI dry-run upload/install check
4. inspect TestPyPI metadata and installed artifact behavior
5. GO #2 from Snir for real publication
6. push git tag v0.7.1 at the accepted publication source
7. production workflow publishes PyPI and GitHub release
8. verify public PyPI/GitHub surfaces
9. record publication evidence
```

PyPI upload is the least reversible step. It requires a second explicit human
go/no-go after TestPyPI dry-run inspection.

GO #2 must not be inferred from GO #1.

## Authorized Publication Actions

If and only if all final pre-publication checks pass and GO #1 is given, this
gate authorizes:

```text
upload the exact accepted wheel artifact to TestPyPI
install/check the TestPyPI artifact in an isolated environment
inspect TestPyPI metadata
prepare a local tag command plan for v0.7.1
```

Only after GO #2 is given, this gate authorizes:

```text
create and push tag v0.7.1 at the accepted publication source
real PyPI upload through the production trusted publishing workflow
GitHub release publication through the production workflow
record publication evidence after the upload/release
```

## Still Forbidden

This publication gate does not authorize:

```text
changing source code
changing version after acceptance
changing wheel content
changing release notes beyond the accepted boundary
runner implementation
severance action
automatic remediation
claiming independent certification
claiming audit
claiming endorsement
claiming third-party validation
claiming security or trust guarantee
```

## Required Publication Record

After any publication action, a record must be written:

```text
research/nesira_policy_profile/nesira_phase2_combined_verdict_publication_record.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_publication_record.json
```

The record must include:

```text
tag name and tag target SHA
GitHub release URL or NOT_PERFORMED
PyPI project/version URL or NOT_PERFORMED
uploaded wheel filename
uploaded wheel SHA256
release notes SHA256 or workflow-generated-notes verification
timestamp
operator
final pre-publication check results
rollback plan reference
blocked surfaces still blocked
```

## Required Verdicts

The publication record must return one of:

```text
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_COMPLETED
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_PARTIAL
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_NOT_PERFORMED
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_BLOCKED
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_REJECTED
```

## Human Go/No-Go

This authorization requires explicit human go/no-go before any actual external
publication command is executed.

It requires two separate human decisions:

```text
GO_1_PREVIEW_PUBLICATION_STAGING:
  permits TestPyPI dry-run only

GO_2_REAL_PUBLICATION:
  permits tag push that triggers real PyPI upload and GitHub release publication
```

GO #2 must not be inferred from GO #1.

The go/no-go owner is:

```text
Snir
```
