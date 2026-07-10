# Agent Evidence Memory Flow Regression v1

Created: 2026-07-10T16:05:53.321438Z

```text
cold wall seconds: 0.855413
warm cache wall seconds: 0.017353
warm cache speedup ratio: 49.30x
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
