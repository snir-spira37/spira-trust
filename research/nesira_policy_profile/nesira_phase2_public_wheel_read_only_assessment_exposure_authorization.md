# Nesira Phase 2 Public Wheel Read-Only Assessment Exposure Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PRODUCT_EXPOSURE_GATE
SCOPE: PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE

AUTHORIZES:
PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_IMPLEMENTATION

RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

This document authorizes the next narrow product-exposure gate after the
accepted cold reproduction of the internal read-only assessment tool. It may
expose the accepted Nesira Phase 2 assessment surface through the public wheel
only as read-only assessment functionality.

It does not authorize publishing a release, making a public capability claim,
changing product verdict behavior, or executing any operational action.

## Authoritative Starting Point

```text
read_only_exposure_commit:
9f9729d83015a1a2bc4948a0867ca4672c5aef2a

read_only_exposure_cold_record_commit:
0a0810fb3ab44e52d69e3db6b88cd5ddbdc98e78

accepted_verdict:
NESIRA_PHASE2_READ_ONLY_ASSESSMENT_EXPOSURE_COLD_VERIFICATION_ACCEPTED
```

The accepted statement remains:

```text
The tool runs the accepted Phase 2 assessment engine and emits the raw
assessment artifact. The artifact is conditional on declared trust roots and
recorded NOT_PROVEN assumptions.

It is assessment-only. It is not execution, not severance authorization, not a
combined verdict, not a public product claim, and not a release.
```

## Authorized Exposure

The implementation may expose only a read-only assessment surface in the public
wheel.

The allowed runtime modules are limited to the already accepted assessment
wiring and runtime adapters, plus a narrow public-wheel CLI/module wrapper:

```text
spira_core/nesira_phase2_assessment_wiring.py
spira_core/nesira_phase2_signature_adapter.py
spira_core/nesira_phase2_identity_adapter.py
spira_core/nesira_phase2_authority_adapter.py
spira_core/nesira_phase2_isolation_attestation_adapter.py
spira_core/nesira_phase2_read_only_assessment_cli.py
```

The following remain excluded from the public wheel:

```text
*_harness.py
tests
fixtures
research reports
external reproduction package internals
Lean files
runner or execution code
combined verdict integration code for Nesira Phase 2
```

If any harness, test fixture, research artifact, runner, or combined-verdict
integration enters the public wheel, the implementation must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Packaging Boundary

The current public wheel builder is explicit-allowlist based. This gate may
touch only the wheel packaging surfaces required to expose the narrow runtime
surface:

```text
tools/build_spira_trust_public.py
pyproject.toml
tests/test_nesira_phase2_public_wheel_read_only_assessment_exposure.py
tests/test_nesira_phase2_read_only_assessment_exposure.py
tests/test_nesira_phase2_assessment_wiring.py
tests/test_nesira_phase2_signature_adapter.py
tests/test_nesira_phase2_identity_adapter.py
tests/test_nesira_phase2_authority_adapter.py
tests/test_nesira_phase2_isolation_attestation_adapter.py
source/spira_core/nesira_phase2_read_only_assessment_cli.py
research/nesira_policy_profile/nesira_phase2_public_wheel_read_only_assessment_exposure_report.md
research/nesira_policy_profile/nesira_phase2_public_wheel_read_only_assessment_exposure_results.json
research/nesira_policy_profile/nesira_phase2_public_wheel_read_only_assessment_exposure_review.md
research/nesira_policy_profile/nesira_phase2_public_wheel_read_only_assessment_exposure_review_results.json
```

The existing tests listed above may be updated only to invert the previous
public-wheel exclusion assertions for the newly authorized runtime modules.
They must continue to assert that harnesses, fixtures, tests, reports, runner
code, combined-verdict integration, and unauthorized dependencies remain
excluded.

Because this gate may change files pinned by the Formal Core V1 external
reproduction package, the following manifest maintenance files are also
authorized, but only for narrow hash/size refreshes of files changed by this
gate:

```text
research/formal_core/external_reproduction_package/artifact_manifest.json
research/formal_core/external_reproduction_package/SHA256SUMS
```

The refresh must not add Nesira Phase 2 runtime modules to the Formal Core V1
inventory or claims. It may only keep the V1 external reproduction package
self-check coherent after authorized packaging-surface changes.

The implementation may add the accepted runtime adapter modules to the public
wheel allowlist only for this read-only surface. It may not change their
assessment semantics.

## Crypto Posture

The base product dependency list must remain empty:

```text
[project]
dependencies = []
```

The implementation may add a named optional extra for explicit opt-in
assessment use:

```text
[project.optional-dependencies]
nesira-assessment = ["cryptography==49.0.0"]
```

The hash-locked requirements file remains the canonical reproduction and cold
verification source for the crypto dependency:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

Wheel metadata may mention `cryptography==49.0.0` only under the named optional
extra. It must not become an unconditional `Requires-Dist` dependency of the
base wheel.

The public surface must fail closed with a clean tool error if the optional
crypto dependency is missing or the installed version does not match the pinned
version. It must not silently fall back to weaker crypto, stdlib-only crypto, or
hand-rolled verification.

## CLI and Exit-Code Boundary

This authorization does not require adding a public console entry point. If the
implementation proposes one, it must be the same read-only run-and-report
surface and must be reviewed explicitly.

The exposed surface may do only this:

```text
read input assessment request
invoke accepted Nesira Phase 2 assessment wiring
emit canonical JSON assessment artifact
optionally write the same artifact to a caller-specified output file
return a process exit code that reflects tool success, not permission to act
```

Exit code 0 means only that the tool successfully produced an assessment
artifact. It must be returned for successful production of all three assessment
verdicts:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

Non-zero exit codes are reserved for tool/input failure.

The following flags or modes are forbidden:

```text
--enforce
--apply
--execute
--sever
--proceed
--auto
--fix
--remediate
--run-isolation
--combined-verdict
```

The following output fields are forbidden:

```text
agent_action
recommended_agent_action
combined_verdict
permission_to_sever
safe_to_sever
execute
proceed
release
```

## Claim Boundary

The public wheel may expose code, but this gate does not authorize a public
capability claim.

Docs, metadata, CLI help, and report text may state only:

```text
read-only assessment artifact
conditional on declared trust roots and recorded NOT_PROVEN assumptions
assessment-only, not execution
```

They must not state or imply:

```text
severance authorized
safe to proceed
trust roots are absolutely legitimate
attestation truth is proven
isolation truth is proven
product verdict changed
release approved
```

Human-readable output should preserve raw verdict tokens instead of relabeling
them with approval-style wording.

## Required Implementation Gates

The implementation review must verify:

```text
public wheel includes only the authorized Nesira Phase 2 runtime modules
public wheel excludes harnesses, fixtures, reports, tests, Lean files, and runner code
base dependencies remain []
cryptography appears only under the named optional extra, exact version 49.0.0
hash-locked crypto requirements remain intact
read-only surface runs from the built wheel
all three verdicts return exit code 0 when assessment production succeeds
malformed input returns clean JSON tool error, not traceback
no forbidden flags or output fields
no combined-verdict imports or calls
no runner/execution imports or calls
two-run byte equality
full pytest remains green
V1 SHA256SUMS self-check remains 622/622
```

If `pyproject.toml` or the public wheel builder changes, the implementation
must rerun the V1 package self-check and refresh only the corresponding
manifest/SHA entries required for 622/622 coherence. A stale V1 manifest is a
blocking failure.

The review must include cold reproduction from a fresh clone before this gate
may be marked accepted.

## Required Verdicts

The implementation review must return one of:

```text
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_NEEDS_REVISION
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_REJECTED
```

Only an accepted verdict may open discussion of a later combined-verdict,
release, or public-claim gate.

## Still Blocked After Acceptance

Even if this public wheel read-only exposure is accepted, the following remain
blocked:

```text
RUNNER
COMBINED_VERDICT
PUBLIC_CLAIM
RELEASE
SEVERANCE_ACTION
```
