# Nesira Phase 2 Identity Adapter Implementation Plan

## Status

```text
DOCUMENT_TYPE: IMPLEMENTATION_PLAN
PHASE: PHASE_2
SCOPE: IDENTITY_ADAPTER_ONLY
IMPLEMENTATION: NOT_STARTED
SIGNATURE_ADAPTER: FROZEN_BASELINE
AUTHORITY_ADAPTER: NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER: NOT_AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This plan prepares implementation of the identity adapter only.

The adapter will classify credential or certificate evidence that binds a
signing key/root to a signer identity under a declared `IDENTITY_BINDING_CA`
root. It will not decide whether the signer has authority.

## Implementation Shape

The implementation should mirror the accepted signature adapter shape:

```text
source/spira_core/nesira_phase2_identity_adapter.py
source/spira_core/nesira_phase2_identity_harness.py
tools/run_nesira_phase2_identity_adapter_conformance.py
tests/test_nesira_phase2_identity_adapter.py
research/nesira_policy_profile/nesira_phase2_identity_adapter_results.json
research/nesira_policy_profile/nesira_phase2_identity_adapter_report.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_review.md
```

The public wheel builder is allowlist-based. The new adapter and harness must
not be added to the allowlist.

## Credential Model For This Gate

This gate should use a deliberately small identity credential model:

```text
issuer root id/version
issuer public key or certificate
credential type
identity namespace
signer identity
bound signing key id or signing root id
subject/environment/purpose context
valid_from / valid_until
revocation status / freshness
credential signature
```

The implementation may use `cryptography` for certificate and signature
verification, but it must not use default platform trust. All issuer and chain
trust must come from the declared identity root.

Do not implement X.509 chain walking, certificate signature math, or issuer
policy logic by hand. Use the pinned `cryptography` X.509 verification APIs for
certificate path validation, with a store rooted only in the declared
`IDENTITY_BINDING_CA` material.

## Crypto Pin

Use the existing adapter/conformance crypto pin:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
cryptography==49.0.0
```

Do not modify:

```text
pyproject.toml
```

The product dependency list must remain:

```text
dependencies = []
```

## Sub-Verdict Mapping

The implementation must use this mapping:

```text
valid credential under declared identity root -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
missing identity root -> TRUST_NOT_EVALUATED
ambiguous identity root -> TRUST_NOT_EVALUATED
malformed identity root -> TRUST_NOT_EVALUATED
unsupported credential type -> TRUST_NOT_EVALUATED
malformed credential before verification -> TRUST_NOT_EVALUATED
invalid credential signature -> TRUST_INSUFFICIENT
certificate / credential chain cannot be built because required evidence is missing -> TRUST_NOT_EVALUATED
chain builds to known but undeclared/untrusted issuer or root -> TRUST_INSUFFICIENT
wrong declared identity root -> TRUST_INSUFFICIENT
untrusted issuer under declared root -> TRUST_INSUFFICIENT
expired credential/intermediate/root -> TRUST_INSUFFICIENT
revoked credential/intermediate/root -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
identity namespace mismatch -> TRUST_INSUFFICIENT
signer identity mismatch -> TRUST_INSUFFICIENT
signing key/root binding mismatch -> TRUST_INSUFFICIENT
subject/environment/purpose context mismatch -> TRUST_INSUFFICIENT
```

The non-confusion guard:

```text
missing identity root -> TRUST_NOT_EVALUATED
wrong identity root   -> TRUST_INSUFFICIENT
unbuildable chain due to missing evidence -> TRUST_NOT_EVALUATED
known but undeclared/untrusted issuer     -> TRUST_INSUFFICIENT
```

## Assumptions

Every output carries the floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

A sufficient identity output carries:

```text
PT-CRYPTO-02
PT-IDENTITY-01
PT-IDENTITY-02
PT-REVOKE-01
PT-REVOKE-02
PT-META-03 when a chain is used
```

Unknown revocation carries:

```text
PT-REVOKE-03
```

Do not carry:

```text
PT-AUTHORITY-*
```

This gate establishes identity binding only, not authority.

## Conformance Corpus

The harness must create a deterministic positive fixture and mutation pairs for
all required identity failure modes from the authorization.

Required minimum:

```text
valid_identity_binding
missing_identity_root
wrong_declared_identity_root
malformed_identity_root
unsupported_credential_type
malformed_credential
bad_credential_signature
chain_unbuildable_missing_intermediate
known_but_undeclared_issuer
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

The harness must record binary metrics for each required failure class.

## End-To-End Composition

The harness must check wiring through the accepted composition oracle:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = adapter output
authority_sub = TRUST_NOT_EVALUATED
isolation_sub = TRUST_NOT_EVALUATED
```

Expected:

```text
identity sufficient -> composite TRUST_NOT_EVALUATED
identity not evaluated -> composite TRUST_NOT_EVALUATED
identity insufficient -> composite TRUST_INSUFFICIENT
```

## Verification Gate

Required local verification:

```text
python -m pip install -r requirements/nesira_adapters_win_amd64_cp312.txt
python tools/run_nesira_phase2_identity_adapter_conformance.py
python -m pytest tests/test_nesira_phase2_identity_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py -q
python -m pytest tests/test_formal_core_v1_external_reproduction_package.py -q
python -m pytest -q
python -m compileall -q source tools tests
git diff --check
```

If `lakefile.toml` is touched, the gate must also include:

```text
Formal Core V1 SHA256SUMS self-check
V1 external reproduction manifest hash check
full pytest in the same commit
```

But identity adapter implementation should not touch `lakefile.toml`.

## Cold Verification Requirement

After local acceptance, a separate cold verification must reproduce the result
from a fresh clone before authority adapter work begins.

## Status Lock

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
IDENTITY_ADAPTER_ONLY
SIGNATURE_ADAPTER_FROZEN_BASELINE
IDENTITY_IS_NOT_AUTHORITY
MISSING_IDENTITY_ROOT_NOT_EVALUATED
WRONG_IDENTITY_ROOT_INSUFFICIENT
CHAIN_UNBUILDABLE_NOT_EVALUATED
KNOWN_UNTRUSTED_ISSUER_INSUFFICIENT
REVOCATION_UNKNOWN_NOT_EVALUATED
CLOCK_FAILURE_NOT_EVALUATED
NO_DEFAULT_CA_STORE
NO_TOFU
NO_HAND_ROLLED_X509_CHAIN_VALIDATION
PT_IDENTITY_ASSUMPTIONS_REQUIRED
PT_AUTHORITY_ASSUMPTIONS_NOT_AUTHORIZED
PUBLIC_WHEEL_EXCLUSION_REQUIRED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
