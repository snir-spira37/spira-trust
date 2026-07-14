# Codex Native Readiness Reliability Diagnostic Authorization

## Status

```text
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_AUTHORIZED

FAILED_PYTEST_ARM_B_CELL_ONLY
MATCHED_ARM_C_CONTROL_ONLY
FIFTEEN_UNSCORED_DIAGNOSTIC_SESSIONS_ONLY

MODEL_FROZEN
CODEX_CLI_VERSION_FROZEN
REASONING_EFFORT_FROZEN
PROMPTS_FROZEN
INPUTS_FROZEN
SCHEMA_FROZEN
ORACLE_FROZEN
COMPARATOR_FROZEN
GLOBAL_ARM_A_POLICY_FROZEN

NO_RESULT_RECLASSIFICATION
NO_PRIMARY_SESSIONS

CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The Codex Native readiness result is:

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

The accepted failure analysis finds:

```text
GENUINE_MODEL_CONTRACT_OMISSION
CONTRACT_PRESENTATION_AMBIGUITY_CANDIDATE_RECORDED
COMPARATOR_OR_ORACLE_DEFECT_NOT_CONFIRMED
```

The failed strict cell is:

```text
domain:
pytest_result

case_id:
synthetic_clean_success

arm:
B
```

The omitted metadata is:

```text
reason_codes:
TESTS_PASSED

not_claimed:
producer_correctness
software_safety
```

The practical decision was preserved:

```text
gate:
PROCEED

recommended action:
PROCEED

false PROCEED:
false
```

This authorization tests whether the omission recurs under the same frozen
conditions. It does not alter the original readiness result.

## Authorized Diagnostic Sessions

Execute exactly 15 unscored diagnostic sessions:

```text
failed Arm B cell:
pytest_result / synthetic_clean_success / B
10 fresh repetitions

matched Arm C control:
pytest_result / synthetic_clean_success / C
5 fresh repetitions
```

No other domain, case, arm, holdout, carryover, or primary session is authorized.

## Frozen Conditions

Every diagnostic session must preserve:

```text
exact resolved Codex model ID:
gpt-5.5

Codex CLI version:
codex-cli 0.130.0-alpha.5

reasoning effort:
xhigh

input hashes
prompt hashes
output schema
case manifest expected values
frozen comparator behavior
global Arm A policy
MVP code
producer code
```

The diagnostic may reuse the accepted Codex readiness runner mechanics, but it
must not change:

```text
prompt text
frozen input files
schema
local validation policy
comparison policy
model configuration
reasoning effort
read-only sandbox requirement
usage provenance requirement
```

## Session Requirements

Each diagnostic session must use:

```text
fresh process
fresh session identifier
fresh config/session directory
fresh workspace
no resume
no conversation history
no hidden retry for semantic failure
no concurrent live agent benchmark
read-only sandbox
structured JSONL output
turn.completed.usage
```

Retries are permitted only for identified provider, transport, or rate-limit
failures against the same frozen cell. A retry may not replace a semantically
incorrect completed answer.

## Required Artifacts

Produce:

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_results.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_report.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_raw_private_manifest.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_review.md
```

The raw private manifest must not publish raw model output. It must record only
safe hashes, byte sizes, logical cell IDs, and outside-repository storage
markers.

## Required Measurements

For every diagnostic session, record:

```text
domain
case_id
arm
diagnostic repetition
schema valid
structured output present
result envelope present
expected reason_codes
observed reason_codes
missing reason_codes
expected not_claimed
observed not_claimed
missing not_claimed
action preserved
stop state preserved
blocking_items preserved
not_evaluated preserved
false PROCEED
usage availability
turn.completed.usage values
workspace mutation status
forbidden tool status
```

## Success And Stop Rules

If the failed Arm B cell passes:

```text
10 / 10 exact
```

and the matched Arm C control passes:

```text
5 / 5 exact
```

then the diagnostic review may record:

```text
ORIGINAL_ARM_B_OMISSION_NOT_REPRODUCED
FULL_NINE_CELL_CODEX_READINESS_RERUN_JUSTIFIED
```

This still does not authorize Codex primary.

If the Arm B cell fails even once:

```text
CODEX_NATIVE_DIRECT_CONTRACT_RELIABILITY_NOT_READY
CONTRACT_PRESENTATION_AMBIGUITY_STRENGTHENED
CODEX_PRIMARY_NOT_AUTHORIZED
```

If infrastructure prevents completion:

```text
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INFRASTRUCTURE_BLOCKED
```

## Forbidden

```text
Codex primary benchmark
readiness result reclassification
full nine-cell readiness rerun
holdout
carryover
DeepSeek execution
prompt changes
input changes
schema changes
oracle changes
comparator changes
case changes
MVP code changes
producer changes
efficiency claim
release / version / tag / PyPI
```

## Completion Statuses

The diagnostic must end with one of:

```text
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INCOMPLETE
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_INFRASTRUCTURE_BLOCKED
CODEX_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_AUTHORIZATION_REVISION_REQUIRED
```

Completion does not accept readiness and does not authorize primary.
