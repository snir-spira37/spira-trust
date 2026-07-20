# Nesira Phase 2 Execution Authorization Conformance Spec

## Status

```text
DOCUMENT_TYPE: RESEARCH -- EXECUTION AUTHORIZATION CONFORMANCE SPEC
PHASE: PHASE_2_EXECUTION_AUTHORIZATION_CONFORMANCE_GATE
SCOPE: SPEC_ONLY

AUTHORIZES:
future conformance matrix
future oracle expectations
future implementation hard stops

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

This specification defines the conformance cases a future execution
authorization implementation would have to satisfy. It does not authorize that
implementation.

## Core Locks

```text
AUTHENTICATED_HUMAN_GO_IS_REQUIRED
SELF_AUTHORIZATION_IS_FORBIDDEN
TRUSTED_VERIFIER_MUST_BE_INDEPENDENT
VERIFIER_CHECKS_RUNNER_INTENDED_CONTEXT
HUMAN_TEXT_MUST_BE_READABLE
NONCE_REPLAY_PREVENTION_REQUIRED
AUTHORIZATION_IS_NOT_EXECUTION
```

## Verdict Vocabulary Under Test

```text
EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
EXECUTION_NOT_AUTHORIZED
EXECUTION_AUTHORIZATION_NOT_EVALUATED
ACTION_NOT_PERFORMED
```

No expected result in this spec permits subprocess execution, filesystem
mutation, network execution, severance, or remediation.

## Required Artifact Fields

Future conformance fixtures must include enough structure to test:

```text
human_go_id
approver_root_id
approver_identity_ref
approval_method
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
runner_intended_context_digest
trusted_verifier_ref
human_acknowledgement_text_digest
nonce_or_one_time_use_id
operator_identity_ref
operator_role_policy
not_before
not_after
revocation_status
revocation_checked_at
```

The `runner_intended_context_digest` is load-bearing. It represents the context
the future runner would actually receive, not a bundle prepared by the agent.

## Conformance Matrix

Every future implementation must include at least these cases:

```text
01_all_machine_checks_pass_no_human_go:
  expected: EXECUTION_NOT_AUTHORIZED
  carries: floor assumptions

02_agent_created_human_go:
  expected: EXECUTION_NOT_AUTHORIZED

03_runner_created_human_go:
  expected: EXECUTION_NOT_AUTHORIZED

04_ci_success_as_human_go:
  expected: EXECUTION_NOT_AUTHORIZED

05_human_go_signed_by_undeclared_root:
  expected: EXECUTION_NOT_AUTHORIZED

06_missing_human_go_root:
  expected: EXECUTION_AUTHORIZATION_NOT_EVALUATED

07_expired_human_go_with_trusted_clock:
  expected: EXECUTION_NOT_AUTHORIZED

08_clock_missing:
  expected: EXECUTION_AUTHORIZATION_NOT_EVALUATED

09_revocation_unknown:
  expected: EXECUTION_AUTHORIZATION_NOT_EVALUATED

10_dry_run_digest_mismatch:
  expected: EXECUTION_NOT_AUTHORIZED

11_action_authority_digest_mismatch:
  expected: EXECUTION_NOT_AUTHORIZED

12_subject_context_mismatch:
  expected: EXECUTION_NOT_AUTHORIZED

13_runner_intended_context_differs_from_approved_context:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-TCB-03, EA-MISAPPLICATION-02

14_prepared_bundle_matches_but_runner_input_differs:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-TCB-03, EA-MISAPPLICATION-02

15_opaque_hash_without_human_readable_text:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-HUMAN-TEXT-01

16_acknowledgement_text_digest_mismatch:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-HUMAN-TEXT-02

17_nonce_replay:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-NONCE-01

18_nonce_registry_unavailable:
  expected: EXECUTION_AUTHORIZATION_NOT_EVALUATED
  guards: EA-NONCE-02

19_approver_operator_collapse_without_policy:
  expected: EXECUTION_NOT_AUTHORIZED
  guards: EA-ROLE-02

20_rollback_or_abort_missing:
  expected: EXECUTION_NOT_AUTHORIZED

21_action_class_not_allowlisted:
  expected: EXECUTION_NOT_AUTHORIZED

22_all_authorization_evidence_sufficient_no_runner_gate:
  expected: EXECUTION_AUTHORIZATION_SUFFICIENT_FOR_FUTURE_RUNNER_GATE
  action_marker: ACTION_NOT_PERFORMED
```

The final case is intentionally not execution. It may only open discussion of a
later runner implementation gate.

## Assumption-Carrying Expectations

Every case must carry a non-empty assumption set.

The floor must be present in every case:

```text
EA-HUMAN-01
EA-TCB-01
EA-TCB-03
EA-CLOCK-01
EA-META-01
EA-META-02
```

Case-specific assumptions must be included when relevant:

```text
signature or approval-system check -> EA-SIGN-01
credential custody -> EA-SIGN-02
revocation checked or unknown -> EA-REVOKE-01 / EA-REVOKE-02
role policy evaluated -> EA-ROLE-01 / EA-ROLE-02
context digest compared -> EA-CONTEXT-01 / EA-CONTEXT-02
rollback or abort considered -> EA-ROLLBACK-01 / EA-ROLLBACK-02
human-readable text checked -> EA-HUMAN-TEXT-01 / EA-HUMAN-TEXT-02
nonce or replay-prevention checked -> EA-NONCE-01 / EA-NONCE-02
misapplication guard evaluated -> EA-MISAPPLICATION-01 / EA-MISAPPLICATION-02
```

Missing floor assumptions are a conformance failure even when the expected
verdict is negative.

## Trusted Verifier Cases

The future verifier must fail closed unless it compares the human-approved
context to the runner-intended context.

Forbidden passing cases:

```text
verifier compares only a prepared bundle
verifier trusts agent-supplied runner context
verifier trusts target-supplied context
verifier is the runner itself
verifier cannot distinguish runner input from approval bundle
```

Any one of these must produce:

```text
EXECUTION_NOT_AUTHORIZED
```

or:

```text
EXECUTION_AUTHORIZATION_NOT_EVALUATED
```

depending on whether the verifier evidence was checked and failed or could not
be evaluated.

## Forbidden Outputs

Future conformance artifacts must not include:

```text
command
command_line
script
shell
subprocess_args
write_paths
network_targets
copy_paste_steps
runbook
execution_approved
safe_to_execute
severance_authorized
```

Any output that can reasonably be read as executable instruction fails the
spec.

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later implementation plan:

```text
omits runner-intended context comparison
does not test agent-created or runner-created human go
does not test CI-success-as-go
does not test nonce replay
does not test opaque-hash-only approval
allows sufficient authorization to perform execution
adds subprocess, filesystem mutation, or network execution
adds public CLI behavior
changes release behavior
```

## Authorized Files

This gate may create or edit only:

```text
research/nesira_policy_profile/nesira_phase2_execution_authorization_ledger.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_ledger.json
research/nesira_policy_profile/nesira_phase2_execution_authorization_ledger_review.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_conformance_spec.md
research/nesira_policy_profile/nesira_phase2_execution_authorization_conformance_spec_review.md
```

Any source, tests, workflow, pyproject, manifest, version, release, tag,
publication, public claim, CLI, runner, subprocess, filesystem mutation, or
network execution change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Next Step

If this spec is accepted, the next step is still not runner code.

A future gate may draft an implementation authorization for an
execution-authorization evaluator only. That evaluator would still be
non-executing and must prove these conformance cases before any runner gate is
discussed.
