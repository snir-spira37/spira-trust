# SPIRA Formal Core V1 Differential Harness Report

## Status

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION
PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED
```

## Result

The generic differential comparison did not execute.

Reason:

```text
blocked before comparison because no accepted Python typed-evidence entrypoint exists
```

## Discovery

Accepted Python typed-evidence entrypoints:

```json
[]
```

Domain-specific candidates observed but not accepted as generic typed-evidence entrypoints:

```json
[
  "source/spira_core/mvp_unified.py",
  "source/spira_core/test_build_failure_producer.py",
  "source/spira_core/terraform_plan_producer.py",
  "source/spira_core/agent_summary.py"
]
```

## Boundary

No Python source, domain adapter, benchmark, corpus, oracle, or historical result was modified.
