# Claude Native Usage Telemetry Runner Delta Analysis Review

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_RUNNER_DELTA_ANALYSIS_ACCEPTED
RUNNER_DELTA_ANALYSIS_REVIEW_COMPLETE
HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
USAGE_TELEMETRY_INVOCATION_REPAIR_REQUIRED
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
authorization:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis_authorization.md

analysis JSON:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis.json

analysis report:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis.md
```

## Review Findings

The static code comparison is accepted.

Baseline readiness runner:

```text
--output-format json:
PRESENT

--allowedTools:
ABSENT
```

Hardened diagnostic runner:

```text
--output-format json:
ABSENT

--allowedTools Read,Glob,Grep:
PRESENT
```

The previous hardening diagnostic therefore should not be characterized as a
failure of usage accounting under a fully hardened JSON-output invocation. It
was a hardened invocation with `--json-schema`, but without explicit
`--output-format json`.

## Corrected Interpretation

```text
READ_PERMISSION_CONFIGURATION_SUPPORTED
CONTRACT_CORRECTNESS_20_OF_20
READ_PERMISSION_DENIALS_ZERO

HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
USAGE_TELEMETRY_ROOT_CAUSE_CANDIDATE_IDENTIFIED

READ_HARDENING_NOT_YET_FORMALLY_ACCEPTED
FULL_READINESS_RERUN_NOT_AUTHORIZED
```

## Verdict

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_RUNNER_DELTA_ANALYSIS_ACCEPTED
USAGE_TELEMETRY_INVOCATION_REPAIR_REQUIRED
```

## Next Authorized State

No code change is authorized by this review.

The next document may authorize exactly one runner repair:

```text
add:
--output-format json
```

to the hardened diagnostic invocation while preserving all other invocation
arguments, prompts, cases, schema, comparator, model, and MVP code.

The next diagnostic should be limited to:

```text
Read nonce:
3

Critical Arm B:
2

Matched Arm C:
1

Total:
6 unscored telemetry probes
```

Only if those probes pass may a later authorization rerun the full 20-session
hardening diagnostic.

Still blocked:

```text
readiness rerun
primary benchmark
efficiency claim
release / version / tag / PyPI
```
