# Nesira Phase 2 Release Candidate Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PRODUCT_EXPOSURE_GATE
SCOPE: RELEASE_CANDIDATE_PREPARATION

AUTHORIZES:
RELEASE_CANDIDATE_VERSION_BUMP
RELEASE_CANDIDATE_WHEEL_BUILD
RELEASE_CANDIDATE_EVIDENCE_ASSEMBLY
RELEASE_NOTES_DRAFTING
ROLLBACK_PLAN_DRAFTING
NARROW_V1_MANIFEST_REFRESH_FOR_AUTHORIZED_PINNED_FILES

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

This document opens only the preparation of a release candidate for the
accepted Nesira Phase 2 read-only assessment surface.

It does not authorize publishing a release. It authorizes creating a local,
reviewable candidate with an exact version, wheel hash, release notes draft,
rollback plan, and evidence manifest that a human may later approve or reject.

## Authoritative Starting Point

```text
release_readiness_authorization_commit:
5f2e96b3664d03a6d7d9bf4701a68facf6a15044

release_readiness_package_commit:
77ed65f917e8c1a4ffd374dcaac7086401ddfde1

release_readiness_claim_polish_commit:
73890877ad5c418d096edf7e4c1adeb664fe00d7

accepted_readiness_boundary:
PUBLICATION_NOT_AUTHORIZED
```

The accepted product boundary remains:

```text
Nesira Phase 2 is exposed only as an opt-in read-only assessment surface.
It validates declared trust evidence against declared trust roots and composes
the result through a verified fail-closed composition core, conditional on the
declared trust roots and recorded NOT_PROVEN assumptions.

It emits an assessment artifact only.

It is not execution, not severance authorization, not permission to proceed,
not proof that isolation happened, not proof that trust roots are absolutely
legitimate, not combined verdict integration, and not release approval.
```

## What This Gate May Produce

This gate may produce only release-candidate preparation artifacts:

```text
research/nesira_policy_profile/nesira_phase2_release_candidate_plan.md
research/nesira_policy_profile/nesira_phase2_release_candidate_release_notes.md
research/nesira_policy_profile/nesira_phase2_release_candidate_rollback_plan.md
research/nesira_policy_profile/nesira_phase2_release_candidate_evidence_manifest.json
research/nesira_policy_profile/nesira_phase2_release_candidate_review.md
research/nesira_policy_profile/nesira_phase2_release_candidate_review_results.json
```

It may also build a local candidate wheel for hashing and inspection. The wheel
artifact is release-candidate evidence only. It must not be uploaded, attached
to a release, or advertised as published.

## Allowed Source Changes

The implementation gate opened by this authorization may change only:

```text
pyproject.toml
tools/build_spira_trust_public.py
research/formal_core/external_reproduction_package/artifact_manifest.json
research/formal_core/external_reproduction_package/SHA256SUMS
the release-candidate readiness artifacts listed above
```

The `pyproject.toml` change is limited to:

```text
project.version
```

The `tools/build_spira_trust_public.py` change is limited to:

```text
VERSION
```

The builder `VERSION` must match `pyproject.toml` `project.version` exactly.
The candidate wheel filename must be derived from the built wheel, not assumed
from the previous release filename.

The following must remain unchanged:

```text
project.dependencies = []
project.optional-dependencies.nesira-assessment = ["cryptography==49.0.0"]
console scripts / entry points
runtime behavior
combined verdict wiring
runner behavior
```

## Narrow V1 Manifest Refresh Rule

`pyproject.toml` is pinned by the Formal Core V1 external reproduction package.
Therefore, an authorized version bump will make the V1 package hashes stale
unless the pinned entry is refreshed in the same gate.

This authorization permits only a narrow refresh:

```text
artifact_manifest.json:
  update only the pyproject.toml entry hash/size/metadata affected by the
  authorized version bump

SHA256SUMS:
  update only pyproject.toml and artifact_manifest.json entries required by
  that narrow refresh
```

It does not authorize regenerating or expanding the V1 package scope.

The following must remain unchanged and V1-scoped:

```text
proof_and_axiom_inventory
expected_results
FORMAL_CLAIMS_AND_BOUNDARIES
claims documents
V1 package file list except the pinned pyproject.toml metadata refresh
```

Any Phase 2, Nesira adapter, runner, combined verdict, public claim, or release
content appearing in the V1 claims/inventory/expected-results surfaces must
stop with:

```text
V1_SCOPE_CONTAMINATION_REJECTED
```

## Release Notes Claim Boundary

Release notes are public-facing claim text. They must obey the same ceiling as
the accepted claim draft.

They may state only:

```text
opt-in Nesira Phase 2 read-only assessment surface
declared trust evidence checked against declared trust roots
verified fail-closed composition core
conditional on declared trust roots and recorded NOT_PROVEN assumptions
assessment artifact only
```

They must carry the boundary:

```text
not execution
not severance authorization
not permission to proceed
not proof that isolation happened
not proof that trust roots are absolutely legitimate
not combined verdict integration
not runner behavior
not certification
not endorsement
not security or trust guarantee
```

Forbidden release-note language includes:

```text
severance authorized
safe to proceed
agent may proceed
isolation proven
isolation occurred
attestation proves execution truth
trust roots are globally legitimate
SPIRA performs severance
SPIRA runs isolation
SPIRA product verdict now incorporates Nesira Phase 2
independently certified
audited
externally endorsed
externally approved
third-party validated
security guarantee
trust guarantee
```

Any release-note wording that a reasonable reader could interpret as execution,
permission, severance, absolute trust, certification, endorsement, audit,
third-party validation, or guarantee must stop with:

```text
RELEASE_NOTES_SCOPE_REVISION_REQUIRED
```

## Release Candidate Evidence Requirements

The release-candidate evidence manifest must record:

```text
candidate commit SHA
candidate version
candidate wheel filename
candidate wheel SHA256
claim text SHA256
release notes SHA256
rollback plan SHA256
runtime wheel entries
wheel metadata dependency posture
cryptography optional extra posture
full pytest summary
public wheel runtime execution summary
V1 SHA256SUMS self-check result
V1 scope scan result
blocked-surface list
publication status: NOT_AUTHORIZED
```

The release candidate must preserve:

```text
dependencies=[]
cryptography only under the nesira-assessment optional extra
no unconditional Requires-Dist for cryptography
assessment-only CLI semantics
exit code reflects tool success, not permission to act
raw verdict tokens, no friendly approval labels
```

## Rollback Plan Requirements

The rollback plan must be explicit enough for the later publication gate. It
must describe at least:

```text
how to yank a PyPI release if one is later published
how to remove or supersede a GitHub release if one is later created
how to publish a correction notice if claim text is found to overstate scope
how to point users back to the prior accepted version
who makes the human go/no-go decision
```

The rollback plan is preparation only. It must not perform any rollback action
or assume that a release exists.

## Publication Boundary

The following remain blocked throughout this gate:

```text
twine upload
PyPI Trusted Publishing
GitHub release creation
git tag creation
release asset upload
public README/docs claim changes outside release-candidate drafts
package index publication
announcement
```

Any command or workflow that publishes, tags, uploads, announces, or otherwise
makes the release candidate externally available must stop with:

```text
PUBLICATION_AUTHORIZATION_REQUIRED
```

## Required Review Checks

The review must verify:

```text
version bump is exact and recorded
pyproject change is limited to project.version
public wheel builder change is limited to VERSION
builder VERSION equals pyproject project.version
candidate wheel filename is derived dynamically from the built artifact
dependencies remain []
cryptography remains optional-extra only, exact version 49.0.0
no console entry point was added
release notes obey the claim allowlist and forbidden-language rules
reproduction is not described as certification, audit, endorsement, approval,
  third-party validation, or guarantee
candidate wheel hash is recorded
candidate wheel content boundary matches the accepted read-only public wheel
assessment-only CLI behavior remains unchanged
V1 manifest refresh is narrow: pyproject.toml only in artifact_manifest
SHA256SUMS refresh is narrow: pyproject.toml + artifact_manifest.json only
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results have 0 Phase2 scope hits
no tag was created
no PyPI upload occurred
no GitHub release was created
combined verdict remains untouched
runner/severance code remains untouched
rollback plan exists and is non-executing
```

## Required Verdicts

The review must return one of:

```text
NESIRA_PHASE2_RELEASE_CANDIDATE_ACCEPTED
NESIRA_PHASE2_RELEASE_CANDIDATE_NEEDS_REVISION
NESIRA_PHASE2_RELEASE_CANDIDATE_REJECTED
```

Only an accepted release-candidate verdict may open discussion of a later
publication authorization.

## Still Blocked After Acceptance

Even if this release-candidate gate is accepted, the following remain blocked:

```text
PUBLICATION
PYPI_UPLOAD
GITHUB_RELEASE
GIT_TAG
COMBINED_VERDICT
RUNNER
SEVERANCE_ACTION
```
