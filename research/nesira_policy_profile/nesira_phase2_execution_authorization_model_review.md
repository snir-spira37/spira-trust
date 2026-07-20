# Nesira Phase 2 Execution Authorization Model Review

## Verdict

```text
NESIRA_PHASE2_EXECUTION_AUTHORIZATION_MODEL_ACCEPTED
```

## Scope Reviewed

This review covers the design-only execution authorization model. It does not
authorize runner code, subprocess execution, filesystem mutation, network
execution, severance, remediation, CLI changes, version changes, release, or
public claim expansion.

## Findings

No blocking findings.

## Human-Go Authenticity

The model closes the main gap from the execution boundary:

```text
HUMAN_GO_MUST_BE_AUTHENTICATED_AND_NON_SELF_AUTHORIZED
```

The human go is not accepted as a self-reported field. It must be independently
authenticated, supplied outside the agent/runner path, and bound to the exact
action and evidence bundle.

The model explicitly rejects:

```text
agent-created approval
runner-created approval
dry-run-created approval
combined-verdict-created approval
CI success
exit code 0
absence of blockers
```

This prevents the evaluating machine from minting the approval it is supposed
to require.

## Role Separation

The approver/operator split is explicit:

```text
APPROVER_AND_OPERATOR_ARE_SEPARATE_ROLES
```

Silent role collapse is forbidden. If policy wants the same person to act as
both approver and operator, that coalescing must be explicit and recorded.

This is the correct default for an execution-adjacent model because it prevents
"the process that runs the action approved itself" from hiding behind a generic
human-go field.

## Binding Review

The human-go artifact must bind:

```text
action id and class
subject and environment context
target scope
expected side effects
rollback or abort reference
evidence bundle
combined verdict
action authority
dry-run artifact
operator identity or role
```

Digest mismatch, stale evidence, omitted fields, or context learned from the
target artifact all fail closed. This protects against replay and context
confusion.

## Fail-Closed Review

The model keeps default-deny semantics:

```text
explicit deny -> not authorized
approver not allowed -> not authorized
role collapse without policy -> not authorized
digest/context mismatch -> not authorized
missing rollback/abort -> not authorized
agent/runner/CI-created go -> not authorized
missing root -> not evaluated
malformed artifact -> not evaluated
clock unavailable -> not evaluated
revocation unknown -> not evaluated
approval system unavailable -> not evaluated
```

Both not-authorized and not-evaluated outcomes fail closed.

## Boundary Review

Even the strongest execution authorization vocabulary is named:

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
```

It does not mean current permission to execute, permission to sever, automatic
remediation, proof of safety, or proof of isolation.

The most important pair is preserved:

```text
machine checks all pass + no authenticated external human go -> no execution
authenticated external human go + no future runner gate -> ACTION_NOT_PERFORMED
```

This keeps execution behind a separate future gate.

## Ledger Requirement

The model correctly defers a future ledger gate for execution-authorization
assumptions:

```text
EA-HUMAN
EA-SIGN
EA-CLOCK
EA-REVOKE
EA-ROLE
EA-CONTEXT
EA-ROLLBACK
EA-META
```

This matches the Phase 2 discipline: every sufficient result must carry the
assumptions it depends on.

## Accepted Boundary

The model is accepted as design-only.

It opens only a future execution authorization ledger gate. It does not open
runner implementation or execution.
