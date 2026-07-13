# Claude Native Full Readiness Rerun Authorization

## Status

```text
CLAUDE_NATIVE_FULL_READINESS_RERUN_AUTHORIZED
NINE_FROZEN_READINESS_CELLS_ONLY
HARDENED_HARNESS_CONFIGURATION_FROZEN

PROMPTS_FROZEN
CASES_FROZEN
INPUTS_FROZEN
SCHEMA_FROZEN
COMPARATOR_FROZEN
MODEL_FROZEN
MVP_CODE_FROZEN

PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The accepted hardening rerun records:

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_ACCEPTED
READ_GLOB_GREP_PERMISSION_CONFIGURATION_CONFIRMED
JSON_RESULT_ENVELOPE_CONFIRMED
USAGE_TELEMETRY_CONFIRMED
```

The previous readiness result remains a historical pre-hardening result. This
authorization permits a new scored readiness rerun under the accepted hardened
harness.

## Authorized Sessions

Exactly nine fresh readiness sessions are authorized:

```text
Domain 1 x Arms A/B/C
Domain 2 x Arms A/B/C
Domain 3 x Arms A/B/C
```

Each session must use:

```text
fresh process
fresh session ID
fresh workspace
no resume
no hidden retry
no prompt or input changes
```

## Required Harness Configuration

```text
--permission-mode dontAsk
--tools Read,Glob,Grep
--allowedTools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*
--output-format json
--json-schema <inline canonical frozen schema>
```

## Required Gates

```text
JSON result envelope:
9 / 9

structured_output:
9 / 9

schema valid:
9 / 9

usage available:
9 / 9

permission denials:
0

workspace mutations:
0

repository mutations:
0

forbidden tool calls:
0

false PROCEED:
0
```

Fidelity remains strict and frozen:

```text
exact action
reason codes
NOT_EVALUATED
blocking lists
evidence references
not-claimed boundaries
```

## Possible Review Outcomes

All 9 cells exact:

```text
CLAUDE_NATIVE_FULL_READINESS_ACCEPTED
CLAUDE_NATIVE_PRIMARY_PROPOSAL_ALLOWED_NEXT
```

Arms B/C pass and only Arm A fails strict fidelity:

```text
CLAUDE_NATIVE_COMPACT_AND_UNIFIED_CONTRACT_READINESS_PASS
CLAUDE_NATIVE_STRICT_FULL_READINESS_NOT_ACCEPTED
ARM_A_RAW_EVIDENCE_FIDELITY_LIMITATION_REPRODUCED
GLOBAL_ARM_A_POLICY_REVIEW_REQUIRED
```

Arm B or Arm C fails:

```text
CLAUDE_NATIVE_CONTRACT_READINESS_NOT_READY
PRIMARY_BENCHMARK_BLOCKED
```

Harness, usage, permission, or telemetry regression:

```text
CLAUDE_NATIVE_HARNESS_REGRESSION_OBSERVED
READINESS_RESULT_NOT_ACCEPTED
```

## Forbidden

```text
primary benchmark execution
holdout execution
carryover execution
prompt changes
case changes
input changes
schema changes
comparator changes
model changes
MVP code changes
producer changes
threshold changes
Claude-specific Arm A policy changes
publishing raw private responses
publishing private raw paths
efficiency claim
release / version / tag / PyPI
```
