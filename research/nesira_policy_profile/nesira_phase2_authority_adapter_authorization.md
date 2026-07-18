# Nesira Phase 2 Authority Adapter Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: AUTHORITY_ADAPTER_PLAN_AND_IMPLEMENTATION_GATE
SCOPE: AUTHORITY_ADAPTER_ONLY
SIGNATURE_ADAPTER_BASELINE: COLD_VERIFIED
IDENTITY_ADAPTER_BASELINE: COLD_VERIFIED
ISOLATION_ATTESTATION_ADAPTER: NOT_AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes the next narrow Phase 2 adapter gate: signer authority
lookup only.

The authority adapter may evaluate whether an already-established signer
identity is explicitly authorized for a bounded action by a declared
`AUTHORITY_POLICY_SOURCE` root.

It must not verify signatures, re-evaluate identity credentials, evaluate
isolation attestation, execute isolation, perform operational severance, wire
combined verdict integration, expose a CLI, enter the public wheel, make public
claims, or release.

## Preconditions

The following baselines are required and accepted:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

Recorded in:

```text
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_results.json
```

The signature and identity adapters are treated as frozen for this gate. Authority
work must not modify them except through a separate remediation authorization.

## Authoritative Inputs

The authority adapter must obey:

```text
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_review.md
```

Any conflict is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be resolved by silently changing the trust model, ledger,
composition core, signature adapter, identity adapter, or V1 artifacts.

## Authorized Adapter Scope

The authority adapter may produce only a Phase 2 sub-assessment verdict:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

It may evaluate:

```text
declared AUTHORITY_POLICY_SOURCE root shape
policy source availability and parseability
policy root identity/version/scope
policy freshness and validity window
revocation/freshness status for the policy source
whether established signer identity is explicitly allowed for the bounded action
whether established signer identity is explicitly denied for the bounded action
whether established signer identity is absent from the policy
subject/environment/purpose/action/policy-version context binding
```

It must not evaluate:

```text
signature cryptographic validity
identity credential validity
identity-to-key binding
isolation attestation
actual isolation execution
permission to sever
```

Authority is a policy lookup over an already-established identity. It must not
re-verify certificates, chains, signing keys, or cryptographic signatures.

## Semantics

Accepted reading:

```text
The established signer identity is explicitly authorized for this bounded
action by the declared AUTHORITY_POLICY_SOURCE, under declared roots and
assumptions.
```

Forbidden readings:

```text
the signature was verified by this adapter
the identity credential was verified by this adapter
the authority policy source is legitimate in an absolute sense
the signer may sever
the system may execute severance
isolation occurred
```

Authority is not execution.

## Policy Dependency Rule

The authority adapter should not require a new crypto dependency. If the policy
source is signed, signature verification must be handled by the already
accepted signature adapter or by a separately authorized signature-policy gate.

This gate is policy evaluation only:

```text
policy bytes / object -> deterministic authority lookup
```

No new dependency, parser, schema format, or policy language is authorized
unless it is specified in the implementation plan and reviewed as part of this
gate.

`pyproject.toml` must remain unchanged:

```text
dependencies = []
```

## Sub-Verdict Mapping

The core distinction for authority is:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS:
  the declared policy was consulted and contains an explicit in-scope allow

TRUST_INSUFFICIENT:
  the declared policy was consulted and did not authorize the request

TRUST_NOT_EVALUATED:
  the declared policy could not be consulted or interpreted under the declared root
```

Required mapping:

```text
valid policy source
+ declared AUTHORITY_POLICY_SOURCE root matches
+ established signer identity provided
+ signer identity explicitly allowed for subject/environment/purpose/action
+ policy version/context match
+ policy source not expired
+ policy source not revoked
+ revocation confirmed fresh
+ clock available and declared
  -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

missing authority policy root
  -> TRUST_NOT_EVALUATED

ambiguous authority policy root
  -> TRUST_NOT_EVALUATED

malformed authority policy root
  -> TRUST_NOT_EVALUATED

policy source missing, unreadable, malformed, unsupported, or unparseable
  -> TRUST_NOT_EVALUATED

established signer identity missing
  -> TRUST_NOT_EVALUATED

identity sub-verdict not sufficient
  -> TRUST_NOT_EVALUATED

signer identity explicitly denied by policy
  -> TRUST_INSUFFICIENT

signer identity absent from policy
  -> TRUST_INSUFFICIENT

signer identity present but action not explicitly allowed
  -> TRUST_INSUFFICIENT

policy root id/version mismatch
  -> TRUST_INSUFFICIENT

policy subject/environment/purpose/action mismatch
  -> TRUST_INSUFFICIENT

policy version stale or out of scope
  -> TRUST_INSUFFICIENT

policy source expired or not yet valid
  -> TRUST_INSUFFICIENT

policy source revoked
  -> TRUST_INSUFFICIENT

revocation unknown, stale, unreachable, missing, or inconclusive
  -> TRUST_NOT_EVALUATED

clock missing or untrusted
  -> TRUST_NOT_EVALUATED
```

The most important non-confusion rule is:

```text
no declared policy root -> TRUST_NOT_EVALUATED
identity absent from policy -> TRUST_INSUFFICIENT
explicit policy deny -> TRUST_INSUFFICIENT
explicit policy allow -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

Default-deny is mandatory. Absence from an otherwise consultable policy is not a
gap; it is a denial for this gate.

## Assumption Carrying

Every output must carry the unconditional floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

A sufficient authority output must also carry:

```text
PT-AUTHORITY-01
PT-AUTHORITY-02
PT-REVOKE-01
PT-REVOKE-02
```

Unknown or inconclusive revocation must carry:

```text
PT-REVOKE-03
```

If a specific clock root is used, the result must also carry:

```text
PT-CLOCK-02
```

The authority adapter must not carry:

```text
PT-IDENTITY-* as if it had verified identity
PT-ISOLATION-*
```

It may echo the established signer identity as input evidence, but it must not
claim to have produced or verified that identity.

## No Default Authority

The adapter must not use:

```text
implicit admin role
implicit owner role
implicit repository owner authority
implicit cloud account owner authority
default allow
permit unless denied
fallback policy
any known identity is authorized
any valid identity is authorized
```

Only explicit in-scope allow entries in the declared authority policy source can
support sufficiency.

## Required Conformance

The implementation must include fixtures and mutation pairs for:

```text
valid_explicit_allow
missing_authority_policy_root
ambiguous_authority_policy_root
malformed_authority_policy_root
policy_source_missing
policy_source_malformed
unsupported_policy_type
established_identity_missing
identity_sub_verdict_not_sufficient
explicit_deny
identity_absent_from_policy
action_not_allowed
subject_context_mismatch
environment_context_mismatch
purpose_context_mismatch
policy_version_mismatch
policy_root_mismatch
policy_version_stale
policy_expired
policy_not_yet_valid
policy_revoked
revocation_unknown
revocation_stale
revocation_unreachable
clock_missing
clock_untrusted
```

Required metrics:

```text
required_authority_failure_modes_without_fixture: 0
required_authority_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
missing_policy_root_mapped_to_insufficient: 0
identity_absent_mapped_to_not_evaluated: 0
explicit_deny_mapped_to_not_evaluated: 0
action_not_allowed_mapped_to_not_evaluated: 0
default_allow_paths: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
authority_outputs_with_identity_verification_semantics: 0
authority_outputs_with_execution_semantics: 0
composition_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## End-to-End Composition Check

The implementation must feed authority sub-verdicts into the accepted Phase 2
composition oracle.

For the authority-only gate, the expected setup is:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
authority_sub = adapter output
isolation_sub = TRUST_NOT_EVALUATED
```

Expected composite results:

```text
authority sufficient    -> composite TRUST_NOT_EVALUATED
authority not evaluated -> composite TRUST_NOT_EVALUATED
authority insufficient  -> composite TRUST_INSUFFICIENT
```

This verifies wiring only. It does not claim full Phase 2 sufficiency.

## Stop Conditions

The implementation must stop on:

```text
DEFAULT_ALLOW_DETECTED
PERMIT_UNLESS_DENIED_DETECTED
IDENTITY_ABSENT_WRONGLY_MARKED_NOT_EVALUATED
EXPLICIT_DENY_WRONGLY_MARKED_NOT_EVALUATED
ACTION_NOT_ALLOWED_WRONGLY_MARKED_NOT_EVALUATED
MISSING_POLICY_ROOT_WRONGLY_MARKED_INSUFFICIENT
POLICY_SOURCE_UNREADABLE_WRONGLY_MARKED_INSUFFICIENT
REVOCATION_UNKNOWN_SOFT_PASS
CLOCK_FAILURE_SOFT_PASS
AUTHORITY_ADAPTER_REVERIFIES_SIGNATURE
AUTHORITY_ADAPTER_REVERIFIES_IDENTITY
AUTHORITY_ADAPTER_EMITS_EXECUTION
AUTHORITY_ADAPTER_EMITS_PERMISSION_TO_SEVER
COMPOSITION_CORE_BYPASSED
SIGNATURE_ADAPTER_MODIFIED_WITHOUT_AUTHORIZATION
IDENTITY_ADAPTER_MODIFIED_WITHOUT_AUTHORIZATION
FROZEN_SURFACE_MODIFIED
```

## Required Review

The implementation review must attack:

```text
1. Is authority separated from signature and identity verification?
2. Is missing policy root NOT_EVALUATED?
3. Is identity absent from a consultable policy INSUFFICIENT?
4. Is explicit deny INSUFFICIENT?
5. Is action-not-allowed INSUFFICIENT?
6. Is only explicit in-scope allow SUFFICIENT?
7. Do revocation unknown/stale/unreachable and clock failure fail closed?
8. Are PT-AUTHORITY assumptions carried, without claiming PT-IDENTITY was verified here?
9. Is there no default allow, fallback policy, implicit admin/owner, or permit-unless-denied path?
10. Does conformance include every required mutation pair?
11. Does the adapter feed the accepted composition oracle rather than bypass it?
12. Are adapter modules, fixtures, reports, and any new dependencies excluded from the public wheel?
13. Are signature adapter, identity adapter, composition core, V1, Domain4, and Phase 1 unchanged?
```

## Status Lock

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_AUTHORIZED
AUTHORITY_ADAPTER_ONLY
SIGNATURE_ADAPTER_BASELINE_COLD_VERIFIED
IDENTITY_ADAPTER_BASELINE_COLD_VERIFIED
AUTHORITY_IS_POLICY_NOT_CRYPTO
AUTHORITY_CONSUMES_ESTABLISHED_IDENTITY
MISSING_POLICY_ROOT_NOT_EVALUATED
POLICY_SOURCE_NOT_EVALUATED_IF_UNREADABLE
IDENTITY_ABSENT_FROM_POLICY_INSUFFICIENT
EXPLICIT_DENY_INSUFFICIENT
ACTION_NOT_ALLOWED_INSUFFICIENT
EXPLICIT_ALLOW_REQUIRED_FOR_SUFFICIENT
DEFAULT_DENY_REQUIRED
NO_DEFAULT_ALLOW
NO_PERMIT_UNLESS_DENIED
NO_IMPLICIT_ADMIN_OR_OWNER
REVOCATION_UNKNOWN_NOT_EVALUATED
CLOCK_FAILURE_NOT_EVALUATED
PT_AUTHORITY_ASSUMPTIONS_REQUIRED
PUBLIC_WHEEL_EXCLUSION_REQUIRED

ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
