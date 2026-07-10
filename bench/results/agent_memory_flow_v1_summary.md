# Agent Evidence Memory Flow Regression v1

Created: 2026-07-10T16:01:10.765340Z

```text
cold wall seconds: 0.563539
warm cache wall seconds: 0.015909
warm cache speedup ratio: 35.42x
clean cache response bytes: 993
clean plan response bytes: 1854
all cases passed: True
```

Cases:

- clean_cache_hit: passed=True
- artifact_mutation: passed=True
- policy_mutation: passed=True
- lockfile_mutation: passed=True
- semantics_mutation: passed=True
- tool_version_mutation: passed=True
- context_ambiguity: passed=True
- exact_context_result_conflict: passed=True
- missing_summary_or_context: passed=True
- corrupted_summary: passed=True
- unsupported_schema: passed=True

Not claimed: CPU cycles, energy, CO2, or live-agent token savings.
