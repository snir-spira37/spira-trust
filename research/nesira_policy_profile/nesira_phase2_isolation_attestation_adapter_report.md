# Nesira Phase 2 Isolation Attestation Adapter Implementation Report

## Status

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_IMPLEMENTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_CONFORMANCE_ACCEPTED
```

This gate implements the fourth Phase 2 sub-assessment adapter:

```text
isolation attestation adapter only
```

It does not implement a runner, runtime observation, CLI wiring, combined
verdict integration, public wheel exposure, public claims, or release.

## Implemented Scope

Implemented:

```text
source/spira_core/nesira_phase2_isolation_attestation_adapter.py
source/spira_core/nesira_phase2_isolation_attestation_harness.py
tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py
tests/test_nesira_phase2_isolation_attestation_adapter.py
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_results.json
```

The adapter classifies:

```text
attestation object + declared ATTESTATION_AUTHORITY root + caller-supplied expected profile
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

## Attestation Boundary

The adapter verifies an Ed25519 attestation signature over a canonical
attestation payload and checks that the payload claims the caller-supplied
candidate, environment, and profile.

The expected profile inputs come from caller context. They are not learned from
the attestation payload.

The adapter never emits an execution result. It also carries:

```text
PT-ISOLATION-01
```

on every sub-verdict.

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

## Sub-Verdict Mapping

Implemented mapping:

```text
valid attestation under declared authority -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
missing attestation authority root -> TRUST_NOT_EVALUATED
ambiguous attestation authority root -> TRUST_NOT_EVALUATED
malformed attestation authority root -> TRUST_NOT_EVALUATED
attestation missing/malformed/unsupported -> TRUST_NOT_EVALUATED
bad attestation signature -> TRUST_INSUFFICIENT
known undeclared attestation authority -> TRUST_INSUFFICIENT
attestation root mismatch -> TRUST_INSUFFICIENT
candidate/environment/profile claim mismatch -> TRUST_INSUFFICIENT
attestation expired/not-yet-valid -> TRUST_INSUFFICIENT
attestation authority revoked -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
clock missing with expired attestation -> TRUST_NOT_EVALUATED
```

The clock precedence case is preserved by a dedicated fixture:

```text
clock_missing_with_expired_attestation -> TRUST_NOT_EVALUATED
```

## Language Guard

The harness enforces an allowlist over attestation outputs. Summary:

```text
forbidden_isolation_language_hits: 0
non_allowlisted_isolation_language_hits: 0
```

The allowlist permits machine keys and phrases for:

```text
isolation attestation
isolation profile
isolation sub-verdict
isolation caveat
PT-ISOLATION-01
```

It does not permit truth-claim language.

## Conformance Result

Recorded results:

```text
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_results.json
```

Summary:

```text
verdict: NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED
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
composition_mismatches: 0
composite_caveat_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## Local Verification

The implementation gate was checked locally with:

```text
python tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_isolation_attestation_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_nesira_phase2_authority_adapter.py tests/test_nesira_phase2_isolation_attestation_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m compileall -q source tools tests
python -m pytest -q
git diff --check
```

Result:

```text
isolation attestation focused pytest: 12 passed
signature + identity + authority + isolation attestation + V1 package regression: 46 passed
compileall: PASS
full pytest: 327 passed
git diff --check: PASS
Formal Core V1 SHA256SUMS: 622 checked, 0 failures
```

## Boundaries

Still not implemented or claimed:

```text
actual execution
runner
runtime observation
filesystem observation
network observation
process observation
CLI
combined verdict integration
public wheel exposure
public capability claim
release
```

## Required Next Step

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_REQUIRED
```

Further Phase 2 integration work remains blocked until this attestation
adapter is reproduced from a fresh clone.
