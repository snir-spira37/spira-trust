# Nesira Phase 2 Runner / Action Boundary Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_RUNNER_ACTION_BOUNDARY_GATE
SCOPE: RUNNER_ACTION_BOUNDARY_DESIGN_ONLY

AUTHORIZES:
runner/action boundary analysis
action-authority model planning
non-executing dry-run runner plan
review of required hard stops and conformance cases

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

This gate opens only the boundary design for any future runner or action layer.
It does not authorize code that executes, mutates, observes a live runtime, or
changes the public product behavior shipped in `spira-trust` 0.7.1.

## Current Baseline

`spira-trust` 0.7.1 publicly ships the accepted Nesira Phase 2 combined verdict
integration:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS -> OK only
TRUST_INSUFFICIENT                   -> BLOCK
TRUST_NOT_EVALUATED                  -> not sufficient
malformed/action-looking/caveat-missing artifacts -> fail closed
```

The published integration is opt-in and conservative. Nesira can block or
preserve the existing result, but it cannot authorize execution and cannot
upgrade any other layer.

## Core Boundary

The central invariant for all future runner/action work is:

```text
NESIRA_SUFFICIENT_IS_NOT_ACTION_AUTHORIZATION
```

Combined verdict output may be a precondition for later action consideration.
It is never permission to run, sever, remediate, mutate, or proceed.

Any design that treats:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
GRAPH_OK
recommended_agent_action = PROCEED
```

as sufficient authorization for execution must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Required Separation

Any future active layer must be separated into at least four concepts:

```text
assessment:
  evaluates declared trust evidence against declared roots

combined_verdict:
  aggregates policy layers conservatively and may block

action_authority:
  independently states who or what is allowed to authorize an action

runner:
  if ever authorized, executes only after separate action authorization and
  explicit human or policy go/no-go
```

Assessment and combined verdict may provide evidence to an action authority.
They cannot replace it.

## Action Authority Is A Required Future Gate

Before any runner implementation can be discussed, a separate document must
define an action-authority model.

That model must answer:

```text
who may authorize an action
what action is authorized
what subject/context the action binds
what time window applies
what revocation/freshness checks apply
what evidence is recorded
what rollback/abort channel exists
```

The action-authority model must not be inferred from Nesira trust roots. Signing
keys, identity roots, authority policy roots, and attestation authorities are
trust-assessment roots, not automatic runtime-action roots.

## Non-Executing Dry-Run Plan

The only runner-adjacent artifact this gate may plan is a non-executing dry-run
plan.

Allowed dry-run output may describe:

```text
requested action id
bound subject/context
required action authority
combined verdict precondition result
missing authorization or evidence
would-run plan summary
```

Dry-run output must also carry:

```text
DRY_RUN_ONLY_NOT_EXECUTION
ACTION_NOT_PERFORMED
NESIRA_SUFFICIENT_NOT_AUTHORIZATION
```

Dry-run output must not contain commands that a consumer can copy as an
execution instruction.

## Forbidden Outputs And Behavior

Forbidden fields, labels, CLI flags, or report headings include:

```text
sever
severance_authorized
permission_to_sever
safe_to_sever
execute
run
run_isolation
apply
remediate
auto_remediate
automatic_remediation
enforce
proceed_with_action
action_authorized_by_nesira
```

Any future artifact that can reasonably be read as an instruction to perform an
action must stop with:

```text
ACTION_SCOPE_REVISION_REQUIRED
```

## Future Hard Stops

Future implementation planning must stop if any proposal:

```text
uses Nesira SUFFICIENT as permission
uses combined GRAPH_OK as permission
adds a runner flag to the public CLI
executes subprocesses, network calls, or filesystem mutations
observes a live isolation runtime and calls that proof
claims isolation happened
claims severance is authorized
adds automatic remediation
changes public release behavior without a new publication gate
```

## Required Conformance For A Later Gate

If a later gate proposes a non-executing dry-run implementation, it must include
tests proving:

```text
1. Nesira SUFFICIENT without action authority -> dry-run blocked/not authorized.
2. combined GRAPH_OK without action authority -> dry-run blocked/not authorized.
3. action authority without sufficient preconditions -> blocked.
4. BLOCK in any combined layer -> blocked.
5. malformed/action-looking assessment -> blocked.
6. dry-run emits no executable command string.
7. no subprocess/filesystem/network side effect occurs.
8. public CLI and wheel behavior remain unchanged unless separately authorized.
```

## Authorized Files

This gate may create or edit only research planning documents:

```text
research/nesira_policy_profile/nesira_phase2_runner_action_boundary_authorization.md
research/nesira_policy_profile/nesira_phase2_runner_action_boundary_authorization_review.md
```

Any source code, tests, workflow, release, version, pyproject, manifest, or
public-claim change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this boundary authorization is accepted, the next gate is not runner code.
The next gate is:

```text
nesira_phase2_action_authority_model
```

Only after an action-authority model is accepted may a later gate consider a
non-executing dry-run runner plan. Actual execution remains a separate future
decision.
