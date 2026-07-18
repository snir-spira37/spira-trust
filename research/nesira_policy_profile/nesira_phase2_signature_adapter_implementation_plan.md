# Nesira Phase 2 Signature Adapter Implementation Plan

## Status

```text
DOCUMENT_TYPE: IMPLEMENTATION_PLAN
PHASE: PHASE_2
SCOPE: SIGNATURE_ADAPTER_ONLY
IMPLEMENTATION: NOT_STARTED
CRYPTO_LIBRARY_SELECTION: PROPOSED
IDENTITY_ADAPTER: NOT_AUTHORIZED
AUTHORITY_ADAPTER: NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER: NOT_AUTHORIZED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This plan prepares the first Phase 2 adapter implementation gate: a signature
sub-assessment adapter only.

The adapter will verify a signature against a declared `SIGNING_KEY` trust root
and produce a Phase 2 sub-assessment verdict for the accepted composition core.
It will not implement identity chains, authority policy lookup, attestation
verification, isolation execution, CLI exposure, combined verdict integration,
public wheel exposure, public claims, or release.

## Authoritative Inputs

The implementation must follow:

```text
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_sketch.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization_review.md
```

Any conflict between implementation behavior and these artifacts is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be corrected by silently changing the trust model, ledger,
composition core, or adapter authorization.

## Adapter Purpose

The signature adapter classifies:

```text
signed payload + signature evidence + declared SIGNING_KEY root + bounded context
```

into:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

The output is a sub-assessment only. It must be consumed by the accepted Phase 2
composition core.

It must never output:

```text
execute
sever
permission_to_sever
authorized_to_sever
safe_to_sever
isolation_occurred
isolation_proven
```

## Crypto Dependency Strategy

The implementation must use:

```text
pyca/cryptography
```

as the controlled cryptographic dependency for signature verification.

The exact version must be pinned before implementation acceptance:

```text
cryptography==<exact-version>
```

The implementation report must record:

```text
crypto_library_name: cryptography
crypto_library_version
pinning_method
dependency_lock_or_hash
algorithms_used
wheel_exclusion_result
assumption_ids_carried
```

The project-level product dependency list must remain:

```text
dependencies = []
```

`cryptography` must be a gated adapter/conformance dependency, not a general
product dependency and not a public wheel dependency.

## No Hand-Rolled Crypto

The adapter must call `cryptography` verification primitives. It must not
implement signature algorithms, curve arithmetic, RSA padding checks, digest
comparison logic, certificate validation, or signature parsing rules as custom
cryptographic primitives.

Permitted custom code is limited to:

```text
input validation
declared-root lookup
bounded-context checks
policy-field checks
calling cryptography verify APIs
mapping observed outcomes to sub-verdicts
attaching assumptions and reason codes
```

Any hand-rolled cryptographic primitive is:

```text
HAND_ROLLED_CRYPTO_DETECTED
NESIRA_PHASE2_SIGNATURE_ADAPTER_REJECTED_UNSAFE_CRYPTO
```

## Sub-Verdict Mapping

The core distinction is:

```text
TRUST_INSUFFICIENT:
  the relevant check was performed and failed

TRUST_NOT_EVALUATED:
  the relevant check could not be performed under the declared roots and context
```

Both are fail-closed. Neither may support composite sufficiency unless the other
three sub-assessments are also sufficient and this adapter is sufficient.

Required mapping:

```text
valid signature
+ declared root matches
+ root not expired
+ root not revoked
+ revocation confirmed fresh
+ clock available and declared
  -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

invalid signature
  -> TRUST_INSUFFICIENT

signature produced by a key that does not match the declared root
  -> TRUST_INSUFFICIENT

declared signing root missing
  -> TRUST_NOT_EVALUATED

declared signing root malformed or unsupported
  -> TRUST_NOT_EVALUATED

declared signing root expired
  -> TRUST_INSUFFICIENT

declared signing root revoked
  -> TRUST_INSUFFICIENT

revocation status unknown, stale, unreachable, or inconclusive
  -> TRUST_NOT_EVALUATED

clock missing, untrusted, or outside declared policy
  -> TRUST_NOT_EVALUATED

payload or signature malformed before verification can be attempted
  -> TRUST_NOT_EVALUATED

payload class outside declared root scope
  -> TRUST_INSUFFICIENT

subject, environment, purpose, or action outside declared root scope
  -> TRUST_INSUFFICIENT
```

The most important non-confusion rule is:

```text
missing root -> TRUST_NOT_EVALUATED
wrong root   -> TRUST_INSUFFICIENT
```

There is no default trust fallback.

## Assumption Carrying

Every adapter output must carry the unconditional floor from the trust ledger.

A sufficient signature sub-assessment must also carry the conditional
assumptions for the trust roots used:

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

Unknown revocation must carry:

```text
PT-REVOKE-03
```

The exact carried set for each failure fixture must be recorded in the
implementation report and verified by conformance tests.

## Required Fail-Closed Rules

The implementation must enforce:

```text
revocation_unknown -> not sufficient
clock_missing_or_untrusted -> not sufficient
no_declared_root -> not sufficient
wrong_declared_root -> not sufficient
expired_root -> not sufficient
revoked_root -> not sufficient
scope_mismatch -> not sufficient
```

No rule may map these states to:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

## No Default Trust

The adapter must not use:

```text
default operating-system trust store
default CA store
trust on first use
any valid signature
implicit signing authority
implicit key acceptance
```

Every successful result must be bound to:

```text
declared SIGNING_KEY root_id@version
```

## Conformance Corpus

The signature adapter conformance corpus must include a positive fixture and
mutation pairs for every safety-critical failure mode.

Required cases:

```text
valid_signature_declared_root_fresh_revocation
bad_signature
wrong_declared_root
missing_declared_root
malformed_declared_root
expired_declared_root
revoked_declared_root
revocation_unknown
revocation_stale
revocation_unreachable
clock_missing
clock_untrusted
payload_malformed
signature_malformed
payload_class_out_of_scope
subject_scope_mismatch
environment_scope_mismatch
purpose_scope_mismatch
action_scope_mismatch
```

Required metrics:

```text
required_signature_failure_modes_without_fixture: 0
required_signature_failure_modes_without_mutation_pair: 0
unexpected_sufficient_verdicts: 0
missing_root_mapped_to_insufficient: 0
wrong_root_mapped_to_not_evaluated: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
adapter_outputs_with_execution_semantics: 0
two_run_semantic_diff: 0
wheel_exclusion_failures: 0
```

## End-to-End Composition Check

The implementation must include an end-to-end conformance check:

```text
signature adapter output
+ identity_sub = TRUST_NOT_EVALUATED
+ authority_sub = TRUST_NOT_EVALUATED
+ isolation_sub = TRUST_NOT_EVALUATED
-> accepted Phase 2 composition core
```

Expected composite results:

```text
signature sufficient      -> composite TRUST_NOT_EVALUATED
signature not evaluated   -> composite TRUST_NOT_EVALUATED
signature insufficient    -> composite TRUST_INSUFFICIENT
```

This check verifies wiring only. It does not claim full Phase 2 sufficiency,
because the other three adapters remain unimplemented.

## Wheel Exclusion Requirement

The signature adapter, its fixtures, reports, and adapter-only crypto dependency
must remain excluded from the public wheel.

The implementation must verify:

```text
public wheel does not contain signature adapter modules
public wheel does not contain signature adapter fixtures
public wheel does not contain signature adapter reports
public wheel does not introduce cryptography as a product dependency
pyproject project.dependencies remains []
```

If the implementation location is under a source tree that may enter the public
wheel, the wheel exclusion mechanism must be inspected before writing code.

## Implementation Outputs

The implementation gate may create only the files needed for the signature
adapter, its fixtures, its conformance runner, and its report/review artifacts.

It must not modify:

```text
Formal Core V1
Domain4 Lean core
Nesira Phase 1 validator
Nesira Phase 2 trust model
Nesira Phase 2 trust ledger
Nesira Phase 2 decision table
Nesira Phase 2 Lean composition core
public CLI
combined verdict integration
```

## Stop Conditions

The implementation must stop on:

```text
HAND_ROLLED_CRYPTO_DETECTED
CRYPTOGRAPHY_NOT_PINNED
CRYPTOGRAPHY_ADDED_TO_PRODUCT_DEPENDENCIES
CRYPTOGRAPHY_ADDED_TO_PUBLIC_WHEEL
REVOCATION_UNKNOWN_SOFT_PASS
CLOCK_FAILURE_SOFT_PASS
DEFAULT_TRUST_USED
TOFU_USED
ANY_VALID_SIGNATURE_ACCEPTED
MISSING_ROOT_WRONGLY_MARKED_INSUFFICIENT
WRONG_ROOT_WRONGLY_MARKED_NOT_EVALUATED
ADAPTER_EMITS_EXECUTION
COMPOSITION_CORE_BYPASSED
FROZEN_SURFACE_MODIFIED
```

## Required Review

The implementation review must attack:

```text
1. Is the INSUFFICIENT vs NOT_EVALUATED mapping faithful to the trust model?
2. Is missing-root NOT_EVALUATED and wrong-root INSUFFICIENT?
3. Is cryptography pinned, gated, and absent from product dependencies?
4. Is there no hand-rolled crypto primitive?
5. Does SUFFICIENT carry PT-CRYPTO, PT-KEYLEGIT, PT-REVOKE, PT-CLOCK, and the floor?
6. Do revocation unknown, clock failure, and no declared root fail closed?
7. Is there no default trust, TOFU, or any-valid-signature path?
8. Does the adapter feed the composition core rather than bypass it?
9. Does the adapter output no execution or severance semantics?
10. Does conformance include mutation pairs for every required failure mode?
11. Does end-to-end wiring produce the expected composite result with the other three adapters NOT_EVALUATED?
12. Are the adapter and cryptography excluded from the public wheel?
```

## Status Lock

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
SIGNATURE_ADAPTER_ONLY
CRYPTOGRAPHY_PROPOSED_AND_MUST_BE_PINNED
PROJECT_DEPENDENCIES_REMAIN_EMPTY
PUBLIC_WHEEL_EXCLUSION_REQUIRED
NO_HAND_ROLLED_CRYPTO
MISSING_ROOT_NOT_EVALUATED
WRONG_ROOT_INSUFFICIENT
REVOCATION_UNKNOWN_NOT_EVALUATED
CLOCK_FAILURE_NOT_EVALUATED
NO_DEFAULT_TRUST
NO_TOFU
NO_ANY_VALID_SIGNATURE
ADAPTER_FEEDS_COMPOSITION_CORE
IDENTITY_ADAPTER_NOT_AUTHORIZED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
