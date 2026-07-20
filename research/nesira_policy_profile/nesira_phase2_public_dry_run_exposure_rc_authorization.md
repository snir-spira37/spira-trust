# Nesira Phase 2 Public Dry-Run Exposure Release Candidate Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PUBLIC_DRY_RUN_EXPOSURE_RC_GATE
SCOPE: OPTION_B_PUBLIC_LIBRARY_MODULE_ONLY_RELEASE_CANDIDATE

AUTHORIZES:
release-candidate source preparation for public library-module exposure
version bump to 0.7.2
public wheel allowlist update for the dry-run evaluator module
post-install wheel tests
release-candidate notes draft
narrow V1 manifest refresh for pyproject.toml only if required
release-candidate report and review

PUBLIC_CLI_CHANGE: NOT_AUTHORIZED
PYPROJECT_ENTRY_POINT_CHANGE: NOT_AUTHORIZED
TESTPYPI_UPLOAD: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG_CREATION: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLICATION: NOT_AUTHORIZED
RUNNER_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION_BY_DRY_RUN: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
```

This gate authorizes preparation of a release candidate only. It does not
authorize publishing, tagging, uploading, creating a GitHub release, or exposing
actual execution.

## Selected Option

The selected exposure option is:

```text
Option B: public library module only
```

This means:

```text
include spira_core/nesira_phase2_dry_run_runner.py in the public wheel
do not add a public CLI
do not add a pyproject console entry point
do not expose tools/run_nesira_phase2_dry_run_review.py in the wheel
do not change runtime defaults
```

Public CLI exposure remains a separate higher-risk gate.

## Candidate Version

The candidate version is:

```text
0.7.2
```

This version is required because the public wheel content changes. The version
bump must be limited to:

```text
pyproject.toml project.version
tools/build_spira_trust_public.py VERSION
```

No dependency posture change is authorized:

```text
dependencies=[]
cryptography remains optional under nesira-assessment only
```

## Authorized Source Changes

Implementation may touch only:

```text
pyproject.toml
tools/build_spira_trust_public.py
tests/test_nesira_phase2_non_executing_dry_run_runner.py
tests/test_nesira_phase2_dry_run_exposure.py
tests/test_nesira_phase2_public_dry_run_exposure_rc.py
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_release_notes.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_rc_report.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_rc_results.json
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_rc_review.md
research/nesira_policy_profile/nesira_phase2_public_dry_run_exposure_rc_review_results.json
```

The following narrow V1 refresh is authorized only if `pyproject.toml` changes:

```text
research/formal_core/external_reproduction_package/artifact_manifest.json
research/formal_core/external_reproduction_package/SHA256SUMS
```

The V1 refresh must update only the `pyproject.toml` record. It must not add
Phase 2, Nesira, dry-run, runner, or public-exposure files to V1 inventory,
claims, expected-results, or FORMAL_CLAIMS.

The two existing dry-run tests may be updated only to replace the previous
public-wheel absence invariant with the new public-library-module-only
invariant:

```text
spira_core/nesira_phase2_dry_run_runner.py is present as an importable library module
tools/run_nesira_phase2_dry_run_review.py remains absent
no dry-run console entry point is added
no executable output fields are introduced
```

Any other file change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Public Wheel Boundary

The candidate wheel must include:

```text
spira_core/nesira_phase2_dry_run_runner.py
```

The candidate wheel must not include:

```text
tools/run_nesira_phase2_dry_run_review.py
tests/
research/
*_harness.py
runner execution modules
subprocess/filesystem/network execution helpers
```

The wheel metadata must not claim runner behavior, execution, permission, safety,
severance authorization, automatic remediation, certification, audit,
endorsement, or security/trust guarantee.

## Release Notes Boundary

Release notes are public text and must stay inside the accepted claim draft:

```text
dry-run is not execution
dry-run is not action authorization
ACTION_NOT_PERFORMED is always carried
separate execution authorization remains required
actual execution remains out of scope
reproduction is not certification
```

Forbidden release-note wording:

```text
ready to run
safe to run
permission granted
action authorized
runner
executes
severance authorized
automatic remediation
security guarantee
certified
audited
endorsed
third-party validated
```

## Required RC Tests

The release-candidate tests must prove:

```text
1. built wheel is version 0.7.2.
2. built wheel contains spira_core/nesira_phase2_dry_run_runner.py.
3. built wheel does not contain tools/run_nesira_phase2_dry_run_review.py.
4. installed wheel can import spira_core.nesira_phase2_dry_run_runner.
5. installed wheel strongest dry-run path emits ACTION_NOT_PERFORMED.
6. installed wheel emits no executable/runbook/copy-paste fields.
7. no public console entry point was added.
8. dependencies=[] and crypto optional-extra posture remain intentional.
9. actual execution modules remain absent.
10. public release notes stay inside claim boundary.
11. V1 SHA256SUMS remains 622/622 after narrow pyproject refresh.
```

## Required Verification

Before RC acceptance:

```text
targeted RC pytest passes
full pytest passes
V1 SHA256SUMS self-check is 622/622
V1 claims/inventory/expected-results have 0 Phase2/Nesira/dry-run scope additions
wheel rebuild is deterministic
wheel install test passes from the built artifact
no public CLI or pyproject entry point change
release notes reviewed word-for-word
```

TestPyPI upload is not part of this RC gate. It belongs to a later publication
authorization with explicit GO.

## Stop Conditions

Stop immediately if:

```text
public CLI exposure is needed
pyproject scripts change
dry-run output omits ACTION_NOT_PERFORMED
wheel includes internal tool/tests/research/harnesses
release notes can be read as runner/action permission
V1 refresh expands beyond pyproject.toml
version bump changes dependencies or crypto posture
```

## Next Step

If this RC is accepted, a separate publication authorization may be opened for
0.7.2. That later gate must require TestPyPI staging and a separate human GO
for real publication.
