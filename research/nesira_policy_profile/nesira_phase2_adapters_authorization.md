# Nesira Phase 2 Adapters Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: SUB_ASSESSMENT_ADAPTERS_AND_CONFORMANCE_ONLY
COMPOSITION_CORE: FROZEN
SUB_ASSESSMENT_ADAPTERS: AUTHORIZED
ADAPTER_CONFORMANCE: AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes the next Phase 2 implementation gate: sub-assessment
adapters and their conformance checks only.

The adapters may classify real-world evidence into already-defined Phase 2
sub-assessment verdicts. They must not execute severance, run isolation, bypass
the Lean composition core, expose public wheel behavior, wire combined verdicts,
or create a public capability claim.

## Authoritative Inputs

The adapter implementation must obey the accepted Phase 2 artifacts:

```text
research/nesira_policy_profile/nesira_phase2_proposal.md
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_sketch.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table_spec.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_report.md
research/nesira_policy_profile/nesira_phase2_lean_composition_results.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
```

If any adapter behavior conflicts with those artifacts, the implementation must
stop with:

```text
SCOPE_REVISION_REQUIRED
```

and must not silently redefine the trust model, ledger, decision table, or
composition core.

## Frozen Surfaces

The following surfaces are frozen for this gate:

```text
Formal Core V1
Domain4 / Nesira Lean core
Nesira Phase 1 validator
Nesira Phase 1 accepted artifacts
Nesira Phase 2 trust model
Nesira Phase 2 trust ledger
Nesira Phase 2 assessment sketch
Nesira Phase 2 assessment decision table and JSON oracle
Nesira Phase 2 Lean composition core and proofs
public wheel contents
combined verdict integration
```

The adapters must feed the accepted composition core. They must not modify it or
replace it.

## Authorized Adapter Scope

The authorized adapters are exactly:

```text
signature
identity
authority
isolation_attestation
```

Each adapter may produce only a Phase 2 sub-assessment verdict:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

Each adapter output must carry:

```text
sub_verdict
declared_root_id
declared_root_version
assumption_ids
not_evaluated_items
blocking_items
evidence_references
reason_codes
```

The output must not contain, imply, or authorize:

```text
execute
sever
permission_to_sever
authorized_to_sever
safe_to_sever
isolation_occurred
isolation_proven
```

## Adapter Contract

Adapters classify world evidence into sub-assessment verdicts:

```text
world evidence + declared root + bounded context -> sub-assessment verdict
```

The proven composition core consumes those sub-verdicts:

```text
four sub-assessment verdicts -> composite assessment
```

Adapters must not bypass the composition core and must not produce the composite
assessment themselves except through the accepted core.

## Crypto Dependency Rule

Cryptographic verification introduces the first Phase 2 supply-chain surface.

The implementation must use a controlled, maintained, version-pinned
cryptographic library. It must not implement signature algorithms, certificate
validation, digest comparison, or attestation signature verification by
hand-rolled cryptography.

Before first use, the implementation report must record:

```text
crypto_library_name
crypto_library_version
pinning_method
dependency_lock_or_hash
used_algorithms
wheel_exclusion_result
assumption_ids_carried
```

The correctness of the library is not proven by SPIRA. It must be carried as
trust assumptions, including:

```text
PT-CRYPTO-01
PT-CRYPTO-02 when signature or attestation verification is used
PT-CRYPTO-03 when key custody is relevant
```

The adapter implementation and the crypto dependency must remain excluded from
the public wheel unless a later authorization explicitly changes that boundary.

## Required Fail-Closed Trust Rules

The implementation must enforce the three Phase 2 trust traps mechanically.

### Revocation

Revocation uncertainty is not evidence of safety.

```text
revoked                     -> TRUST_INSUFFICIENT
revocation_stale            -> not sufficient
revocation_unreachable      -> not sufficient
revocation_unknown          -> not sufficient
revocation_root_missing     -> not sufficient
```

The exact choice between `TRUST_INSUFFICIENT` and `TRUST_NOT_EVALUATED` must
follow the accepted trust model. In every case above, the result must not be
`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`.

Unknown revocation status must carry:

```text
PT-REVOKE-03
```

### Clock

Time is a declared trust assumption, not an ambient fact.

```text
clock_missing
clock_untrusted
clock_out_of_scope
validity_window_uncheckable
freshness_uncheckable
```

must fail closed to a non-sufficient verdict and must carry the applicable
clock assumptions, including:

```text
PT-CLOCK-01
```

### No Default Trust

No adapter may rely on:

```text
default operating-system trust store
default CA store
trust on first use
any valid signature
implicit signing authority
implicit attestation authority
```

Every successful sub-assessment must be tied to a declared trust root:

```text
root_id@version
```

If the declared root is missing, malformed, expired, revoked, stale,
out-of-scope, or not applicable to the evidence class, the result must not be
`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`.

## Isolation Attestation Adapter Boundary

The isolation attestation adapter may verify only an attestation artifact:

```text
well_formed_attestation
signature_against_declared_attestation_root
binding_to_declared_subject_and_context
freshness_against_declared_clock_policy
revocation_status_against_declared_revocation_policy
```

It must not run isolation and must not claim that isolation occurred.

Every isolation-related sub-assessment must carry:

```text
PT-ISOLATION-01
```

The forbidden reading is:

```text
attestation checked -> isolation proven
```

The only permitted reading is:

```text
attestation evidence was assessed against declared roots under explicit assumptions
```

## Conformance Requirements

The adapter conformance corpus must include fixtures and mutation pairs for
each safety-critical failure mode.

Required mutation-pair coverage includes at least:

```text
bad_signature
revoked_root_or_key
expired_root_or_key
unknown_revocation
stale_revocation
missing_declared_root
wrong_declared_root
out_of_scope_root
malformed_signature_payload
malformed_identity_binding
malformed_authority_policy
malformed_attestation
attestation_context_mismatch
attestation_freshness_failure
clock_missing_or_untrusted
```

Acceptance metrics:

```text
safety_critical_failure_modes_without_mutation_pair: 0
unexpected_sufficient_verdicts: 0
adapter_outputs_with_execution_semantics: 0
composition_core_bypasses: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

The end-to-end conformance gate must prove empirically:

```text
adapters -> accepted composition core -> expected composite assessment
```

It must not claim to prove:

```text
cryptographic library correctness
trust-root legitimacy
signer authority as an absolute fact
isolation execution truth
```

Those remain trust assumptions carried by ID.

## Wheel Exclusion Requirement

The adapter implementation location must be chosen only after verifying that
the public wheel exclusion boundary covers it.

If the implementation is placed under a source tree that normally enters the
public wheel, the implementation must include an explicit wheel-exclusion check
before acceptance.

The public wheel must not contain:

```text
Phase 2 adapters
adapter fixtures
adapter reports
cryptographic dependency introduced only for adapters
attestation verifier implementation
```

If any adapter or adapter-only dependency enters the public wheel, the gate
fails.

## Stop Conditions

The implementation must stop if any of the following is observed:

```text
HAND_ROLLED_CRYPTO_DETECTED
CRYPTO_DEPENDENCY_NOT_PINNED
REVOCATION_UNKNOWN_SOFT_PASS
CLOCK_FAILURE_SOFT_PASS
DEFAULT_TRUST_STORE_USED
TRUST_ON_FIRST_USE_USED
ANY_VALID_SIGNATURE_ACCEPTED
ADAPTER_EMITS_EXECUTION
ATTESTATION_CHECK_COLLAPSES_TO_ISOLATION_PROOF
COMPOSITION_CORE_BYPASSED
ADAPTER_OR_CRYPTO_DEPENDENCY_ENTERED_PUBLIC_WHEEL
FROZEN_SURFACE_MODIFIED_WITHOUT_AUTHORIZATION
```

Any stop condition yields:

```text
NESIRA_PHASE2_ADAPTERS_NEEDS_REVISION
```

or, for an unsafe soft-pass:

```text
NESIRA_PHASE2_ADAPTERS_REJECTED_UNSAFE_TRUST_PATH
```

## Required Review

The implementation must receive adversarial review before it may be accepted.

The review must attack at least:

```text
1. Is crypto provided by a controlled, pinned library rather than hand-rolled code?
2. Is crypto-library correctness carried as PT-CRYPTO assumptions?
3. Does unknown revocation always block sufficiency?
4. Does missing or untrusted clock state always block sufficiency?
5. Is every sufficient result tied to an explicit declared root_id@version?
6. Is there no default CA store, default trust store, TOFU, or any-valid-signature path?
7. Do adapters emit only sub-verdicts and never execution or severance semantics?
8. Does the isolation adapter check attestation only and carry PT-ISOLATION-01?
9. Does the conformance corpus contain mutation pairs for every safety-critical failure?
10. Does end-to-end conformance feed the accepted composition core rather than bypass it?
11. Are adapter modules, fixtures, reports, and adapter-only crypto dependencies excluded from the public wheel?
12. Are combined verdict wiring, CLI exposure, public claims, and release still absent?
```

## Authorized Next Gate

The next gate may implement:

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
adapter conformance corpus
adapter conformance runner
adapter implementation report
adapter implementation review
```

Only within the boundaries above.

## Status Lock

```text
NESIRA_PHASE2_ADAPTERS_AUTHORIZED
SUB_ASSESSMENT_ADAPTERS_AND_CONFORMANCE_ONLY
CRYPTO_DEPENDENCY_GOVERNANCE_REQUIRED
NO_HAND_ROLLED_CRYPTO
NO_DEFAULT_TRUST
REVOCATION_UNKNOWN_NOT_SUFFICIENT
CLOCK_TRUST_ASSUMPTION_ENFORCED
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN
PT_ISOLATION_01_MANDATORY
WHEEL_EXCLUSION_REQUIRED
COMPOSITION_CORE_FROZEN
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
