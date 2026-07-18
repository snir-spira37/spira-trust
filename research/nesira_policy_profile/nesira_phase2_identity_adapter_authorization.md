# Nesira Phase 2 Identity Adapter Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: IDENTITY_ADAPTER_PLAN_AND_IMPLEMENTATION_GATE
SCOPE: IDENTITY_ADAPTER_ONLY
SIGNATURE_ADAPTER_BASELINE: COLD_VERIFIED
AUTHORITY_ADAPTER: NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER: NOT_AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes the next narrow Phase 2 adapter gate: signer identity
binding only.

The identity adapter may evaluate whether a credential or certificate binds a
signing key / signing root to a signer identity within a declared identity
namespace and context.

It must not evaluate signer authority, isolation attestation, isolation
execution, operational severance, CLI behavior, combined verdict integration,
public wheel exposure, public claims, or release.

## Preconditions

The following baseline is required and accepted:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

Recorded in:

```text
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_results.json
```

The signature adapter is treated as frozen for this gate. Identity work must not
modify it except through a separate remediation authorization.

## Authoritative Inputs

The identity adapter must obey:

```text
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_review.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
```

Any conflict is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be resolved by silently changing the trust model, ledger,
composition core, signature adapter, or V1 artifacts.

## Authorized Adapter Scope

The identity adapter may produce only a Phase 2 sub-assessment verdict:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

It may evaluate:

```text
credential or certificate well-formedness
issuer chain against declared IDENTITY_BINDING_CA root
credential signature verification through pinned cryptography
credential-to-key binding
credential-to-signer-identity binding
identity namespace match
subject / environment / purpose context binding
validity window
revocation status and freshness
```

It must not evaluate:

```text
whether the signer has authority for the requested action
whether severance is permitted
whether isolation occurred
whether an attestation is true
whether an external CA/root is legitimate beyond its declared root record
```

## Identity Boundary

The accepted reading of a sufficient identity sub-assessment is:

```text
the credential evidence binds the signing key/root to the declared signer
identity under the declared identity root and explicit assumptions
```

The forbidden reading is:

```text
the signer is authorized
the signer may approve severance
the identity issuer is proven honest
the identity registry is proven correct
```

Identity is not authority.

## Crypto Dependency Rule

The identity adapter may use the existing Phase 2 adapter crypto dependency:

```text
cryptography==49.0.0
```

and only through the existing hash-pinned requirements file:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

The product dependency list must remain:

```text
dependencies = []
```

No pyproject optional extra is authorized in this gate.

If additional platform wheels, dependency hashes, or a new crypto dependency are
needed, this authorization is insufficient and a supply-chain boundary review is
required.

The adapter must not implement X.509 path validation, certificate signature
math, chain walking, or issuer policy logic by hand. Certificate path validation
must use the pinned `cryptography` X.509 verification APIs, anchored only in the
declared `IDENTITY_BINDING_CA` root. The operating-system trust store, browser
trust store, and any implicit CA bundle remain forbidden.

## Sub-Verdict Mapping

The core distinction remains:

```text
TRUST_INSUFFICIENT:
  the identity check was performed and failed

TRUST_NOT_EVALUATED:
  the identity check could not be performed under the declared roots/context
```

Required mapping:

```text
valid identity credential
+ declared IDENTITY_BINDING_CA root matches
+ credential binds expected signing key/root to expected signer identity
+ namespace and context match
+ credential/root/intermediates not expired
+ credential/root/intermediates not revoked
+ revocation confirmed fresh
+ clock available and declared
  -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

missing identity root
  -> TRUST_NOT_EVALUATED

ambiguous identity root
  -> TRUST_NOT_EVALUATED

malformed identity root
  -> TRUST_NOT_EVALUATED

unsupported credential type
  -> TRUST_NOT_EVALUATED

malformed credential or certificate before verification can be attempted
  -> TRUST_NOT_EVALUATED

credential signature invalid
  -> TRUST_INSUFFICIENT

certificate / credential chain builds to a known issuer/root that is not the
declared identity root, or is rejected by the declared root/policy
  -> TRUST_INSUFFICIENT

credential issued by a root or issuer that does not match the declared root
  -> TRUST_INSUFFICIENT

untrusted issuer under the declared root
  -> TRUST_INSUFFICIENT

certificate / credential chain cannot be built because required intermediate,
anchor, or chain evidence is missing
  -> TRUST_NOT_EVALUATED

expired credential, intermediate, or root
  -> TRUST_INSUFFICIENT

revoked credential, intermediate, or root
  -> TRUST_INSUFFICIENT

revocation unknown, stale, unreachable, missing, or inconclusive
  -> TRUST_NOT_EVALUATED

clock missing or untrusted
  -> TRUST_NOT_EVALUATED

identity namespace mismatch
  -> TRUST_INSUFFICIENT

expected signer identity mismatch
  -> TRUST_INSUFFICIENT

signing key/root binding mismatch
  -> TRUST_INSUFFICIENT

subject/environment/purpose context mismatch
  -> TRUST_INSUFFICIENT
```

The most important non-confusion rule is:

```text
missing identity root -> TRUST_NOT_EVALUATED
wrong identity root   -> TRUST_INSUFFICIENT
unbuildable chain due to missing evidence -> TRUST_NOT_EVALUATED
known but undeclared/untrusted issuer     -> TRUST_INSUFFICIENT
```

## Assumption Carrying

Every output must carry the unconditional floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

A sufficient identity sub-assessment must also carry:

```text
PT-CRYPTO-02
PT-IDENTITY-01
PT-IDENTITY-02
PT-REVOKE-01
PT-REVOKE-02
PT-META-03 when a chain is evaluated
```

Unknown or inconclusive revocation must carry:

```text
PT-REVOKE-03
```

If a specific clock root is used, the result must also carry:

```text
PT-CLOCK-02
```

The adapter must not carry authority assumptions:

```text
PT-AUTHORITY-*
```

unless a later authority adapter gate explicitly authorizes that domain.

## No Default Trust

The adapter must not use:

```text
default operating-system trust store
default CA store
browser trust store
trust on first use
any valid certificate
any valid credential
implicit identity issuer
implicit namespace
```

Every sufficient identity result must be tied to:

```text
declared IDENTITY_BINDING_CA root_id@version
declared identity namespace
declared credential type
declared bounded context
```

## Required Conformance

The implementation must include fixtures and mutation pairs for:

```text
valid_identity_binding
missing_identity_root
ambiguous_identity_root
malformed_identity_root
unsupported_credential_type
malformed_credential
bad_credential_signature
chain_unbuildable_missing_intermediate
known_but_undeclared_issuer
wrong_declared_identity_root
untrusted_issuer
expired_credential
expired_intermediate
expired_identity_root
revoked_credential
revoked_intermediate
revoked_identity_root
revocation_unknown
revocation_stale
revocation_unreachable
clock_missing
clock_untrusted
namespace_mismatch
signer_identity_mismatch
signing_key_binding_mismatch
subject_context_mismatch
environment_context_mismatch
purpose_context_mismatch
```

Required metrics:

```text
required_identity_failure_modes_without_fixture: 0
required_identity_failure_modes_without_mutation_pair: 0
unexpected_sufficient_verdicts: 0
missing_root_mapped_to_insufficient: 0
wrong_root_mapped_to_not_evaluated: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
chain_unbuildable_mapped_to_insufficient: 0
known_untrusted_issuer_mapped_to_not_evaluated: 0
identity_outputs_with_authority_semantics: 0
identity_outputs_with_execution_semantics: 0
composition_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## End-to-End Composition Check

The implementation must feed identity sub-verdicts into the accepted Phase 2
composition oracle.

For the identity-only gate, the expected setup is:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = adapter output
authority_sub = TRUST_NOT_EVALUATED
isolation_sub = TRUST_NOT_EVALUATED
```

Expected composite results:

```text
identity sufficient    -> composite TRUST_NOT_EVALUATED
identity not evaluated -> composite TRUST_NOT_EVALUATED
identity insufficient  -> composite TRUST_INSUFFICIENT
```

This verifies wiring only. It does not claim full Phase 2 sufficiency.

## Stop Conditions

The implementation must stop on:

```text
HAND_ROLLED_CRYPTO_DETECTED
CRYPTOGRAPHY_NOT_PINNED
CRYPTOGRAPHY_ADDED_TO_PRODUCT_DEPENDENCIES
CRYPTOGRAPHY_ADDED_TO_PUBLIC_WHEEL
DEFAULT_CA_STORE_USED
BROWSER_TRUST_STORE_USED
TOFU_USED
ANY_VALID_CERTIFICATE_ACCEPTED
ANY_VALID_CREDENTIAL_ACCEPTED
HAND_ROLLED_X509_CHAIN_VALIDATION_DETECTED
REVOCATION_UNKNOWN_SOFT_PASS
CLOCK_FAILURE_SOFT_PASS
MISSING_ROOT_WRONGLY_MARKED_INSUFFICIENT
WRONG_ROOT_WRONGLY_MARKED_NOT_EVALUATED
CHAIN_UNBUILDABLE_WRONGLY_MARKED_INSUFFICIENT
KNOWN_UNTRUSTED_ISSUER_WRONGLY_MARKED_NOT_EVALUATED
IDENTITY_ADAPTER_EMITS_AUTHORITY
IDENTITY_ADAPTER_EMITS_EXECUTION
COMPOSITION_CORE_BYPASSED
SIGNATURE_ADAPTER_MODIFIED_WITHOUT_AUTHORIZATION
FROZEN_SURFACE_MODIFIED
```

## Required Review

The implementation review must attack:

```text
1. Is identity separated from authority?
2. Is missing identity root NOT_EVALUATED and wrong identity root INSUFFICIENT?
3. Is an unbuildable chain due to missing evidence NOT_EVALUATED?
4. Are known-but-undeclared or untrusted issuers INSUFFICIENT?
5. Are invalid credential signatures and binding mismatches INSUFFICIENT?
6. Are malformed/unparseable credentials and unsupported credential types NOT_EVALUATED?
7. Do revocation unknown/stale/unreachable and clock failure fail closed?
8. Is there no hand-rolled X.509 chain validation?
9. Is there no default CA store, browser trust store, TOFU, or any-valid-certificate path?
10. Are PT-IDENTITY assumptions carried, and are PT-AUTHORITY assumptions absent?
11. Is cryptography pinned through the existing hash-locked adapter requirements?
12. Does the adapter feed the accepted composition oracle rather than bypass it?
13. Are adapter modules, fixtures, reports, and crypto dependency excluded from the public wheel?
14. Are signature adapter, composition core, V1, Domain4, and Phase 1 unchanged?
```

## Status Lock

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_AUTHORIZED
IDENTITY_ADAPTER_ONLY
SIGNATURE_ADAPTER_BASELINE_COLD_VERIFIED
IDENTITY_IS_NOT_AUTHORITY
MISSING_IDENTITY_ROOT_NOT_EVALUATED
WRONG_IDENTITY_ROOT_INSUFFICIENT
CHAIN_UNBUILDABLE_NOT_EVALUATED
KNOWN_UNTRUSTED_ISSUER_INSUFFICIENT
UNTRUSTED_ISSUER_INSUFFICIENT
BINDING_MISMATCH_INSUFFICIENT
MALFORMED_CREDENTIAL_NOT_EVALUATED
REVOCATION_UNKNOWN_NOT_EVALUATED
CLOCK_FAILURE_NOT_EVALUATED
NO_DEFAULT_CA_STORE
NO_BROWSER_TRUST_STORE
NO_TOFU
NO_ANY_VALID_CERTIFICATE
NO_HAND_ROLLED_X509_CHAIN_VALIDATION
PT_IDENTITY_ASSUMPTIONS_REQUIRED
PT_AUTHORITY_ASSUMPTIONS_NOT_AUTHORIZED
PUBLIC_WHEEL_EXCLUSION_REQUIRED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
