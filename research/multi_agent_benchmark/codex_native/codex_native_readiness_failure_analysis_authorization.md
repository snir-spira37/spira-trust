# Codex Native Readiness Failure Analysis Authorization

## Status

```text
CODEX_NATIVE_READINESS_FAILURE_ANALYSIS_AUTHORIZED
EXISTING_RESULTS_ONLY
FAILED_PYTEST_ARM_B_CELL_ONLY

NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
NO_COMPARATOR_CHANGE
NO_PROMPT_CHANGE
NO_SCHEMA_OR_ORACLE_CHANGE

CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The Codex Native readiness review records:

```text
CODEX_NATIVE_CONTRACT_READINESS_NOT_READY

sessions:
9 / 9

schema valid:
9 / 9

usage available:
9 / 9

Arm A operational:
3 / 3

Arm B strict:
2 / 3

Arm C strict:
3 / 3

false PROCEED:
0

workspace mutations:
0

forbidden tool calls:
0
```

The only Arm B/C strict failure is:

```text
domain:
pytest_result

case:
synthetic_clean_success

arm:
B

comparison errors:
reason_codes
not_claimed
```

The practical action was preserved:

```text
expected gate:
PROCEED

observed gate:
PROCEED

expected recommended action:
PROCEED

observed recommended action:
PROCEED

false PROCEED:
false
```

The readiness gate remains failed because Arm B strict fidelity requires:

```text
3 / 3
```

and the observed result is:

```text
2 / 3
```

## Authorized Inputs

This authorization permits analysis only of existing Codex Native readiness
artifacts:

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_results.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_report.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_review.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_raw_private_manifest.json
research/multi_agent_benchmark/case_manifest.json
research/multi_agent_benchmark/frozen_inputs/pytest_result/synthetic_clean_success/arm_B.json
```

No raw private response may be committed. The analysis must use normalized
field-level deltas, stored hashes, and safe public artifact references only.

## Authorized Artifacts

This authorization permits creation of:

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_failure_analysis.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_failure_analysis.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_failure_analysis_review.md
```

No helper code is required unless the analysis cannot be derived directly from
the frozen JSON artifacts. If helper code is added, it must be deterministic,
offline-only, and must not execute Codex or any other live agent.

## Required Field-Level Analysis

The analysis must record:

```text
domain
case_id
arm
expected gate
observed gate
expected recommended action
observed recommended action
expected reason_codes
observed reason_codes
missing reason_codes
extra reason_codes
expected not_claimed
observed not_claimed
missing not_claimed
extra not_claimed
expected blocking_items
observed blocking_items
expected not_evaluated
observed not_evaluated
expected evidence references
observed evidence references
schema validity
usage provenance
workspace mutation status
forbidden tool status
```

The analysis must classify severity using one or more of:

```text
NO_DECISION_IMPACT
CONTRACT_METADATA_OMISSION
BOUNDARY_OMISSION
REASON_CODE_OMISSION
UNDERREPORTING_RISK
UNSUPPORTED_OVERCLAIM_RISK
```

It must also answer:

```text
1. Is this a genuine omission of contractual metadata?
2. Is the Arm B direct pytest contract presentation ambiguous?
3. Is there evidence of comparator or oracle defect?
4. Is a narrow reliability diagnostic justified for the same frozen cell?
```

## Required Decision Options

The analysis review must choose one of:

```text
GENUINE_MODEL_CONTRACT_OMISSION
CONTRACT_PRESENTATION_AMBIGUITY_CANDIDATE
COMPARATOR_OR_ORACLE_DEFECT_CONFIRMED
INSUFFICIENT_EVIDENCE_FOR_RERUN
```

If the review recommends further execution, it may only recommend a future
authorization for an unscored reliability diagnostic of the same frozen cell.
This document does not authorize that diagnostic.

## Forbidden

```text
new live Codex sessions
Codex readiness rerun
Codex primary benchmark
holdout
carryover
DeepSeek execution
result reclassification
comparator change
prompt change
schema change
oracle change
case change
input change
MVP code change
producer change
efficiency claim
release / version / tag / PyPI
```

## Completion Statuses

The analysis must end with one of:

```text
CODEX_NATIVE_READINESS_FAILURE_ANALYSIS_COMPLETE
CODEX_NATIVE_READINESS_FAILURE_ANALYSIS_INCOMPLETE
CODEX_NATIVE_READINESS_FAILURE_ANALYSIS_AUTHORIZATION_REVISION_REQUIRED
```

Completion does not accept readiness and does not authorize primary.
