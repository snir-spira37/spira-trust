# Nesira Phase 2 Action Authority Model Review

## Verdict

```text
NESIRA_PHASE2_ACTION_AUTHORITY_MODEL_ACCEPTED
```

The model is accepted because it preserves the required separation between
assessment, combined verdict, action authority, and any future runner.

## Crux Review

The load-bearing rule is explicit:

```text
ACTION_AUTHORITY_IS_INDEPENDENT_OF_ASSESSMENT
```

The model does not allow any of these to authorize action:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
GRAPH_OK
recommended_agent_action = PROCEED
identity_sub = SUFFICIENT
authority_sub = SUFFICIENT
isolation_sub = SUFFICIENT
```

This closes the main collapse risk: trusted-for-assessment does not become
authorized-to-act.

## Fail-Closed Review

The verdict mapping is default-deny:

```text
explicit allow + matching context + fresh revocation + valid time + rollback
  -> sufficient for consideration only

explicit deny / absent from policy / out of scope / mismatch
  -> not authorized

missing root / malformed / clock missing / revocation unknown / source unavailable
  -> not evaluated
```

Both non-authorized and not-evaluated outcomes block any future runner-adjacent
path. There is no soft-fail path.

## Non-Circularity Review

The model correctly requires the expected action, subject, environment, and
authority root to come from caller-supplied context outside the evidence being
evaluated.

The following circular patterns are explicitly forbidden:

```text
assessment defines authorization
combined verdict defines authorization
attestation defines expected action for itself
runner derives the subject from the artifact it would act on
```

This is the same structural protection that made the assessment wiring safe:
one external expected context binds all evidence.

## Scope Review

Accepted:

```text
action-authority vocabulary
authority-root separation
fail-closed mapping
future dry-run conformance requirements
```

Still blocked:

```text
runner implementation
subprocess execution
filesystem mutation
network execution
severance action
automatic remediation
CLI changes
combined verdict behavior changes
release/version/public-claim changes
```

## Required Next Gate

The next safe step is not execution code. It is:

```text
nesira_phase2_non_executing_dry_run_runner_plan
```

That plan must demonstrate, on paper, that:

```text
Nesira sufficient without action authority cannot run
combined GRAPH_OK without action authority cannot run
sufficient action authority still produces only dry-run output
dry-run output contains no executable command string
no side effects are possible
```

If those cannot be stated and tested cleanly, runner work remains blocked.

## Boundary

This review accepts only the model. It does not authorize implementation,
publication, or action.
