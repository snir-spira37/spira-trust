# SPIRA MVP Unified Benchmark Report

## Status

```text
MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM
EFFICIENCY_CLAIM_AUTHORIZED: false
LIVE_AGENT_EXECUTED: false
```

## Smoke Shape

```text
domains: pytest_result, python_artifact, terraform_plan
arms: raw_evidence, domain_compact_contract, unified_product_flow
repetitions per arm: 3
session count: 27
```

This is protocol smoke tooling. It does not make a public efficiency claim.

## Measurements

```text
raw evidence median estimated input tokens: 372
domain compact median estimated input tokens: 196
unified product median estimated input tokens: 176
median unified overhead ratio: -0.10204081632653061
overhead limit ratio: 0.15
```

The 15 percent threshold applies only to direct compact contract vs unified
product flow overhead. It is not a claim about savings versus raw evidence.

## Preservation

```text
all preservation gates: PASS
action preserved
reason_codes preserved
NOT_EVALUATED preserved
BLOCK preserved
zero false PROCEED
zero safety overclaim
evidence drill-down preserved
not-claimed boundaries preserved
```

## Boundary

```text
public efficiency claim: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
```
