# Nesira Phase 2 Execution Authorization Evaluator Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_EXECUTION_AUTHORIZATION_EVALUATOR_GATE
SCOPE: NON_EXECUTING_EVALUATOR_ONLY

AUTHORIZES:
pure in-memory execution-authorization evaluator
local conformance fixtures for the 22-case spec
local tests for non-execution and assumption carrying
implementation report and review

RUNNER_IMPLEMENTATION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
CLI_FLAG_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE_CHANGE: NOT_AUTHORIZED
COMBINED_VERDICT_BEHAVIOR_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```

This gate authorizes only a pure evaluator that checks execution-authorization
consistency. It does not authorize runner code or execution.

## Core Lock

```text
EVALUATOR_CHECKS_AUTHORIZATION_CONSISTENCY_NOT_RUNNER_TRUTH
```

The evaluator may compare declared artifacts and digests supplied to it. It
must not claim that `runner_intended_context_digest` was truly produced by a
future runner, because no runner is authorized or implemented here.

`EA-TCB-03` remains an explicit assumption carried by every result:

```text
the trusted verifier observes the same action context that a future runner
would receive
```

The evaluator checks whether the supplied trusted-verifier evidence is
consistent with that model. It does not prove the verifier, runner, UI, nonce
registry, approval system, or rollback channel.

## Authorized Output

A future evaluator may return only a data artifact with:

```text
schema_id
schema_version
verdict
action_not_performed
assumptions
conditional_on_roots
trusted_verifier_ref
human_go_ref
precondition_breakdown
blocking_reasons
not_evaluated_reasons
evidence_refs
```

The verdict vocabulary is limited to:

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
EXECUTION_NOT_AUTHORIZED
EXECUTION_AUTHORIZATION_NOT_EVALUATED
```

Every output, including the strongest result, must carry:

```text
ACTION_NOT_PERFORMED
EA-META-01
EA-META-02
```

## Forbidden Output

The evaluator must not emit:

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
execution_approved
safe_to_execute
severance_authorized
automatic_remediation
```

Any output that can reasonably be read as an instruction to execute must stop
with:

```text
EXECUTION_SCOPE_REVISION_REQUIRED
```

## Purity Requirement

The evaluator must be a pure in-memory function.

Allowed:

```text
read already-supplied dictionaries or dataclasses
compare strings, booleans, timestamps, lists, and digests already supplied
return a structured result
```

Forbidden:

```text
subprocess
os.system
os.popen
socket
requests
urllib
http client calls
filesystem reads or writes
Path.write_*
tempfile creation
environment variable reads for authorization
dynamic import for execution
```

The source must not import execution-capable libraries. If the evaluator needs
I/O, it is no longer this gate.

## Mapping Rule

The evaluator is fail-closed:

```text
checked and failed -> EXECUTION_NOT_AUTHORIZED
could not be checked -> EXECUTION_AUTHORIZATION_NOT_EVALUATED
all declared authorization evidence consistent -> EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
```

The sufficient result means only:

```text
the non-executing authorization evidence is consistent enough to open a later
runner-gate discussion, under declared roots and recorded assumptions.
```

It is not permission to execute.

## Required Conformance

The implementation must cover every case from:

```text
nesira_phase2_execution_authorization_conformance_spec.md
```

The 22 required cases must include:

```text
agent-created human go -> EXECUTION_NOT_AUTHORIZED
runner-created human go -> EXECUTION_NOT_AUTHORIZED
CI success as human go -> EXECUTION_NOT_AUTHORIZED
missing human-go root -> EXECUTION_AUTHORIZATION_NOT_EVALUATED
clock missing -> EXECUTION_AUTHORIZATION_NOT_EVALUATED
revocation unknown -> EXECUTION_AUTHORIZATION_NOT_EVALUATED
runner-intended context differs from approved context -> EXECUTION_NOT_AUTHORIZED
prepared bundle matches but runner input differs -> EXECUTION_NOT_AUTHORIZED
opaque hash without human-readable text -> EXECUTION_NOT_AUTHORIZED
nonce replay -> EXECUTION_NOT_AUTHORIZED
all authorization evidence sufficient -> ACTION_NOT_PERFORMED
```

## Assumption Carrying

Every result must carry a non-empty assumptions array.

The floor must be present in every result:

```text
EA-HUMAN-01
EA-TCB-01
EA-TCB-03
EA-CLOCK-01
EA-META-01
EA-META-02
```

The strongest result must also carry all conditional assumptions whose evidence
was used, including human text, nonce, misapplication, role, rollback, context,
signature, and revocation assumptions as applicable.

Missing `EA-TCB-03` is a hard failure.

## No Runner Truth Claim

The evaluator must not say:

```text
runner input verified as real
safe to run
ready to execute
execution approved
human approved execution
isolation proven
```

Allowed language:

```text
authorization evidence consistent
authorization evidence not authorized
authorization evidence not evaluated
action not performed
future runner gate still required
```

## Authorized Files

This gate may edit only:

```text
source/spira_core/nesira_phase2_execution_authorization_evaluator.py
tests/test_nesira_phase2_execution_authorization_evaluator.py
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_authorization.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_authorization_review.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_report.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_results.json
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_review.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_evaluator_review_results.json
```

Any CLI, public wheel metadata, workflow, pyproject, manifest, version, release,
tag, public claim, combined-verdict behavior, runner, subprocess, filesystem
mutation, or network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

If V1-pinned files are touched unexpectedly, stop before refreshing any
manifest.

## Required Verification

Before acceptance:

```text
pure-source grep: no subprocess/os/socket/requests/urllib/http/path-write/tempfile
22 conformance cases pass
ACTION_NOT_PERFORMED in every output
EA-TCB-03 in every assumption set
forbidden output fields absent
two-run equality
full pytest
V1 SHA256SUMS remains 622/622 if unchanged
wheel/public behavior unchanged
```

## Next Step

If this authorization is accepted, the next step may implement the pure
evaluator only.

Actual runner implementation and execution remain blocked.
