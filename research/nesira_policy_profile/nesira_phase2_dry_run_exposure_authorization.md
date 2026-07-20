# Nesira Phase 2 Dry-Run Exposure Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_DRY_RUN_EXPOSURE_GATE
SCOPE: INTERNAL_READ_ONLY_DRY_RUN_EXPOSURE_ONLY

AUTHORIZES:
internal read-only dry-run exposure planning
private source-tree command or harness design
conformance tests for exposure boundary
implementation report and review

PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
PYPROJECT_ENTRY_POINT_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
RUNNER_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION_BY_DRY_RUN: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
```

This gate may expose the cold-verified non-executing dry-run evaluator only as
an internal read-only surface for local review and testing.

It does not authorize shipping the dry-run evaluator in the public wheel,
adding a public CLI flag, changing product defaults, publishing a new release,
or performing any action.

## Baseline

The accepted cold-verified evaluator is:

```text
commit: e14c4e3142f694203f31cc8ca156d0c132213403
verdict: NESIRA_PHASE2_NON_EXECUTING_DRY_RUN_RUNNER_COLD_VERIFICATION_ACCEPTED
targeted pytest: 17 passed
full pytest: 378 passed
V1 SHA256SUMS: 622 OK / 0 FAILED
source side-effect scan: 0 hits
public wheel dry-run module present: false
```

The exposure must preserve all of those properties unless a separate release
gate explicitly changes the public surface.

## Allowed Exposure Shape

Allowed:

```text
private source-tree harness under tools/ or tests/
read-only JSON-in / JSON-out local tool for internal review
no console entry point
no pyproject script entry
no public wheel allowlist entry
no package metadata mention
```

The exposed tool may:

```text
read explicitly supplied JSON files
call evaluate_dry_run(...)
print or write a dry-run artifact
return exit code for tool success/failure only
```

The exposed tool may not:

```text
execute the requested action
emit command/runbook/copy-paste steps
mutate target artifacts
open network connections
spawn subprocesses for dry-run behavior
observe live runtime isolation
claim action approval
claim severance authorization
```

## Exit-Code Discipline

If this gate introduces an internal command or harness, its exit code must mean
only:

```text
0: tool parsed inputs and emitted dry-run artifact
non-zero: tool/input error
```

Exit code must not encode:

```text
preconditions satisfied
permission to act
safe to run
authorization to execute
```

This repeats the 0.7.0/0.7.1 discipline: tool success is not permission.

## Output Boundary

Every exposed dry-run artifact must preserve:

```text
ACTION_NOT_PERFORMED
DRY_RUN_ONLY_NOT_EXECUTION
SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED
NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION
ACTION_AUTHORITY_NOT_EXECUTION
```

The output must still not contain:

```text
command
command_line
script
shell
powershell
bash
python -m
subprocess_args
cwd
environment_variables
write_paths
network_targets
copy_paste_steps
runbook
execute
apply
remediate
sever
```

Any output readable as operational instructions must stop with:

```text
EXPOSURE_SCOPE_REVISION_REQUIRED
```

## Public Surface Boundary

The dry-run evaluator must remain absent from the public wheel in this gate.

Required checks:

```text
spira_core/nesira_phase2_dry_run_runner.py not in public wheel
no dry-run metadata mention
no pyproject entry point
no public CLI flag
dependencies=[] unchanged
cryptography posture unchanged
```

If exposure requires changing `tools/build_spira_trust_public.py`,
`pyproject.toml`, release notes, workflows, version, or public claim text, stop
with:

```text
SCOPE_REVISION_REQUIRED
```

## Authorized Files

Implementation may touch only:

```text
tools/run_nesira_phase2_dry_run_review.py
tests/test_nesira_phase2_dry_run_exposure.py
research/nesira_policy_profile/nesira_phase2_dry_run_exposure_report.md
research/nesira_policy_profile/nesira_phase2_dry_run_exposure_results.json
research/nesira_policy_profile/nesira_phase2_dry_run_exposure_review.md
research/nesira_policy_profile/nesira_phase2_dry_run_exposure_review_results.json
```

This authorization document and review may also be added.

No source module, public wheel builder, pyproject, workflow, manifest, version,
release, or public claim change is authorized by this gate.

## Required Tests

Tests must prove:

```text
1. internal tool emits a dry-run artifact for valid inputs.
2. exit code 0 means tool success only, including blocked/not-evaluated dry-runs.
3. malformed input returns clean JSON error and non-zero exit, no traceback.
4. output includes all mandatory non-execution markers.
5. output contains no executable/runbook/copy-paste keys.
6. strongest dry-run path still carries ACTION_NOT_PERFORMED.
7. public wheel still excludes the dry-run evaluator and exposure tool.
8. pyproject entry points are unchanged.
9. source side-effect scan for evaluator remains 0.
10. V1 SHA256SUMS remains 622/622.
```

## Required Verification

Before acceptance:

```text
targeted exposure pytest passes
full pytest passes
V1 SHA256SUMS self-check remains 622/622
public wheel non-exposure check passes
source side-effect scan remains 0
no public CLI or pyproject entry point change
```

## Stop Conditions

Stop immediately if:

```text
dry-run exposure enters public wheel
exit code can be read as permission to act
output includes command/runbook/copy-paste fields
tool executes or mutates anything except writing its own report
tool opens network connections
public claim/release/version changes are needed
```

## Next Step

If this exposure gate is accepted, a later human-gated decision may consider a
public dry-run exposure RC. Actual runner execution remains separately blocked.
