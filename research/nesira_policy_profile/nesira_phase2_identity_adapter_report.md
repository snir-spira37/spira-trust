# Nesira Phase 2 Identity Adapter Implementation Report

## Status

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_IMPLEMENTED
NESIRA_PHASE2_IDENTITY_ADAPTER_CONFORMANCE_ACCEPTED
```

This gate implements the second Phase 2 sub-assessment adapter:

```text
identity adapter only
```

It does not implement signer authority, isolation attestation, an isolation
runner, CLI wiring, combined verdict integration, public wheel exposure, public
claims, or release.

## Implemented Scope

Implemented:

```text
source/spira_core/nesira_phase2_identity_adapter.py
source/spira_core/nesira_phase2_identity_harness.py
tools/run_nesira_phase2_identity_adapter_conformance.py
tests/test_nesira_phase2_identity_adapter.py
research/nesira_policy_profile/nesira_phase2_identity_adapter_results.json
```

The adapter classifies:

```text
X.509 identity credential + declared IDENTITY_BINDING_CA root + bounded context
```

into one of:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

The output is a sub-assessment only and carries the fixed execution marker:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## Crypto Boundary

The adapter reuses the accepted Phase 2 adapter crypto pin:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
cryptography==49.0.0
```

The product dependency list remains:

```text
dependencies = []
```

No pyproject optional extra was added.

The adapter uses `cryptography.x509.verification.PolicyBuilder` and `Store`
for certificate path validation. It does not use the operating-system trust
store, browser trust store, TOFU, any-valid-certificate logic, or hand-rolled
X.509 path validation.

## Sub-Verdict Mapping

Implemented mapping:

```text
valid identity binding under declared root -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
missing identity root -> TRUST_NOT_EVALUATED
ambiguous identity root -> TRUST_NOT_EVALUATED
malformed identity root -> TRUST_NOT_EVALUATED
unsupported credential type -> TRUST_NOT_EVALUATED
malformed credential before verification -> TRUST_NOT_EVALUATED
invalid credential signature -> TRUST_INSUFFICIENT
chain cannot be built because evidence is missing -> TRUST_NOT_EVALUATED
chain builds to known but undeclared/untrusted root -> TRUST_INSUFFICIENT
wrong declared identity root -> TRUST_INSUFFICIENT
untrusted issuer under declared root -> TRUST_INSUFFICIENT
expired credential/intermediate/root -> TRUST_INSUFFICIENT
revoked credential/intermediate/root -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
namespace mismatch -> TRUST_INSUFFICIENT
signer identity mismatch -> TRUST_INSUFFICIENT
signing key/root binding mismatch -> TRUST_INSUFFICIENT
subject/environment/purpose context mismatch -> TRUST_INSUFFICIENT
```

The key distinction is preserved by separate fixtures:

```text
chain_unbuildable_missing_intermediate -> TRUST_NOT_EVALUATED
known_but_undeclared_issuer -> TRUST_INSUFFICIENT
```

## Conformance Result

Recorded results:

```text
research/nesira_policy_profile/nesira_phase2_identity_adapter_results.json
```

Summary:

```text
verdict: NESIRA_PHASE2_IDENTITY_ADAPTER_ACCEPTED
required_identity_failure_modes_without_fixture: 0
required_identity_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
missing_root_mapped_to_insufficient: 0
wrong_root_mapped_to_not_evaluated: 0
chain_unbuildable_mapped_to_insufficient: 0
known_untrusted_issuer_mapped_to_not_evaluated: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
adapter_outputs_with_authority_semantics: 0
adapter_outputs_with_execution_semantics: 0
composition_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## Local Verification

The implementation gate was checked locally with:

```text
python tools/run_nesira_phase2_identity_adapter_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_identity_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m compileall -q source tools tests
python -m pytest -q
```

Result:

```text
identity focused pytest: 10 passed
signature + V1 package regression: 14 passed
compileall: PASS
full pytest: 305 passed
```

## Boundaries

Still not implemented or claimed:

```text
signer authority
permission to sever
isolation attestation
actual isolation execution
isolation runner
CLI
combined verdict integration
public wheel exposure
public capability claim
release
```

## Required Next Step

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_REQUIRED
```

Authority adapter work remains blocked until the identity adapter is reproduced
from a fresh clone.
