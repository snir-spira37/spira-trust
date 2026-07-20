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
wheel_sha256: 0ca716776b54bd8850b1fed0e8ce5d502d17c9ee567c22a5643b2de3aa60b8d7
```

The wheel filename was derived from the built artifact, not copied from the
previous release name.

This refresh supersedes the historical `956f15e...` candidate, which superseded
`29a52445...`.

The `29a52445... -> 956f15e...` refresh fixed a public-wheel runtime packaging
omission exposed by the TestPyPI staging dry-run. It added the transitive
public CLI runtime module `spira_core/unification_proof.py` to the wheel
allowlist and added an installed wheel `graph` runtime test.

The `956f15e... -> 0ca716...` refresh fixes the release self-check
`agent_summary.json <= 3KB` contract without relaxing the 3KB guard. It removes
duplicated approval prose already carried by `not_claimed` and omits empty
`blockers`, `warnings`, and `notes` arrays while preserving those fields when
they contain evidence.

This plan does not authorize publication.

## Required Source Changes

```text
pyproject.toml:
  project.version: 0.6.1 -> 0.7.0

tools/build_spira_trust_public.py:
  VERSION: 0.6.1 -> 0.7.0
  public wheel allowlist includes spira_core/unification_proof.py

source/spira_core/agent_summary.py:
  release self-check summary remains below 3KB without changing the protected
  schema
```

No dependency, optional-extra, entry-point, runtime behavior, combined verdict,
runner, or severance-action change is part of this candidate.

## V1 Manifest Refresh

The Formal Core V1 external reproduction package pins `pyproject.toml`.

The release candidate requires only a narrow refresh:

```text
artifact_manifest.json:
  pyproject.toml entry
  source/spira_core/agent_summary.py entry

SHA256SUMS:
  pyproject.toml
  source/spira_core/agent_summary.py
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
