# DeepSeek Model Identity Amendment

## Status

```text
DEEPSEEK_MODEL_IDENTITY_AMENDMENT_PROPOSED
PROVIDER_CONFIRMED_MODEL_ID_PINNED_AS_DEEPSEEK_V4_PRO
ONE_MILLION_CONTEXT_CAPABILITY_NOT_CLAIMED
PRIOR_DS_R0_BLOCKED_RESULT_PRESERVED
DS_R0_RERUN_NOT_YET_AUTHORIZED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This amendment responds to the accepted DS-R0 blocked result:

```text
DS_R0_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
MODEL_IDENTITY_REVIEW_COMPLETE
DEEPSEEK_TRACK_MODEL_ID_AMENDMENT_REQUIRED
```

The goal is to make the DeepSeek benchmark track auditable under the model
identity actually confirmed by the provider response, without changing the
frozen benchmark cases, prompts, inputs, thresholds, MVP implementation, or
correctness requirements.

## Prior Blocked Result Preserved

The prior DS-R0 run remains valid history:

```text
run:
DS-R0 Run 1

requested identity:
deepseek-v4-pro[1m]

provider resolved identity:
deepseek-v4-pro

result:
DS_R0_TECHNICAL_PROBES_BLOCKED

reason:
exact requested model identity not confirmed
```

This amendment does not reinterpret that run as passing. It does not resume the
probe sequence from P2. Any future DS-R0 rerun must start again at P1.

## Identity Decision

### Original Requested Identity

```text
deepseek-v4-pro[1m]
```

This identity was used by the prepared DeepSeek track and by DS-R0 Run 1.

### Provider-Confirmed Resolved Identity

```text
deepseek-v4-pro
```

The direct provider call returned `deepseek-v4-pro` as the resolved model
identity.

### One-Million Context Capability

```text
[1m] capability:
NOT_INDEPENDENTLY_CONFIRMED
```

The benchmark will not treat the `[1m]` suffix as a separately verified model
identity or as an independently enforced context capability.

The benchmark may cite provider documentation when describing the DeepSeek V4
Pro track, but the executed model identity for the benchmark is pinned to the
provider-confirmed API response identity:

```text
deepseek-v4-pro
```

## New Benchmark Requested Identity

```text
deepseek-v4-pro
```

The benchmark will pin the provider-confirmed response identity
`deepseek-v4-pro`.

The previously requested `[1m]` suffix is not treated as a separately verified
capability or model identity.

## Authorized Future Changes After Review

If this amendment is accepted by a separate review, the next implementation
cell may update only DeepSeek model-identity references needed for a fresh
DS-R0 rerun:

```text
requested model ID
DeepSeek configuration template
DS-R0 runner expectation
report terminology
model-resolution acceptance rule
```

Those changes must preserve:

```text
18 benchmark cases
54 Arm A/B/C inputs
prompt templates
output schema
randomization
correctness thresholds
overhead threshold
MVP code
producer semantics
Gate A behavior
prior DS-R0 blocked result
```

## Frozen Assets

The following remain frozen and are not modified by this amendment:

```text
research/multi_agent_benchmark/case_manifest.json
research/multi_agent_benchmark/frozen_input_manifest.json
research/multi_agent_benchmark/frozen_inputs/
research/multi_agent_benchmark/prompt_templates_v1.md
research/multi_agent_benchmark/agent_output.schema.json
research/multi_agent_benchmark/randomization_manifest_v1.json
source/spira_core/
```

## Required Review

This amendment is only a proposal. It does not authorize execution.

The next artifact must be:

```text
research/multi_agent_benchmark/deepseek/deepseek_model_identity_amendment_review.md
```

The review must return exactly one of:

```text
DEEPSEEK_MODEL_IDENTITY_AMENDMENT_ACCEPTED
DEEPSEEK_MODEL_IDENTITY_AMENDMENT_NEEDS_REVISION
DEEPSEEK_MODEL_IDENTITY_AMENDMENT_REJECTED
```

Only an accepted amendment may authorize a narrow DS-R0 rerun update and fresh
technical-probe execution.

## Rerun Boundary

If authorized later, the rerun must start from the beginning:

```text
P1 direct provider resolution
P2 Claude Code init/model/tool inventory
structured output
tool isolation
session isolation
usage accounting
```

The rerun must not:

```text
reuse Run 1 P1 as an accepted probe
start nine readiness sessions
start primary, holdout, or carryover benchmark sessions
change cases or prompts
change MVP code
claim efficiency
trigger release/version/tag/PyPI work
```

## Current Status After This Amendment

```text
DeepSeek model identity amendment:
PROPOSED

DS-R0 rerun:
NOT YET AUTHORIZED

nine live readiness sessions:
NOT AUTHORIZED

primary benchmark:
NOT AUTHORIZED

MVP code:
UNCHANGED

efficiency claim:
NOT AUTHORIZED

release:
NOT AUTHORIZED
```
