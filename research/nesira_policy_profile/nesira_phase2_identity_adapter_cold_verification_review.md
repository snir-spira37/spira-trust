# Nesira Phase 2 Identity Adapter Cold Verification Review

## Verdict

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

This review records cold verification of the identity adapter from a fresh clone
at:

```text
41cdabdf58e1cd163b24bdc9fdd2c8a03e9d5b7a
```

It accepts only the identity adapter gate. It does not authorize authority,
isolation attestation, isolation execution, CLI, combined verdict integration,
public wheel exposure, public claims, or release.

## Source Reproduction

Result: PASS

The commit was fetched from the public remote, checked out detached, and the
working tree remained clean after verification.

The identity implementation commit changed only the identity adapter gate:

```text
research/nesira_policy_profile/nesira_phase2_identity_adapter_report.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_results.json
research/nesira_policy_profile/nesira_phase2_identity_adapter_review.md
source/spira_core/nesira_phase2_identity_adapter.py
source/spira_core/nesira_phase2_identity_harness.py
tests/test_nesira_phase2_identity_adapter.py
tools/run_nesira_phase2_identity_adapter_conformance.py
```

It did not change `pyproject.toml`, `lakefile.toml`, or Formal Core V1 external
reproduction artifacts.

## Dependency Boundary

Result: PASS

The cold clone used:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
cryptography==49.0.0
--require-hashes
```

The product dependency list remains:

```text
dependencies = []
```

No project optional dependencies are present.

## Identity Conformance

Result: PASS

Command:

```text
python tools/run_nesira_phase2_identity_adapter_conformance.py --write-results
```

Reported verdict:

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_ACCEPTED
```

Key metrics:

```text
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

## Split Chain Fixture Check

Result: PASS

The two identity-specific chain cases are distinct and reproduced:

```text
chain_unbuildable_missing_intermediate
  -> TRUST_NOT_EVALUATED
  -> IDENTITY_CHAIN_NOT_EVALUATED

known_but_undeclared_issuer
  -> TRUST_INSUFFICIENT
  -> IDENTITY_KNOWN_UNDECLARED_ISSUER
```

The root distinction also remains intact:

```text
missing_identity_root
  -> TRUST_NOT_EVALUATED
  -> IDENTITY_DECLARED_ROOT_MISSING

wrong_declared_identity_root
  -> TRUST_INSUFFICIENT
  -> IDENTITY_DECLARED_ROOT_MISMATCH
```

## X.509 And Trust Store Boundary

Result: PASS

The adapter uses:

```text
cryptography.x509.verification.PolicyBuilder
cryptography.x509.verification.Store
```

No default trust store path was detected:

```text
default_store: absent
load_default: absent
certifi/default bundle: absent
```

No hand-rolled certificate signature verification path was detected in the
identity adapter:

```text
public_key().verify: absent
load_pem_public_key: absent
```

The harness includes forbidden execution-key names only as a negative scan set;
they are not emitted by adapter outputs.

## Regression Gates

Result: PASS

Executed:

```text
python -m pytest tests/test_nesira_phase2_identity_adapter.py -q
  -> 10 passed

python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
  -> 14 passed

python -m compileall -q source tools tests
  -> PASS

python -m pytest -q
  -> 305 passed

git diff --check
  -> PASS
```

The Formal Core V1 external reproduction package self-check was also run
directly:

```text
SHA256SUMS total: 622
SHA256SUMS ok: 622
SHA256SUMS fail: 0
```

## Public Wheel Boundary

Result: PASS

The public wheel remains free of the identity adapter and crypto dependency:

```text
adapter_entries: []
cryptography_entries: []
metadata_mentions_cryptography: false
wheel_exclusion_failures: 0
```

## Accepted Boundary

Accepted:

```text
identity credential classification
declared-root-only X.509 path validation
no default trust
identity sub-verdict conformance
identity-to-composition wiring
public wheel exclusion
V1 package self-check
```

Not accepted or authorized:

```text
signer authority
permission to sever
isolation attestation
actual isolation execution
isolation runner
CLI
combined verdict integration
public capability claim
release
```

## Next Gate

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_AUTHORIZATION_REQUIRED
```

Authority adapter implementation remains blocked until a separate authorization
is written and accepted.
