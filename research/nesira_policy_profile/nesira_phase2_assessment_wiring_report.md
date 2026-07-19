# Nesira Phase 2 Assessment Wiring Report

## Status

```text
NESIRA_PHASE2_ASSESSMENT_WIRING_IMPLEMENTED
ACCEPTED_PENDING_COLD_VERIFICATION
```

This gate implements internal Phase 2 assessment wiring only.

It connects:

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
accepted 81-row composition oracle
```

and returns one internal assessment artifact.

It does not implement a runner, combined verdict integration, CLI, public wheel
exposure, public claim, or release.

## Files Added

```text
source/spira_core/nesira_phase2_assessment_wiring.py
source/spira_core/nesira_phase2_assessment_wiring_harness.py
tools/run_nesira_phase2_assessment_wiring_conformance.py
tests/test_nesira_phase2_assessment_wiring.py
research/nesira_policy_profile/nesira_phase2_assessment_wiring_results.json
research/nesira_policy_profile/nesira_phase2_assessment_wiring_report.md
research/nesira_policy_profile/nesira_phase2_assessment_wiring_review.md
```

## Local Result

```text
NESIRA_PHASE2_ASSESSMENT_WIRING_ACCEPTED
```

Required metrics:

```text
wiring_rows_checked: 81
wiring_oracle_disagreements: 0
cross_subject_mismatch_produced_sufficient: 0
outputs_missing_floor: 0
sufficient_outputs_missing_pt_isolation_01: 0
outputs_with_forbidden_semantics: 0
two_run_semantic_diff: 0
```

## Context Boundary

The wiring uses one caller-supplied `expected_context` and passes it to all
four adapters.

The `cross_subject_mismatch` fixture mutates multiple evidence artifacts so
they point at different candidates or subjects while the caller context expects
one subject. The result is:

```text
composite verdict: TRUST_INSUFFICIENT
not sufficient: true
```

## Composition Boundary

The wiring composes only sub-verdicts:

```text
signature_sub
identity_sub
authority_sub
isolation_sub
```

The oracle check covers all 81 rows and reports zero disagreements.

## Output Boundary

The output marker remains:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

The output does not contain action fields, product combined verdict fields, CLI
fields, or public release claims.

## Required Next Step

```text
NESIRA_PHASE2_ASSESSMENT_WIRING_COLD_VERIFICATION_REQUIRED
```

