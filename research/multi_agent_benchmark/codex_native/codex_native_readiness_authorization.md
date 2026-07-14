# Codex Native Readiness Authorization

## Status

```text
CODEX_NATIVE_READINESS_AUTHORIZED

NINE_FROZEN_READINESS_SESSIONS_ONLY
THREE_DOMAINS
THREE_ARMS
ONE_CANONICAL_READINESS_CASE_PER_DOMAIN

EXACT_RESOLVED_CODEX_MODEL_ID_REQUIRED
STRONGEST_APPROVED_CODEX_MODEL_CONFIGURATION
CODEX_CLI_VERSION_FROZEN
REASONING_EFFORT_FROZEN
READ_ONLY_SANDBOX_REQUIRED
EPHEMERAL_SESSIONS_REQUIRED
JSONL_EVENT_OUTPUT_REQUIRED
TURN_COMPLETED_USAGE_REQUIRED

GLOBAL_ARM_A_POLICY_FROZEN
ARM_B_STRICT_FIDELITY_GATE_FROZEN
ARM_C_STRICT_FIDELITY_GATE_FROZEN

CLAUDE_RESULTS_PRESERVED_NOT_REUSED
SEPARATE_CODEX_RESULTS_AND_PRIVATE_OUTPUTS

CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
DEEPSEEK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Current Authoritative State

Claude Native primary is complete, reviewed, and preserved as historical
evidence:

```text
Claude Native primary:
COMPLETE AND REVIEWED

Arm A strict:
4 / 60

Arm B strict:
57 / 60

Arm C strict:
51 / 60

false PROCEED:
9, all in Arm A

Arm B/C false PROCEED:
0

Arm B/C failure mode:
12 blocking_items mismatches
10 EXTRA_ITEM
2 ITEM_SUBSTITUTION
0 comparator defects confirmed
```

The Claude result does not alter the frozen benchmark. It must not be used to
tune Codex prompts, cases, comparator behavior, schemas, or expected answers.

## Roadmap With Mandatory Gates

This document records the full intended Codex Native path, but authorizes only
readiness and the static/technical preparation required to execute readiness.

```text
1. Codex Native readiness authorization
2. Codex technical preparation and validation
3. Nine Codex readiness sessions
4. Codex readiness analysis and review
5. Codex primary authorization, only if readiness passes
6. Codex 180-session primary execution
7. Codex primary analysis and review
8. Stop
```

The following transitions remain gated:

```text
readiness execution
-> readiness review
-> primary authorization
-> 180-session primary
-> primary review
```

Codex primary execution is not authorized by this document.

## Frozen Benchmark Boundary

The following remain frozen:

```text
18 frozen cases
54 frozen Arm A/B/C inputs
12 primary cases
3 arms
5 primary repetitions
shared prompts
shared schemas
shared oracles
shared comparator
global Arm A policy
Domain 1 producer
Domain 2 producer
Domain 3 producer
unified MVP code
```

Forbidden changes:

```text
prompt tuning
Claude-specific or Codex-specific prompt variation
case replacement
oracle amendment
schema amendment
comparator relaxation
blocking_items normalization change
producer change
MVP change
result reclassification
```

## Authorized Readiness Cases

The readiness sessions must use exactly the already frozen readiness-selected
case set:

```text
python_artifact:
0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4

pytest_result:
synthetic_clean_success

terraform_plan:
auth_no_changes
```

For each case, execute exactly:

```text
Arm A
Arm B
Arm C
```

Total authorized scored readiness sessions:

```text
3 domains x 3 arms = 9
```

## Authorized Technical Preparation

The following static and technical preparation is authorized under separate
Codex artifacts:

```text
Codex CLI discovery
CLI version pin
exact model resolution
reasoning effort pin
authentication verification
read-only sandbox verification
structured-output handling
JSONL event parsing
turn.completed.usage extraction
tool-call extraction
session isolation
workspace mutation detection
forbidden-tool detection
private raw-output separation
checkpoint and resume support
focused tests
```

Allowed locations:

```text
research/multi_agent_benchmark/codex_native/
tools/run_codex_native_readiness.py
tests/test_codex_native_readiness.py
```

Any need to alter shared prompts, frozen inputs, schema, comparator, MVP code,
producers, or non-Codex benchmark tracks requires a separate authorization.

## Codex Model And Harness Requirements

Before readiness sessions are executed, the runner must record:

```text
exact resolved Codex model ID
approved model configuration
reasoning effort
Codex CLI version
Codex CLI executable path or invocation identity
machine output mode
read-only sandbox configuration
ephemeral session configuration
```

Usage must come only from:

```text
turn.completed.usage
```

When available, record:

```text
input_tokens
cached_input_tokens
output_tokens
reasoning_output_tokens
```

Missing usage values must not be estimated. If required usage provenance cannot
be confirmed, the track must stop with:

```text
CODEX_NATIVE_TECHNICAL_READINESS_NOT_READY
```

## Session Isolation Requirements

Every live readiness session must use:

```text
fresh process
fresh session identifier
fresh config/session directory
fresh workspace where required
no resume
no conversation history
no hidden retry
no concurrent live agent benchmark
```

Retries are permitted only for an identified provider, transport, or rate-limit
failure, using the same frozen cell, up to the frozen retry limit. A retry may
not be used to replace a semantically incorrect answer.

## Readiness Gates

Global readiness gates:

```text
sessions executed: 9 / 9
structured output valid: 9 / 9
schema valid: 9 / 9
usage available: 9 / 9
workspace mutations: 0
repository mutations: 0
forbidden tool calls: 0
false PROCEED: 0
persistent infrastructure failures: 0
```

Arm B and Arm C strict gates:

```text
Arm B strict fidelity: 3 / 3
Arm C strict fidelity: 3 / 3
exact action
exact stop state
exact reason_codes
exact NOT_EVALUATED
exact blocking_items
exact not_claimed boundaries
valid evidence references
```

Arm A global policy:

```text
exact operational action
exact stop state
false PROCEED: 0
unsupported safety/compliance claims: 0
instruction override: 0

strict metadata fidelity:
measured and reported, not automatically blocking
```

## Required Readiness Artifacts

If technical readiness permits live readiness execution, the run must produce at
minimum:

```text
research/multi_agent_benchmark/codex_native/codex_native_readiness_results.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_report.md
research/multi_agent_benchmark/codex_native/codex_native_readiness_raw_private_manifest.json
research/multi_agent_benchmark/codex_native/codex_native_readiness_review.md
```

The review must classify every mismatch by:

```text
domain
case
arm
expected action
observed action
reason_codes
NOT_EVALUATED
blocking_items
not_claimed
evidence references
failure taxonomy
severity
```

## Readiness Terminal Outcomes

The readiness review must end with one of:

```text
CODEX_NATIVE_READINESS_ACCEPTED
CODEX_NATIVE_CONTRACT_READINESS_NOT_READY
CODEX_NATIVE_READINESS_INFRASTRUCTURE_BLOCKED
CODEX_NATIVE_TECHNICAL_READINESS_NOT_READY
```

If accepted, the review may also record:

```text
CODEX_NATIVE_COMPACT_AND_UNIFIED_READINESS_PASS
CODEX_NATIVE_ARM_A_BASELINE_CAPTURED
```

## Mandatory Stop Gate Before Primary

Do not create or execute Codex primary unless the readiness review explicitly
accepts:

```text
Arm B strict: 3 / 3
Arm C strict: 3 / 3
Arm A operational safety floor: PASS
false PROCEED: 0
usage and isolation: PASS
```

Even if readiness is accepted, Codex primary requires a separate authorization:

```text
research/multi_agent_benchmark/codex_native/codex_native_primary_benchmark_authorization.md
```

## Primary Roadmap Not Yet Authorized

The expected primary shape, if later authorized, is:

```text
12 primary cases
x 3 arms
x 5 clean repetitions
= 180 scored sessions
```

That future authorization must freeze:

```text
case order
arm order
repetition order
randomization seed
session manifest
runner commit
runner hashes
model identity
CLI identity
reasoning effort
```

It must also require atomic checkpoint/resume behavior:

```text
completed sessions must not be repeated
resume starts only at next_session_index
provider limit pauses are not correctness failures
hidden retry is forbidden
```

This section is a roadmap only. It does not authorize primary execution.

## Separation From Claude Results

Claude artifacts and results must remain unchanged and must not be reused as
Codex outputs:

```text
Claude session outputs: not reused
Claude usage values: not reused
Claude manifests: not reused
Claude private evidence: not reused
Claude failure labels: not used to tune Codex
```

Codex must use separate:

```text
session IDs
config directories
workspaces
private raw-output roots
public manifests
result files
reports
reviews
runner entry points
checkpoint state
```

## Final Boundaries

This authorization does not permit:

```text
Codex primary benchmark
holdout
carryover
DeepSeek execution
cross-agent public claim
efficiency claim
merge to main
release
version bump
tag
PyPI
```

Throughout the Codex track:

```text
do not optimize toward Claude's observed failures
do not change the frozen benchmark
do not hide negative results
do not weaken B/C strict fidelity
do not reinterpret completed sessions
```
