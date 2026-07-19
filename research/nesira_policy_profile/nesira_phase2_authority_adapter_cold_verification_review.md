# Nesira Phase 2 Authority Adapter Cold Verification Review

## Verdict

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

This review records cold verification of the authority adapter from a fresh
clone at:

```text
93858fdaade1f7e592cd91f64a11f32feee5fccc
```

It accepts only the authority adapter gate. It does not authorize isolation
attestation, isolation execution, CLI, combined verdict integration, public
wheel exposure, public claims, or release.

## Source Reproduction

Result: PASS

The commit was fetched from the public remote, checked out detached, and the
working tree remained clean after verification.

The authority implementation commit changed only the authority adapter gate:

```text
research/nesira_policy_profile/nesira_phase2_authority_adapter_report.md
research/nesira_policy_profile/nesira_phase2_authority_adapter_results.json
research/nesira_policy_profile/nesira_phase2_authority_adapter_review.md
source/spira_core/nesira_phase2_authority_adapter.py
source/spira_core/nesira_phase2_authority_harness.py
tests/test_nesira_phase2_authority_adapter.py
tools/run_nesira_phase2_authority_adapter_conformance.py
```

It did not change `pyproject.toml`, `lakefile.toml`, or Formal Core V1 external
reproduction artifacts.

## Authority Conformance

Result: PASS

Command:

```text
python tools/run_nesira_phase2_authority_adapter_conformance.py --write-results
```

Reported verdict:

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_ACCEPTED
```

Key metrics:

```text
required_authority_failure_modes_without_fixture: 0
required_authority_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
default_allow_paths: 0
missing_policy_root_mapped_to_insufficient: 0
identity_absent_mapped_to_not_evaluated: 0
explicit_deny_mapped_to_not_evaluated: 0
action_not_allowed_mapped_to_not_evaluated: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
authority_outputs_with_identity_verification_semantics: 0
authority_outputs_with_execution_semantics: 0
composition_mismatches: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## Default-Deny Fixture Check

Result: PASS

The authority-specific default-deny cases are distinct and reproduced:

```text
explicit_deny
  -> TRUST_INSUFFICIENT
  -> AUTHORITY_EXPLICIT_DENY

identity_absent_from_policy
  -> TRUST_INSUFFICIENT
  -> AUTHORITY_IDENTITY_ABSENT_FROM_POLICY

action_not_allowed
  -> TRUST_INSUFFICIENT
  -> AUTHORITY_ACTION_NOT_ALLOWED
```

Missing/unreadable policy material remains not-evaluated rather than
insufficient:

```text
missing_authority_policy_root
  -> TRUST_NOT_EVALUATED
  -> AUTHORITY_DECLARED_ROOT_MISSING

policy_source_missing
  -> TRUST_NOT_EVALUATED
  -> AUTHORITY_POLICY_SOURCE_MISSING
```

## Dependency And Crypto Boundary

Result: PASS

The authority adapter introduces no new dependency:

```text
dependencies = []
new_dependencies = []
```

The adapter does not use `cryptography`, does not verify signatures or
certificates, and does not re-establish identity. It consumes the identity
sub-verdict as an input.

## Regression Gates

Result: PASS

Executed from the fresh clone:

```text
python -m pytest tests/test_nesira_phase2_authority_adapter.py -q
  -> 10 passed

python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_formal_core_v1_external_reproduction_package.py tests/test_nesira_phase2_authority_adapter.py -q
  -> 34 passed

python -m compileall -q source tools tests
  -> PASS

python -m pytest -q
  -> 315 passed

git diff --check
  -> PASS
```

The Formal Core V1 external reproduction package self-check was also run
directly:

```text
SHA256SUMS total: 622
SHA256SUMS fail: 0
```

## Public Wheel Boundary

Result: PASS

The public wheel remains free of the authority adapter and new dependency
metadata:

```text
adapter_entries: []
metadata_dependency_headers: []
wheel_exclusion_failures: 0
```

## Accepted Boundary

Accepted:

```text
authority policy classification
default-deny semantics
declared-root-only authority policy source
authority sub-verdict conformance
authority-to-composition wiring
public wheel exclusion
V1 package self-check
```

Not accepted or authorized:

```text
isolation attestation
actual isolation execution
permission to sever
CLI
combined verdict integration
public wheel exposure
public capability claim
release
```

## Next Required Gate

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_AUTHORIZATION_REQUIRED
```

The next gate is not implementation-by-default. It requires separate
authorization because it is the highest overclaim-risk adapter: attestation
checking must not become a claim that isolation occurred.
