# Nesira Phase 2 Assessment Wiring Implementation Plan

## Status

```text
DOCUMENT_TYPE: IMPLEMENTATION_PLAN
PHASE: PHASE_2
SCOPE: INTERNAL_ASSESSMENT_WIRING_ONLY
IMPLEMENTATION: NOT_STARTED
SIGNATURE_ADAPTER: FROZEN_BASELINE
IDENTITY_ADAPTER: FROZEN_BASELINE
AUTHORITY_ADAPTER: FROZEN_BASELINE
ISOLATION_ATTESTATION_ADAPTER: FROZEN_BASELINE
COMPOSITION_CORE: FROZEN_BASELINE
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This plan prepares implementation of the internal Phase 2 assessment wiring
gate only.

The wiring will call the four accepted adapters, collect their sub-verdicts,
compose them by the accepted 81-row decision table, and emit one internal
assessment artifact.

It will not execute severance, produce permission to sever, expose a CLI, enter
the public wheel, or connect to any combined verdict surface.

## Implementation Shape

The implementation should mirror the accepted adapter gate shape:

```text
source/spira_core/nesira_phase2_assessment_wiring.py
source/spira_core/nesira_phase2_assessment_wiring_harness.py
tools/run_nesira_phase2_assessment_wiring_conformance.py
tests/test_nesira_phase2_assessment_wiring.py
research/nesira_policy_profile/nesira_phase2_assessment_wiring_results.json
research/nesira_policy_profile/nesira_phase2_assessment_wiring_report.md
research/nesira_policy_profile/nesira_phase2_assessment_wiring_review.md
```

Cold verification should later add:

```text
research/nesira_policy_profile/nesira_phase2_assessment_wiring_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_assessment_wiring_cold_verification_review.md
```

The public wheel builder is allowlist-based. The wiring module and harness must
not be added to the allowlist.

## Accepted Inputs

The wiring input is a caller-supplied assessment request containing:

```text
expected_context
signature_payload
signature_evidence
signature_root
identity_credential
identity_roots
authority_policy_source
authority_root
attestation_evidence
attestation_root
now_utc
```

The exact fixture shape may remain deliberately small, but each field must be
caller supplied. Expected candidate, environment, action, identity, authority
purpose, and attestation profile values must not be learned from evidence.

There is exactly one `expected_context` for the assessment request. The wiring
must pass that same object to all four adapters. It must not construct
per-adapter expected contexts or allow evidence from one adapter to define the
expected subject for another adapter.

## Adapter Invocation Order

The wiring should invoke adapters in dependency order:

```text
1. signature adapter
2. identity adapter
3. authority adapter
4. isolation attestation adapter
5. composition
```

The authority adapter consumes the already-established identity context and the
identity sub-verdict. It must not re-verify identity credentials.

The composition step consumes only the four sub-verdict outputs.

## Composition Algorithm

The implementation must use the accepted 81-row oracle:

```text
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

The recommended implementation is:

```text
load oracle rows
build key from four adapter sub-verdicts
select exactly one row
copy composite_verdict and execution_marker from the row
construct per_domain_breakdown from adapter outputs
construct assumptions and roots from adapter outputs according to the row
```

Hard requirements:

```text
row lookup count for exhaustive conformance: 81
duplicate oracle keys: 0
missing oracle keys: 0
oracle disagreements: 0
```

## Output Contract

The wiring output must contain:

```text
verdict
per_domain_breakdown
sub_assessments
trust_roots_used
assumptions
checked_facts
gaps
not_evaluated_items
blocking_items
evidence_references
reason_codes
execution_marker
```

The output must not contain:

```text
proceed
sever
execute
permission verdict fields
safety-to-sever verdict fields
combined_verdict
agent_action
```

The required marker is:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## Assumption Carrying

The output assumptions must be:

```text
floor assumptions
union of assumptions from all evaluated sub-assessments
```

The sufficient composite fixture must prove:

```text
PT-ISOLATION-01 in assumptions
assumptions is not empty
all four sub-assessment assumption sets included
```

If any assumption required by the oracle row is missing, the harness must fail.

## Trust Roots Used

`trust_roots_used` must be the deterministic union of declared roots used by
the four adapters:

```text
root_id@version
```

Ordering must be canonical and stable. Missing roots remain visible through
per-domain gaps and not-evaluated items.

## Failure Handling

Adapter exceptions, malformed adapter outputs, unknown sub-verdicts, missing
execution markers, or execution-looking adapter outputs must fail closed:

```text
affected domain -> TRUST_NOT_EVALUATED
reason code -> ASSESSMENT_WIRING_SUB_RESULT_MALFORMED
composite -> not sufficient unless another domain is explicitly insufficient
```

The wiring must not silently skip a failed adapter, reuse stale results, or
upgrade an unknown result.

## Conformance Corpus

The harness must include:

```text
all_four_sufficient
signature_insufficient
identity_insufficient
authority_insufficient
attestation_insufficient
signature_not_evaluated
identity_not_evaluated
authority_not_evaluated
attestation_not_evaluated
mixed_insufficient_and_not_evaluated
malformed_adapter_result
missing_caller_context
cross_subject_mismatch
```

The `cross_subject_mismatch` fixture must use one caller-supplied
`expected_context` while at least two evidence artifacts point at different
candidates or subjects. At least one adapter must return `TRUST_INSUFFICIENT`,
and the composite verdict must be not sufficient.

Required checks:

```text
all 81 oracle rows reproduced
strict AND respected
INSUFFICIENT dominates NOT_EVALUATED
cross-subject mismatch produces not sufficient
floor carried on every output
PT-ISOLATION-01 carried on sufficient composite row
per-domain breakdown preserved
reason codes preserve source domains
two-run semantic diff: 0
outputs with execution or severance semantics: 0
```

## Boundary Checks

The local and cold verification must run:

```text
python tools/run_nesira_phase2_assessment_wiring_conformance.py --write-results
python -m pytest tests/test_nesira_phase2_assessment_wiring.py -q
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_nesira_phase2_authority_adapter.py tests/test_nesira_phase2_isolation_attestation_adapter.py tests/test_nesira_phase2_assessment_wiring.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m pytest -q
python -m compileall -q source tools tests
```

The cold verification must also check:

```text
V1 SHA256SUMS: 622/622
git diff --check
no local path or secret hits
public wheel excludes wiring, adapters, harnesses, and adapter crypto dependency
pyproject.toml unchanged with dependencies = []
requirements unchanged unless separately authorized
lakefile and V1 manifest unchanged
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if:

```text
the wiring needs a new trust root kind
the wiring needs a new adapter verdict
the wiring needs to reinterpret an adapter result
the 81-row oracle is insufficient
caller context cannot be separated from evidence
an output can be read as permission to sever
combined verdict, CLI, wheel exposure, or release is touched
```

## Acceptance Target

The implementation may be accepted only after cold verification from a fresh
clone returns:

```text
NESIRA_PHASE2_ASSESSMENT_WIRING_COLD_VERIFICATION_ACCEPTED
```

Until then:

```text
ASSESSMENT_WIRING_IMPLEMENTATION_NOT_ACCEPTED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
