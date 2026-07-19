# Nesira Phase 2 Isolation Attestation Adapter Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: ISOLATION_ATTESTATION_ADAPTER_PLAN_AND_IMPLEMENTATION_GATE
SCOPE: ISOLATION_ATTESTATION_ADAPTER_ONLY
SIGNATURE_ADAPTER_BASELINE: COLD_VERIFIED
IDENTITY_ADAPTER_BASELINE: COLD_VERIFIED
AUTHORITY_ADAPTER_BASELINE: COLD_VERIFIED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes the next narrow Phase 2 adapter gate: isolation
attestation checking only.

The central rule of this gate is:

```text
attestation checked != isolation proven
```

The adapter may evaluate whether an isolation attestation is authentic under a
declared `ATTESTATION_AUTHORITY` root and whether the attestation claims bind
the expected candidate/environment/isolation profile supplied by the caller's
external assessment context.

It must not run isolation, observe isolation, inspect a live process, inspect a
filesystem sandbox, inspect network isolation, perform severance, wire combined
verdict integration, expose a CLI, enter the public wheel, make public claims,
or release.

## Preconditions

The following baselines are required and accepted:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

Recorded in:

```text
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_authority_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_authority_adapter_cold_verification_results.json
```

The signature, identity, authority, and composition-core baselines are treated
as frozen for this gate. Isolation attestation work must not modify them except
through a separate remediation authorization.

## Authoritative Inputs

The isolation attestation adapter must obey:

```text
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_authority_adapter_cold_verification_review.md
```

Any conflict is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be resolved by silently changing the trust model, ledger,
composition core, previous adapters, or V1 artifacts.

## Authorized Adapter Scope

The isolation attestation adapter may produce only a Phase 2 sub-assessment
verdict:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

It may evaluate:

```text
declared ATTESTATION_AUTHORITY root shape
attestation availability and parseability
attestation root identity/version/scope
attestation signature authenticity against the declared authority
attestation validity window
revocation/freshness status for the attestation authority or attestation
binding of attested claims to expected candidate/environment/isolation profile
```

It must not evaluate:

```text
actual isolation execution
runtime isolation observation
filesystem isolation truth
network isolation truth
process isolation truth
permission to sever
operational severance
```

The adapter checks an attestation object. It does not prove that isolation
occurred.

The expected candidate, environment, and isolation profile must come from the
caller-supplied assessment context. They must not be learned from the
attestation being checked. Otherwise the binding check is circular and must
stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Semantics

Accepted reading:

```text
The attestation was checked against the declared ATTESTATION_AUTHORITY and
claims the expected isolation properties under declared roots and assumptions.
```

Forbidden readings:

```text
isolation occurred
isolation happened
isolation was confirmed
isolation was proven
the runtime was observed to be isolated
the filesystem was observed to be isolated
the network was observed to be isolated
the process was observed to be isolated
the system may sever
the system may execute severance
```

Attestation verification is not isolation execution.

## Crypto Dependency Rule

The adapter may reuse the accepted gated Phase 2 crypto dependency:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
cryptography==49.0.0
--require-hashes
```

No new dependency is authorized by this gate.

`pyproject.toml` must remain unchanged:

```text
dependencies = []
```

The implementation must not hand-roll signature primitives, hash primitives, or
attestation signature verification. If the existing `cryptography` boundary is
insufficient, stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Sub-Verdict Mapping

Required mapping:

```text
authentic attestation
+ declared ATTESTATION_AUTHORITY root matches
+ expected candidate/environment/isolation profile is claimed by the attestation
+ attestation not expired
+ attestation authority/root not revoked
+ revocation confirmed fresh
+ clock available and declared
  -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

missing attestation authority root
  -> TRUST_NOT_EVALUATED

ambiguous attestation authority root
  -> TRUST_NOT_EVALUATED

malformed attestation authority root
  -> TRUST_NOT_EVALUATED

attestation missing, unreadable, malformed, unsupported, or unparseable
  -> TRUST_NOT_EVALUATED

bad attestation signature
  -> TRUST_INSUFFICIENT

known but undeclared attestation authority
  -> TRUST_INSUFFICIENT

attestation root id/version mismatch
  -> TRUST_INSUFFICIENT

attestation binds wrong candidate/environment/isolation profile
  -> TRUST_INSUFFICIENT

attestation expired or not yet valid
  -> TRUST_INSUFFICIENT

attestation authority/root revoked
  -> TRUST_INSUFFICIENT

revocation unknown, stale, unreachable, missing, or inconclusive
  -> TRUST_NOT_EVALUATED

clock missing or untrusted
  -> TRUST_NOT_EVALUATED
```

The most important non-confusion rule is:

```text
attestation verified against a declared authority -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
attestation claims do not bind expected profile -> TRUST_INSUFFICIENT
missing declared attestation root -> TRUST_NOT_EVALUATED
verified attestation -> not a claim that isolation occurred
```

Clock failure has precedence over temporal expiry:

```text
clock missing or untrusted + attestation expired/not-yet-valid
  -> TRUST_NOT_EVALUATED
```

Expiry and not-yet-valid classifications require a trusted clock. If the clock
cannot be evaluated, the adapter must not infer temporal invalidity.

## Isolation Caveat Carrying

Every isolation sub-verdict must carry:

```text
PT-ISOLATION-01
```

including:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

`PT-ISOLATION-01` is mandatory because isolation execution truth is delegated to
the attestation authority. SPIRA does not verify that isolation occurred.

Every output must also carry the unconditional floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

A sufficient isolation-attestation output carries the applicable declared-root
and revocation assumptions, plus `PT-ISOLATION-01`.

Unknown revocation carries:

```text
PT-REVOKE-03
```

## Reason-Code Language Rule

Reason codes, reports, and test expected values must use an allowlist for
isolation-language. Any token matching:

```text
isolat*
sandbox*
contain*
```

is forbidden unless it appears inside one of the explicitly allowed phrases
below. This is an allowlist, not a blocklist.

Allowed phrases:

```text
ATTESTATION_VERIFIED_AGAINST_DECLARED_AUTHORITY
ATTESTATION_CLAIMS_BOUND_EXPECTED_PROFILE
ATTESTATION_SIGNATURE_INVALID
ATTESTATION_CLAIMS_MISMATCH
ATTESTATION_AUTHORITY_NOT_EVALUATED
attestation checked != isolation proven
isolation attestation
isolation profile
isolation profile claim
isolation profile claims
isolation profile id
isolation profile version
expected isolation profile
PT-ISOLATION-01
isolation caveat
isolation sub-verdict
```

Forbidden phrases include, but are not limited to:

```text
ISOLATION_OCCURRED
ISOLATION_HAPPENED
ISOLATION_CONFIRMED
ISOLATION_PROVEN
ISOLATION_EXECUTED
ISOLATION_VERIFIED
ISOLATION_ESTABLISHED
ISOLATION_GUARANTEED
ISOLATION_ENSURED
ISOLATION_ENFORCED
SANDBOXED
CONTAINED
RAN_IN_ISOLATION
WAS_ISOLATED
RUNTIME_ISOLATED
FILESYSTEM_ISOLATED
NETWORK_ISOLATED
PROCESS_ISOLATED
```

If implementation cannot keep this language separation mechanically, stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Conformance Requirements

The implementation gate must include deterministic fixtures and mutation pairs
for at least:

```text
valid_attestation_under_declared_authority
missing_attestation_authority_root
ambiguous_attestation_authority_root
malformed_attestation_authority_root
attestation_missing
attestation_malformed
unsupported_attestation_type
bad_attestation_signature
known_undeclared_attestation_authority
attestation_root_mismatch
candidate_claim_mismatch
environment_claim_mismatch
isolation_profile_claim_mismatch
attestation_expired
attestation_not_yet_valid
attestation_authority_revoked
revocation_unknown
revocation_stale
revocation_unreachable
clock_missing
clock_untrusted
```

Required metrics:

```text
required_isolation_failure_modes_without_fixture: 0
required_isolation_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
missing_root_mapped_to_insufficient: 0
known_undeclared_authority_mapped_to_not_evaluated: 0
claims_mismatch_mapped_to_not_evaluated: 0
clock_failure_mapped_to_temporal_invalid: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
outputs_without_pt_isolation_01: 0
outputs_with_execution_semantics: 0
outputs_with_isolation_truth_semantics: 0
forbidden_isolation_language_hits: 0
non_allowlisted_isolation_language_hits: 0
composition_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## Composition Wiring

The harness must check end-to-end wiring through the accepted composition
oracle:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
authority_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation_sub = adapter output
```

Expected:

```text
isolation sufficient -> composite TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation not evaluated -> composite TRUST_NOT_EVALUATED
isolation insufficient -> composite TRUST_INSUFFICIENT
```

The harness must also verify that composite sufficiency still carries the
isolation caveat:

```text
PT-ISOLATION-01
```

## Stop Conditions

Stop if implementation requires or emits:

```text
isolation occurred
isolation happened
isolation confirmed
isolation proven
isolation verified
isolation established
isolation guaranteed
isolation ensured
isolation enforced
ran in isolation
was isolated
sandboxed
contained
runtime observation
filesystem observation
network observation
process observation
isolation runner
execution/severance output
permission to sever
combined verdict wiring
new dependency
pyproject change
lakefile change
V1 artifact change
```

Stop if the attestation format cannot separate:

```text
authentic claim by declared authority
```

from:

```text
truth of isolation execution
```

## Cold Verification Requirement

After local acceptance, a separate cold verification must reproduce the result
from a fresh clone before any CLI, combined verdict, public wheel exposure,
public claim, release, or isolation-runner work is considered.

## Status Lock

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_AUTHORIZATION_ACCEPTED
ISOLATION_ATTESTATION_ADAPTER_ONLY
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN_ACCEPTED
PT_ISOLATION_01_ALWAYS_CARRIED_REQUIRED
ISOLATION_RUNNER_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
