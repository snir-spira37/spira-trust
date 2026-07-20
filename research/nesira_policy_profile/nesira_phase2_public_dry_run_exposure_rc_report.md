# Nesira Phase 2 Public Dry-Run Exposure RC Report

## Verdict

```text
NESIRA_PHASE2_PUBLIC_DRY_RUN_EXPOSURE_RC_LOCAL_VERIFICATION_ACCEPTED
```

Cold verification is also accepted:

```text
NESIRA_PHASE2_PUBLIC_DRY_RUN_EXPOSURE_RC_COLD_VERIFICATION_ACCEPTED
```

## Candidate

```text
version: 0.7.2
wheel: spira_trust-0.7.2-py3-none-any.whl
wheel_sha256: 3048960dd0a218121c41a749e19ac622bbc2a253cccb253aca078caaacdd2cea
surface: public library module only
```

## Changes

Authorized source preparation added the pure non-executing dry-run evaluator to
the public wheel:

```text
spira_core/nesira_phase2_dry_run_runner.py
```

It did not add:

```text
public CLI
pyproject console entry point
tools/run_nesira_phase2_dry_run_review.py
tests/
research/
harnesses
publication/tag/upload
```

The package version was bumped to `0.7.2`. Base dependencies remain empty, and
`cryptography==49.0.0` remains optional under `nesira-assessment` only.

## Boundary

The exposed dry-run evaluator remains assessment-only. Even the strongest result
is:

```text
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION
```

Every artifact carries `ACTION_NOT_PERFORMED` and
`SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED`. No executable command, runbook,
copy-paste instruction, network target, write path, or subprocess argument is
emitted.

## Verification

Targeted RC tests passed:

```text
tests/test_nesira_phase2_non_executing_dry_run_runner.py
tests/test_nesira_phase2_dry_run_exposure.py
tests/test_nesira_phase2_public_dry_run_exposure_rc.py
tests/test_formal_core_v1_external_reproduction_package.py

34 passed
```

The installed-wheel test imports `spira_core.nesira_phase2_dry_run_runner` from
the built wheel and evaluates the strongest dry-run path from the installed
artifact, not from the source tree.

## V1 Boundary

The V1 external reproduction package was refreshed narrowly:

```text
pyproject.toml record updated
artifact_manifest.json hash updated in SHA256SUMS
```

No Phase 2, Nesira, dry-run, runner, or public-exposure material was added to V1
claims, inventory, expected-results, or FORMAL_CLAIMS.

## Final Verification

RC verification passed:

```text
targeted RC pytest: PASS (34 passed)
full pytest: PASS (390 passed)
V1 SHA256SUMS: PASS (622/622)
V1 Phase2/dry-run scope additions: PASS (0)
release notes word-for-word review: PASS
wheel rebuild determinism: PASS
cold reproduction: PASS (390 passed, V1 622/622, wheel SHA match)
```

This is a local RC acceptance record only. TestPyPI upload, PyPI upload, GitHub
release creation, and git tag creation remain blocked until a separate
publication authorization and explicit human GO.
