# Nesira Phase 2 Action Authority Model

## Status

```text
DOCUMENT_TYPE: RESEARCH -- ACTION AUTHORITY MODEL
PHASE: PHASE_2_ACTION_AUTHORITY_GATE
SCOPE: MODEL_ONLY

AUTHORIZES:
action-authority model
future dry-run precondition vocabulary
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

This document defines the missing layer between a conservative combined verdict
and any future runner. It does not authorize code or execution.

## Core Invariant

```text
ACTION_AUTHORITY_IS_INDEPENDENT_OF_ASSESSMENT
```

Nesira Phase 2 assessment roots are trust-assessment roots. They are not
runtime-action roots.

The following are never sufficient action authorization:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
GRAPH_OK
recommended_agent_action = PROCEED
identity_sub = SUFFICIENT
authority_sub = SUFFICIENT
isolation_sub = SUFFICIENT
```

They may be evidence or preconditions. They cannot replace a separate
action-authority decision.

## Model Layers

The active stack remains separated:

```text
assessment:
  checks declared trust evidence against declared roots

combined_verdict:
  aggregates policy layers conservatively; can block

action_authority:
  states whether a specific action is authorized by an independent action root

runner:
  not authorized here; may only be discussed after action authority and dry-run
  gates are accepted
```

The action-authority layer consumes assessment and combined-verdict outputs only
as bounded inputs. It must not learn the action, subject, or authority from the
assessment artifact itself.

## Authority Roots

An action-authority root is a separately declared root that answers:

```text
who may authorize action
which action class is in scope
which subject/context is bound
which time window applies
which revocation/freshness source applies
which abort/rollback channel is required
```

Examples of root kinds for future design:

```text
ACTION_HUMAN_APPROVER
ACTION_POLICY_SOURCE
ACTION_CHANGE_CONTROL_RECORD
ACTION_BREAK_GLASS_RECORD
```

These roots are not equivalent to:

```text
SIGNING_KEY
IDENTITY_BINDING_CA
AUTHORITY_POLICY_SOURCE
ATTESTATION_AUTHORITY
```

A key or identity may be trusted for assessment evidence and still have no
authority to authorize runtime action.

## Action Authorization Artifact

A future action-authorization artifact must be caller-supplied and non-circular.
It must not be derived from the assessment it is authorizing.

Minimum fields:

```text
schema_id
schema_version
authorization_id
action_authority_root_id
issuer_or_policy_ref
authorized_action_class
authorized_subject_context
authorized_environment_context
not_before
not_after
issued_at
revocation_status
revocation_checked_at
freshness_window
required_preconditions
rollback_or_abort_ref
evidence_refs
```

The action to be considered must be bound outside the artifact under review by
the caller's expected context. The artifact may match that context; it may not
define it for itself.

## Verdict Vocabulary

The action-authority model uses a separate vocabulary:

```text
ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION
ACTION_NOT_AUTHORIZED
ACTION_NOT_EVALUATED
```

No verdict in this vocabulary means execution occurred or may occur.

`ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION` means only:

```text
the declared action-authority evidence is sufficient for a later non-executing
dry-run gate to consider the requested action, under declared action roots and
recorded assumptions.
```

It is not:

```text
permission to execute
permission to sever
permission to remediate
proof that the action is safe
proof that isolation happened
```

## Fail-Closed Mapping

The action-authority mapping is default-deny:

```text
explicit allow by declared action authority, matching action/subject/context,
fresh, within time window, not revoked, with rollback/abort ref
  -> ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION

explicit deny
  -> ACTION_NOT_AUTHORIZED

identity/action absent from policy
  -> ACTION_NOT_AUTHORIZED

action class outside scope
  -> ACTION_NOT_AUTHORIZED

subject/context mismatch
  -> ACTION_NOT_AUTHORIZED

rollback/abort ref missing
  -> ACTION_NOT_AUTHORIZED

missing action-authority root
  -> ACTION_NOT_EVALUATED

artifact malformed or unparseable
  -> ACTION_NOT_EVALUATED

clock unavailable or untrusted
  -> ACTION_NOT_EVALUATED

revocation unknown or freshness not established
  -> ACTION_NOT_EVALUATED

authority source unavailable
  -> ACTION_NOT_EVALUATED
```

Both non-authorized and not-evaluated outcomes fail closed for any future
runner-adjacent gate.

## Required Preconditions

A sufficient action-authority result is still not enough by itself.

Future dry-run consideration must require at minimum:

```text
combined verdict is non-blocking
Nesira assessment is present if required
Nesira assumptions remain visible
PT-ISOLATION-01 remains carried when isolation evidence is present
action authority is sufficient for consideration
caller expected context matches every consumed artifact
```

If any precondition is absent, malformed, stale, or mismatched:

```text
ACTION_NOT_AUTHORIZED
```

or:

```text
ACTION_NOT_EVALUATED
```

depending on whether the evidence was checked and failed or could not be
evaluated.

## Non-Circularity Rule

The model must reject circular authority.

Forbidden circular patterns:

```text
assessment says the action is authorized
authority_sub says the action is authorized
combined verdict says the action is authorized
attestation payload defines the expected action for itself
the runner derives the expected subject from the artifact it will execute
```

The expected action, subject, environment, and authority root must come from a
caller-supplied context outside the evidence being evaluated.

## Recorded Assumptions

Action authority remains conditional. A future ledger extension must assign
stable IDs for at least:

```text
PA-AUTHORITY-01  legitimacy of declared action authority root
PA-POLICY-01     correctness of action policy interpretation
PA-CLOCK-01      trusted time source for action windows
PA-REVOKE-01     revocation source honesty and freshness
PA-ROLLBACK-01   rollback/abort channel availability
PA-META-01       action authority is not execution
```

These assumptions must be carried with any sufficient action-authority result.

## Forbidden Output Language

Future reports must not say:

```text
action authorized by Nesira
safe to run
safe to sever
permission granted
execution approved
automatic remediation approved
isolation proven
```

Allowed language is limited to:

```text
action-authority evidence sufficient for consideration
action not authorized
action authority not evaluated
dry-run only
action not performed
```

## Required Future Conformance

Any future implementation plan must include conformance cases:

```text
1. Nesira SUFFICIENT + no action authority -> ACTION_NOT_EVALUATED or NOT_AUTHORIZED, never sufficient.
2. combined GRAPH_OK + no action authority -> not authorized.
3. explicit allow + BLOCK combined verdict -> not authorized.
4. explicit allow + mismatched subject -> not authorized.
5. explicit allow + missing rollback/abort ref -> not authorized.
6. policy absent identity/action -> not authorized.
7. missing authority root -> not evaluated.
8. revocation unknown -> not evaluated.
9. clock missing -> not evaluated.
10. circular context source -> not authorized.
11. sufficient action authority still emits ACTION_NOT_PERFORMED in dry-run.
12. no subprocess/filesystem/network side effects occur.
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later design:

```text
uses assessment roots as action roots
uses Nesira sufficient as action authorization
uses combined verdict as action authorization
does not require separate caller-supplied expected context
permits action when revocation is unknown
permits action when clock is unavailable
omits rollback/abort binding
emits executable commands in dry-run output
adds public runner behavior without a release gate
```

## Next Step

If this model is accepted, the next gate may draft:

```text
nesira_phase2_non_executing_dry_run_runner_plan
```

That next gate remains design-only unless separately authorized. Actual runner
implementation and any execution remain blocked.
