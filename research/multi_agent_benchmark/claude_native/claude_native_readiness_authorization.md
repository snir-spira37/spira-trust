# Claude Native Readiness Authorization

## Status

```text
CLAUDE_NATIVE_READINESS_AUTHORIZED
NINE_READINESS_SESSIONS_ONLY
CHEAP_MODEL_PIN_HAIKU
PRIMARY_BENCHMARK_NOT_AUTHORIZED
HOLDOUT_BENCHMARK_NOT_AUTHORIZED
CARRYOVER_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

Claude native C0 technical probes were accepted:

```text
CLAUDE_NATIVE_C0_TECHNICAL_PROBES_ACCEPTED
CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS
```

Confirmed prerequisites:

```text
model:
haiku

Claude Code:
2.1.206

structured JSON:
PASS

Read / Glob / Grep:
PASS

tool isolation:
PASS

fresh session isolation:
PASS

usage accounting:
PASS
```

## Scope

This authorization permits only the Claude native readiness set:

```text
3 domains
x 3 arms
x 1 readiness-selected case per domain
= 9 live readiness sessions
```

Allowed selected inputs are only those in:

```text
research/multi_agent_benchmark/frozen_input_manifest.json
```

with:

```text
readiness_selected == true
```

## Required Execution Rules

Each readiness session must use:

```text
fresh Claude Code process
fresh session-id
--no-session-persistence
requested model: haiku
same frozen input bytes
same output schema
read-only benchmark workspace
no web
no write
no subagents
raw stdout/stderr outside repository
```

The agent must not see:

```text
oracle expected answers
other arm contracts
benchmark evaluator results
producer source code
```

## Required Measurements

For every readiness session record:

```text
domain
case_id
arm
input_sha256
prompt_sha256
returncode
schema-valid output status
exact action
recommended_agent_action
reason_codes
not_evaluated
not_claimed
drilldown_used
evidence/proof references
fresh input tokens
cached input tokens
total input tokens
output tokens
cost, if reported by Claude Code
tool calls
workspace mutation status
forbidden tool calls
```

## Readiness Pass Gates

The readiness run may pass only if:

```text
9 / 9 sessions completed
9 / 9 outputs parse as JSON
9 / 9 outputs satisfy the frozen output schema
9 / 9 exact action preservation
9 / 9 reason-code preservation where expected values are available
9 / 9 explicit NOT_EVALUATED preservation
false PROCEED: 0
workspace mutations: 0
executed forbidden tool calls: 0
usage accounting available: 9 / 9
raw private outputs outside repository
```

## Allowed Files

```text
tools/run_claude_native_readiness.py
tests/test_claude_native_readiness.py
research/multi_agent_benchmark/claude_native/claude_native_readiness_results.json
research/multi_agent_benchmark/claude_native/claude_native_readiness_report.md
research/multi_agent_benchmark/claude_native/claude_native_readiness_raw_private_manifest.json
```

## Forbidden

```text
primary benchmark
holdout benchmark
carryover benchmark
more than 9 readiness sessions
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing MVP code
changing producers
changing Gate A
changing thresholds
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Terminal Statuses

The readiness run must end with exactly one of:

```text
CLAUDE_NATIVE_READINESS_PASS
CLAUDE_NATIVE_READINESS_NEEDS_REVISION
CLAUDE_NATIVE_READINESS_FAILED
CLAUDE_NATIVE_READINESS_INCOMPLETE
CLAUDE_NATIVE_READINESS_AUTHORIZATION_REVISION_REQUIRED
```

## Required Validation

After execution:

```text
focused readiness tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```

## Next Required Artifact

After readiness execution:

```text
research/multi_agent_benchmark/claude_native/claude_native_readiness_review.md
```

Only if readiness is accepted may a later artifact consider authorizing Claude
native primary benchmark execution.
