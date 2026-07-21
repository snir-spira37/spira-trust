# Nesira Phase 2 Audit Append Non-Writing Evaluators Public Exposure RC Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_NON_WRITING_EVALUATORS_PUBLIC_EXPOSURE_RC_GATE
SCOPE: OPTION_C_PUBLIC_LIBRARY_EXPOSURE_OF_NON_WRITING_EVALUATORS_ONLY

SELECTED_OPTION:
Option C: public library exposure of non-writing evaluators only

AUTHORIZES:
release-candidate source preparation for public library exposure
version bump to 0.7.4
public wheel allowlist update for two non-writing evaluator modules
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
RUNNER_PUBLIC_EXPOSURE: NOT_AUTHORIZED
PROVIDER_PUBLIC_EXPOSURE: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION_BY_EXPOSED_MODULES: NOT_AUTHORIZED
SECOND_SIDE_EFFECT_CLASS: NOT_AUTHORIZED
GENERIC_RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
PUBLIC_CLAIM_USE: NOT_AUTHORIZED
```

This gate authorizes preparation of a release candidate only. It does not
authorize publication, tagging, uploading, GitHub release creation, public CLI
exposure, or exposure of side-effect-capable runner/provider code.

## Selected Surface

The selected public runtime surface is limited to:

```text
spira_core/nesira_phase2_execution_authorization_evaluator.py
spira_core/nesira_phase2_audit_append_evaluator.py
```

These modules are non-writing evaluators. They check consistency of supplied
artifacts and return in-memory artifacts. They must not perform filesystem,
network, subprocess, or runtime action effects.

The following remain excluded from the public wheel:

```text
spira_core/nesira_phase2_audit_append_runner.py
spira_core/nesira_phase2_audit_append_provider.py
tools/
tests/
research/
*_harness.py
```

No action-authority evaluator module is exposed by this gate because no such
separate source module exists in the current codebase.

## Candidate Version

The candidate version is:

```text
0.7.4
```

The version bump must be limited to:

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
tests/test_nesira_phase2_execution_authorization_evaluator.py
tests/test_nesira_phase2_audit_append_evaluator.py
tests/test_nesira_phase2_public_dry_run_exposure_rc.py
tests/test_nesira_phase2_audit_append_non_writing_evaluators_public_exposure_rc.py
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_public_exposure_release_notes.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_public_exposure_rc_report.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_public_exposure_rc_results.json
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_public_exposure_rc_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_non_writing_evaluators_public_exposure_rc_review_results.json
```

The following narrow V1 refresh is authorized only because `pyproject.toml`
changes:

```text
research/formal_core/external_reproduction_package/artifact_manifest.json
research/formal_core/external_reproduction_package/SHA256SUMS
```

The V1 refresh must update only the `pyproject.toml` record in
`artifact_manifest.json`, plus the corresponding `pyproject.toml` and
`artifact_manifest.json` checksum lines in `SHA256SUMS`. It must not add Phase
2, Nesira, audit-append, runner, provider, public-exposure, or release files to
V1 inventory, claims, expected-results, or FORMAL_CLAIMS.

The existing evaluator tests may be updated only to replace the previous public
wheel absence invariant with the new public-library-module-only invariant for
the two selected evaluator modules. They must continue to assert runner and
provider absence.

The existing public dry-run exposure RC test may be updated only for the
candidate version constant and to tolerate the new non-writing evaluator module
allowlist. It must not add CLI or runner/provider exposure.

Any other file change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Public Wheel Boundary

The candidate wheel must include:

```text
spira_core/nesira_phase2_execution_authorization_evaluator.py
spira_core/nesira_phase2_audit_append_evaluator.py
```

The candidate wheel must not include:

```text
spira_core/nesira_phase2_audit_append_runner.py
spira_core/nesira_phase2_audit_append_provider.py
tests/
research/
tools/
*_harness.py
```

The wheel metadata must not claim execution, append behavior, runner behavior,
permission, safety, severance authorization, automatic remediation,
certification, audit, endorsement, or security/trust guarantee.

## Claim Boundary

Release-candidate notes may state only:

```text
SPIRA exposes non-writing evaluators that check consistency of supplied
execution-authorization and AUDIT_RECORD_APPEND_ONLY precondition artifacts.
```

They must also state:

```text
the public surface does not write
runner and provider remain absent from the public wheel
APPEND_APPLIED is not emitted by the exposed modules
APPEND_APPLIED remains a provider status report, not proof
EA-TCB-03 remains assumed, not proven
provider behavior remains outside the Lean-proven core
```

Forbidden release-note wording:

```text
safe to write
safe to run
execution approved
permission granted by Nesira
append performed
append proof
durability proven
idempotency proven
provider included
provider proven by Lean
generic runner
arbitrary path support
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
1. built wheel is version 0.7.4.
2. built wheel contains the two selected evaluator modules.
3. built wheel does not contain runner/provider modules.
4. installed wheel can import both selected evaluator modules.
5. installed wheel can evaluate a sufficient execution authorization artifact.
6. installed wheel can evaluate a sufficient audit append evaluator artifact.
7. both installed-wheel outputs are in-memory artifacts and contain no executable fields.
8. audit append evaluator positive path carries ACTION_NOT_PERFORMED.
9. execution authorization evaluator carries EA-TCB-03.
10. no public console entry point was added.
11. dependencies=[] and optional crypto posture remain intentional.
12. V1 SHA256SUMS remains 622/622 after narrow pyproject refresh.
13. public wheel inspection confirms no runner/provider/second side-effect class exposure.
```

## Required Verification

Before RC acceptance:

```text
targeted RC pytest passes
full pytest passes
V1 SHA256SUMS self-check is 622/622
V1 claims/inventory/expected-results have 0 Phase2/Nesira/audit-append scope additions
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
runner or provider enters the public wheel
the exposed modules import filesystem/network/subprocess primitives
public output includes path, command, runbook, network target, or copy-paste fields
release notes imply append behavior or execution permission
V1 refresh touches anything other than the pyproject.toml record and the
corresponding SHA256SUMS lines
README.md is changed
```

## Next Step

If accepted, implement the release-candidate changes and run the required
verification. Publication remains a separate future gate.
