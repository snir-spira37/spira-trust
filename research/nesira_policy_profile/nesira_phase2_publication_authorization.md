# Nesira Phase 2 Publication Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLICATION_GATE
SCOPE: PUBLICATION_OF_ACCEPTED_READ_ONLY_RELEASE_CANDIDATE

AUTHORIZES_CONDITIONALLY:
FINAL_PRE_PUBLICATION_CHECKS
GIT_TAG_CREATION_FOR_V0_7_0
GITHUB_RELEASE_DRAFT_OR_PUBLICATION_FOR_V0_7_0
PYPI_UPLOAD_FOR_V0_7_0
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
cbc200f9d4a644f97dc776e3680ca440823bff78

candidate_code_commit:
404246ebd97b38a1fe9160b028a855dd2ba61bc0

version:
0.7.0

wheel:
spira_trust-0.7.0-py3-none-any.whl

wheel_sha256:
29a52445a5045c76264fcce60df5288836cbe870193411c9b84d16ad9e454c6b

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
candidate wheel SHA256 equals 29a52445a5045c76264fcce60df5288836cbe870193411c9b84d16ad9e454c6b
full pytest passes
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results still have 0 Phase2 scope hits
dependencies=[]
cryptography appears only under optional extra nesira-assessment
no unconditional cryptography Requires-Dist
release notes hash matches accepted RC evidence
rollback plan hash matches accepted RC evidence
no combined verdict integration change
no runner/severance action change
no existing v0.7.0 tag already points elsewhere
no existing PyPI 0.7.0 release already exists
```

If any check fails, publication must stop.

## Authorized Publication Actions

If and only if all final pre-publication checks pass, this gate authorizes:

```text
git tag v0.7.0 at the accepted publication commit
push tag v0.7.0
create GitHub release v0.7.0 using the accepted release notes
attach the exact accepted wheel artifact
upload the exact accepted wheel artifact to PyPI
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

The go/no-go owner is:

```text
Snir
```
