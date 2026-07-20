# Nesira Phase 2 Non-Executing Dry-Run Runner Plan

## Status

```text
DOCUMENT_TYPE: RESEARCH -- NON-EXECUTING DRY-RUN RUNNER PLAN
PHASE: PHASE_2_DRY_RUN_RUNNER_GATE
SCOPE: DESIGN_ONLY

AUTHORIZES:
non-executing dry-run artifact design
dry-run precondition matrix
future implementation conformance expectations

DRY_RUN_IMPLEMENTATION: NOT_AUTHORIZED
RUNNER_IMPLEMENTATION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
FILESYSTEM_MUTATION: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
CLI_FLAG_CHANGE: NOT_AUTHORIZED
COMBINED_VERDICT_BEHAVIOR_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```

This plan defines the shape of a future dry-run runner artifact. It does not
authorize implementation, execution, public exposure, or any behavior change in
the published product.

## Core Invariant

```text
DRY_RUN_IS_NOT_EXECUTION
```

A dry-run artifact may report whether all declared preconditions would be
available for a later human-gated execution discussion. It must never perform
the action, authorize the action, or provide a copy-paste execution recipe.

Every dry-run artifact must carry:

```text
ACTION_NOT_PERFORMED
DRY_RUN_ONLY_NOT_EXECUTION
SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED
NESIRA_SUFFICIENT_NOT_ACTION_AUTHORIZATION
ACTION_AUTHORITY_NOT_EXECUTION
```

These markers are mandatory even when every precondition is satisfied.

## Inputs

A future dry-run implementation may consume only already bounded artifacts:

```text
expected_context:
  caller-supplied action/subject/environment context

combined_verdict:
  conservative product verdict, including optional Nesira layer

nesira_assessment:
  Phase 2 assessment artifact, if required by policy

action_authority_result:
  result of the independent action-authority model
```

The expected action, subject, environment, and authority root must come from the
caller-supplied context. They must not be learned from the assessment,
attestation, combined verdict, or artifact to be acted on.

## Dry-Run Verdict Vocabulary

The dry-run vocabulary is separate:

```text
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION
DRY_RUN_BLOCKED
DRY_RUN_NOT_EVALUATED
```

No dry-run verdict means:

```text
execute
run
sever
remediate
permission granted
safe to act
```

`DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION` means only:

```text
the declared non-executing preconditions are present for a later, separate,
human-gated execution authorization discussion.
```

## Precondition Matrix

The future dry-run rule is fail-closed:

```text
combined verdict has BLOCK
  -> DRY_RUN_BLOCKED

combined verdict has WARN/NOTE/NOT_EVALUATED and policy requires clean state
  -> DRY_RUN_BLOCKED or DRY_RUN_NOT_EVALUATED

Nesira assessment is required but missing
  -> DRY_RUN_NOT_EVALUATED

Nesira assessment is malformed/action-looking/caveat-missing
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

Even the final row still emits `ACTION_NOT_PERFORMED`.

## Output Contract

A future dry-run artifact may include:

```text
schema_id
schema_version
dry_run_id
dry_run_verdict
action_not_performed
execution_authorization_required
expected_context_digest
precondition_summary
blocking_reasons
not_evaluated_reasons
assumptions_carried
rollback_or_abort_ref_present
evidence_refs
```

The artifact must not include:

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
```

If a future design needs to include operational instructions, it is no longer
dry-run and must stop with:

```text
EXECUTION_SCOPE_REVISION_REQUIRED
```

## Plan Summary Language

Allowed summary language:

```text
preconditions satisfied for later human review
action not performed
dry-run only
separate execution authorization required
blocked by combined verdict
blocked by action authority
not evaluated because evidence was unavailable
```

Forbidden summary language:

```text
ready to run
safe to run
run approved
execution approved
permission granted
severance authorized
remediation authorized
isolation proven
copy this command
```

## Side-Effect Budget

A future dry-run implementation must have:

```text
side_effect_budget = 0
```

It must not:

```text
spawn subprocesses
open network connections
write outside its declared output file
mutate target artifacts
inspect live process state
observe or claim runtime isolation
perform cleanup/remediation
```

Reading declared input artifacts and writing the dry-run report are the only
future implementation-adjacent operations this plan can contemplate.

## Conformance Required For Later Implementation

Any later implementation gate must include tests for:

```text
1. Nesira SUFFICIENT + no action authority -> DRY_RUN_BLOCKED.
2. combined GRAPH_OK + no action authority -> DRY_RUN_BLOCKED.
3. action authority sufficient + combined BLOCK -> DRY_RUN_BLOCKED.
4. action authority sufficient + context mismatch -> DRY_RUN_BLOCKED.
5. action authority sufficient + rollback missing -> DRY_RUN_BLOCKED.
6. action authority not evaluated -> DRY_RUN_NOT_EVALUATED.
7. all preconditions satisfied -> DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION.
8. all preconditions satisfied still carries ACTION_NOT_PERFORMED.
9. output contains no executable command or copy-paste runbook.
10. subprocess/filesystem/network side-effect probes remain zero.
11. public CLI behavior is unchanged unless separately authorized.
12. malformed/action-looking inputs fail closed.
```

The most important pair is:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS + no action_authority -> DRY_RUN_BLOCKED
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS + sufficient action_authority -> ACTION_NOT_PERFORMED
```

This pair proves that assessment is not authorization and authorization is not
execution.

## Future Implementation Guardrails

A later implementation plan must prove before code:

```text
no public CLI flag is added
no public wheel behavior changes without a release gate
no executable command fields are serializable
no target write path can be supplied
no network target can be supplied
all outputs are JSON data, not instructions
exit code reflects tool success only, not permission to act
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_plan.md
research/nesira_policy_profile/nesira_phase2_non_executing_dry_run_runner_plan_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, or public
claim change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this plan is accepted, the next gate may be:

```text
nesira_phase2_non_executing_dry_run_runner_authorization
```

That future gate may authorize implementation of the dry-run artifact only. It
still must not authorize actual execution, subprocesses, filesystem mutation,
network access, severance, remediation, release, or public claim expansion.
