# Nesira Phase 2 Non-Executing Dry-Run Runner Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_DRY_RUN_RUNNER_IMPLEMENTATION_GATE
SCOPE: PURE_NON_EXECUTING_DRY_RUN_EVALUATOR_ONLY

AUTHORIZES:
pure in-memory dry-run evaluator implementation
conformance tests
static side-effect scans
implementation report and review

CLI_FLAG_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
RUNNER_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_READ_OF_TARGETS: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
COMBINED_VERDICT_BEHAVIOR_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```

This gate authorizes only a pure evaluator that turns already supplied
assessment, combined-verdict, action-authority, and expected-context inputs into
a non-executing dry-run artifact.

It does not authorize a runner, a public command, file or network effects, or
any action.

## Frozen Inputs

The implementation must translate the accepted design documents exactly:

```text
nesira_phase2_runner_action_boundary_authorization.md
nesira_phase2_action_authority_model.md
nesira_phase2_non_executing_dry_run_runner_plan.md
```

No design latitude is granted for execution semantics.

## Implementation Shape

The implementation must be library-only and pure:

```text
evaluate_dry_run(
  expected_context,
  combined_verdict,
  nesira_assessment,
  action_authority_result,
) -> dry_run_artifact
```

The function may inspect only its arguments. It must not open files, inspect
live process state, execute commands, access the network, mutate inputs, or
write output.

The returned artifact must be JSON-serializable data, not an instruction.

## Mandatory Markers

Every output path must carry:

```text
ACTION_NOT_PERFORMED
DRY_RUN_ONLY_NOT_EXECUTION
SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED
NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION
ACTION_AUTHORITY_NOT_EXECUTION
```

This includes:

```text
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION
DRY_RUN_BLOCKED
DRY_RUN_NOT_EVALUATED
malformed input paths
```

If any output lacks `ACTION_NOT_PERFORMED`, the implementation fails.

## Verdict Mapping

The implementation must be fail-closed:

```text
combined verdict has BLOCK
  -> DRY_RUN_BLOCKED

Nesira assessment required but missing
  -> DRY_RUN_NOT_EVALUATED

Nesira malformed/action-looking/caveat-missing
  -> DRY_RUN_BLOCKED

Nesira TRUST_INSUFFICIENT
  -> DRY_RUN_BLOCKED

Nesira TRUST_NOT_EVALUATED
  -> DRY_RUN_NOT_EVALUATED

Nesira TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS without action authority
  -> DRY_RUN_BLOCKED

combined GRAPH_OK without action authority
  -> DRY_RUN_BLOCKED

action authority ACTION_NOT_AUTHORIZED
  -> DRY_RUN_BLOCKED

action authority ACTION_NOT_EVALUATED
  -> DRY_RUN_NOT_EVALUATED

action authority sufficient but context mismatch
  -> DRY_RUN_BLOCKED

action authority sufficient but rollback/abort ref missing
  -> DRY_RUN_BLOCKED

all declared preconditions satisfied
  -> DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION
```

The strongest verdict remains non-executing.

## Forbidden Output Surface

The implementation must not serialize any of these keys anywhere in the output:

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

It must not serialize any value that can reasonably be read as a command to
perform the action.

If this cannot be enforced mechanically, stop with:

```text
EXECUTION_SCOPE_REVISION_REQUIRED
```

## Side-Effect Budget

The implementation must have:

```text
side_effect_budget = 0
```

The source module must not import or call:

```text
subprocess
os.system
socket
requests
urllib
http.client
pathlib.Path.write_text
pathlib.Path.write_bytes
open(..., "w")
open(..., "a")
shutil
```

The tests must include static source scans for these forbidden operations.

## Context And Non-Circularity

The expected action, subject, environment, and authority root must come from
`expected_context`.

The implementation must reject:

```text
assessment-derived action
combined-verdict-derived action
action-authority artifact defining the expected context for itself
artifact-to-be-acted-on defining its own subject
```

Context mismatch must produce `DRY_RUN_BLOCKED`.

## Exit-Code Discipline

This gate does not authorize a CLI. If tests add a private test harness, its
exit code must reflect tool/harness success only, not permission to act.

No public console entry point may be added.

## Authorized Files

Implementation may touch only:

```text
source/spira_core/nesira_phase2_dry_run_runner.py
tests/test_nesira_phase2_non_executing_dry_run_runner.py
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_implementation_report.md
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_implementation_results.json
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_implementation_review.md
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_implementation_review_results.json
```

This authorization document and its review may also be added.

Any change to `pyproject.toml`, workflows, release notes, version, public claim,
combined verdict behavior, manifests, or existing public CLI code must stop
with:

```text
SCOPE_REVISION_REQUIRED
```

## Required Tests

Conformance tests must prove:

```text
1. Nesira SUFFICIENT + no action authority -> DRY_RUN_BLOCKED.
2. combined GRAPH_OK + no action authority -> DRY_RUN_BLOCKED.
3. action authority sufficient + combined BLOCK -> DRY_RUN_BLOCKED.
4. action authority sufficient + context mismatch -> DRY_RUN_BLOCKED.
5. action authority sufficient + rollback missing -> DRY_RUN_BLOCKED.
6. action authority not evaluated -> DRY_RUN_NOT_EVALUATED.
7. all preconditions satisfied -> DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION.
8. all preconditions satisfied still carries ACTION_NOT_PERFORMED.
9. every output path carries all mandatory markers.
10. output contains no forbidden executable key.
11. static source scan finds no side-effect imports/calls.
12. public CLI behavior and pyproject entry points are unchanged.
13. malformed/action-looking inputs fail closed.
14. caller context is not learned from consumed artifacts.
```

The crux pair is:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS + no action_authority -> DRY_RUN_BLOCKED
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS + sufficient action_authority -> ACTION_NOT_PERFORMED
```

## Required Verification

Before acceptance:

```text
targeted pytest for dry-run runner passes
full pytest passes
static side-effect scan passes
forbidden output-key scan passes on all fixtures
V1 SHA256SUMS remains 622/622
dependencies=[] remains unchanged
no console entry point added
no release/version/public-claim change
```

If any V1-pinned file is touched, stop unless a narrow manifest refresh is
explicitly authorized.

## Stop Conditions

Stop immediately if:

```text
any code path can execute a command
any output can be copied as a command/runbook
any sufficient path omits ACTION_NOT_PERFORMED
Nesira sufficient becomes action authorization
combined GRAPH_OK becomes action authorization
action authority becomes execution authorization
side-effect scan fails
public CLI or wheel behavior changes without release authorization
```

## Next Step

If this authorization is accepted, implementation may proceed under the file
and behavior limits above.

Actual execution remains a separate future gate and is not authorized.
