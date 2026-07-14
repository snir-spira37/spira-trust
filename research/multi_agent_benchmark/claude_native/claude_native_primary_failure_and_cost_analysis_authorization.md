# Claude Native Primary Failure And Cost Analysis Authorization

## Status

```text
CLAUDE_NATIVE_PRIMARY_FAILURE_AND_COST_ANALYSIS_AUTHORIZED
EXISTING_RESULTS_ONLY
NO_NEW_LIVE_SESSIONS

TWELVE_BC_BLOCKING_LIST_FAILURES_IN_SCOPE
FIELD_LEVEL_FAILURE_SEVERITY_ANALYSIS_AUTHORIZED
EXISTING_USAGE_AND_TOOL_TELEMETRY_ANALYSIS_AUTHORIZED

PROMPTS_FROZEN
CASES_FROZEN
INPUTS_FROZEN
SCHEMA_FROZEN
ORACLES_FROZEN
COMPARATOR_FROZEN
MVP_CODE_FROZEN
PRODUCERS_FROZEN

NO_RESULT_RECLASSIFICATION
NO_COMPARATOR_CHANGE
NO_PROMPT_CHANGE
NO_BENCHMARK_RERUN

CODEX_LIVE_READINESS_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The accepted Claude native primary benchmark review records:

```text
CLAUDE_NATIVE_PRIMARY_BENCHMARK_EXECUTION_COMPLETE
CLAUDE_NATIVE_PRIMARY_INFRASTRUCTURE_VALID
CLAUDE_NATIVE_ARM_A_RAW_EVIDENCE_LIMITATION_CONFIRMED
CLAUDE_NATIVE_ARM_B_STRICT_FIDELITY_GATE_NOT_ACCEPTED
CLAUDE_NATIVE_ARM_C_STRICT_FIDELITY_GATE_NOT_ACCEPTED
CLAUDE_NATIVE_PRIMARY_STRICT_CONTRACT_ACCEPTANCE_NOT_ACHIEVED
CLAUDE_NATIVE_PRIMARY_REVIEW_COMPLETE
```

The execution is valid infrastructure evidence:

```text
completed scored sessions:
180 / 180

schema valid:
180 / 180

usage available:
180 / 180

persistent infrastructure failures:
0
```

The strict contract result is not accepted:

```text
Arm B direct SPIRA:
57 / 60 strict fidelity

Arm C unified SPIRA:
51 / 60 strict fidelity

required:
60 / 60 for each strict contract arm
```

The review classifies all 12 Arm B/C strict failures as:

```text
BLOCKING_LIST_MISMATCH
```

No Arm B or Arm C session produced a false `PROCEED`.

## Authorized Inputs

This authorization permits analysis only of already captured Claude native
primary benchmark artifacts:

```text
research/multi_agent_benchmark/claude_native/claude_native_primary_results.json
research/multi_agent_benchmark/claude_native/claude_native_primary_report.md
research/multi_agent_benchmark/claude_native/claude_native_primary_session_manifest.json
research/multi_agent_benchmark/claude_native/claude_native_primary_raw_private_manifest.json
research/multi_agent_benchmark/claude_native/claude_native_primary_benchmark_review.md
```

No raw private responses may be committed. If a private response is needed to
explain a field-level delta, the analysis must use normalized deltas, safe short
excerpts when necessary, and hashes or manifest references.

## Authorized Artifacts

This authorization permits creation of:

```text
research/multi_agent_benchmark/claude_native/claude_native_primary_failure_matrix.json
research/multi_agent_benchmark/claude_native/claude_native_primary_cost_breakdown.json
research/multi_agent_benchmark/claude_native/claude_native_primary_failure_and_cost_analysis.md
research/multi_agent_benchmark/claude_native/claude_native_primary_failure_and_cost_analysis_review.md
```

The analysis may add narrow helper code or focused tests only if needed to
derive these artifacts from the frozen results. Any such helper must be
deterministic, offline-only, and must not execute Claude Code or any other live
agent.

## Failure Analysis Scope

For each of the 12 Arm B/C `BLOCKING_LIST_MISMATCH` sessions, the analysis must
compare the expected and observed `blocking_items` lists and classify the
mismatch using one or more of:

```text
ORDER_ONLY
DUPLICATE_ONLY
WORDING_OR_NORMALIZATION_ONLY
MISSING_ITEM
EXTRA_ITEM
ITEM_SUBSTITUTION
SEMANTIC_CONTRADICTION
```

Each mismatch must also receive a severity label:

```text
REPRESENTATION_ONLY
NO_DECISION_IMPACT
REMEDIATION_DETAIL_LOSS
UNDERBLOCKING_RISK
OVERBLOCKING_RISK
```

The analysis must distinguish:

```text
order-only or formatting-only candidates
missing blocker details
extra blocker details
substituted blocker details
contradictory blocker details
```

This authorization does not permit result reclassification. Comparator-defect
candidates may be identified but not applied.

## Required Failure Matrix Fields

The failure matrix must record, for each of the 12 Arm B/C failures:

```text
session_index
repetition
domain
case_id
arm
expected gate
observed gate
expected action
observed action
expected reason_codes
observed reason_codes
expected blocking_items
observed blocking_items
expected not_evaluated
observed not_evaluated
expected evidence references
observed evidence references
blocking_items_classification
severity
comparator_defect_candidate
prompt_or_contract_presentation_candidate
semantic_loss_candidate
```

The matrix must also explicitly confirm for these 12 sessions:

```text
false_proceed:
0

action_preserved:
true or false per session

stop_state_preserved:
true or false per session
```

## Cost Analysis Scope

The cost analysis may use only usage and telemetry fields already preserved in
the frozen primary results and manifests.

Where present, the analysis must break down:

```text
fresh input tokens
cached input tokens
cache creation tokens
output tokens
total input tokens
total tokens
provider cost
tool calls
files opened
raw bytes read
drill-down count
wall-clock duration
provider/API duration
```

If a field was not preserved in the frozen results, the analysis must record:

```text
NOT_EVALUATED
```

The analysis must not infer missing per-session timing, token, cost, tool, or
file data from scheduler runtime, aggregate wall-clock time, filenames, or
assumptions.

## Required Cost Cuts

The cost breakdown must compute the available metrics by:

```text
arm
domain
case
repetition
```

It must also compute paired comparisons:

```text
Arm C versus Arm B:
all 60 pairs

Arm C versus Arm B:
strict-equivalent pairs only

Arm C versus Arm A:
all 60 pairs as cost-and-fidelity comparison

Arm C versus Arm A:
split by Arm A operational pass/fail
```

The analysis must test whether any apparent Arm C cost advantage occurs only in
sessions where Arm C lost strict `blocking_items` fidelity.

## Efficiency Claim Boundary

The existing review records only descriptive token findings:

```text
Arm C versus Arm B median total-input overhead:
approximately -0.31%

Arm C versus Arm A median total-input reduction:
approximately 1.15%
```

This authorization does not permit a public efficiency claim. The analysis may
state descriptive measurements, confidence limitations, and missing telemetry
fields, but must keep:

```text
EFFICIENCY_CLAIM_NOT_AUTHORIZED
```

## Forbidden

```text
new live Claude sessions
Codex live readiness
Codex primary benchmark
DeepSeek live execution
holdout execution
carryover execution
benchmark rerun
hidden retry
prompt changes
case changes
input changes
schema changes
oracle changes
comparator changes
MVP code changes
producer changes
result reclassification
threshold changes
publishing raw private responses
efficiency claim
release / version / tag / PyPI
```

## Completion Statuses

The analysis must end with one of:

```text
CLAUDE_NATIVE_PRIMARY_FAILURE_COST_ANALYSIS_COMPLETE
CLAUDE_NATIVE_PRIMARY_FAILURE_COST_ANALYSIS_INCOMPLETE
CLAUDE_NATIVE_PRIMARY_FAILURE_COST_ANALYSIS_AUTHORIZATION_REVISION_REQUIRED
```

A successful analysis may report:

```text
STRICT_CONTRACT_FAILURE_MODE_CLASSIFIED
B_C_ACTION_AND_SAFETY_PRESERVATION_CONFIRMED
TOKEN_EFFICIENCY_CLAIM_REMAINS_NOT_AUTHORIZED
```

## Required Review

The analysis review must decide whether the evidence supports one of:

```text
COMPARATOR_DEFECT_CANDIDATE_CONFIRMED
GENUINE_BLOCKING_DETAIL_LOSS_CONFIRMED
PROMPT_OR_CONTRACT_PRESENTATION_WEAKNESS_CONFIRMED
INSUFFICIENT_EVIDENCE_FOR_AMENDMENT
```

No comparator amendment, prompt amendment, benchmark rerun, Codex readiness, or
Codex primary execution is authorized by this document.
