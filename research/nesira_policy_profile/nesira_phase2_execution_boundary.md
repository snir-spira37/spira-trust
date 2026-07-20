# Nesira Phase 2 Execution Boundary

## Status

```text
DOCUMENT_TYPE: RESEARCH -- EXECUTION BOUNDARY
PHASE: PHASE_2_EXECUTION_BOUNDARY_GATE
SCOPE: DESIGN_ONLY

AUTHORIZES:
execution boundary taxonomy
future execution authorization prerequisites
future runner hard-stop requirements
future conformance expectations

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

This document defines the boundary that must be crossed before any future code
may perform an action. It does not authorize runner code or execution.

## Current Baseline

`spira-trust` 0.7.3 publicly ships:

```text
Nesira Phase 2 assessment
conservative combined-verdict integration
public non-executing dry-run evaluator library module
```

The published dry-run surface always carries:

```text
ACTION_NOT_PERFORMED
DRY_RUN_ONLY_NOT_EXECUTION
SEPARATE_EXECUTION_AUTHORIZATION_REQUIRED
```

The 0.7.3 public package does not execute, remediate, sever, spawn
subprocesses, mutate target filesystems, open network execution paths, or
authorize action.

## Core Invariant

```text
EXECUTION_REQUIRES_SEPARATE_HUMAN_GO
```

None of the following is sufficient execution authorization:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
GRAPH_OK
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION
ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION
recommended_agent_action = PROCEED
```

They may be evidence or preconditions. They cannot become permission to act.

## Layer Separation

The active stack remains separated:

```text
assessment:
  checks declared trust evidence against declared trust roots

combined_verdict:
  aggregates policy layers conservatively and may block

action_authority:
  independently evaluates whether an action is authorized for consideration

dry_run:
  reports whether declared preconditions are present without executable output

execution:
  not authorized here; performs side effects only after a separate future gate
  and explicit human go/no-go
```

The execution layer must not learn the action, subject, environment, authority,
or target from the artifact it will act on. It must receive them from a
caller-supplied execution context that is independent of the evidence being
evaluated.

## What Counts As Execution

Any future design enters execution scope if it does any of the following:

```text
spawns a subprocess
invokes shell, PowerShell, bash, cmd, Python module execution, or task runner
opens a network connection to perform or coordinate an action
writes, deletes, moves, chmods, renames, or mutates a target file or directory
changes process, service, container, VM, or host state
observes a live runtime and claims the observation proves isolation
performs cleanup, rollback, remediation, severance, or enforcement
emits a command or runbook intended for copy-paste execution
passes executable arguments to another tool or API
```

If any of these are needed, the work is no longer dry-run and must stop with:

```text
EXECUTION_SCOPE_REVISION_REQUIRED
```

## Minimum Future Execution Authorization

Before any runner implementation can be authorized, a separate future
authorization must define at minimum:

```text
exact action class allowlist
forbidden action class denylist
caller-supplied execution context schema
independent action authority root and decision artifact
human go/no-go owner
operator confirmation protocol
target scoping and path/network boundaries
rollback or abort mechanism
kill-switch or stop channel
side-effect budget
audit log schema
secret-handling boundary
failure and partial-failure semantics
post-action verification boundary
public exposure and claim boundary
```

The allowlist must name concrete action classes. A generic shell command,
arbitrary subprocess, arbitrary path mutation, or arbitrary network target is
not an action class.

## Required Human Go

Any future execution design must include an explicit human go/no-go step after
all machine checks complete.

The human go must bind:

```text
action id
action class
subject/context
target scope
expected side effects
rollback/abort reference
evidence bundle digest
dry-run artifact digest
action-authority artifact digest
```

The go must not be inferred from:

```text
exit code 0
GRAPH_OK
dry-run satisfied
action authority sufficient
Nesira sufficient
absence of blockers
```

## Fail-Closed Rules

Execution consideration must fail closed if:

```text
action authority is missing, stale, revoked, or not evaluated
dry-run artifact is missing, stale, malformed, or action-looking
combined verdict has BLOCK, WARN, NOTE, or NOT_EVALUATED when clean state is required
Nesira assumptions are missing when Nesira evidence is required
PT-ISOLATION-01 is missing when isolation evidence is present
caller context mismatches any consumed artifact
rollback or abort channel is unavailable
clock is unavailable or untrusted
revocation freshness is unknown
target scope is ambiguous
requested action class is not explicitly allowlisted
human go is absent or binds a different digest/context
```

The failure result must not be upgraded by any successful assessment,
authority, or dry-run precondition.

## Forbidden Public Language

Future public text must not say:

```text
Nesira authorizes execution
dry-run approval
safe to run
safe to sever
execution approved
permission granted
automatic remediation approved
isolation proven
runner verified isolation
```

Allowed language before an actual execution gate is limited to:

```text
non-executing dry-run
action not performed
separate execution authorization required
preconditions satisfied for later human review
execution remains not authorized
```

## Future Conformance Requirements

Any future execution implementation authorization must require tests proving:

```text
1. dry-run satisfied + no human go -> no execution.
2. action authority sufficient + no human go -> no execution.
3. Nesira sufficient + no action authority -> no execution.
4. combined verdict non-blocking + no action authority -> no execution.
5. human go for a different digest/context -> no execution.
6. requested action class not allowlisted -> no execution.
7. rollback/abort missing -> no execution.
8. clock missing or revocation unknown -> no execution.
9. malformed/action-looking dry-run artifact -> no execution.
10. executable command supplied through input -> rejected.
11. side effects are absent in all negative cases.
12. audit record distinguishes considered, authorized-for-consideration, and performed.
```

The most important pair is:

```text
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION + no human go -> ACTION_NOT_PERFORMED
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION + human go -> still requires a future execution gate
```

This pair preserves the final separation: dry-run is not execution, and a human
go cannot be implemented until execution code is separately authorized.

## Hard Stops

Stop with `SCOPE_REVISION_REQUIRED` if a later proposal:

```text
uses any assessment or dry-run result as permission to execute
uses action-authority sufficient as permission without separate human go
allows arbitrary commands, arbitrary paths, or arbitrary network targets
adds subprocess, filesystem mutation, or network execution before authorization
emits copy-paste commands in a dry-run or review artifact
omits rollback or abort binding
omits auditability for a performed action
changes public CLI behavior without release authorization
expands public claims beyond non-executing dry-run
claims actual isolation occurred or was proven
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_execution_boundary.md
research/nesira_policy_profile/nesira_phase2_execution_boundary_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation, or
network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this boundary is accepted, the next step is still not execution code.

A future gate may draft:

```text
nesira_phase2_execution_authorization_model
```

That future model must define the concrete action classes, human go protocol,
side-effect budget, rollback/abort mechanism, and audit schema before any runner
implementation can be considered.
