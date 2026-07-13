# Claude Native Readiness Reliability Diagnostic Authorization

## Status

```text
CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_AUTHORIZED
FAILED_CELLS_ONLY
UNSCORED_DIAGNOSTIC_SESSIONS_ONLY
MODEL_FROZEN
PROMPTS_FROZEN
CASES_FROZEN
SCHEMA_FROZEN
COMPARATOR_FROZEN
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The accepted failure analysis records:

```text
CLAUDE_NATIVE_READINESS_FAILURE_ANALYSIS_ACCEPTED
CLAUDE_NATIVE_READINESS_STILL_NEEDS_REVISION
```

Failure distribution:

```text
Arm A failures:
3

Arm B failures:
1

Arm C failures:
0
```

The critical failure is:

```text
domain:
pytest_result

case:
synthetic_clean_success

arm:
B

failure:
OUTPUT_NOT_OBJECT
```

Because Arm B is the direct compact-contract path, this must be diagnosed
before any primary benchmark authorization.

## Authorized Diagnostic Sessions

This authorization permits exactly 30 unscored diagnostic sessions:

```text
critical Arm B cell:
pytest_result synthetic_clean_success arm B
10 repetitions

failed Arm A cells:
pytest_result synthetic_clean_success arm A
5 repetitions

python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm A
5 repetitions

terraform_plan auth_no_changes arm A
5 repetitions

matched Arm C control:
pytest_result synthetic_clean_success arm C
5 repetitions
```

Total:

```text
30 diagnostic sessions
```

## Frozen Conditions

Every repetition must preserve:

```text
Claude model
Claude Code version
prompt bytes
input bytes
inline canonical schema
schema hash
tool allowlist
session isolation
comparison policy
expected oracle
```

Each repetition must use:

```text
fresh process
fresh session ID
no resume
no retry inside the same session
```

## Authorized Artifacts

Allowed files:

```text
tools/run_claude_native_reliability_diagnostic.py
tests/test_claude_native_reliability_diagnostic.py
research/multi_agent_benchmark/claude_native/claude_native_readiness_reliability_diagnostic_results.json
research/multi_agent_benchmark/claude_native/claude_native_readiness_reliability_diagnostic_report.md
research/multi_agent_benchmark/claude_native/claude_native_readiness_reliability_diagnostic_raw_private_manifest.json
```

## Required Measurements

Each session must record:

```text
return code
schema valid
output object present
exact action
reason codes
NOT_EVALUATED
blocking items
evidence references
tool calls
usage
failure classification
```

The report must summarize:

```text
OUTPUT_NOT_OBJECT recurrence count
schema-valid rate by cell
correctness rate by cell
usage availability
false PROCEED count
workspace mutation count
forbidden tool count
```

## Forbidden

```text
primary benchmark execution
holdout execution
carryover execution
prompt changes
case changes
schema changes
comparator changes
MVP code changes
producer changes
threshold changes
majority-vote acceptance
publishing raw private responses
efficiency claim
release / version / tag / PyPI
```

## Post-Diagnostic Branches

The diagnostic does not itself authorize readiness acceptance.

After review, one of the following branches may be authorized separately:

```text
full nine-session readiness rerun
global prompt / policy amendment
comparator fix
Claude native track blocked / not ready
```
