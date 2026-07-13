# DeepSeek Structured Output Diagnostic Authorization

## Status

```text
DEEPSEEK_STRUCTURED_OUTPUT_DIAGNOSTIC_AUTHORIZED
TECHNICAL_DIAGNOSTIC_ONLY
NO_BENCHMARK_CASES_AUTHORIZED
DS_R0_RERUN_NOT_AUTHORIZED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
DS_R0_STRUCTURED_OUTPUT_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
MODEL_IDENTITY_CONFIRMED
CLAUDE_CODE_HARNESS_CONFIRMED
P1_DIRECT_PROVIDER_PASS
P2_CLAUDE_INIT_TOOL_INVENTORY_PASS
DEEPSEEK_STRUCTURED_OUTPUT_NOT_READY
STRUCTURED_OUTPUT_DIAGNOSTIC_AUTHORIZATION_REQUIRED
```

## Purpose

The diagnostic is authorized only to determine why DS-R0 P3 failed:

```text
returncode:
1

structured_output_found:
false

raw stdout bytes:
0
```

The diagnostic must capture enough safe metadata to distinguish:

```text
Claude Code invocation / flag interaction
Windows quoting or schema-path issue
DeepSeek backend incompatibility with Claude Code structured output
JSON mode support without schema enforcement
schema enforcement unsupported or unreliable
provider/backend error surfaced through stderr or event metadata
```

## Allowed Technical Probes

The diagnostic may run only unscored technical probes that do not use benchmark
cases.

Allowed probes:

```text
1. --output-format json without --json-schema
2. --output-format stream-json to capture system/error events
3. minimal inline schema versus schema file
4. Windows quoting and schema path checks
5. same call with --tools ""
6. same call without flags unnecessary for P3
7. capture full stderr, exit code, timeout status, and safe response metadata
8. direct provider structured-output probe if supported by the provider API
```

All prompts must be synthetic diagnostic prompts, not benchmark cases.

## Allowed Files

The diagnostic may create:

```text
tools/run_deepseek_structured_output_diagnostic.py
tests/test_deepseek_structured_output_diagnostic.py
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_results.json
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_report.md
research/multi_agent_benchmark/deepseek/structured_output_diagnostic_raw_private_manifest.json
```

No raw provider or Claude output may be committed. Raw outputs must remain
outside the repository, with only hashes, byte sizes, classifications, and safe
metadata recorded publicly.

## Required Safety

The diagnostic must not record:

```text
API keys
Authorization headers
raw private paths
raw full stderr if it contains paths or secrets
raw full stdout if it contains paths or secrets
```

Safe metadata may include:

```text
exit code
timeout status
stdout byte size
stderr byte size
stdout sha256
stderr sha256
sanitized stderr category
Claude Code version
model identity
usage availability
tool call counts
```

## Forbidden

The diagnostic must not:

```text
change benchmark output schema
change frozen prompts
change benchmark cases
change frozen Arm A/B/C inputs
change randomization
change MVP code
change producers
weaken structured output requirements
parse prose as structured output
start DS-R0 rerun
start readiness sessions
start primary/holdout/carryover sessions
make efficiency claims
merge to main
release/version/tag/PyPI
```

## Terminal Statuses

The diagnostic must end with exactly one of:

```text
STRUCTURED_OUTPUT_INVOCATION_DEFECT_FOUND
STRUCTURED_OUTPUT_SCHEMA_ENFORCEMENT_UNSUPPORTED
STRUCTURED_OUTPUT_UNSUPPORTED_OR_UNRELIABLE
STRUCTURED_OUTPUT_DIAGNOSTIC_INCOMPLETE
STRUCTURED_OUTPUT_DIAGNOSTIC_AUTHORIZATION_REVISION_REQUIRED
```

## Required Validation

After diagnostic execution:

```text
focused diagnostic tests
benchmark asset validator
JSON validation
secret/private-path scan
full pytest
frozen asset diff check
```

## Next Required Artifact

After the diagnostic:

```text
research/multi_agent_benchmark/deepseek/deepseek_structured_output_diagnostic_review.md
```

Possible verdicts:

```text
DEEPSEEK_STRUCTURED_OUTPUT_DIAGNOSTIC_ACCEPTED
DEEPSEEK_STRUCTURED_OUTPUT_DIAGNOSTIC_NEEDS_REVISION
DEEPSEEK_STRUCTURED_OUTPUT_DIAGNOSTIC_REJECTED
```

Only a future accepted diagnostic review may decide whether a narrow tooling
fix, a protocol amendment, or track blockage is the correct next step.
