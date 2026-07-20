# Nesira Phase 2 Execution Authorization Model

## Status

```text
DOCUMENT_TYPE: RESEARCH -- EXECUTION AUTHORIZATION MODEL
PHASE: PHASE_2_EXECUTION_AUTHORIZATION_GATE
SCOPE: MODEL_ONLY

AUTHORIZES:
execution authorization model
authenticated human-go requirements
approver/operator role separation
future execution authorization conformance expectations

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

This document defines what a future execution authorization must prove before
any runner implementation can even be discussed. It does not authorize runner
code or execution.

## Core Invariant

```text
HUMAN_GO_MUST_BE_AUTHENTICATED_AND_NON_SELF_AUTHORIZED
```

A human go is not a JSON field that the evaluating system may fill for itself.
It must be an independently authenticated artifact, supplied from outside the
agent/runner path, bound to the exact action and evidence bundle under review.

The following must never be accepted as human go:

```text
agent-created approval
runner-created approval
assessment-created approval
combined-verdict-created approval
dry-run-created approval
CI success
exit code 0
absence of blockers
```

## Relationship To Existing Layers

Execution authorization consumes earlier outputs only as preconditions:

```text
Nesira assessment:
  evidence assessment under declared trust roots

combined verdict:
  conservative product aggregation that may block

action authority:
  independent authority evidence sufficient for consideration

dry-run:
  non-executing precondition report with ACTION_NOT_PERFORMED

human go:
  independently authenticated final authorization to enter a future execution
  gate; still not execution by itself
```

None of these layers may impersonate another layer.

## Human-Go Root

A future implementation must define a separately declared human-go root.

Example root kinds:

```text
EXECUTION_HUMAN_APPROVER_IDENTITY
EXECUTION_APPROVAL_SIGNING_KEY
EXECUTION_CHANGE_CONTROL_SYSTEM
EXECUTION_BREAK_GLASS_APPROVER
```

These are not equivalent to Phase 2 trust roots:

```text
SIGNING_KEY
IDENTITY_BINDING_CA
AUTHORITY_POLICY_SOURCE
ATTESTATION_AUTHORITY
```

They are also not equivalent to action-authority roots unless explicitly bound
by policy. A person or key may be trusted to approve evidence for consideration
and still not be authorized to approve execution.

## Approver And Operator Roles

The model distinguishes two roles:

```text
approver:
  the human or change-control authority that grants the execution go/no-go

operator:
  the person or process that may later initiate the already-authorized runner
  action, if a future execution gate exists
```

Default rule:

```text
APPROVER_AND_OPERATOR_ARE_SEPARATE_ROLES
```

They may be the same person only if a future policy explicitly declares that
coalescing and records it in the authorization artifact. Silent role collapse is
not allowed.

The agent, evaluator, runner, CI job, or automated release process must not be
the approver.

## Human-Go Artifact

A future human-go artifact must be caller-supplied and non-circular. It must
not be derived from the assessment, combined verdict, dry-run artifact, action
authority artifact, or target artifact it authorizes.

Minimum fields:

```text
schema_id
schema_version
human_go_id
approver_root_id
approver_identity_ref
approval_method
issued_at
not_before
not_after
revocation_status
revocation_checked_at
freshness_window
authorized_action_id
authorized_action_class
authorized_subject_context_digest
authorized_environment_context_digest
authorized_target_scope_digest
expected_side_effects_digest
rollback_or_abort_ref_digest
evidence_bundle_digest
combined_verdict_digest
action_authority_digest
dry_run_artifact_digest
operator_identity_ref
operator_role_policy
human_acknowledgement_text_digest
```

The artifact may include a signature, change-control reference, or approval
system reference, but the validating system must treat the correctness of that
root as an explicit assumption, not as proof of absolute legitimacy.

## Binding Rule

The human go must bind exactly the same action context that the future runner
would consider:

```text
action id
action class
subject context
environment context
target scope
expected side effects
rollback/abort channel
evidence bundle
combined verdict
action authority result
dry-run artifact
operator identity or role
```

Any digest mismatch, omitted field, stale artifact, or context learned from the
artifact under action must fail closed.

## Self-Authorization Prohibition

Forbidden patterns:

```text
the agent signs its own go
the runner accepts its own generated approval
the dry-run artifact contains a go flag
combined verdict contains a go flag
the target artifact contains its own approval
approval is inferred from the same credential that produced assessment evidence
approval is inferred from "all checks passed"
approval is inferred from a CI workflow conclusion
```

If the system cannot distinguish the approver from the evaluating agent or
runner, it must return:

```text
EXECUTION_AUTHORIZATION_NOT_EVALUATED
```

or:

```text
EXECUTION_NOT_AUTHORIZED
```

according to whether the evidence was unavailable or checked and failed.

## Verdict Vocabulary

The execution authorization model uses a separate vocabulary:

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
EXECUTION_NOT_AUTHORIZED
EXECUTION_AUTHORIZATION_NOT_EVALUATED
```

No verdict in this vocabulary means that execution occurred, may occur now, or
is implemented.

`EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE` means only:

```text
the declared execution-authorization evidence is sufficient to open a later
runner implementation discussion, under declared roots and recorded assumptions.
```

It is not:

```text
permission to execute in the current system
permission to sever
permission to remediate
proof that the action is safe
proof that isolation happened
```

## Fail-Closed Mapping

The mapping is default-deny:

```text
authenticated human go from declared approver root, fresh, not revoked, within
time window, bound to exact action/context/evidence/dry-run/authority digests,
with rollback/abort binding and non-circular approver/operator roles
  -> EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE

explicit deny
  -> EXECUTION_NOT_AUTHORIZED

approver not allowed for action class
  -> EXECUTION_NOT_AUTHORIZED

approver/operator role collapse not allowed by policy
  -> EXECUTION_NOT_AUTHORIZED

digest or context mismatch
  -> EXECUTION_NOT_AUTHORIZED

rollback/abort binding missing
  -> EXECUTION_NOT_AUTHORIZED

requested action class outside allowlist
  -> EXECUTION_NOT_AUTHORIZED

human go created by agent, runner, dry-run, combined verdict, CI, or target
  -> EXECUTION_NOT_AUTHORIZED

missing human-go root
  -> EXECUTION_AUTHORIZATION_NOT_EVALUATED

human-go artifact malformed or unparseable
  -> EXECUTION_AUTHORIZATION_NOT_EVALUATED

clock unavailable or untrusted
  -> EXECUTION_AUTHORIZATION_NOT_EVALUATED

revocation unknown or freshness not established
  -> EXECUTION_AUTHORIZATION_NOT_EVALUATED

approval system unavailable
  -> EXECUTION_AUTHORIZATION_NOT_EVALUATED
```

Both not-authorized and not-evaluated outcomes fail closed.

## Recorded Assumptions

Execution authorization remains conditional. A future ledger extension must
assign stable IDs for at least:

```text
EA-HUMAN-01     legitimacy of declared human-go approver root
EA-SIGN-01      correctness of approval signature or approval-system check
EA-CLOCK-01     trusted time source for human-go validity windows
EA-REVOKE-01    revocation source honesty and freshness
EA-ROLE-01      correctness of approver/operator role policy
EA-CONTEXT-01   correctness of caller-supplied execution context binding
EA-ROLLBACK-01  rollback or abort channel availability
EA-META-01      execution authorization is not execution
```

These assumptions must be carried with any sufficient execution-authorization
result.

## Required Future Conformance

Any future implementation plan must include conformance cases:

```text
1. all preconditions satisfied + no human go -> not authorized.
2. agent-created human go -> not authorized.
3. runner-created human go -> not authorized.
4. CI success as human go -> not authorized.
5. human go signed by undeclared approver root -> not authorized.
6. missing human-go root -> not evaluated.
7. expired human go with trusted clock -> not authorized.
8. missing clock -> not evaluated.
9. revocation unknown -> not evaluated.
10. digest mismatch against dry-run artifact -> not authorized.
11. digest mismatch against action authority -> not authorized.
12. subject/context mismatch -> not authorized.
13. approver/operator collapse without explicit policy -> not authorized.
14. rollback/abort binding missing -> not authorized.
15. sufficient authorization still emits ACTION_NOT_PERFORMED until a later
    runner gate is separately authorized.
```

The most important pair is:

```text
machine checks all pass + no authenticated external human go -> no execution
authenticated external human go + no future runner gate -> ACTION_NOT_PERFORMED
```

This pair prevents both self-authorization and premature execution.

## Forbidden Public Language

Future reports or release notes must not say:

```text
human approved by Nesira
execution approved by assessment
safe to execute
safe to sever
automatic execution enabled
runner authorized by dry-run
CI approved execution
approval inferred
```

Allowed language before a separately authorized runner exists is limited to:

```text
execution authorization evidence sufficient for future runner gate
execution not authorized
execution authorization not evaluated
authenticated human go required
action not performed
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later design:

```text
treats human go as an unverified field
allows the agent or runner to generate its own go
allows CI success to stand in for human approval
does not bind human go to exact action/evidence/dry-run digests
collapses approver and operator roles silently
omits revocation or freshness checks
permits action when clock is unavailable
omits rollback or abort binding
expands public claims beyond authorization evidence
implements subprocess, filesystem mutation, or network execution
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_execution_authorization_model.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_model_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation, or
network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this model is accepted, the next step is still not execution code.

A future gate may draft:

```text
nesira_phase2_execution_authorization_ledger
```

That future gate would assign stable assumption IDs for the execution
authorization model. Actual runner implementation remains blocked.
