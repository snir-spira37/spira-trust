# Nesira Phase 2 Combined Verdict Release Candidate Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_RELEASE_CANDIDATE_GATE
SCOPE: RELEASE_CANDIDATE_FOR_COMBINED_VERDICT_INTEGRATION

AUTHORIZES:
version bump to 0.7.1
local public wheel build
release candidate notes
release candidate evidence manifest
cold reproduction

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
CLAIM_EXPANSION_BEYOND_ACCEPTED_BOUNDARY: NOT_AUTHORIZED
```

This gate authorizes preparation of a local `spira-trust` 0.7.1 release
candidate that carries the accepted Nesira Phase 2 combined verdict
integration.

It does not authorize publication. A later publication gate must be opened
separately if this release candidate is accepted.

## Candidate Scope

The release candidate may include:

```text
accepted 0.7.0 public read-only assessment surface
accepted combined verdict integration from commit 167cce2
Nesira as explicit opt-in combined verdict layer
no default Nesira requirement
no Nesira upgrade of existing BLOCK/WARN/NOTE results
fail-closed Nesira malformed/action-looking/marker/caveat failures
```

The release candidate must not include:

```text
runner
severance action
automatic remediation
new action vocabulary
claim that isolation happened
claim that trust roots are absolutely legitimate
claim that Nesira sufficient authorizes proceeding
```

## Authorized Files

The release candidate may touch only:

```text
pyproject.toml
tools/build_spira_trust_public.py
research/formal_core/external_reproduction_package/artifact_manifest.json
research/formal_core/external_reproduction_package/SHA256SUMS
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_plan.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_release_notes.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_rollback_plan.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_evidence_manifest.json
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_review.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_review_results.json
```

The V1 manifest refresh must be narrow:

```text
pyproject.toml
tools/build_spira_trust_public.py
research/formal_core/external_reproduction_package/artifact_manifest.json
```

It must not add Phase 2/Nesira claims to V1 claims, inventory, expected results,
or the historical protected-surface snapshot.

## Required Checks

Before acceptance:

```text
version is 0.7.1 in pyproject and public wheel builder
PyPI 0.7.1 does not already exist before RC publication planning
public wheel filename is derived dynamically
wheel SHA256 is recorded
dependencies=[] remains unchanged
cryptography remains optional extra only
combined verdict integration tests pass
full pytest passes
V1 SHA256SUMS self-check remains 622/622
V1 claims/inventory/expected-results have 0 Phase2/Nesira expansion
agent_summary release self-check remains <= 3KB
cold reproduction from a fresh clone passes
```

## Claim Boundary

Release candidate notes may say only:

```text
0.7.1 prepares the accepted Nesira Phase 2 combined verdict integration.
Nesira is an explicit opt-in conservative combined verdict layer.
Nesira can block or report-not-evaluated; sufficient cannot upgrade another
layer or authorize action.
```

Release candidate notes must retain:

```text
assessment-only
not execution
not severance authorization
not permission to proceed
not proof that isolation happened
not proof that trust roots are absolutely legitimate
not runner behavior
not independent certification/audit/endorsement/guarantee
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if:

```text
the release candidate changes runner/severance behavior
the release candidate changes public claim beyond the accepted boundary
Nesira sufficient can upgrade an existing conservative verdict
V1 manifest refresh expands V1 claims/inventory/expected-results
public wheel adds unconditional cryptography dependency
publication/tag/upload is attempted
```

## Next Step

If the release candidate is accepted, the next gate may prepare publication
authorization for `spira-trust` 0.7.1.

Publication remains blocked until that separate gate and explicit human GO.
