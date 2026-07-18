# Nesira Phase 2 Signature Adapter Implementation Plan Review

## Verdict

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
```

This review accepts the signature-only implementation plan as the next narrow
Phase 2 adapter gate.

It does not authorize identity, authority, isolation-attestation, isolation
runner, CLI, combined verdict wiring, public wheel exposure, public claims, or
release.

## Review Summary

The plan correctly makes the first adapter step small:

```text
declared SIGNING_KEY root + signature evidence -> signature sub-verdict
```

It preserves the accepted Phase 2 structure:

```text
adapter classifies world evidence
composition core combines sub-verdicts
SPIRA emits assessment only
```

The plan also separates the two most error-prone outcomes:

```text
TRUST_INSUFFICIENT = checked and failed
TRUST_NOT_EVALUATED = could not be checked under declared roots/context
```

## Checks

### 1. Scope Is Signature-Only

Result: PASS

The plan opens only the signature adapter and its conformance corpus.

It keeps blocked:

```text
identity adapter
authority adapter
isolation attestation adapter
isolation runner
CLI
combined verdict
public wheel exposure
public claim
release
```

### 2. Sub-Verdict Mapping

Result: PASS

The plan preserves the required distinction:

```text
invalid signature -> TRUST_INSUFFICIENT
wrong declared root -> TRUST_INSUFFICIENT
missing declared root -> TRUST_NOT_EVALUATED
revocation unknown -> TRUST_NOT_EVALUATED
clock missing or untrusted -> TRUST_NOT_EVALUATED
```

This matches the trust-model boundary: active failure is insufficient; inability
to evaluate under declared roots is not evaluated. Both remain fail-closed.

### 3. Missing Root vs Wrong Root

Result: PASS

The plan explicitly locks:

```text
missing root -> TRUST_NOT_EVALUATED
wrong root   -> TRUST_INSUFFICIENT
```

This prevents the easiest classification collapse in the signature adapter.

### 4. Crypto Dependency Strategy

Result: PASS

The plan selects `pyca/cryptography` as the controlled crypto dependency and
requires an exact pin before implementation acceptance.

It also keeps:

```text
dependencies = []
```

for the product project dependency list.

The dependency remains adapter/conformance-gated and must not enter the public
wheel.

### 5. No Hand-Rolled Crypto

Result: PASS

The plan forbids custom cryptographic primitives and requires use of
`cryptography` verification APIs.

The allowed custom code is limited to validation, declared-root lookup,
bounded-context checks, API calls, and verdict mapping.

### 6. Assumption Carrying

Result: PASS

The plan requires sufficient signature results to carry:

```text
PT-CRYPTO-01
PT-CRYPTO-02
PT-CRYPTO-03
PT-KEYLEGIT-01
PT-KEYLEGIT-02
PT-REVOKE-01
PT-REVOKE-02
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

It also requires unknown revocation to carry:

```text
PT-REVOKE-03
```

### 7. Three Trust Traps

Result: PASS

The plan mechanically enforces:

```text
revocation_unknown -> not sufficient
clock_missing_or_untrusted -> not sufficient
no_declared_root -> not sufficient
```

It blocks default trust, TOFU, and any-valid-signature acceptance.

### 8. Composition Wiring

Result: PASS

The plan requires end-to-end checks through the accepted composition core with
the unimplemented adapters set to `TRUST_NOT_EVALUATED`.

Expected results are correctly fail-closed:

```text
signature sufficient -> composite TRUST_NOT_EVALUATED
signature not evaluated -> composite TRUST_NOT_EVALUATED
signature insufficient -> composite TRUST_INSUFFICIENT
```

### 9. Conformance Coverage

Result: PASS

The plan requires fixtures and mutation pairs for bad signatures, wrong roots,
missing roots, malformed roots, expiry, revocation, revocation unknown/stale/
unreachable, clock failures, malformed payloads, malformed signatures, and
scope mismatches.

The metrics are binary and include explicit guards for the common classification
mistakes.

### 10. Wheel Boundary

Result: PASS

The plan requires proof that the signature adapter, fixtures, reports, and
`cryptography` dependency remain out of the public wheel and out of product
dependencies.

## Residual Risks

The exact `cryptography` version is not pinned in this plan. That must be done
in the implementation report before acceptance.

The plan does not implement or evaluate:

```text
identity chain verification
authority policy lookup
isolation attestation verification
isolation execution
```

Those remain separate gates.

## Required Next Gate

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTATION_AUTHORIZED
```

The next gate may implement the signature adapter only, under this plan and the
Phase 2 adapter authorization.

## Status

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
SIGNATURE_ADAPTER_ONLY_ACCEPTED
SUB_VERDICT_MAPPING_ACCEPTED
MISSING_ROOT_NOT_EVALUATED_ACCEPTED
WRONG_ROOT_INSUFFICIENT_ACCEPTED
CRYPTOGRAPHY_SELECTED_PENDING_EXACT_PIN
PROJECT_DEPENDENCIES_REMAIN_EMPTY_ACCEPTED
PUBLIC_WHEEL_EXCLUSION_REQUIRED_ACCEPTED
NO_HAND_ROLLED_CRYPTO_ACCEPTED
REVOCATION_UNKNOWN_NOT_EVALUATED_ACCEPTED
CLOCK_FAILURE_NOT_EVALUATED_ACCEPTED
NO_DEFAULT_TRUST_ACCEPTED
NO_TOFU_ACCEPTED
NO_ANY_VALID_SIGNATURE_ACCEPTED
ADAPTER_FEEDS_COMPOSITION_CORE_ACCEPTED
IDENTITY_ADAPTER_NOT_AUTHORIZED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
