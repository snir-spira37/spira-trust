# DeepSeek Read Tool Diagnostic Review

## Status

```text
DEEPSEEK_READ_TOOL_DIAGNOSTIC_ACCEPTED
DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY
READ_ONLY_TOOL_EXECUTION_UNSUPPORTED_IN_CURRENT_DEEPSEEK_CLAUDE_HARNESS
READ_TOOL_INVOCATION_AND_CONFIGURATION_PROBES_EXHAUSTED
DS_R0_REMAINS_BLOCKED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
diagnostic commit:
ea37c2071074192ceb9baacd9cf05cd56ff3d66e

results:
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_results.json

report:
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_report.md

raw private manifest:
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_raw_private_manifest.json

runner:
tools/run_deepseek_read_tool_diagnostic.py

tests:
tests/test_deepseek_read_tool_diagnostic.py
```

## Review Question

```text
Did the authorized P4 diagnostic identify a narrow runner or configuration
defect that can be fixed, or does DS-R0 remain blocked on current
DeepSeek-via-Claude-Code read-only tool-call compatibility?
```

## Verdict

```text
DEEPSEEK_READ_TOOL_DIAGNOSTIC_ACCEPTED
DS_R0_REMAINS_BLOCKED
```

The diagnostic is accepted as a factual technical result.

It did not find a safe narrow invocation fix. Under the current harness,
DeepSeek-via-Claude-Code did not produce observable Read, Glob, or Grep tool
calls in any authorized probe.

## Confirmed Prior Gates

The diagnostic preserves the previously closed gates:

```text
model identity:
deepseek-v4-pro confirmed

Claude Code harness:
installed and launchable

structured output:
confirmed with inline canonical JSON schema transport

schema semantics:
unchanged
```

The current blocker is not a model-identity blocker, not a Claude executable
blocker, and not the prior schema-file transport blocker.

## Diagnostic Coverage

Authorized probes covered:

```text
Read-only default prompt
Read-only manual permission mode
Glob-only probe
Grep-only probe
tool use with JSON output
alternate --tools syntax
```

Observed result:

```text
probe count:
6

tool calls observed:
0

benchmark cases sent:
0

readiness sessions started:
0
```

The diagnostic exercised the allowed invocation and configuration variations
without using benchmark evidence.

## Blocking Finding

### DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY

Observed:

```text
all Read / Glob / Grep probes:
no observable tool calls

stream-json probes:
returncode 1

JSON-output tool probe:
returncode 1

safe stderr category:
EMPTY or NONEMPTY_OTHER
```

The accepted finding is deliberately narrow:

```text
The current DeepSeek-via-Claude-Code harness is not ready for DS-R0 P4
read-only tool execution.
```

This review does not claim that DeepSeek cannot ever support tool use, and it
does not claim that Claude Code tools are globally broken. It records only
that the current pinned combination did not satisfy the benchmark harness
requirements.

## Isolation Preserved

```text
workspace mutation:
0

repository mutation:
0

forbidden tool calls:
0

benchmark cases sent:
0

readiness sessions:
0

primary / holdout / carryover sessions:
0
```

The diagnostic failed closed before any scored session or benchmark case.

## Validation

```text
focused diagnostic tests:
4 passed

benchmark asset validator:
PASS

JSON validation:
PASS

secret / private-path scan:
PASS

full pytest:
135 passed

frozen asset diff check:
PASS
```

No MVP code, frozen benchmark assets, prompts, cases, schemas, producers, or
Gate A artifacts were changed.

## Run History Preserved

```text
Run 1:
BLOCKED - model identity normalization

Run 2:
BLOCKED - Claude executable unavailable

Run 3:
BLOCKED - schema file-path transport

Run 4:
P1-P3 PASS
BLOCKED - read-only tool probe

Diagnostic:
P4 invocation/configuration probes executed
BLOCKED - current DeepSeek-via-Claude-Code tool-call compatibility not ready
```

No prior blocked result is deleted or reinterpreted.

## Not Authorized

This review does not authorize:

```text
DS-R0 rerun
readiness sessions
primary / holdout / carryover benchmark sessions
weakening the read-only tool requirement
removing tool-use isolation
parsing prose as a tool result
changing benchmark cases
changing prompts
changing frozen Arm A/B/C inputs
changing MVP code
changing producers
changing thresholds
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Next Status

```text
DeepSeek track:
BLOCKED AT DS-R0 P4

readiness:
NOT AUTHORIZED

primary benchmark:
NOT AUTHORIZED

efficiency claim:
NOT AUTHORIZED

release:
NOT AUTHORIZED
```

Future work requires a separate methodological decision. Acceptable next
directions may include a different harness, a provider/tooling update followed
by a new remediation chain, or leaving the DeepSeek-via-Claude-Code benchmark
track blocked. None is authorized by this review.
