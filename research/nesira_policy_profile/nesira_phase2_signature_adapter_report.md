# Nesira Phase 2 Signature Adapter Implementation Report

## Status

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTED
NESIRA_PHASE2_SIGNATURE_ADAPTER_CONFORMANCE_ACCEPTED
```

This gate implements the first Phase 2 sub-assessment adapter:

```text
signature adapter only
```

It does not implement identity, authority, isolation-attestation, an isolation
runner, CLI wiring, combined verdict integration, public wheel exposure, public
claims, or release.

## Implemented Scope

Implemented:

```text
source/spira_core/nesira_phase2_signature_adapter.py
source/spira_core/nesira_phase2_signature_harness.py
tools/run_nesira_phase2_signature_adapter_conformance.py
tests/test_nesira_phase2_signature_adapter.py
requirements/nesira_adapters_win_amd64_cp312.txt
research/nesira_policy_profile/nesira_phase2_signature_adapter_results.json
```

The adapter classifies:

```text
signed payload + signature evidence + declared SIGNING_KEY root + bounded context
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

## Crypto Pin

The adapter uses `pyca/cryptography` verification primitives only.

Pinned adapter/conformance dependency:

```text
cryptography==49.0.0
```

Hash-pinned requirements:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

Pinned artifacts:

```text
cryptography-49.0.0-cp311-abi3-win_amd64.whl
sha256=e5dfc1e64de5677cec922ffa8da89c546d0415bf6efdf081842e5d44c84e1f0e

cffi-2.1.0-cp312-cp312-win_amd64.whl
sha256=c97f080ea627e2863524c5af3836e2270b5f5dfff1f104392b959f8df0c5d384

pycparser-3.0-py3-none-any.whl
sha256=b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992
```

The runtime adapter checks:

```text
cryptography.__version__ == 49.0.0
```

If the dependency is missing or the version does not match, the adapter returns
a fail-closed non-sufficient result.

## Pyproject Boundary

The product dependency list remains:

```text
dependencies = []
```

No `[project.optional-dependencies]` entry was added.

Reason: `pyproject.toml` is part of the Formal Core V1 external reproduction
source manifest. Adding an optional extra there would mutate a V1-locked source
artifact from a Phase 2 adapter gate. The exact pin is therefore carried by the
hash-pinned requirements file for this adapter/conformance gate.

If a pyproject extra is still desired later, it requires a separate boundary
authorization.

## Sub-Verdict Mapping

Implemented mapping:

```text
valid signature under declared fresh root -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
invalid signature -> TRUST_INSUFFICIENT
wrong declared root -> TRUST_INSUFFICIENT
missing declared root -> TRUST_NOT_EVALUATED
malformed declared root -> TRUST_NOT_EVALUATED
expired declared root -> TRUST_INSUFFICIENT
revoked declared root -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
malformed payload/signature before verify -> TRUST_NOT_EVALUATED
payload/context/scope mismatch -> TRUST_INSUFFICIENT
```

The critical distinction is preserved:

```text
missing root -> TRUST_NOT_EVALUATED
wrong root   -> TRUST_INSUFFICIENT
```

## Assumption Carrying

Sufficient signature sub-assessments carry:

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

Unknown revocation carries:

```text
PT-REVOKE-03
```

## Conformance Results

Recorded result:

```text
research/nesira_policy_profile/nesira_phase2_signature_adapter_results.json
```

Summary:

```text
verdict: NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED
fixture_count: 19
required_signature_failure_modes_without_fixture: 0
required_signature_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
missing_root_mapped_to_insufficient: 0
wrong_root_mapped_to_not_evaluated: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
adapter_outputs_with_execution_semantics: 0
composition_mismatches: 0
wheel_exclusion_failures: 0
two_run_semantic_diff: 0
```

## End-to-End Composition Wiring

The conformance harness feeds the signature sub-verdict into the accepted Phase
2 composition oracle with the three unimplemented adapters set to:

```text
TRUST_NOT_EVALUATED
```

Expected and observed:

```text
signature sufficient    -> composite TRUST_NOT_EVALUATED
signature not evaluated -> composite TRUST_NOT_EVALUATED
signature insufficient  -> composite TRUST_INSUFFICIENT
```

This verifies wiring only. It does not claim full Phase 2 sufficiency.

## Wheel Exclusion

The public wheel exclusion check passed:

```text
signature adapter entries in wheel: 0
signature harness entries in wheel: 0
cryptography entries in wheel: 0
cryptography metadata mentions: false
wheel_exclusion_failures: 0
```

## Formal Core V1 Manifest Maintenance

During full pytest, the existing Formal Core V1 external reproduction package
manifest was found to still contain the pre-Phase2 hash for:

```text
formal/spira_formal_core_v1/lakefile.toml
```

This file had already changed in the accepted Phase 2 Lean target separation.
The fix in this gate is narrow:

```text
updated lakefile.toml bytes and sha256 in artifact_manifest.json
updated lakefile.toml and artifact_manifest.json hashes in SHA256SUMS
```

No Domain4 or Phase 2 source files were added to the V1 inventory, and V1
claims/inventory text was not expanded.

## Verification

Executed:

```text
python -m pip install -r requirements/nesira_adapters_win_amd64_cp312.txt
python tools/run_nesira_phase2_signature_adapter_conformance.py
python -m pytest tests/test_nesira_phase2_signature_adapter.py -q
python -m pytest -q
python -m compileall -q source tools tests
git diff --check
```

Results:

```text
cryptography runtime version: 49.0.0
pip check: PASS
signature adapter focused tests: 9 passed
full pytest: 295 passed
Formal Core V1 SHA256SUMS self-check: 0 failures
compileall: PASS
git diff --check: PASS
```

## Not Claimed

This implementation does not claim:

```text
identity established
signer authority established
authority policy checked
attestation checked
isolation occurred
isolation proven
permission to sever
safe to sever
production readiness
release readiness
```

## Status

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTED
NESIRA_PHASE2_SIGNATURE_ADAPTER_CONFORMANCE_ACCEPTED
CRYPTOGRAPHY_49_0_0_PINNED
HASH_PINNED_REQUIREMENTS_ACCEPTED
PROJECT_DEPENDENCIES_REMAIN_EMPTY
PYPROJECT_OPTIONAL_EXTRA_NOT_ADDED_V1_BOUNDARY_PRESERVED
NO_HAND_ROLLED_CRYPTO
MISSING_ROOT_NOT_EVALUATED
WRONG_ROOT_INSUFFICIENT
REVOCATION_UNKNOWN_NOT_EVALUATED
CLOCK_FAILURE_NOT_EVALUATED
NO_DEFAULT_TRUST
NO_TOFU
NO_ANY_VALID_SIGNATURE
ADAPTER_FEEDS_COMPOSITION_CORE
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
