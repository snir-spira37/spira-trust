# Nesira Phase 2 Release and Public Claim Readiness Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PRODUCT_EXPOSURE_GATE
SCOPE: RELEASE_AND_PUBLIC_CLAIM_READINESS_PACKAGE

AUTHORIZES:
RELEASE_READINESS_PACKAGE_PREPARATION
PUBLIC_CLAIM_TEXT_DRAFTING
RELEASE_CANDIDATE_EVIDENCE_ASSEMBLY

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

This document opens only the readiness gate for a possible future public
release and public claim of the accepted Nesira Phase 2 read-only assessment
surface.

It does not authorize publishing anything. It authorizes preparing the evidence
and exact claim language that a human may later approve or reject.

## Authoritative Starting Point

```text
public_wheel_read_only_exposure_commit:
181ee58e06eb56794237ee9fc25e96421d18cb03

public_wheel_read_only_cold_record_commit:
0f255c33f425110dc46e907f3a629b7b7be986c7

accepted_verdict:
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED
```

The accepted boundary remains:

```text
Nesira Phase 2 is exposed in the public wheel only as an opt-in read-only
assessment surface. It emits assessment artifacts conditional on declared trust
roots and recorded NOT_PROVEN assumptions.

It is not execution, not severance authorization, not combined verdict
integration, not runner behavior, and not release approval.
```

## What This Gate May Produce

This gate may produce only readiness artifacts:

```text
research/nesira_policy_profile/nesira_phase2_release_and_public_claim_readiness_plan.md
research/nesira_policy_profile/nesira_phase2_release_and_public_claim_readiness_claim_text.md
research/nesira_policy_profile/nesira_phase2_release_and_public_claim_readiness_evidence_manifest.json
research/nesira_policy_profile/nesira_phase2_release_and_public_claim_readiness_review.md
research/nesira_policy_profile/nesira_phase2_release_and_public_claim_readiness_review_results.json
```

It may inspect and reference the already accepted wheel build/cold reproduction
records. It may not upload, tag, publish, bump a version, alter product runtime
behavior, or change release metadata outside the readiness artifacts above.

## Publication Boundary

The following remain blocked:

```text
twine upload
PyPI Trusted Publishing
GitHub release creation
git tag for release
version bump
release asset upload
README/docs public claim changes outside the readiness draft
```

Any actual publication requires a later explicit human authorization with the
final candidate SHA, wheel SHA, release notes, claim text, and rollback plan.

## Claim Allowlist

The draft public claim may state only:

```text
SPIRA includes an opt-in Nesira Phase 2 read-only assessment surface in the
public wheel.

The surface validates declared trust evidence against declared trust roots and
composes the result through a verified fail-closed assessment core.

The result is conditional on declared trust roots and recorded NOT_PROVEN
assumptions.

The surface emits an assessment artifact only.
```

The draft must carry the exact boundary:

```text
not execution
not severance authorization
not permission to proceed
not proof that isolation happened
not proof that trust roots are absolutely legitimate
not combined verdict integration
not runner behavior
```

## Forbidden Claim Language

The draft public claim must not state or imply:

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
production release approved
```

Any claim wording that a reasonable reader could interpret as execution,
permission, severance, or absolute trust must stop with:

```text
CLAIM_SCOPE_REVISION_REQUIRED
```

## Evidence Requirements

The readiness package must cite:

```text
Phase 1 validator acceptance and cold reproduction
Phase 2 external reproduction acceptance
read-only internal exposure cold verification
public wheel read-only exposure cold verification
V1 manifest boundary: 622/622 and 0 Phase2 scope hits
wheel content boundary: runtime entries only, no harnesses
crypto posture: dependencies=[], cryptography optional extra only
Lean composition core: accepted, sorry-free, assumption-carrying theorems
adapter cold verifications: signature, identity, authority, isolation attestation
assessment wiring cold verification
```

The readiness package must also cite the still-blocked surfaces:

```text
RUNNER
COMBINED_VERDICT
SEVERANCE_ACTION
```

## Release Candidate Evidence

If this gate prepares a release candidate evidence manifest, it must be
read-only and local:

```text
commit SHA
public wheel SHA256
wheel runtime entries
wheel metadata dependency posture
test summary
cold reproduction summary
claim text hash
blocked-surface list
rollback/non-publication note
```

It must not create a release, upload assets, or tag the repository.

## Required Review Checks

The review must verify:

```text
claim text matches the allowlist
forbidden claim language absent
assessment-only boundary appears in the headline and body
trust-root conditionality appears in the headline or first paragraph
NOT_PROVEN assumptions are explicitly carried
no release publication action occurred
no version bump occurred
no tag was created
no PyPI/GitHub release upload occurred
combined verdict remains untouched
runner/severance code remains untouched
```

## Required Verdicts

The review must return one of:

```text
NESIRA_PHASE2_RELEASE_AND_PUBLIC_CLAIM_READINESS_ACCEPTED
NESIRA_PHASE2_RELEASE_AND_PUBLIC_CLAIM_READINESS_NEEDS_REVISION
NESIRA_PHASE2_RELEASE_AND_PUBLIC_CLAIM_READINESS_REJECTED
```

Only an accepted readiness verdict may open discussion of an actual release
authorization.

## Still Blocked After Acceptance

Even if this readiness gate is accepted, the following remain blocked:

```text
PUBLICATION
PYPI_UPLOAD
GITHUB_RELEASE
VERSION_BUMP
COMBINED_VERDICT
RUNNER
SEVERANCE_ACTION
```
