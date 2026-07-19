# Nesira Phase 2 Read-Only Assessment Exposure Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PRODUCT_EXPOSURE_GATE
SCOPE: READ_ONLY_INTERNAL_ASSESSMENT_EXPOSURE

AUTHORIZES:
READ_ONLY_ASSESSMENT_REPORT_IMPLEMENTATION
READ_ONLY_INTERNAL_ASSESSMENT_CLI_IMPLEMENTATION

RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

This document authorizes the smallest product-adjacent exposure of the accepted
Nesira Phase 2 internal assessment engine: a read-only report surface and a
read-only internal assessment CLI.

The authorized surface may run the already accepted assessment wiring and print
or write the resulting assessment artifact. It may not execute operational
actions, alter system state, emit a product combined verdict, enter the public
wheel, claim public capability, or release.

## Authoritative Starting Point

```text
internal_assessment_milestone:
NESIRA_PHASE2_INTERNAL_ASSESSMENT_ENGINE_COMPLETE_INTERNAL_ONLY

external_reproduction_verdict:
SPIRA_NESIRA_PHASE2_COLD_EXTERNAL_REPRODUCTION_ACCEPTED

source_assessment_commit:
26b560822ca9ad2a518ec74334fe6cc7abb864e5

package_artifact_commit:
17b34e0fa716b5326fa7e854b5705359a7dd309b

current_package_note_commit:
b958a13821fa1dd07a62900f24246f905ae11cb5
```

The read-only exposure must preserve the accepted Phase 2 milestone statement:

```text
Phase 2 internal assessment engine is externally reproducible from a cold
environment. It validates declared trust evidence against declared roots and
composes the result through a verified fail-closed core, conditional on the
declared trust roots and the recorded NOT_PROVEN assumptions.

This remains assessment-only. It is not execution, not severance authorization,
not a public product claim, and not a release.
```

## Authorized Files

The implementation gate opened by this authorization may touch only the
following new files unless a later review explicitly expands scope:

```text
tools/run_nesira_phase2_read_only_assessment.py
tests/test_nesira_phase2_read_only_assessment_exposure.py
research/nesira_policy_profile/nesira_phase2_read_only_assessment_exposure_report.md
research/nesira_policy_profile/nesira_phase2_read_only_assessment_exposure_results.json
research/nesira_policy_profile/nesira_phase2_read_only_assessment_exposure_review.md
research/nesira_policy_profile/nesira_phase2_read_only_assessment_exposure_review_results.json
```

No console entry point may be added to `pyproject.toml`. No public-wheel builder
allowlist entry may be added. If the implementation requires touching
`pyproject.toml`, public-wheel build rules, combined-verdict surfaces, release
metadata, or runtime action code, it must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Read-Only CLI Contract

The internal CLI may do only this:

```text
read input assessment request
invoke accepted Nesira Phase 2 assessment wiring
emit canonical JSON assessment artifact
optionally write the same artifact to a caller-specified output file
return a process exit code that reflects tool success, not permission to act
```

The CLI must not expose any mode, option, flag, function, or output field that
does more than run and report. The following are forbidden:

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

No output may include fields named:

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

The required marker remains:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## Crypto Posture

The Phase 2 crypto dependency remains gated:

```text
pyproject dependencies: []
cryptography: hash-locked adapter requirement only
public wheel dependency metadata: absent
public wheel module entries for Phase 2 exposure: absent
```

The read-only exposure must not add `cryptography` or any adapter dependency to
product dependencies. It may require the existing hash-locked adapter
requirements for local/internal execution:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

If the read-only exposure cannot run without changing product dependency
posture, it must stop.

## Combined Verdict Boundary

Combined verdict is not part of this authorization.

This gate is exposure-only. It does not allow the assessment result to influence
the existing product verdict, agent action, public API, release gate, or any
operational decision.

Any proposed mapping from assessment verdict to product verdict, agent action,
or operational permission requires a separate authorization at a higher risk
bar.

## Runner and Execution Boundary

The read-only exposure must not implement or call:

```text
isolation runner
container runner
sandbox runner
process execution
filesystem mutation
network mutation
deployment
remediation
severance action
```

The CLI may read input files and write the requested report file. That is the
only authorized filesystem write.

## Claim Boundary

The exposed report may state only that it is an internal assessment artifact
over declared inputs and declared roots, conditional on recorded assumptions.

It must not state or imply:

```text
trust roots are absolutely legitimate
attestation truth is proven
isolation truth is proven
severance is authorized
the system may proceed
the product verdict changed
the capability is publicly available
release is approved
```

## Required Implementation Gates

The implementation must provide deterministic, testable behavior:

```text
canonical JSON output
two-run semantic equality
input parse failure -> clean tool error, not Python traceback
adapter exception -> fail-closed assessment result or clean tool error
no forbidden output fields
no forbidden CLI flags
no combined-verdict imports or calls
no runner/execution imports or calls
public wheel exclusion preserved
pyproject dependencies remain empty
full pytest remains green
V1 external reproduction manifest remains coherent
```

The read-only exposure review must include a cold reproduction from a fresh
clone before any further product exposure is considered.

## Required Verdicts

The implementation review must return one of:

```text
NESIRA_PHASE2_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED
NESIRA_PHASE2_READ_ONLY_ASSESSMENT_EXPOSURE_NEEDS_REVISION
NESIRA_PHASE2_READ_ONLY_ASSESSMENT_EXPOSURE_REJECTED
```

Only an accepted verdict may open discussion of later exposure gates.

## Still Blocked After Acceptance

Even if this read-only exposure is accepted, the following remain blocked:

```text
RUNNER
COMBINED_VERDICT
PUBLIC_WHEEL_EXPOSURE
PUBLIC_CLAIM
RELEASE
SEVERANCE_ACTION
```

