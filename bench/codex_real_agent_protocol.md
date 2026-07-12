# SPIRA Codex Real-Agent Benchmark Protocol

## Status

```text
PROTOCOL_LOCKED_PENDING_CODEX_CLI_SMOKE
```

## Boundary

This protocol defines a live autonomous agent tool-use benchmark for SPIRA
artifact gate questions.

It does not authorize:

```text
new SPIRA capability
new producer
orchestrator
DeepSeek results presented as Codex results
token or energy claim before a valid run
```

The primary path is:

```text
Codex CLI
real tools
clean sessions
provider/tool usage counters from Codex transcripts
```

Secondary replication may use Claude Code. DeepSeek API remains fallback only,
and must be labeled as a prompt-injection/file-ingestion benchmark, not an
autonomous agent tool-use benchmark.

## Required Smoke Before Running

Before any benchmark run, Codex CLI must pass an operational smoke:

```text
codex --version
start one minimal clean session
confirm a new transcript/JSONL is written
confirm usage counters are present
confirm tool calls are represented in the transcript
```

If the smoke fails, the benchmark status remains:

```text
CODEX_REAL_AGENT_RUN_NOT_AUTHORIZED
```

No fallback run may be reported as Codex.

## Cases

The two cases are frozen from `bench/results/live_v2/` and the PEP 770 corpus
manifest:

```text
median_minijinja
package: minijinja
version: 2.18.0
wheel: minijinja-2.18.0-cp38-abi3-win_amd64.whl
sha256: f6e9ac8256fc5453e2c5ab91a44201447ea4975c341535a7aa623447b88b7c4e

p90_nutpie
package: nutpie
version: 0.16.8
wheel: nutpie-0.16.8-cp314-cp314-win_amd64.whl
sha256: 80c067162053510d41ab4635a14bf38328b6d531d0d68e896ca95e9024b31823
```

The cases may not be replaced after results are observed.

## Arms

### Arm A - Raw Discovery

The agent receives only:

```text
artifact path
evidence directory
shared task prompt
```

The prompt does not mention `agent_summary.json`, status, cache, action
contract, or unification proof.

The agent chooses which files and tools to inspect.

### Arm B - Agent Summary

The agent receives the same task with this additional instruction:

```text
Read agent_summary.json first.
Use full evidence only if required.
```

### Arm C - Current SPIRA Flow

The agent receives the same task with this additional instruction:

```text
Run status --agent first.
If checked and unchanged, query the exact-context cache.
Use the returned action contract and unification reference.
Drill down only if the compact contract is insufficient.
```

Arm C must read the status/cache output that contains `stop`,
`recommended_agent_action`, and `reason_codes`. The 176-byte unification handle
alone is not the decision; it is a proof/drill-down reference.

### Arm D - Repeated Exact-Context Query

Arm D is measured inside the same session as Arm C:

```text
first gate question
-> status/cache/action

same gate question again
-> exact-context cache hit
```

This measures repeated-query reuse. It is not compared against a fresh clean
session.

## Shared Prompt

```text
Based only on the available SPIRA evidence, determine whether the artifact gate
says PROCEED or STOP for the specified wheel.

Return exactly:
- PROCEED or STOP
- SPIRA verdict
- recommended_agent_action
- reason_codes
- not_evaluated
- evidence or proof reference
- one sentence describing what is not claimed

Do not claim that the package is safe, malware-free, or production-ready.
Do not reinterpret SPIRA gate semantics when an explicit stop/action contract is available.
```

Arm-specific instructions are appended after the shared prompt.

## Run Count

Main arms:

```text
2 wheels
x 3 arms
x 3 repetitions
= 18 clean sessions
```

Repeated cache arm:

```text
2 wheels
x 3 repeated-query measurements
= 6 Arm D measurements
```

Every A/B/C run must use a clean session. Arm D intentionally reuses the Arm C
session because it measures exact-context reuse inside a continuing agent
interaction.

## Validity Gates

A run is valid only if it returns:

```text
expected PROCEED/STOP
exact recommended_agent_action
semantic reason_codes
NOT_EVALUATED preserved
no safety overclaim
```

Token savings without action equivalence are a failure, not a success.

## Metrics

For every run, record:

```text
fresh input tokens
cached input tokens
total input tokens
output tokens
tool-call count
files read
wall-clock time
final verdict correctness
exact action preservation
reason-code preservation
drill-down count
```

Separately record:

```text
first-query cost
second-query cache-hit cost
```

## Predeclared Decision Rules

```text
C improves less than 10% over B on first query
-> no additional token-efficiency claim beyond agent_summary
-> unification remains binding/audit value, not token-saving value

C improves at least 10% over B with equal correctness
-> current SPIRA flow may claim live-agent efficiency improvement

Repeated cache query improves at least 20% over first C query
-> cache may claim narrow live benefit for repeated exact-context queries

Repeated cache query improves less than 20%
-> cache remains correctness/reuse feature with regression speed result only

Any arm loses exact action or reason codes
-> that arm fails regardless of token savings
```

## Expected Outcome

The predeclared expectation is:

```text
A -> B:
large improvement

B -> C first query:
small or zero improvement

C first -> C repeated:
cache value should appear here

unification handle:
audit/binding value, not large additional token savings by itself
```

This expectation is not a result. The benchmark must report the measured
outcome even when it is weaker than expected.

## Not Claimed

This protocol does not claim:

```text
SPIRA saves tokens in every agent workflow
Codex behavior generalizes to every agent
DeepSeek API results are Codex tool-use results
unification proof is a safety proof
cache is human approval
any package is safe
energy or CO2 savings
```

## Next Authorized Action

The only next authorized action is:

```text
complete a Codex CLI operational smoke
```

Only if that smoke passes may the 18 clean sessions and 6 repeated-query
measurements be run.

