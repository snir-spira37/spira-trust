# Nesira Phase 2 Authority Adapter Implementation Plan

## Status

```text
DOCUMENT_TYPE: IMPLEMENTATION_PLAN
PHASE: PHASE_2
SCOPE: AUTHORITY_ADAPTER_ONLY
IMPLEMENTATION: NOT_STARTED
SIGNATURE_ADAPTER: FROZEN_BASELINE
IDENTITY_ADAPTER: FROZEN_BASELINE
ISOLATION_ATTESTATION_ADAPTER: NOT_AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This plan prepares implementation of the authority adapter only.

The adapter will classify authority policy evidence for an already-established
signer identity under a declared `AUTHORITY_POLICY_SOURCE` root. It will not
verify the signature or identity again.

## Implementation Shape

The implementation should mirror the accepted signature and identity adapter
shape:

```text
source/spira_core/nesira_phase2_authority_adapter.py
source/spira_core/nesira_phase2_authority_harness.py
tools/run_nesira_phase2_authority_adapter_conformance.py
tests/test_nesira_phase2_authority_adapter.py
research/nesira_policy_profile/nesira_phase2_authority_adapter_results.json
research/nesira_policy_profile/nesira_phase2_authority_adapter_report.md
research/nesira_policy_profile/nesira_phase2_authority_adapter_review.md
```

The public wheel builder is allowlist-based. The new adapter and harness must
not be added to the allowlist.

## Policy Model For This Gate

This gate should use a deliberately small deterministic policy model:

```text
authority policy root id/version
policy type
policy id/version
subject/environment/purpose/action scope
valid_from / valid_until
revocation status / freshness
explicit allow entries
explicit deny entries
established signer identity
bounded subject/environment/purpose/action request
```

Each allow/deny entry should bind at least:

```text
signer_identity
subject
environment
purpose
action
policy_version
```

## Dependency Boundary

No new crypto dependency is expected for this gate.

Do not modify:

```text
pyproject.toml
requirements/nesira_adapters_win_amd64_cp312.txt
```

The product dependency list must remain:

```text
dependencies = []
```

If signed policy material is required, this plan is insufficient. Signature
verification must be delegated to the accepted signature adapter or authorized
as a separate policy-signature gate.

## Sub-Verdict Mapping

The implementation must use this mapping:

```text
explicit in-scope allow -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
missing authority policy root -> TRUST_NOT_EVALUATED
ambiguous authority policy root -> TRUST_NOT_EVALUATED
malformed authority policy root -> TRUST_NOT_EVALUATED
policy source missing/unreadable/malformed/unsupported -> TRUST_NOT_EVALUATED
established signer identity missing -> TRUST_NOT_EVALUATED
identity sub-verdict not sufficient -> TRUST_NOT_EVALUATED
explicit deny -> TRUST_INSUFFICIENT
identity absent from consultable policy -> TRUST_INSUFFICIENT
action not explicitly allowed -> TRUST_INSUFFICIENT
policy root id/version mismatch -> TRUST_INSUFFICIENT
subject/environment/purpose/action mismatch -> TRUST_INSUFFICIENT
policy version stale or out of scope -> TRUST_INSUFFICIENT
policy expired/not-yet-valid -> TRUST_INSUFFICIENT
policy revoked -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
```

The non-confusion guard:

```text
missing policy root -> TRUST_NOT_EVALUATED
identity absent from consultable policy -> TRUST_INSUFFICIENT
explicit deny -> TRUST_INSUFFICIENT
no matching allow -> TRUST_INSUFFICIENT
```

Default-deny is the safety rule. Policy absence and unreadability are
`NOT_EVALUATED`; absence of an identity or action inside a readable policy is
`INSUFFICIENT`.

## Assumptions

Every output carries the floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

A sufficient authority output carries:

```text
PT-AUTHORITY-01
PT-AUTHORITY-02
PT-REVOKE-01
PT-REVOKE-02
```

Unknown revocation carries:

```text
PT-REVOKE-03
```

Do not carry:

```text
PT-IDENTITY-* as an identity-verification claim
PT-ISOLATION-*
```

This gate establishes authority lookup only, not identity verification,
isolation, or execution.

## Conformance Corpus

The harness must create a deterministic positive fixture and mutation pairs for
all required authority failure modes from the authorization.

Required minimum:

```text
valid_explicit_allow
missing_authority_policy_root
ambiguous_authority_policy_root
malformed_authority_policy_root
policy_source_missing
policy_source_malformed
unsupported_policy_type
established_identity_missing
identity_sub_verdict_not_sufficient
explicit_deny
identity_absent_from_policy
action_not_allowed
subject_context_mismatch
environment_context_mismatch
purpose_context_mismatch
policy_version_mismatch
policy_root_mismatch
policy_version_stale
policy_expired
policy_not_yet_valid
policy_revoked
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
authority_sub = adapter output
isolation_sub = TRUST_NOT_EVALUATED
```

Expected:

```text
authority sufficient -> composite TRUST_NOT_EVALUATED
authority not evaluated -> composite TRUST_NOT_EVALUATED
authority insufficient -> composite TRUST_INSUFFICIENT
```

## Verification Gate

Required local verification:

```text
python tools/run_nesira_phase2_authority_adapter_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_authority_adapter.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m compileall -q source tools tests
python -m pytest -q
git diff --check
```

If `lakefile.toml` or Formal Core V1 reproduction artifacts are touched, the
gate must also include:

```text
Formal Core V1 SHA256SUMS self-check
V1 external reproduction manifest hash check
full pytest in the same commit
```

Authority adapter implementation should not touch `lakefile.toml` or Formal
Core V1 artifacts.

## Stop Conditions

Stop if implementation requires:

```text
default allow
permit unless denied
implicit admin/owner
fallback policy
identity verification inside authority adapter
signature verification inside authority adapter
isolation attestation
execution/severance output
combined verdict wiring
new dependency
pyproject change
lakefile change
V1 artifact change
```

## Cold Verification Requirement

After local acceptance, a separate cold verification must reproduce the result
from a fresh clone before isolation-attestation adapter work begins.

## Status Lock

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
AUTHORITY_ADAPTER_ONLY
AUTHORITY_IS_POLICY_NOT_CRYPTO
AUTHORITY_CONSUMES_ESTABLISHED_IDENTITY
DEFAULT_DENY_REQUIRED
MISSING_POLICY_ROOT_NOT_EVALUATED
IDENTITY_ABSENT_FROM_POLICY_INSUFFICIENT
EXPLICIT_DENY_INSUFFICIENT
ACTION_NOT_ALLOWED_INSUFFICIENT
PT_AUTHORITY_ASSUMPTIONS_REQUIRED
PUBLIC_WHEEL_EXCLUSION_REQUIRED
```
