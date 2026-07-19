# Nesira Phase 2 Release Candidate Authorization Review

## Verdict

```text
NESIRA_PHASE2_RELEASE_CANDIDATE_AUTHORIZATION_ACCEPTED
```

## Review Scope

This review evaluates whether
`nesira_phase2_release_candidate_authorization.md` opens only a release
candidate preparation gate.

This review does not publish a release, upload to PyPI, create a GitHub
release, create a tag, authorize combined verdict integration, authorize
runner execution, or authorize severance action.

## Scope

The authorization opens only:

```text
RELEASE_CANDIDATE_VERSION_BUMP
RELEASE_CANDIDATE_WHEEL_BUILD
RELEASE_CANDIDATE_EVIDENCE_ASSEMBLY
RELEASE_NOTES_DRAFTING
ROLLBACK_PLAN_DRAFTING
NARROW_V1_MANIFEST_REFRESH_FOR_AUTHORIZED_PINNED_FILES
```

It keeps publication and execution surfaces closed:

```text
PUBLICATION
PYPI_UPLOAD
GITHUB_RELEASE
GIT_TAG
COMBINED_VERDICT
RUNNER
SEVERANCE_ACTION
```

Review finding: PASS.

## Version-Bump Boundary

The authorization correctly recognizes the recurring V1 pinning hazard:
`pyproject.toml` is pinned by the Formal Core V1 external reproduction package.

It authorizes the version bump but limits the pyproject change to:

```text
project.version
```

It preserves:

```text
dependencies=[]
cryptography only under the nesira-assessment optional extra
no console entry point
no runtime behavior change
```

Review finding: PASS.

## Narrow V1 Manifest Refresh

The authorization permits only the refresh needed to keep the V1 package
self-consistent after the authorized version bump:

```text
artifact_manifest.json: pyproject.toml entry only
SHA256SUMS: pyproject.toml + artifact_manifest.json only
```

It explicitly forbids broad regeneration or scope expansion of the V1 package.
The following remain V1-scoped and unchanged:

```text
proof_and_axiom_inventory
expected_results
FORMAL_CLAIMS_AND_BOUNDARIES
claims documents
```

Any Phase 2 or release content appearing in V1 claims/inventory/expected
results is rejected as `V1_SCOPE_CONTAMINATION_REJECTED`.

Review finding: PASS.

## Release Notes Boundary

The authorization correctly treats release notes as public-facing claim text,
not as casual changelog prose.

It applies the same claim ceiling as the accepted claim draft:

```text
opt-in read-only assessment
declared trust evidence checked against declared trust roots
verified fail-closed composition core
conditional on recorded NOT_PROVEN assumptions
assessment artifact only
```

It blocks language implying:

```text
execution
permission to proceed
severance authorization
isolation truth
absolute root legitimacy
combined verdict integration
certification
audit
endorsement
third-party validation
security or trust guarantee
```

Review finding: PASS.

## RC Is Not Publication

The authorization cleanly separates release-candidate preparation from
publication. It blocks:

```text
twine upload
PyPI Trusted Publishing
GitHub release creation
git tag creation
release asset upload
package index publication
announcement
```

Any such action must stop with `PUBLICATION_AUTHORIZATION_REQUIRED`.

Review finding: PASS.

## Rollback Plan

The authorization requires a rollback plan before any later publication
authorization can be considered. The plan must cover PyPI yanking, GitHub
release removal or supersession, correction notice, prior-version guidance, and
the human go/no-go owner.

The rollback plan is non-executing and does not assume that a release already
exists.

Review finding: PASS.

## Required Gate Checks

The implementation review must verify:

```text
exact version recorded
pyproject limited to project.version
release notes claim language accepted
candidate wheel SHA recorded
V1 manifest refresh narrow
V1 SHA256SUMS 622/622
0 Phase2 scope hits in V1 claims/inventory/expected-results
no tag
no upload
no GitHub release
no combined verdict
no runner
no severance action
```

Review finding: PASS.

## Final Status

```text
NESIRA_PHASE2_RELEASE_CANDIDATE_AUTHORIZATION_ACCEPTED

NEXT_ALLOWED_STEP:
RELEASE_CANDIDATE_PREPARATION

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

The next step may prepare a local release candidate only. Actual publication
remains a separate later human decision.
