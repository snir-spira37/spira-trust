# Codex Native Cross-Arm Metadata Omission Analysis Authorization

## Status

```text
CODEX_NATIVE_CROSS_ARM_METADATA_OMISSION_ANALYSIS_AUTHORIZED

EXISTING_RESULTS_ONLY

PYTEST_CLEAN_SUCCESS_ARM_B_AND_ARM_C_ONLY

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PROMPT_CHANGE

NO_SCHEMA_CHANGE

NO_ORACLE_CHANGE

NO_COMPARATOR_CHANGE

NO_INPUT_CHANGE

CODEX_PRIMARY_NOT_AUTHORIZED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Purpose

Determine why the same contractual metadata omission was observed across both
direct and unified SPIRA contracts for:

```text
domain:
pytest_result

case:
synthetic_clean_success
```

The omitted fields were:

```text
reason_codes:
TESTS_PASSED

not_claimed:
producer_correctness
software_safety
```

The analysis must distinguish between:

```text
MODEL_SERIALIZATION_VARIABILITY

GLOBAL_CONTRACT_PRESENTATION_AMBIGUITY

SCHEMA_CONTENT_ENFORCEMENT_LIMITATION

PROMPT_CONTRACT_PRESERVATION_WEAKNESS

OTHER_CROSS_ARM_CAUSE
```

No finding may reclassify an existing readiness or diagnostic result.

## Evidence in Scope

Analyze only existing frozen evidence from:

```text
original Codex readiness Arm B failure

Codex readiness failure analysis

10 / 10 Arm B diagnostic successes

4 / 5 Arm C diagnostic successes

the single Arm C metadata omission

frozen Arm B input

frozen Arm C input

shared prompt

shared output schema

expected oracle

accepted comparator

public normalized results

private raw evidence only where separately authorized
and without publishing private paths or raw responses
```

## Required Input Comparison

Compare Arm B and Arm C at field level.

For each arm, record:

```text
location of reason_codes in the input

location of not_claimed in the input

distance from the requested output contract

nesting depth

field ordering

surrounding explanatory text

presence of duplicate or competing representations

whether the fields appear as authoritative machine values

whether the prompt explicitly requires verbatim preservation

whether the model is asked to infer, summarize or regenerate them
```

## Schema Analysis

Determine whether the output schema requires:

```text
field presence

array type

minimum item count

specific enum values

exact expected content

additional-items restrictions
```

The analysis must clearly distinguish:

```text
schema-valid output

from

oracle-exact output
```

If the schema requires the fields but does not encode their expected contents,
record:

```text
SCHEMA_ENFORCES_STRUCTURE_NOT_INSTANCE_CONTENT
```

This is not automatically a schema defect.

## Prompt Analysis

Inspect whether the shared prompt clearly requires:

```text
copying contractual fields without omission

preserving reason_codes exactly

preserving not_claimed exactly

not summarizing contractual metadata

not replacing machine fields with natural-language explanation
```

Do not amend the prompt under this authorization.

Record only whether the current wording is:

```text
EXPLICIT_AND_UNAMBIGUOUS

EXPLICIT_BUT_LOW_SALIENCE

IMPLICIT

AMBIGUOUS

CONFLICTING_WITH_OTHER_INSTRUCTIONS
```

## Cross-Arm Failure Comparison

Produce a normalized comparison of:

```text
original Arm B failure

Arm C diagnostic failure
```

For each failure, record:

```text
expected action
observed action

expected stop state
observed stop state

expected reason_codes
observed reason_codes

expected not_claimed
observed not_claimed

blocking_items
not_evaluated

schema validity
usage availability
false PROCEED
unsupported inference
```

Determine whether the two omissions are:

```text
SEMANTICALLY_IDENTICAL

STRUCTURALLY_IDENTICAL

PARTIALLY_MATCHING

UNRELATED
```

## Architectural Interpretation

Evaluate the following hypothesis:

```text
SPIRA machine contract is reliable as stored evidence.

LLM regeneration of the contract is not guaranteed
to preserve every contractual field at 100%.
```

The analysis must distinguish:

```text
contract source integrity

contract transport integrity

model-read comprehension

model-generated serialization fidelity
```

No failure may be attributed to SPIRA contract integrity unless the frozen source
contract itself is shown to be missing, contradictory or malformed.

## Required Artifacts

Create:

```text
codex_native_cross_arm_metadata_omission_analysis.json

codex_native_cross_arm_metadata_omission_analysis.md

codex_native_cross_arm_metadata_omission_analysis_review.md
```

The JSON artifact must include:

```text
evidence inventory

Arm B and C input-field locations

prompt findings

schema findings

failure comparison

root-cause candidates

confirmed findings

not-confirmed findings

recommended next branch
```

## Permitted Terminal Findings

### Global presentation weakness confirmed

```text
GLOBAL_CONTRACT_PRESENTATION_WEAKNESS_CONFIRMED

CROSS_ARM_METADATA_OMISSION_EXPLAINED_BY_SHARED_PRESENTATION

GLOBAL_CONTRACT_PRESENTATION_AMENDMENT_REQUIRED
```

Any amendment must apply to:

```text
Claude
Codex
DeepSeek
all future agent tracks
```

It must not be Codex-specific.

### Presentation ambiguity remains only a candidate

```text
CONTRACT_PRESENTATION_AMBIGUITY_REMAINS_CANDIDATE

MODEL_SERIALIZATION_VARIABILITY_CONFIRMED

CODEX_NATIVE_STRICT_METADATA_RELIABILITY_NOT_READY
```

Under this outcome:

```text
Codex primary remains blocked.
```

### Schema limitation identified but not defective

```text
SCHEMA_ENFORCES_STRUCTURE_NOT_ORACLE_CONTENT

MODEL_INSTANCE_CONTENT_OMISSION_CONFIRMED

NO_SCHEMA_DEFECT_CONFIRMED
```

This outcome does not authorize weakening the comparator.

### Contract or oracle defect confirmed

```text
GLOBAL_CONTRACT_OR_ORACLE_DEFECT_CONFIRMED
```

This outcome requires a separate global amendment proposal and review.

Existing results remain historical and are not silently reclassified.

## Final Boundary

This authorization permits only offline analysis of existing evidence.

It does not authorize:

```text
new Codex sessions

full readiness rerun

Codex primary

prompt editing

schema editing

oracle editing

comparator relaxation

contract rewriting

MVP or producer changes

holdout

carryover

efficiency claims

release
```

The purpose of this analysis is to determine whether there is a shared
presentation weakness that can be corrected globally, or whether the finding is a
basic limitation of a language model that understands the action but is not a
deterministic serializer of a machine contract.
