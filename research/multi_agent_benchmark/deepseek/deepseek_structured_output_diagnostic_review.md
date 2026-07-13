# DeepSeek Structured Output Diagnostic Review

## Status

```text
STRUCTURED_OUTPUT_DIAGNOSTIC_ACCEPTED
STRUCTURED_OUTPUT_INVOCATION_DEFECT_CONFIRMED
DEEPSEEK_STRUCTURED_OUTPUT_CAPABILITY_CONFIRMED
CLAUDE_CODE_JSON_OUTPUT_CONFIRMED
INLINE_JSON_SCHEMA_CONFIRMED
SCHEMA_FILE_PATH_INVOCATION_REJECTED
DS_R0_RUNNER_NARROW_FIX_REQUIRED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
diagnostic authorization:
32710f94b60a4cc7b2756fcb37e09e3d493e57d7

diagnostic result:
69c386d6c368f8f67dbc09988f9ad249ec517170

results:
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_results.json

report:
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_report.md

raw private manifest:
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_raw_private_manifest.json
```

## Review Question

```text
Did the structured-output diagnostic identify whether DS-R0 P3 failed because
structured output is unsupported, because schema enforcement is unsupported, or
because the runner invoked Claude Code incorrectly?
```

## Verdict

```text
STRUCTURED_OUTPUT_DIAGNOSTIC_ACCEPTED
STRUCTURED_OUTPUT_INVOCATION_DEFECT_CONFIRMED
```

The diagnostic is accepted.

It shows that Claude Code with the DeepSeek backend can produce JSON output and
can enforce an inline JSON Schema. The failing condition is specifically
passing a schema file path to `--json-schema`.

## Diagnostic Findings

```text
--output-format json:
PASS

--output-format stream-json:
PASS

--json-schema "<inline JSON>":
PASS

--json-schema "<path-to-schema-file>":
FAIL
```

The observed failure mode:

```text
json_with_minimal_schema_file:
returncode: 1
stderr category: JSON_SCHEMA_ERROR

json_with_benchmark_schema_file:
returncode: 1
stderr category: JSON_SCHEMA_ERROR
```

The accepted interpretation:

```text
DeepSeek structured output capability:
CONFIRMED

Claude Code JSON output:
CONFIRMED

inline JSON Schema:
CONFIRMED

schema file path invocation:
REJECTED
```

## What This Does Not Prove

This review does not claim:

```text
readiness sessions can start
primary benchmark can start
all DS-R0 probes pass
benchmark cases were evaluated
efficiency can be claimed
the benchmark schema may be changed
```

The diagnostic sent no benchmark cases and started no readiness sessions.

## Required Runner Fix

The next artifact must be a narrow runner-fix authorization:

```text
research/multi_agent_benchmark/deepseek/deepseek_ds_r0_runner_fix_authorization.md
```

The fix may allow only:

```text
read the frozen schema file
parse it as JSON
pass the exact parsed schema object as inline canonical JSON to --json-schema
update DS-R0 tests/results/reports
```

The fix must record:

```text
schema_transport: INLINE_CANONICAL_JSON
schema_semantics_changed: false
schema file SHA-256 unchanged
inline schema object == frozen schema object
additionalProperties unchanged
required fields unchanged
enum/const constraints unchanged
```

## Frozen Assets

The fix must not change:

```text
research/multi_agent_benchmark/agent_output.schema.json
research/multi_agent_benchmark/case_manifest.json
research/multi_agent_benchmark/frozen_input_manifest.json
research/multi_agent_benchmark/frozen_inputs/
research/multi_agent_benchmark/prompt_templates_v1.md
research/multi_agent_benchmark/randomization_manifest_v1.json
MVP code
producers
Gate A
thresholds
expected answers
```

## Required Sequence

```text
diagnostic review
→ runner-fix authorization
→ narrow runner fix
→ runner-fix review
→ full DS-R0 rerun from P1
→ DS-R0 review
→ only then possible 9 readiness sessions
```

The next DS-R0 run must start from the beginning because the runner behavior
will change:

```text
P1 model resolution
P2 Claude init/tool inventory
P3 structured output
P4 read-only tools
P5 write/web/subagent denial
P6/P7 session isolation
P8 usage accounting
```

## Run History Preserved

```text
Run 1:
BLOCKED — model identity normalization

Run 2:
BLOCKED — Claude executable unavailable

Run 3:
BLOCKED — schema file-path invocation defect

Diagnostic:
INLINE SCHEMA WORKS
INVOCATION DEFECT CONFIRMED
```

## Current Status

```text
DS-R0:
BLOCKED

structured output capability:
CONFIRMED

runner invocation:
NEEDS NARROW FIX

readiness:
NOT AUTHORIZED

efficiency claim:
NOT AUTHORIZED

release:
NOT AUTHORIZED
```
