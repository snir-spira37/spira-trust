# Nesira Phase 2 Release Candidate Plan

## Status

```text
DOCUMENT_TYPE: RELEASE_CANDIDATE_PLAN
STATUS: DRAFT_FOR_REVIEW
CANDIDATE_VERSION: 0.7.0

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

## Scope

Prepare a local release candidate for the accepted Nesira Phase 2 read-only
assessment surface.

The candidate may update only the package version and the public wheel builder
version constant, then build and inspect a local wheel.

This plan does not authorize publication, upload, tag creation, GitHub release
creation, combined verdict integration, runner behavior, or severance action.

## Candidate

```text
version: 0.7.0
wheel: spira_trust-0.7.0-py3-none-any.whl
wheel_sha256: 29a52445a5045c76264fcce60df5288836cbe870193411c9b84d16ad9e454c6b
```

The wheel filename was derived from the built artifact, not copied from the
previous release name.

## Required Source Changes

```text
pyproject.toml:
  project.version: 0.6.1 -> 0.7.0

tools/build_spira_trust_public.py:
  VERSION: 0.6.1 -> 0.7.0
```

No dependency, optional-extra, entry-point, runtime behavior, combined verdict,
runner, or severance-action change is part of this candidate.

## V1 Manifest Refresh

The Formal Core V1 external reproduction package pins `pyproject.toml`.

The release candidate requires only a narrow refresh:

```text
artifact_manifest.json:
  pyproject.toml entry only

SHA256SUMS:
  pyproject.toml
  research/formal_core/external_reproduction_package/artifact_manifest.json
```

No Phase 2 source, adapter, release note, claim, runner, or combined-verdict
content may enter V1 claims, inventory, expected results, or scope statements.

## Review Gates

Before any later publication authorization, the candidate must pass:

```text
release notes claim-boundary review
rollback plan review
candidate wheel content inspection
wheel metadata dependency posture inspection
V1 SHA256SUMS self-check
V1 scope scan
full pytest
git diff --check
no tag / no upload / no GitHub release check
```

Acceptance of this release candidate may open only discussion of a later
publication authorization. It is not itself publication approval.
