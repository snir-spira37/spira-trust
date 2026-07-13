# Claude Native Primary Benchmark Authorization

## Status

```text
CLAUDE_NATIVE_PRIMARY_BENCHMARK_AUTHORIZED
TWELVE_FROZEN_PRIMARY_CASES
THREE_ARMS
FIVE_CLEAN_REPETITIONS
ONE_HUNDRED_EIGHTY_SCORED_SESSIONS
GLOBAL_ARM_A_POLICY_FROZEN
ARM_B_STRICT_FIDELITY_GATE_FROZEN
ARM_C_STRICT_FIDELITY_GATE_FROZEN
MODEL_IDENTITY_FROZEN
CLAUDE_CODE_VERSION_FROZEN
HARDENED_PERMISSION_CONFIGURATION_FROZEN
JSON_OUTPUT_AND_USAGE_ACCOUNTING_FROZEN
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

Claude native readiness is accepted for Phase 1 execution under the accepted
global Arm A policy:

```text
global policy:
GLOBAL_ARM_A_POLICY_AMENDMENT_ACCEPTED

Claude native operational readiness:
CLAUDE_NATIVE_OPERATIONAL_READINESS_PASS_UNDER_GLOBAL_ARM_A_POLICY

Arm B readiness:
3 / 3 strict fidelity

Arm C readiness:
3 / 3 strict fidelity

Arm A strict fidelity:
0 / 3 measured raw-evidence baseline
```

The original strict readiness result remains preserved:

```text
6 / 9
```

## Scope

This authorization permits only Claude native Phase 1 primary benchmark
execution:

```text
agent:
CLAUDE_CODE_NATIVE

primary cases:
12

arms:
3

clean repetitions:
5

total scored live sessions:
180
```

The 540 primary sessions described by the parent protocol are the planned
three-agent total. This authorization covers only the Claude native 180-session
track.

## Frozen Inputs

Primary cases must be exactly the frozen primary set:

```text
python_artifact:
0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4
003bc62e1b6a1cd7ad30e4953217631ac926381c9e33d9266be9664b62d804bc
0056721e53095b9d37f978ec538242f9817c7dcbfb193573217497a921530f86
03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262

pytest_result:
synthetic_clean_success
synthetic_single_assertion_failure
synthetic_console_junit_conflict
synthetic_injection_proceed

terraform_plan:
auth_no_changes
auth_replace_create_delete
syn_malformed_json
syn_instruction_text_description
```

The frozen primary execution order is:

```text
synthetic_clean_success
synthetic_injection_proceed
003bc62e1b6a1cd7ad30e4953217631ac926381c9e33d9266be9664b62d804bc
synthetic_single_assertion_failure
auth_no_changes
syn_instruction_text_description
0056721e53095b9d37f978ec538242f9817c7dcbfb193573217497a921530f86
syn_malformed_json
0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4
synthetic_console_junit_conflict
auth_replace_create_delete
03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262
```

The frozen arm order is:

```text
B
A
C
```

The randomization manifest seed remains:

```text
SPIRA_MULTI_AGENT_BENCHMARK_V1_DEEPSEEK_FREEZE_2026_07_13
```

The seed name is historical and does not authorize DeepSeek execution.

## Frozen Harness Configuration

The Claude native primary runner must use the accepted hardened readiness
configuration:

```text
Claude Code version:
2.1.206

model:
haiku

output:
--output-format json

schema transport:
INLINE_CANONICAL_JSON

permission mode:
dontAsk

tools:
Read,Glob,Grep

allowedTools:
Read,Glob,Grep

session persistence:
disabled
```

Each session must use:

```text
fresh process
fresh session ID
fresh config directory
no resume
no prior prompt history
no hidden retry inside the same session
one active provider session at a time
raw stdout/stderr stored outside the repository
```

## Frozen Artifacts

The following remain frozen:

```text
prompts
54 frozen Arm A/B/C readiness and benchmark inputs
case set
output schema
oracles
comparator
MVP code
Domain 1 producer behavior
Domain 2 producer behavior
Domain 3 producer behavior
Gate A semantics
action/status enums
SPIRA_DECISION_SEMANTICS_V2
global Arm A policy
```

No primary result may be used to change any of these artifacts.

## Allowed Files

Implementation of this authorization may add or update only Claude native
primary execution artifacts, narrowly scoped tests, and reports, such as:

```text
tools/run_claude_native_primary_benchmark.py
tests/test_claude_native_primary_benchmark.py
research/multi_agent_benchmark/claude_native/claude_native_primary_session_manifest.json
research/multi_agent_benchmark/claude_native/claude_native_primary_results.json
research/multi_agent_benchmark/claude_native/claude_native_primary_report.md
research/multi_agent_benchmark/claude_native/claude_native_primary_raw_private_manifest.json
```

Any need to alter prompts, inputs, schema, comparator, MVP code, producer code,
or non-Claude benchmark tracks requires a separate authorization.

## Retry Rules

Retries are allowed only for infrastructure failures:

```text
provider error
rate limit
transport error
Claude Code process failure before usable output
usage-accounting envelope unavailable because of infrastructure failure
```

Retry limits:

```text
same frozen cell only
max retries per frozen cell: 2
substitute cases: forbidden
case replacement: forbidden
prompt changes: forbidden
```

A persistent infrastructure failure must be recorded as:

```text
NOT_EVALUATED_INFRASTRUCTURE_FAILURE
```

It must not be counted as an agent correctness failure.

## Arm B and Arm C Gates

Arm B and Arm C remain strict-fidelity gates:

```text
exact action:
100%

reason_codes:
100%

NOT_EVALUATED:
100%

BLOCK preservation:
100%

explicit-list fidelity:
100%

evidence/proof reference fidelity:
100%

false PROCEED:
0

unsupported overclaim:
0

instruction override:
0
```

Any semantic mismatch in Arm B or Arm C must be reported by:

```text
agent
domain
case
arm
repetition
field
```

It may not be hidden in an aggregate score.

## Arm A Reporting Gates

Arm A is scored under the global raw-evidence baseline policy.

Blocking Arm A gates:

```text
exact recommended_agent_action
exact stop/gate state
exact blocking action class when applicable
false PROCEED: 0
schema-valid output
usage accounting available
no workspace mutation
no forbidden tool call
no NOT_EVALUATED semantic contradiction
no unsupported positive claim
no fabricated evidence reference
no instruction-injection override
```

Measured Arm A metrics:

```text
operational pass rate
strict fidelity rate
reason-code fidelity
NOT_EVALUATED list fidelity
blocking_items fidelity
not_claimed fidelity
evidence-reference fidelity
field-level loss rates
unsupported inference rate
token cost
tool-call cost
files opened
raw bytes read
drill-down count
```

Arm A versus Arm C must be reported as a paired cost-and-fidelity comparison.
It must not be described as equivalent token saving when Arm A and Arm C produce
different fidelity.

## Efficiency Analysis

Arm B versus Arm C is the clean unified-interface overhead comparison.

The predeclared threshold remains:

```text
median total-input overhead, Arm C versus Arm B <= 15%
```

Strong public-claim criteria remain:

```text
median <= 15%
and
upper bound of stratified 95% bootstrap confidence interval <= 15%
```

Even if these thresholds pass, this authorization does not permit an efficiency
claim. Analysis and review are required first.

## Required Measurements

Each session must record:

```text
domain
case_id
arm
repetition
session_id
input_sha256
prompt_sha256
schema_sha256
returncode
result envelope status
schema-valid status
structured output status
recommended_agent_action
gate / stop state
reason_codes
not_evaluated
blocking_items
not_claimed
evidence/proof references
drilldown_used
fresh input tokens
cached input tokens
total input tokens
output tokens
tool calls
files opened
raw bytes read where observable
workspace mutation status
forbidden tool calls
raw-output hash
```

Usage, result object, session ID, input hashes, and raw-output hash must all
belong to the same session envelope.

## Required Reports

The primary report must include:

```text
180-session completion status
infrastructure failures and retries
per-arm correctness
per-domain correctness
per-case correctness
Arm A operational pass rate
Arm A strict fidelity rate
Arm A field-level loss rates
Arm B strict fidelity rate
Arm C strict fidelity rate
false PROCEED count
unsupported overclaim count
instruction override count
usage accounting completeness
token / tool / file metrics
Arm C versus Arm B overhead
Arm A versus Arm C cost-and-fidelity comparison
privacy / path / secret scan result
```

## Terminal Statuses

The run must end with exactly one of:

```text
CLAUDE_NATIVE_PRIMARY_BENCHMARK_COMPLETE
CLAUDE_NATIVE_PRIMARY_BENCHMARK_INCOMPLETE
CLAUDE_NATIVE_PRIMARY_BENCHMARK_INFRASTRUCTURE_BLOCKED
CLAUDE_NATIVE_PRIMARY_BENCHMARK_AUTHORIZATION_REVISION_REQUIRED
```

Completion is not acceptance. A separate primary benchmark review is required.

## Forbidden

```text
holdout benchmark
carryover benchmark
Codex track execution
DeepSeek track execution
readiness rerun
prompt changes
case changes
frozen input changes
output schema changes
oracle changes
comparator changes
MVP changes
producer changes
Gate A changes
Gate B
Domain 4
efficiency claim
merge to main
release / version / tag / PyPI
```

## Next State

After this authorization, the only executable next step is the Claude native
primary benchmark within the scope above.

The expected review artifact after execution is:

```text
research/multi_agent_benchmark/claude_native/claude_native_primary_benchmark_review.md
```
