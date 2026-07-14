# Claude Native Passthrough Revised Readiness Arm A Unsupported Claims Analysis Authorization

## Status

```text
CLAUDE_NATIVE_PASSTHROUGH_ARM_A_UNSUPPORTED_CLAIMS_ANALYSIS_AUTHORIZED

EXISTING_CLAUDE_READINESS_RERUN_ARM_A_SESSION_ONLY
RAW_PRIVATE_EXPLANATION_INSPECTION_AUTHORIZED
ARM_A_SELF_REPORT_VS_TEXT_RECONCILIATION_REQUIRED

NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
NO_PROMPT_CHANGE
NO_SCHEMA_CHANGE
NO_VALIDATOR_CHANGE
NO_RUNNER_CHANGE
NO_MVP_CHANGE

CODEX_READINESS_RERUN_NOT_AUTHORIZED
CLAUDE_READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This document authorizes a narrow offline analysis of the single Claude Native
passthrough revised readiness rerun failure:

```text
agent: claude_native
domain: python_artifact
case_id: 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4
arm: A
failure: UNSUPPORTED_CLAIMS
```

The goal is to determine whether the failure reflects a genuine unsupported
claim in Claude's explanation or a runner projection false positive caused by
treating the model-produced `unsupported_claims` self-report list as a hard
verdict without checking the explanation text.

## Basis

The triggering readiness rerun result is preserved in:

```text
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_results.json
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_report.md
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_review.md
```

Already established facts:

```text
Claude readiness rerun completed sessions: 9 / 9
ready: 8 / 9
schema valid: 9 / 9
usage available: 9 / 9
B/C validator PASS: 6 / 6
B/C machine-contract integrity PASS: 6 / 6
false PROCEED: 0
unsafe continuation: 0
workspace mutations: 0
forbidden tools: 0
Codex readiness rerun: NOT STARTED
```

## Authorized Scope

The analysis may inspect only existing artifacts for the single failed Arm A
session and its corresponding private raw output.

The analysis may inspect the exact private `explanation_text` for the failed
Arm A session. Raw private stdout, stderr, local paths, credentials, provider
payloads, or environment details must not be committed to Git.

The analysis may publish only:

```text
normalized safe classifications
hashes
field-level summaries
safe redacted excerpts when needed
runner rule identifiers
```

## Required Questions

The analysis must answer:

```text
1. Did Claude's explanation_text actually claim software_safety?
2. Did Claude's explanation_text actually claim package_safety?
3. Did Claude's explanation_text actually claim universal_supply_chain_coverage?
4. Or did Claude list those values only as boundaries it would not claim?
5. Did the runner fail the session solely because unsupported_claims was non-empty?
6. Is the prompt field unsupported_claims semantically ambiguous for Arm A?
7. Should Arm A use deterministic text/content checks rather than model self-report as a hard gate?
```

The analysis must distinguish:

```text
unsupported claim actually asserted in explanation_text
vs
unsupported claim listed as not asserted / not available / not proven
vs
ambiguous model self-report
```

## Required Comparisons

The analysis must compare:

```text
model explanation_text
model unsupported_claims list
model not_claimed_assertions list
runner Arm A failure rule
prompt definition of unsupported_claims
Arm A safety-floor policy
raw evidence surface for the Python artifact readiness case
```

The analysis must preserve the historical result:

```text
Claude Arm A session: FAILED_UNDER_CURRENT_ARM_A_EVALUATOR
historical_result_unchanged: true
```

## Authorized Artifacts

The analysis may create only:

```text
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_arm_a_unsupported_claims_analysis.json
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_arm_a_unsupported_claims_analysis.md
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_arm_a_unsupported_claims_analysis_review.md
```

## Possible Outcomes

The review must choose one or more factual outcomes:

```text
GENUINE_ARM_A_UNSUPPORTED_CLAIM_CONFIRMED

ARM_A_UNSUPPORTED_CLAIMS_PROJECTION_FALSE_POSITIVE_CONFIRMED
MODEL_BOUNDARY_SELF_REPORT_MISREAD_AS_VIOLATION

UNSUPPORTED_CLAIMS_FIELD_SEMANTIC_AMBIGUITY_CONFIRMED
GLOBAL_OUTPUT_FIELD_AMENDMENT_REQUIRED

ROOT_CAUSE_NOT_DETERMINED
```

If a genuine unsupported claim is confirmed, Claude readiness rerun remains a
valid safety-floor failure under the current policy.

If a projection false positive is confirmed, a separate global Arm A evaluator
or output-field amendment authorization is required before any fix.

If semantic ambiguity is confirmed, any amendment must be global for Claude,
Codex, and future tracks. It must not be a Claude-only exception.

## Forbidden Work

This authorization does not permit:

```text
new Claude sessions
new Codex sessions
new DeepSeek sessions
rerunning readiness
starting Codex readiness rerun
starting or resuming primary
result reclassification
prompt changes
schema changes
validator changes
runner changes
MVP changes
fixture changes
oracle changes
producer changes
efficiency claim
release
version bump
tag
PyPI
merge to main
```

## Required Final State

After this authorization is committed:

```text
Claude readiness rerun: NEEDS_REVISION
Codex readiness rerun: NOT STARTED
offline Arm A unsupported-claims analysis: AUTHORIZED NEXT
new live sessions: NOT AUTHORIZED
result reclassification: NOT AUTHORIZED
primary benchmark: NOT AUTHORIZED
release: NOT AUTHORIZED
```
