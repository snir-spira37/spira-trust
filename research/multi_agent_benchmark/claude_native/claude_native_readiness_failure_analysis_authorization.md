# Claude Native Readiness Failure Analysis Authorization

## Status

```text
CLAUDE_NATIVE_READINESS_FAILURE_ANALYSIS_AUTHORIZED
EXISTING_RESULTS_ANALYSIS_ONLY
NO_NEW_LIVE_SESSIONS
PROMPTS_FROZEN
CASES_FROZEN
SCHEMA_FROZEN
COMPARISON_POLICY_FROZEN
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The accepted Claude native readiness review records:

```text
CLAUDE_NATIVE_READINESS_NEEDS_REVISION
CLAUDE_NATIVE_READINESS_REVIEW_COMPLETE
SCHEMA_TRANSPORT_FIX_ACCEPTED
```

The readiness run is a real agent readiness result:

```text
sessions:
9 / 9 executed

schema valid:
8 / 9

correct:
5 / 9

usage available:
9 / 9

false PROCEED:
0

workspace mutations:
0

forbidden tool calls:
0
```

## Authorized Work

This authorization permits analysis only of the already captured readiness
results.

Allowed artifacts:

```text
research/multi_agent_benchmark/claude_native/claude_native_readiness_failure_matrix.json
research/multi_agent_benchmark/claude_native/claude_native_readiness_failure_analysis.md
```

Allowed inputs:

```text
research/multi_agent_benchmark/claude_native/claude_native_readiness_results.json
research/multi_agent_benchmark/claude_native/claude_native_readiness_report.md
research/multi_agent_benchmark/claude_native/claude_native_readiness_raw_private_manifest.json
```

## Required Matrix Fields

Each of the 9 readiness cells must record:

```text
case_id
domain
arm
schema_valid
expected action
observed action
expected reason_codes
observed reason_codes
expected NOT_EVALUATED
observed NOT_EVALUATED
expected blocking_items
observed blocking_items
expected evidence references
observed evidence references
tool calls
files opened
usage
failure classification
```

## Failure Classifications

Each mismatch must be classified using one or more of:

```text
OUTPUT_SCHEMA_NONCOMPLIANCE
ACTION_MISMATCH
REASON_CODE_LOSS
REASON_CODE_ADDITION
NOT_EVALUATED_LOSS
NOT_EVALUATED_ADDITION
BLOCKING_LIST_MISMATCH
EVIDENCE_REFERENCE_MISMATCH
UNSUPPORTED_OVERCLAIM
PROMPT_AMBIGUITY_CANDIDATE
COMPARATOR_DEFECT_CANDIDATE
MODEL_CONTRACT_FAILURE
```

## Forbidden

```text
new live sessions
primary benchmark execution
holdout execution
carryover execution
prompt changes
case changes
schema changes
comparison-policy changes
MVP code changes
producer changes
threshold changes
publishing raw private responses
efficiency claim
release / version / tag / PyPI
```

## Required Review

After analysis, a separate review must decide the next branch:

```text
comparator fix
global prompt amendment
reliability diagnostic
track blocked/not ready
```

No branch is authorized by this document.
