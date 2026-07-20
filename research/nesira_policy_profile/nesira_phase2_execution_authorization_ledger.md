# Nesira Phase 2 Execution Authorization Ledger

## Status

```text
DOCUMENT_TYPE: RESEARCH -- EXECUTION AUTHORIZATION ASSUMPTIONS LEDGER
PHASE: PHASE_2_EXECUTION_AUTHORIZATION_LEDGER_GATE
SCOPE: LEDGER_ONLY
LEDGER_ID: SPIRA_NESIRA_PHASE2_EXECUTION_AUTHORIZATION_LEDGER_V2
LEDGER_VERSION: 2
REVISION: EA-TCB-03 promoted to the unconditional assumption floor

AUTHORIZES:
execution-authorization assumption IDs
machine-readable execution-authorization ledger companion
future conformance references

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

This ledger gives every execution-authorization assumption a stable ID. Its
purpose is to prevent a future consumer from reading:

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
```

as assumption-free, self-authorizing, or executable.

## Core Rule

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE is never assumption-free.
```

Every future execution-authorization result must carry:

```text
assumptions: [EA-..., ...]
```

The unconditional assumption floor is always present:

```text
EA-HUMAN-01
EA-TCB-01
EA-TCB-03
EA-CLOCK-01
EA-META-01
EA-META-02
```

Conditional assumptions are added when the corresponding authority source,
signature system, revocation source, role policy, context binding, rollback
channel, human-readable acknowledgement, nonce, or misapplication guard is used.

## ID Categories

```text
EA-HUMAN-*          legitimacy of declared human-go approver roots
EA-SIGN-*           correctness of approval signature or approval-system checks
EA-CLOCK-*          clock and time-source trust for execution windows
EA-REVOKE-*         revocation-source honesty and revocation freshness
EA-ROLE-*           approver/operator role-policy assumptions
EA-CONTEXT-*        caller-supplied execution-context binding assumptions
EA-ROLLBACK-*       rollback or abort channel assumptions
EA-TCB-*            trusted verifier / TCB assumptions
EA-HUMAN-TEXT-*     human-readable acknowledgement assumptions
EA-NONCE-*          one-time-use and replay-prevention assumptions
EA-MISAPPLICATION-* human-go misapplication / confused-deputy assumptions
EA-META-*           meta-boundaries: authorization is not execution
```

## Entry Schema

Each entry has:

```text
id
version
statement
applies_to
universality: UNCONDITIONAL | CONDITIONAL
mandatory_when
forbidden_reading
cross_ref
```

`forbidden_reading` is required. It states what a consumer must not infer from
the assumption.

## Ledger Entries

### EA-HUMAN

```text
EA-HUMAN-01:
  statement: legitimacy of the declared human-go approver root is assumed, not proven.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: a declared approver root is absolutely legitimate.

EA-HUMAN-02:
  statement: the approver identity is assumed to be bound to the declared approver root and approval method.
  universality: CONDITIONAL
  mandatory_when: approver identity is evaluated
  forbidden_reading: identity binding proves the approver was authorized for every action.
```

### EA-SIGN

```text
EA-SIGN-01:
  statement: approval signature or approval-system verification depends on the correctness of the declared verification mechanism.
  universality: CONDITIONAL
  mandatory_when: signed or system-mediated human-go artifact is evaluated
  forbidden_reading: a valid signature or approval-system check proves the action should run.

EA-SIGN-02:
  statement: custody of approval credentials is assumed outside SPIRA.
  universality: CONDITIONAL
  mandatory_when: approval credential is used
  forbidden_reading: signature validity proves the credential was not compromised.
```

### EA-CLOCK

```text
EA-CLOCK-01:
  statement: validity windows, freshness windows, nonce expiry, and revocation freshness depend on declared clock trust.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: SPIRA proves real-world time correctness.

EA-CLOCK-02:
  statement: clock-source identity and freshness are assumed according to the declared execution-authorization clock root.
  universality: CONDITIONAL
  mandatory_when: specific clock root is used
  forbidden_reading: timestamp comparison proves the clock source is honest.
```

### EA-REVOKE

```text
EA-REVOKE-01:
  statement: honesty and correctness of the human-go revocation source are assumed from the declared root.
  universality: CONDITIONAL
  mandatory_when: revocation status is used
  forbidden_reading: revocation check proves the source is honest.

EA-REVOKE-02:
  statement: unknown or stale revocation status is not evidence of non-revocation.
  universality: CONDITIONAL
  mandatory_when: revocation source is missing, unreachable, stale, or inconclusive
  forbidden_reading: unknown revocation status can support execution authorization.
```

### EA-ROLE

```text
EA-ROLE-01:
  statement: correctness of the approver/operator role policy is assumed, not proven.
  universality: CONDITIONAL
  mandatory_when: approver and operator roles are evaluated
  forbidden_reading: role policy correctness is proven by SPIRA.

EA-ROLE-02:
  statement: approver/operator coalescing is assumed valid only when explicitly declared by policy.
  universality: CONDITIONAL
  mandatory_when: approver and operator are the same identity or role
  forbidden_reading: silent role collapse is allowed.
```

### EA-CONTEXT

```text
EA-CONTEXT-01:
  statement: correctness of the caller-supplied execution context is assumed outside the artifact under action.
  universality: CONDITIONAL
  mandatory_when: execution context binding is evaluated
  forbidden_reading: the target artifact may define its own execution context.

EA-CONTEXT-02:
  statement: digest binding correctly represents the intended action, subject, environment, target scope, and side-effect summary.
  universality: CONDITIONAL
  mandatory_when: action/context digest is compared
  forbidden_reading: matching opaque digests alone prove the human understood the action.
```

### EA-ROLLBACK

```text
EA-ROLLBACK-01:
  statement: rollback or abort channel availability is assumed from the declared rollback/abort reference.
  universality: CONDITIONAL
  mandatory_when: rollback_or_abort_ref is required
  forbidden_reading: rollback reference proves rollback will succeed.

EA-ROLLBACK-02:
  statement: rollback or abort authority is distinct from execution authorization unless explicitly declared.
  universality: CONDITIONAL
  mandatory_when: rollback or abort authority is evaluated
  forbidden_reading: permission to execute automatically grants permission to rollback or abort.
```

### EA-TCB

```text
EA-TCB-01:
  statement: a trusted verifier computes and compares execution-context digests independently of the runner or agent.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: the agent or runner may be trusted to validate its own authorization binding.

EA-TCB-02:
  statement: correctness and independence of the trusted verifier / TCB are assumed, not proven.
  universality: CONDITIONAL
  mandatory_when: trusted verifier is used
  forbidden_reading: SPIRA proves the verifier cannot be compromised.

EA-TCB-03:
  statement: the trusted verifier observes the same action context that a future runner would receive.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: checking a prepared bundle proves the later runner input is identical.
```

### EA-HUMAN-TEXT

```text
EA-HUMAN-TEXT-01:
  statement: the human acknowledgement text is assumed to be readable and to describe the action, subject, target, side effects, and rollback/abort reference.
  universality: CONDITIONAL
  mandatory_when: human acknowledgement text digest is used
  forbidden_reading: a human approved a meaningful action by seeing only an opaque hash.

EA-HUMAN-TEXT-02:
  statement: the acknowledgement text digest is assumed to correspond to the exact text presented to the approver.
  universality: CONDITIONAL
  mandatory_when: acknowledgement text is compared
  forbidden_reading: digest binding proves the UI presented the text honestly.
```

### EA-NONCE

```text
EA-NONCE-01:
  statement: human-go artifacts require one-time-use nonce or equivalent replay-prevention binding.
  universality: CONDITIONAL
  mandatory_when: human-go artifact may be replayed within or across validity windows
  forbidden_reading: a fresh approval may be reused for a different run.

EA-NONCE-02:
  statement: nonce registry correctness and single-use enforcement are assumed from the declared nonce authority.
  universality: CONDITIONAL
  mandatory_when: nonce registry or replay-prevention service is used
  forbidden_reading: SPIRA proves nonce storage cannot be bypassed.
```

### EA-MISAPPLICATION

```text
EA-MISAPPLICATION-01:
  statement: an authentic human go must not be applied to a different action, subject, target, environment, side-effect set, or evidence bundle.
  universality: CONDITIONAL
  mandatory_when: human go is matched to requested execution context
  forbidden_reading: a real approval is valid for any similar-looking action.

EA-MISAPPLICATION-02:
  statement: confused-deputy prevention depends on the verifier comparing the human-approved context to the runner-intended context, not to a separately prepared bundle.
  universality: CONDITIONAL
  mandatory_when: runner-intended context exists or will exist
  forbidden_reading: approval authenticity alone prevents misapplication.
```

### EA-META

```text
EA-META-01:
  statement: execution authorization is not execution.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: authorization evidence means the action was performed.

EA-META-02:
  statement: execution-authorization sufficiency is conditional on declared roots, the trusted verifier, and this ledger.
  universality: UNCONDITIONAL
  applies_to: all execution-authorization results
  forbidden_reading: sufficient means unconditional permission or safety.

EA-META-03:
  statement: an execution-authorization result can only open a later runner gate; it does not authorize current runner implementation.
  universality: CONDITIONAL
  mandatory_when: sufficient execution-authorization result is produced
  forbidden_reading: a sufficient authorization model permits immediate runner code.
```

## Assumption Floor

The assumption floor is mandatory for every future execution-authorization
result:

```text
EA-HUMAN-01
EA-TCB-01
EA-TCB-03
EA-CLOCK-01
EA-META-01
EA-META-02
```

Therefore, even:

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
```

must carry a non-empty `assumptions` array.

## Trusted Verifier Rule

The trusted verifier is load-bearing.

It must compute or receive the runner-intended execution context independently
of the agent that requests execution, then compare it against the authenticated
human-go artifact.

Forbidden verifier patterns:

```text
the runner verifies its own binding
the agent chooses both the approved bundle and the runner-intended bundle
the verifier compares only a prepared evidence bundle and not the actual action context
the verifier trusts target-supplied context
the verifier accepts copy-paste human text without digest binding
```

If the verifier cannot establish independence from the agent/runner path, the
result is not sufficient.

## Human-Readable Text Rule

Human approval must not be reduced to approving an opaque hash.

The human-facing acknowledgement text must describe:

```text
action id
action class
subject/context
target scope
expected side effects
rollback or abort reference
evidence bundle digest
dry-run digest
action-authority digest
validity window
one-time-use or replay-prevention status
```

The text may include digests, but the digests cannot replace the human-readable
description.

## Replay Rule

A valid human-go artifact must not be reusable by default.

Replay prevention must bind at least:

```text
nonce or one-time-use id
action id
target scope
context digests
validity window
operator identity or role
```

Reuse of the same human-go artifact without explicit replay policy must fail
closed.

## Carrier Rule

Every future execution-authorization contract must include:

```text
assumptions: [EA-..., ...]
conditional_on_roots: [execution_authorization_root_id@version, ...]
trusted_verifier_ref: verifier_id@version
human_go_ref: human_go_id@version
```

Missing `assumptions` is invalid.

An empty `assumptions` array is invalid.

## Stability Rule

Ledger IDs are stable.

```text
IDs are never deleted silently.
Removing or weakening an assumption requires a new ledger version and review.
```

Changing `forbidden_reading`, `universality`, or `mandatory_when` also requires
a new ledger version.

## Machine-Readable Companion

The companion JSON file is:

```text
research/nesira_policy_profile/nesira_phase2_execution_authorization_ledger.json
```

Future implementation plans, harnesses, and reviews must reference assumption
IDs from the JSON companion rather than copying prose.

## Explicitly Not Authorized

```text
runner implementation
subprocess execution
filesystem mutation
network execution
severance action
automatic remediation
CLI flag change
combined verdict behavior change
version bump
release
public claim expansion
```

## Status

```text
NESIRA_PHASE2_EXECUTION_AUTHORIZATION_LEDGER_SPECIFIED
EA_ASSUMPTION_FLOOR_SPECIFIED
HUMAN_GO_NEVER_ASSUMPTION_FREE
EA_TCB_01_TRUSTED_VERIFIER_REQUIRED
EA_TCB_03_RUNNER_INTENDED_CONTEXT_IN_FLOOR
EA_HUMAN_TEXT_01_HUMAN_READABLE_APPROVAL_REQUIRED
EA_NONCE_01_REPLAY_PREVENTION_REQUIRED
EA_MISAPPLICATION_01_CONFUSED_DEPUTY_GUARD_SPECIFIED
EXECUTION_STILL_NOT_AUTHORIZED
```
