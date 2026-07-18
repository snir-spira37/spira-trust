# Nesira Phase 2 Authority Adapter Implementation Report

## Status

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_IMPLEMENTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_CONFORMANCE_ACCEPTED
```

This gate implements the third Phase 2 sub-assessment adapter:

```text
authority adapter only
```

It does not implement isolation attestation, an isolation runner, CLI wiring,
combined verdict integration, public wheel exposure, public claims, or release.

## Implemented Scope

Implemented:

```text
source/spira_core/nesira_phase2_authority_adapter.py
source/spira_core/nesira_phase2_authority_harness.py
tools/run_nesira_phase2_authority_adapter_conformance.py
tests/test_nesira_phase2_authority_adapter.py
research/nesira_policy_profile/nesira_phase2_authority_adapter_results.json
```

The adapter classifies:

```text
established signer identity + declared AUTHORITY_POLICY_SOURCE root + policy source + bounded request context
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

## Authority Boundary

The adapter is policy-only. It consumes an identity sub-verdict that has already
been established elsewhere; it does not parse certificates, verify signatures,
build certificate chains, or assert signer authority outside the declared
policy source.

No new runtime dependency is introduced:

```text
dependencies = []
new_dependencies = []
```

The authority adapter does not use `cryptography`; the existing crypto pin
remains a signature/identity adapter boundary, not an authority adapter
dependency.

## Sub-Verdict Mapping

Implemented mapping:

```text
explicit allow under declared authority policy root -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
explicit deny -> TRUST_INSUFFICIENT
identity absent from consultable policy -> TRUST_INSUFFICIENT
identity present but action not explicitly allowed -> TRUST_INSUFFICIENT
context mismatch -> TRUST_INSUFFICIENT
policy root id/version mismatch -> TRUST_INSUFFICIENT
policy version outside declared scope -> TRUST_INSUFFICIENT
expired or not-yet-valid policy/root -> TRUST_INSUFFICIENT
revoked policy/root -> TRUST_INSUFFICIENT
missing authority policy root -> TRUST_NOT_EVALUATED
ambiguous authority policy root -> TRUST_NOT_EVALUATED
malformed authority policy root -> TRUST_NOT_EVALUATED
missing or malformed policy source -> TRUST_NOT_EVALUATED
unsupported policy type -> TRUST_NOT_EVALUATED
identity sub-verdict not sufficient -> TRUST_NOT_EVALUATED
established identity missing or malformed -> TRUST_NOT_EVALUATED
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
```

The default-deny distinction is preserved by separate fixtures:

```text
identity_absent_from_policy -> TRUST_INSUFFICIENT
action_not_allowed -> TRUST_INSUFFICIENT
missing_authority_policy_root -> TRUST_NOT_EVALUATED
policy_source_missing -> TRUST_NOT_EVALUATED
```

## Conformance Result

Recorded results:

```text
research/nesira_policy_profile/nesira_phase2_authority_adapter_results.json
```

Summary:

```text
verdict: NESIRA_PHASE2_AUTHORITY_ADAPTER_ACCEPTED
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

## Local Verification

The implementation gate was checked locally with:

```text
python tools/run_nesira_phase2_authority_adapter_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_authority_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_formal_core_v1_external_reproduction_package.py tests/test_nesira_phase2_authority_adapter.py -q
python -m compileall -q source tools tests
python -m pytest -q
git diff --check
```

Result:

```text
authority focused pytest: 10 passed
signature + identity + V1 package + authority regression: 34 passed
compileall: PASS
full pytest: 315 passed
git diff --check: PASS
Formal Core V1 SHA256SUMS: 622 checked, 0 failures
```

## Boundaries

Still not implemented or claimed:

```text
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
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_REQUIRED
```

Isolation attestation work remains blocked until the authority adapter is
reproduced from a fresh clone.
