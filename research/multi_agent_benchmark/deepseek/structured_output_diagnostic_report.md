# DeepSeek Structured Output Diagnostic Report

## Status

```text
STRUCTURED_OUTPUT_INVOCATION_DEFECT_FOUND
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: deepseek-v4-pro
probe count: 5
benchmark cases sent: 0
readiness sessions: 0
```

## Probes

- json_without_schema_tools_empty: rc=0 json=True stderr=EMPTY
- stream_json_without_schema_tools_empty: rc=0 json=True stderr=EMPTY
- json_with_minimal_inline_schema: rc=0 json=True stderr=EMPTY
- json_with_minimal_schema_file: rc=1 json=False stderr=JSON_SCHEMA_ERROR
- json_with_benchmark_schema_file: rc=1 json=False stderr=JSON_SCHEMA_ERROR

## Boundary

```text
No benchmark cases were sent.
No readiness, primary, holdout, or carryover sessions were started.
Raw stdout/stderr stayed outside the repository.
```
