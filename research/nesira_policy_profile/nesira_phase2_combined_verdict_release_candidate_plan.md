# Nesira Phase 2 Combined Verdict Release Candidate Plan

## Status

```text
DOCUMENT_TYPE: RELEASE_CANDIDATE_PLAN
CANDIDATE_VERSION: 0.7.1

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

This plan prepares a local `spira-trust` 0.7.1 release candidate for the
accepted Nesira Phase 2 combined verdict integration.

It does not publish, tag, upload, announce, or authorize action.

## Candidate Scope

The candidate includes:

```text
accepted 0.7.0 public read-only assessment surface
accepted conservative combined verdict integration
Nesira as an explicit opt-in policy layer
no default Nesira requirement
Nesira sufficient contributes only OK and cannot upgrade another layer
Nesira insufficient contributes BLOCK
Nesira malformed/action-looking/marker/caveat failures fail closed
```

The candidate does not include:

```text
runner
severance action
automatic remediation
new action vocabulary
permission to proceed
claim that isolation happened
claim that trust roots are absolutely legitimate
claim of independent certification/audit/endorsement/guarantee
```

## Version Boundary

```text
pyproject.toml: project.version -> 0.7.1
tools/build_spira_trust_public.py: VERSION -> 0.7.1
dependencies=[] remains unchanged
cryptography remains optional extra only
no console entry point is added
```

The public wheel filename must be derived from the built artifact, not from a
hard-coded prior version.

## V1 Boundary

The Formal Core V1 external reproduction package remains V1-scoped.

The authorized refresh is narrow:

```text
artifact_manifest.json: pyproject.toml hash only
SHA256SUMS: pyproject.toml + artifact_manifest.json only
```

The refresh must not add Phase 2, Nesira, Domain4, runner, combined verdict, or
public-claim text to V1 claims, inventory, or expected results.

Historical snapshots pinned to earlier baselines are not regenerated.

## Acceptance Checks

```text
version is 0.7.1 in pyproject and public wheel builder
PyPI 0.7.1 availability checked before later publication planning
candidate wheel builds locally
candidate wheel SHA256 is recorded
installed base wheel reports spira-trust 0.7.1
base install remains crypto-free
cryptography remains optional extra only
full pytest passes
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results have 0 Phase2/Nesira expansion
release self-evidence agent_summary remains <= 3KB
cold reproduction from a fresh clone passes
```

## Publication Boundary

Acceptance of this release candidate may open only a later publication
authorization discussion.

It is not release approval.
