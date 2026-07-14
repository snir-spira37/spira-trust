# Machine Contract Passthrough Revised Readiness Rerun Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_REVISED_READINESS_RERUN_AUTHORIZED

AMENDED_EVALUATOR_REQUIRED
SHARED_EXPLANATION_PROJECTION_AMENDMENT_ACCEPTED

CLAUDE_NATIVE_READINESS_RERUN_AUTHORIZED
CODEX_NATIVE_READINESS_RERUN_AUTHORIZED
EIGHTEEN_TOTAL_READINESS_SESSIONS_AUTHORIZED
SEQUENTIAL_AGENT_EXECUTION_REQUIRED
CONCURRENT_LIVE_TRACKS_FORBIDDEN

PRIMARY_BENCHMARK_NOT_AUTHORIZED
CLAUDE_PRIMARY_RESUME_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
DEEPSEEK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This document authorizes a fresh revised readiness rerun after acceptance of the
machine-contract passthrough explanation projection amendment.

The previous revised readiness result remains preserved. The historical Claude
revised primary partial run remains preserved and incomplete. The old primary
must not be resumed from session 7 because the evaluator projection changed.

## Accepted Basis

The rerun is based on:

```text
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_authorization.md
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_results.json
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_report.md
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_review.md
```

Accepted projection rule:

```text
machine-contract integrity: authoritative
accepted validator verdict: authoritative for explanation compliance
action/stop agreement: authoritative
model self-report fields: non-authoritative telemetry only
```

## Authorized Live Scope

Exactly the following readiness rerun sessions are authorized:

```text
Claude Native:
  3 domains x 3 arms = 9 sessions

Codex Native:
  3 domains x 3 arms = 9 sessions

Total:
  18 readiness sessions
```

The authorized cases remain:

```text
python_artifact:
  0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4

pytest_result:
  synthetic_clean_success

terraform_plan:
  auth_no_changes
```

The authorized arms remain:

```text
Arm A: raw evidence baseline
Arm B: direct domain machine contract passthrough
Arm C: unified MVP machine contract passthrough
```

## Required Frozen Inputs

The rerun must preserve:

```text
shared explanation-only prompt
model output schema
accepted envelope Schema V1
accepted deterministic validator
43-fixture validator corpus
MVP passthrough implementation
Domains 1-3 producers
Gate A semantics
SPIRA_DECISION_SEMANTICS_V2
case manifest
readiness case selection
Arm A global policy
old Claude/Codex results
old Claude primary partial result
```

No prompt, schema, validator, fixture, producer, oracle, or MVP change is
authorized by this document.

## Execution Rules

The rerun must execute sequentially:

```text
Claude Native readiness rerun
-> Claude readiness rerun report/review
-> Codex Native readiness rerun
-> Codex readiness rerun report/review
-> combined readiness rerun report/review
```

Claude and Codex live sessions must not run concurrently.

Each live session must use:

```text
fresh process
fresh session ID
fresh config/session isolation
no resume
no hidden retry except infrastructure retry explicitly recorded
read-only isolation
no web
no subagents
no repository mutation
```

## Acceptance Gates

The readiness rerun can pass only if:

```text
18 / 18 sessions ready
schema valid: 18 / 18
usage available: 18 / 18
B/C validator PASS: 12 / 12
B/C machine-contract integrity PASS: 12 / 12
machine contract hash preserved: 12 / 12
action/stop agreement: 18 / 18
false PROCEED: 0
unsafe explanation accepted: 0
NOT_EVALUATED contradiction accepted: 0
not_claimed violation accepted: 0
fabricated evidence/proof accepted: 0
sensitive exposure accepted: 0
workspace mutations: 0
repository mutations: 0
forbidden tools: 0
```

Model self-report disagreements may be recorded as telemetry:

```text
MODEL_SELF_REPORT_DISAGREES_WITH_VALIDATOR
```

Such disagreements are not hard failures by themselves when the accepted
validator, machine-contract integrity, and deterministic gates pass.

## Authorized Artifacts

The rerun may update or create only the revised readiness rerun artifacts under
the existing readiness locations:

```text
research/multi_agent_benchmark/passthrough_revised_readiness_manifest.json
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_results.json
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_report.md
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_review.md
research/multi_agent_benchmark/codex_native/passthrough_revised_readiness_results.json
research/multi_agent_benchmark/codex_native/passthrough_revised_readiness_report.md
research/multi_agent_benchmark/codex_native/passthrough_revised_readiness_review.md
research/multi_agent_benchmark/machine_contract_passthrough_revised_readiness_combined_report.md
research/multi_agent_benchmark/machine_contract_passthrough_revised_readiness_combined_review.md
```

Private raw stdout/stderr must remain outside the Git repository. Public raw
private manifests may include only hashes, sizes, classifications, and opaque
IDs, not raw paths or raw response bodies.

## Forbidden Work

This authorization does not permit:

```text
resuming Claude primary from session 7
starting Codex primary
starting any primary benchmark
holdout
carryover
DeepSeek execution
prompt changes
schema changes
validator changes
MVP changes
fixture changes
oracle changes
producer changes
result reclassification
deleting historical results
efficiency claim
release
version bump
tag
PyPI
merge to main
```

## Required Outcomes

The combined readiness rerun review must end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_REVISED_READINESS_RERUN_PASS
MACHINE_CONTRACT_PASSTHROUGH_REVISED_READINESS_RERUN_NEEDS_REVISION
MACHINE_CONTRACT_PASSTHROUGH_REVISED_READINESS_RERUN_INFRASTRUCTURE_BLOCKED
```

If the rerun passes, the next step is a separate revised primary benchmark
authorization. The new primary must start from the beginning under one evaluator
projection. It must not append to the historical incomplete Claude primary run.

## Required Final State

After this authorization is committed:

```text
readiness rerun: AUTHORIZED NEXT
Claude primary historical partial: PRESERVED
Claude primary resume: NOT AUTHORIZED
Codex primary: NOT AUTHORIZED
new primary benchmark: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
