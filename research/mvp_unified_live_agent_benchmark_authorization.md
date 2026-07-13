# SPIRA MVP Unified Live-Agent Benchmark Authorization

## Status

```text
UNIFIED_LIVE_AGENT_BENCHMARK_AUTHORIZED
BENCHMARK_EXECUTION_ONLY
EFFICIENCY_CLAIM_NOT_YET_AUTHORIZED
MVP_CODE_FROZEN
RELEASE_NOT_AUTHORIZED
VERSION_BUMP_NOT_AUTHORIZED
TAG_NOT_AUTHORIZED
PYPI_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
MVP implementation:
MVP_IMPLEMENTATION_ACCEPTED

three-domain integration:
ACCEPTED

benchmark smoke:
MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM
live_agent_executed: false
efficiency_claim_authorized: false
```

The smoke benchmark proved tooling shape only. This document authorizes the
next benchmark stage using a live agent or live agent-equivalent API surface
with real usage accounting.

## Purpose

The benchmark must measure whether the accepted unified MVP interface preserves
correctness while introducing acceptable overhead relative to direct domain
compact contracts.

It must not modify the MVP implementation or accepted domain producers.

## Frozen Code and Artifacts

The following are frozen during benchmark execution:

```text
MVP implementation code
source/spira_core/mvp_unified.py
tools/run_mvp_unified_local.py
tools/evaluate_mvp_unified.py
tools/benchmark_mvp_unified_agent.py
tests/test_mvp_unified.py

Domain 1 baseline and behavior
Domain 2 corpus / oracle / validator / producer semantics
Domain 3 corpus / oracle / validator / producer semantics
Gate A semantics
Gate B semantics
action enum
claim-status enum
SPIRA_DECISION_SEMANTICS_V2
```

If benchmark execution requires changing these files or semantics, the run must
stop with:

```text
BENCHMARK_AUTHORIZATION_REVISION_REQUIRED
```

## Authorized Work

Only benchmark execution and reporting are authorized:

```text
1. Select benchmark cases from the accepted Domain 1-3 corpora.
2. Run each selected case through three benchmark arms.
3. Collect live agent usage metrics.
4. Verify exact action/reason/NOT_EVALUATED preservation.
5. Measure unified-over-direct overhead.
6. Produce machine-readable benchmark results.
7. Produce benchmark report.
8. Run JSON/privacy/path/secret checks on benchmark artifacts.
```

No implementation code changes are authorized.

## Benchmark Arms

The benchmark must use exactly these arms:

```text
Arm A:
raw evidence

Arm B:
direct domain compact contract

Arm C:
unified MVP interface
```

The primary overhead gate compares:

```text
Arm C vs Arm B
```

The raw-evidence arm measures SPIRA's evidence compression context. It is not
the denominator for the 15 percent unified-interface overhead gate.

## Minimum Case Set

The benchmark must include at least one representative case from each domain:

```text
Domain 1:
Python artifact evidence

Domain 2:
pytest result evidence

Domain 3:
Terraform Plan JSON evidence
```

Across the selected cases, the benchmark must cover:

```text
PROCEED
STOP_BLOCKED
REPORT_NOT_EVALUATED or RERUN_REQUIRED
```

The benchmark should use at least:

```text
3 clean repetitions per domain / arm combination
```

Minimum smoke shape:

```text
3 domains
3 arms
3 repetitions
= 27 clean live-agent benchmark sessions
```

If a larger benchmark is run, it must preserve the same arms, metrics, and
correctness gates.

## Required Metrics

Each benchmark session must record:

```text
domain
case_id
arm
repetition
model or agent surface
fresh input tokens
cached input tokens
total input tokens
output tokens
tool calls
files opened
wall-clock time
exact action
reason_codes
explicit NOT_EVALUATED list
BLOCK list
drill-down count
not-claimed boundaries
safety/not-claimed overreach flag
```

If a metric is unavailable from the agent surface, it must be recorded as:

```text
NOT_AVAILABLE
```

and the report must explain whether the benchmark remains interpretable.

## Correctness Gates

All correctness gates must pass before any efficiency interpretation:

```text
exact action preservation: 100%
reason-code preservation: 100%
explicit NOT_EVALUATED preservation: 100%
BLOCK preservation: 100%
evidence drill-down preservation: 100%
not-claimed boundaries preserved: 100%
false PROCEED: 0
safety overclaim: 0
instruction override: 0
sensitive value leak: 0
```

Any savings or overhead result that fails these gates is invalid.

## Overhead Gate

The accepted overhead threshold is:

```text
Unified Arm C vs direct Arm B:
median total-input overhead <= 15%
```

Definition:

```text
median_overhead =
median((arm_c_total_input_tokens - arm_b_total_input_tokens)
       / arm_b_total_input_tokens)
```

If:

```text
median total-input overhead <= 15%
```

then:

```text
UNIFIED_INTERFACE_EFFICIENCY_ACCEPTABLE_FOR_MVP_REVIEW
```

If:

```text
median total-input overhead > 15%
```

then:

```text
UNIFIED_INTERFACE_OVERHEAD_REVIEW_REQUIRED
```

In the latter case, do not change producers, Gate A, or accepted domain
semantics to rescue the result. Review only routing/envelope/tool-call overhead
under a new authorization.

## Required Output Artifacts

The benchmark must produce:

```text
research/mvp_unified_live_agent_benchmark_results.json
research/mvp_unified_live_agent_benchmark_report.md
```

The results JSON must include:

```text
schema
schema_version
status
benchmark_kind
live_agent_executed
session_count
domains
arms
repetitions
session_records
correctness_gates
median_total_input_overhead
overhead_threshold
metric_availability
efficiency_claim_authorized: false
errors
```

## Successful Statuses

A successful correctness-preserving benchmark may end with:

```text
UNIFIED_LIVE_AGENT_BENCHMARK_COMPLETE
UNIFIED_INTERFACE_EFFICIENCY_ACCEPTABLE_FOR_MVP_REVIEW
EFFICIENCY_CLAIM_STILL_NOT_AUTHORIZED
```

If correctness passes but overhead exceeds the threshold:

```text
UNIFIED_LIVE_AGENT_BENCHMARK_COMPLETE
UNIFIED_INTERFACE_OVERHEAD_REVIEW_REQUIRED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
```

If correctness fails:

```text
UNIFIED_LIVE_AGENT_BENCHMARK_FAILED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
```

## Review Requirement

Benchmark execution is not self-accepting. After the benchmark is materialized,
a separate review must decide:

```text
UNIFIED_LIVE_AGENT_BENCHMARK_ACCEPTED
UNIFIED_LIVE_AGENT_BENCHMARK_NEEDS_REVISION
UNIFIED_LIVE_AGENT_BENCHMARK_REJECTED
```

Only after benchmark review may an MVP acceptance review be considered.

## Non-Authorization

This document does not authorize:

```text
MVP code changes
producer changes
corpus/oracle/schema/validator changes
Gate A refactor
Gate B
Domain 4
semantic cache reuse
live Terraform state
terraform apply
remote backend
cloud credentials
Kubernetes
release
version bump
tag
PyPI publication
public efficiency claim
```

## Final Boundary

```text
live-agent benchmark: AUTHORIZED
benchmark review: REQUIRED AFTER EXECUTION
MVP code: FROZEN
efficiency claim: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
merge to main: NOT_AUTHORIZED
```
