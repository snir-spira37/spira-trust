# Nesira Phase 2 Signature Adapter Review

## Verdict

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED_PENDING_COLD_VERIFICATION
```

This review accepts the local signature adapter implementation and requires cold
verification before opening the next adapter.

It does not authorize identity, authority, isolation-attestation, isolation
runner, CLI, combined verdict wiring, public wheel exposure, public claims, or
release.

## Review Summary

The implementation correctly keeps the gate narrow:

```text
signature evidence + declared SIGNING_KEY root -> signature sub-assessment
```

It feeds the accepted Phase 2 composition oracle for wiring checks and does not
emit execution or severance semantics.

## Checks

### 1. Crypto Dependency

Result: PASS

The implementation uses `pyca/cryptography` and verifies the runtime version:

```text
cryptography==49.0.0
```

The dependency is hash-pinned in:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

The adapter uses `cryptography` verification APIs. No hand-rolled signature
primitive was introduced.

### 2. Product Dependency Boundary

Result: PASS

The product dependency list remains:

```text
dependencies = []
```

No pyproject optional extra was added in this gate because `pyproject.toml` is
covered by the V1 external reproduction source manifest. The hash-pinned
requirements file carries the adapter/conformance pin without mutating the
product dependency surface.

### 3. Sub-Verdict Mapping

Result: PASS

Observed mapping matches the plan:

```text
bad signature -> TRUST_INSUFFICIENT
wrong declared root -> TRUST_INSUFFICIENT
missing declared root -> TRUST_NOT_EVALUATED
expired root -> TRUST_INSUFFICIENT
revoked root -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
malformed payload/signature -> TRUST_NOT_EVALUATED
scope mismatch -> TRUST_INSUFFICIENT
```

The critical distinction passed:

```text
missing_root_mapped_to_insufficient: 0
wrong_root_mapped_to_not_evaluated: 0
```

### 4. Three Trust Traps

Result: PASS

The conformance metrics show:

```text
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
```

No default trust, TOFU, or any-valid-signature path was accepted.

### 5. Assumption Carrying

Result: PASS

Sufficient signature results carry the required crypto, key-legitimacy,
revocation, clock, and floor assumptions.

Unknown revocation carries:

```text
PT-REVOKE-03
```

### 6. Conformance Corpus

Result: PASS

The harness covers 19 fixtures:

```text
1 positive fixture
18 safety-critical mutation/failure fixtures
```

Metrics:

```text
required_signature_failure_modes_without_fixture: 0
required_signature_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
```

### 7. Composition Wiring

Result: PASS

The signature sub-verdict is fed into the accepted composition oracle with the
three unimplemented adapters set to `TRUST_NOT_EVALUATED`.

Observed:

```text
signature sufficient -> composite TRUST_NOT_EVALUATED
signature not evaluated -> composite TRUST_NOT_EVALUATED
signature insufficient -> composite TRUST_INSUFFICIENT
composition_mismatches: 0
```

### 8. Execution Boundary

Result: PASS

Adapter outputs contain no execution or severance fields:

```text
adapter_outputs_with_execution_semantics: 0
execution_marker: ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

### 9. Wheel Exclusion

Result: PASS

The public wheel does not contain the signature adapter, signature harness,
signature fixtures/reports, or `cryptography` dependency metadata.

```text
wheel_exclusion_failures: 0
metadata_mentions_cryptography: false
```

### 10. Regression Gates

Result: PASS

Executed:

```text
signature adapter focused tests: 9 passed
full pytest: 295 passed
compileall: PASS
pip check: PASS
git diff --check: PASS
Formal Core V1 SHA256SUMS self-check: 0 failures
```

## Boundary Note

The original implementation plan requested a pyproject optional extra as a
possible pin carrier. This review accepts the implemented alternative:

```text
hash-pinned requirements file
```

and does not accept pyproject mutation in this gate.

Reason: pyproject is part of the existing Formal Core V1 external reproduction
source manifest. Mutating it from a Phase 2 adapter gate would reopen a V1
boundary without a separate authorization.

## Residual Risk

The requirements file is specific to the current Windows CPython environment:

```text
win_amd64 / cp312
```

Other platforms must fail closed unless their exact wheels and hashes are added
by a later authorization.

Cold verification is still required from a fresh clone before opening the
identity adapter.

## Required Next Gate

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_REQUIRED
```

## Status

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED_PENDING_COLD_VERIFICATION
SIGNATURE_ADAPTER_ONLY_ACCEPTED
CRYPTOGRAPHY_49_0_0_PIN_ACCEPTED
HASH_PINNED_REQUIREMENTS_ACCEPTED
PROJECT_DEPENDENCIES_REMAIN_EMPTY_ACCEPTED
PYPROJECT_OPTIONAL_EXTRA_NOT_ADDED_V1_BOUNDARY_PRESERVED
NO_HAND_ROLLED_CRYPTO_ACCEPTED
MISSING_ROOT_NOT_EVALUATED_ACCEPTED
WRONG_ROOT_INSUFFICIENT_ACCEPTED
REVOCATION_UNKNOWN_NOT_EVALUATED_ACCEPTED
CLOCK_FAILURE_NOT_EVALUATED_ACCEPTED
NO_DEFAULT_TRUST_ACCEPTED
NO_TOFU_ACCEPTED
NO_ANY_VALID_SIGNATURE_ACCEPTED
ADAPTER_FEEDS_COMPOSITION_CORE_ACCEPTED
PUBLIC_WHEEL_EXCLUSION_ACCEPTED
IDENTITY_ADAPTER_NOT_AUTHORIZED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
