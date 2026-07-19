# Nesira Phase 2 Isolation Attestation Adapter Implementation Plan

## Status

```text
DOCUMENT_TYPE: IMPLEMENTATION_PLAN
PHASE: PHASE_2
SCOPE: ISOLATION_ATTESTATION_ADAPTER_ONLY
IMPLEMENTATION: NOT_STARTED
SIGNATURE_ADAPTER: FROZEN_BASELINE
IDENTITY_ADAPTER: FROZEN_BASELINE
AUTHORITY_ADAPTER: FROZEN_BASELINE
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This plan prepares implementation of the isolation attestation adapter only.

The adapter will classify an attestation object under a declared
`ATTESTATION_AUTHORITY` root. It will not run, observe, or prove isolation.

The implementation mantra is:

```text
attestation checked != isolation proven
```

## Implementation Shape

The implementation should mirror the accepted adapter shape:

```text
source/spira_core/nesira_phase2_isolation_attestation_adapter.py
source/spira_core/nesira_phase2_isolation_attestation_harness.py
tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py
tests/test_nesira_phase2_isolation_attestation_adapter.py
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_results.json
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_report.md
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_review.md
```

The public wheel builder is allowlist-based. The new adapter and harness must
not be added to the allowlist.

## Attestation Model For This Gate

This gate should use a deliberately small deterministic attestation model:

```text
attestation authority root id/version
attestation type
attestation id/version
candidate id/hash
environment id
isolation profile id/version
valid_from / valid_until
revocation status / freshness
attestation signature over canonical attestation payload
declared ATTESTATION_AUTHORITY public key/root material
```

The binding check must mean only:

```text
the attestation claims the expected candidate/environment/isolation profile
```

It must not mean:

```text
the candidate was actually isolated
the environment was actually isolated
the profile was actually enforced
```

## Dependency Boundary

No new dependency is expected for this gate.

The adapter may reuse the accepted gated Phase 2 crypto dependency:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
cryptography==49.0.0
--require-hashes
```

Do not modify:

```text
pyproject.toml
requirements/nesira_adapters_win_amd64_cp312.txt
```

The product dependency list must remain:

```text
dependencies = []
```

If the accepted crypto boundary cannot verify the attestation signature, this
plan is insufficient and the implementation must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Sub-Verdict Mapping

The implementation must use this mapping:

```text
authentic attestation under declared authority + expected claims bound
  -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

missing/ambiguous/malformed attestation authority root
  -> TRUST_NOT_EVALUATED

attestation missing/unreadable/malformed/unsupported
  -> TRUST_NOT_EVALUATED

bad attestation signature
  -> TRUST_INSUFFICIENT

known but undeclared attestation authority
  -> TRUST_INSUFFICIENT

wrong declared attestation authority/root
  -> TRUST_INSUFFICIENT

candidate/environment/isolation-profile claim mismatch
  -> TRUST_INSUFFICIENT

attestation expired/not-yet-valid
  -> TRUST_INSUFFICIENT

attestation authority/root revoked
  -> TRUST_INSUFFICIENT

revocation unknown/stale/unreachable
  -> TRUST_NOT_EVALUATED

clock missing/untrusted
  -> TRUST_NOT_EVALUATED
```

The non-confusion guard:

```text
verified attestation -> checked claim only
verified attestation -> not isolation occurred
verified attestation -> not permission to sever
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

Every isolation output also carries:

```text
PT-ISOLATION-01
```

This is mandatory for all sub-verdicts, including sufficient outputs.

A sufficient isolation-attestation output carries the applicable attestation
authority and revocation assumptions, plus `PT-ISOLATION-01`.

Unknown revocation carries:

```text
PT-REVOKE-03
```

## Forbidden Language And Output Semantics

No adapter output, reason code, report, or test expected value may state or
imply:

```text
isolation occurred
isolation happened
isolation confirmed
isolation proven
isolation executed
runtime isolated
filesystem isolated
network isolated
process isolated
```

Allowed language:

```text
attestation verified against declared authority
attestation claims bind expected profile
attestation signature invalid
attestation claims mismatch
attestation authority not evaluated
```

## Conformance Corpus

The harness must create a deterministic positive fixture and mutation pairs for
all required isolation-attestation failure modes from the authorization.

Required minimum:

```text
valid_attestation_under_declared_authority
missing_attestation_authority_root
ambiguous_attestation_authority_root
malformed_attestation_authority_root
attestation_missing
attestation_malformed
unsupported_attestation_type
bad_attestation_signature
known_undeclared_attestation_authority
attestation_root_mismatch
candidate_claim_mismatch
environment_claim_mismatch
isolation_profile_claim_mismatch
attestation_expired
attestation_not_yet_valid
attestation_authority_revoked
revocation_unknown
revocation_stale
revocation_unreachable
clock_missing
clock_untrusted
```

The harness must record binary metrics for each required failure class.

## Composition Wiring

The harness must check end-to-end wiring through the accepted composition
oracle:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
authority_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation_sub = adapter output
```

Expected:

```text
isolation sufficient -> composite TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation not evaluated -> composite TRUST_NOT_EVALUATED
isolation insufficient -> composite TRUST_INSUFFICIENT
```

The harness must verify that `PT-ISOLATION-01` is carried both by the isolation
sub-verdict and by a sufficient composite assessment.

## Verification Gate

Required local verification:

```text
python tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_isolation_attestation_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_nesira_phase2_authority_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m compileall -q source tools tests
python -m pytest -q
git diff --check
```

The gate must include an explicit scan for forbidden language in:

```text
source/spira_core/nesira_phase2_isolation_attestation_adapter.py
source/spira_core/nesira_phase2_isolation_attestation_harness.py
tests/test_nesira_phase2_isolation_attestation_adapter.py
tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_*.md
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_results.json
```

Forbidden language scan:

```text
isolation occurred
isolation happened
isolation confirmed
isolation proven
isolation executed
runtime isolated
filesystem isolated
network isolated
process isolated
```

If `lakefile.toml` or Formal Core V1 reproduction artifacts are touched, the
gate must also include:

```text
Formal Core V1 SHA256SUMS self-check
V1 external reproduction manifest hash check
full pytest in the same commit
```

Isolation attestation adapter implementation should not touch `lakefile.toml`
or Formal Core V1 artifacts.

## Stop Conditions

Stop if implementation requires:

```text
isolation runner
runtime observation
filesystem observation
network observation
process observation
execution/severance output
permission to sever
combined verdict wiring
new dependency
pyproject change
lakefile change
V1 artifact change
language that says isolation occurred/happened/confirmed/proven
```

## Cold Verification Requirement

After local acceptance, a separate cold verification must reproduce the result
from a fresh clone before any further Phase 2 integration work begins.

## Status Lock

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
ISOLATION_ATTESTATION_ADAPTER_ONLY
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN_REQUIRED
PT_ISOLATION_01_ALWAYS_CARRIED_REQUIRED
ISOLATION_RUNNER_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
