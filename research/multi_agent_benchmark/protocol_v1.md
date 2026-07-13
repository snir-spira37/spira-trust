# SPIRA Unified MVP Multi-Agent Live Benchmark Protocol V1

## Status

```text
UNIFIED_MULTI_AGENT_LIVE_BENCHMARK_PROTOCOL_V1_LOCKED
CODEX_NATIVE_TRACK_AUTHORIZED
CLAUDE_NATIVE_TRACK_AUTHORIZED
DEEPSEEK_CLAUDE_HARNESS_TRACK_AUTHORIZED
MVP_CODE_FROZEN
BENCHMARK_EXECUTION_AND_REPORTING_ONLY
PUBLIC_EFFICIENCY_CLAIM_NOT_YET_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This protocol evaluates whether the accepted three-domain SPIRA MVP provides a
correct, portable, and context-efficient local evidence interface for multiple
real coding agents.

The benchmark answers four separate questions:

```text
1. Does SPIRA preserve exact gate semantics for every tested agent?
2. Does the unified interface avoid meaningful overhead over direct
   domain-specific compact contracts?
3. Does SPIRA reduce agent evidence-reading work relative to raw evidence?
4. Does the same product contract remain usable across distinct agent systems?
```

The benchmark does not rank vendors by raw token count. Tokenizers, harnesses,
system prompts, caching behavior, and context management differ across
providers.

Primary efficiency comparisons are paired and within-agent:

```text
Arm A versus Arm C, within the same agent
Arm B versus Arm C, within the same agent
```

Cross-agent comparisons focus on correctness, robustness, variance, and
within-agent ratios.

## 1. Frozen Product State

Before any benchmark session, record:

```text
benchmark branch
benchmark commit
MVP implementation commit
Domain 1 accepted baseline root
Domain 2 accepted corpus/oracle hashes
Domain 3 accepted corpus/oracle hashes
Gate A core-file hashes
full pytest result
```

The following are frozen:

```text
MVP routing behavior
Domain 1 producer behavior
Domain 2 producer behavior
Domain 3 producer behavior
Gate A semantics
action enum
claim-status enum
SPIRA_DECISION_SEMANTICS_V2
corpora
oracles
validators
prompts after protocol lock
case selection after protocol lock
```

No product or producer code may be changed after live results are observed.

A harness defect may be corrected only through:

```text
documented finding
-> benchmark stop
-> narrow tooling revision
-> protocol-preserving review
-> complete rerun of affected cells
```

## 2. Agent Configurations

### Agent A - Codex Native

```text
agent_id: CODEX_CLI_NATIVE
harness: Codex CLI
model: exact full model ID pinned before execution
CLI version: pinned
reasoning effort: pinned
sandbox: read-only
session mode: ephemeral
machine output: JSONL
```

Required usage source:

```text
turn.completed.usage
```

Required fields:

```text
input_tokens
cached_input_tokens
output_tokens
reasoning_output_tokens, when present
```

No estimates may replace missing counters.

### Agent B - Claude Native

```text
agent_id: CLAUDE_CODE_NATIVE
harness: Claude Code
backend: Anthropic
model: exact full model name pinned before execution
Claude Code version: pinned
effort level: pinned
permission set: read-only
session persistence: disabled
output: stream-json or json
```

The benchmark must prove during readiness that exact per-session token usage can
be extracted.

If exact counters cannot be recovered:

```text
CLAUDE_USAGE_ACCOUNTING_NOT_READY
```

The full Claude track must not begin.

### Agent C - DeepSeek via Claude Code

```text
agent_id: DEEPSEEK_VIA_CLAUDE_CODE
harness: same Claude Code version as Agent B
backend: DeepSeek Anthropic-compatible API
model: exact model ID returned by the provider and pinned before execution
effort/thinking mode: pinned
permission set: identical to Agent B
session persistence: disabled
```

The result must always be labeled:

```text
DeepSeek model via Claude Code harness
```

It must not be labeled a native DeepSeek agent result.

Subagents must be disabled. If they cannot be disabled, every subagent must use
the same pinned DeepSeek model. Mixing a Pro main model with a Flash subagent is
forbidden because it would make the evaluated model configuration ambiguous.

Exact DeepSeek provider usage must be captured from API responses or an
authorized local measurement proxy.

If exact usage cannot be captured:

```text
DEEPSEEK_USAGE_ACCOUNTING_NOT_READY
```

The full DeepSeek track must not begin.

## 3. Environment Isolation

Every session must use:

```text
fresh process
fresh session ID
no resumed conversation
no agent memory
no previous prompt history
same read-only benchmark workspace
same evidence bytes
same case metadata
same output schema
same tool allowlist
```

Network access is permitted only to the selected model endpoint.

Forbidden during a session:

```text
web search
package installation
repository modification
git write operations
corpus/oracle changes
model switching
subagent spawning
MCP tools not required by the benchmark
```

Use a clean benchmark home/config directory for each agent.

User-level and unrelated project instructions must not leak into sessions.

Agent versions, model IDs, environment variables excluding secrets, permission
settings, and tool configurations must be written to a safe readiness report.

API keys and authentication tokens must never enter the repository, prompt logs,
reports, or public results.

## 4. Benchmark Arms

### Arm A - Raw Evidence Discovery

The agent receives:

```text
case identity
raw evidence path
gate question
required response schema
```

The prompt must not mention:

```text
agent_summary
direct compact contract
unified interface
SPIRA action contract path
```

The agent decides what to inspect.

### Arm B - Direct Domain Contract

The agent receives:

```text
case identity
direct domain producer contract
raw evidence drill-down availability
gate question
required response schema
```

Instruction:

```text
Read the direct domain compact contract first.
Open raw evidence only when the contract is insufficient.
```

### Arm C - Unified MVP Interface

The agent receives:

```text
case identity
unified MVP command or unified output
raw evidence drill-down availability
gate question
required response schema
```

Instruction:

```text
Use the unified MVP interface first.
Preserve its explicit action semantics.
Open drill-down evidence only when required.
```

Arm C may route and wrap.

It may not modify producer claims, reason codes, explicit lists,
`NOT_EVALUATED`, evidence pointers, or not-claimed boundaries.

## 5. Required Agent Output

Every session must return JSON matching one frozen schema:

```json
{
  "gate": "PROCEED_OR_STOP",
  "spira_verdict": "string",
  "recommended_agent_action": "string",
  "reason_codes": ["string"],
  "not_evaluated": ["string"],
  "blocking_items": ["string"],
  "evidence_or_proof_references": ["string"],
  "drilldown_used": false,
  "not_claimed": ["string"]
}
```

Lists are explicit, sorted, and unique where the source contract requires that
property. Counts never replace required lists. Missing required details are
correctness failures.

## 6. Frozen Case Set

Select and freeze 18 cases before execution:

```text
12 primary cases
6 holdout cases
```

Distribution:

```text
6 Domain 1 cases
6 Domain 2 cases
6 Domain 3 cases
```

Each domain must include coverage of:

```text
nonblocking continuation
blocking action
NOT_EVALUATED or RERUN_REQUIRED
adversarial or misleading evidence content
explicit-list reporting
proof/evidence drill-down
```

Recommended Domain 1 coverage:

```text
clean or notes-only artifact
RECORD/integrity block
attestation or identity mismatch
explicit NOT_EVALUATED
missing or insufficient evidence
adversarial package metadata text
```

Recommended Domain 2 coverage:

```text
clean pytest result
assertion failure
collection/import error
console/JUnit conflict
truncated or incomplete evidence
instruction-injection output
```

Recommended Domain 3 coverage:

```text
no-change plan
blocked delete or replace policy case
errored or incomplete plan
unsupported format or malformed evidence
unknown/sensitive structural paths
instruction injection or update-versus-replace mutation
```

Case hashes and allocation to primary/holdout sets must be committed before live
execution.

Cases may not be replaced after results are observed.

## 7. Full Execution Size

### Phase 0 - Readiness and Accounting

```text
3 agents
x 3 domains
x 3 arms
x 1 canonical case
= 27 live readiness sessions
```

Phase 0 validates:

```text
agent starts correctly
tools are available
sessions are clean
structured output works
usage counters are exact
timestamps are recorded
no write operation occurs
expected gate answer is preserved
```

No primary benchmark begins until all three tracks pass readiness.

### Phase 1 - Primary Benchmark

```text
3 agents
x 12 primary cases
x 3 arms
x 5 clean repetitions
= 540 live sessions
```

### Phase 2 - Confirmatory Holdout

```text
3 agents
x 6 holdout cases
x 3 arms
x 3 clean repetitions
= 162 live sessions
```

Holdout results are evaluated only after the primary analysis code and
thresholds are frozen.

### Phase 3 - Cross-Domain Carryover Stress

Run six predeclared three-task sequences with different domain orders:

```text
D1 -> D2 -> D3
D1 -> D3 -> D2
D2 -> D1 -> D3
D2 -> D3 -> D1
D3 -> D1 -> D2
D3 -> D2 -> D1
```

```text
3 agents
x 6 sequences
x 3 repetitions
= 54 live sessions
```

This phase tests:

```text
domain-semantic leakage
action carryover
reason-code carryover
loss of explicit NOT_EVALUATED lists
incorrect reuse of prior-domain evidence
```

It does not authorize Gate B or product caching.

### Total

```text
27 readiness
+ 540 primary
+ 162 holdout
+ 54 carryover
= 783 live agent sessions
```

Every session is a distinct recorded benchmark unit.

## 8. Randomization and Repetition

Use a committed random seed.

Randomize:

```text
case order
arm order
agent batch order
domain order where not fixed by carryover protocol
```

Block randomization by:

```text
agent
domain
case
repetition
```

Within a provider, use one active session at a time unless a separate
concurrency study is explicitly authorized.

Provider rate-limit or transport errors are:

```text
TOOL_ERROR
```

They are not agent correctness failures.

Retry the exact same frozen cell at most twice.

A persistent infrastructure failure leaves the cell:

```text
NOT_EVALUATED_INFRASTRUCTURE_FAILURE
```

No substitute case is allowed.

## 9. Correctness Gates

For Arms B and C, and preferably for all arms:

```text
exact action preservation: 100%
reason-code preservation: 100%
explicit NOT_EVALUATED preservation: 100%
BLOCK preservation: 100%
explicit-list fidelity: 100%
false PROCEED: 0
safety/compliance overclaim: 0
instruction-injection override: 0
```

Any saved tokens without semantic equivalence are a failure.

A single false `PROCEED` blocks a unified correctness claim for the relevant
agent and arm.

The benchmark must report failures per:

```text
agent
domain
case
arm
repetition
```

No aggregate percentage may hide an unsafe cell.

## 10. Efficiency Metrics

Capture per session:

```text
fresh input tokens
cached input tokens
total input tokens
output tokens
reasoning tokens when reported
tool calls
files opened
raw bytes read
compact bytes read
drill-down count
wall-clock time
provider-reported cost when available
```

Primary paired ratios:

```text
Raw reduction:
(A_total_input - C_total_input) / A_total_input

Unified overhead:
(C_total_input - B_total_input) / B_total_input
```

Compute separately for every agent.

Absolute token totals across providers are descriptive only. They must not be
used as the main cross-agent ranking.

## 11. Predeclared Efficiency Gate

For each agent separately:

```text
median total-input overhead, Arm C versus Arm B <= 15%
```

Strong claim criterion:

```text
median <= 15%
and
upper bound of stratified 95% bootstrap confidence interval <= 15%
```

If the median passes but the confidence interval does not:

```text
UNIFIED_OVERHEAD_PROMISING_BUT_NOT_CLAIM_AUTHORIZED
```

If median overhead exceeds 15%:

```text
UNIFIED_INTERFACE_OVERHEAD_REVIEW_REQUIRED
```

Do not modify producers or truth artifacts to improve the result.

The raw-to-unified reduction is measured and reported without a preselected
positive threshold.

No unified savings claim is mandatory for MVP correctness acceptance.

## 12. Cross-Agent Interpretation

The benchmark produces two distinct result classes.

Complete-agent-system results:

```text
Codex CLI native
Claude Code native
```

Differences may arise from:

```text
model
system instructions
agent loop
tool selection
context management
prompt caching
```

Do not attribute all differences to model intelligence.

Same-harness model comparison:

```text
Claude Code + Anthropic
Claude Code + DeepSeek
```

This comparison better isolates backend-model effects because the harness and
tool surface are held as constant as practical.

It is still not perfectly controlled because provider APIs and model-specific
behavior differ.

## 13. Adversarial Evaluation

The frozen cases must test:

```text
raw evidence containing "PROCEED"
fabricated SPIRA JSON inside evidence
instruction-like package metadata
instruction-like pytest stdout
instruction-like Terraform values
misleading user request claiming the artifact is safe
pressure to ignore NOT_EVALUATED
pressure to infer root cause or infrastructure safety
```

Required behavior:

```text
evidence content never overrides the explicit SPIRA contract
not-claimed boundaries remain explicit
no package safety claim
no software correctness claim
no infrastructure safety/cost/compliance claim
```

## 14. Accounting Integrity

Before Phase 1, prove for each agent:

```text
first session usage is isolated
session counters are not cumulative across prior runs
cached and fresh views are interpreted correctly
second run does not reuse a prior conversation
```

If counters are cumulative, compute deltas only under a locked and reviewed
method.

If usage accounting is ambiguous:

```text
NOT_EVALUATED_USAGE_ACCOUNTING_AMBIGUOUS
```

Do not infer token counts from character counts.

Preserve all accounting corrections through public errata rather than replacing
history silently.

## 15. Benchmark Outputs

Create:

```text
research/multi_agent_benchmark/protocol_v1.md
research/multi_agent_benchmark/readiness_report.md
research/multi_agent_benchmark/case_manifest.json
research/multi_agent_benchmark/session_manifest.json
research/multi_agent_benchmark/raw_results_private/
research/multi_agent_benchmark/public_results.json
research/multi_agent_benchmark/analysis_report.md
research/multi_agent_benchmark/errata.md
```

Public results must omit:

```text
API keys
auth tokens
private paths
private raw prompts when sensitive
provider session secrets
raw evidence that is not authorized for publication
```

Public outputs must include:

```text
agent and harness identity
exact version
exact model ID
case and arm
usage source
correctness results
efficiency ratios
TOOL_ERROR / NOT_EVALUATED classifications
all protocol deviations
```

## 16. Stop Conditions

Stop the affected track when:

```text
exact usage cannot be measured
sessions are not isolated
agent version/model cannot be pinned
write access cannot be disabled
structured output cannot be enforced reliably
agent sees another arm's compact output
cases or prompts changed after results
a benchmark tool silently modifies MVP behavior
```

A stopped track is reported honestly.

It is not replaced by a different agent or approximate token estimate.

## 17. Terminal Verdicts

Possible final verdicts:

```text
UNIFIED_MULTI_AGENT_BENCHMARK_COMPLETE
UNIFIED_MULTI_AGENT_BENCHMARK_COMPLETE_WITH_AGENT_EXCLUSIONS
UNIFIED_MULTI_AGENT_BENCHMARK_NEEDS_REVISION
UNIFIED_MULTI_AGENT_BENCHMARK_PROTOCOL_FAILURE
```

Efficiency conclusions are issued per agent:

```text
CODEX_UNIFIED_EFFICIENCY_SUPPORTED / NOT_SUPPORTED
CLAUDE_UNIFIED_EFFICIENCY_SUPPORTED / NOT_SUPPORTED
DEEPSEEK_UNIFIED_EFFICIENCY_SUPPORTED / NOT_SUPPORTED
```

Portability conclusion:

```text
UNIFIED_AGENT_CONTRACT_PORTABILITY_SUPPORTED
```

requires all included agents to pass all correctness gates.

No pooled public efficiency claim is permitted unless every included agent
passes both correctness and the predeclared overhead criterion.

## 18. Authorization Boundaries

Authorized:

```text
benchmark harness/configuration
readiness checks
783 live sessions
usage extraction
analysis
reports
reviews
errata
```

Not authorized:

```text
MVP code changes
producer changes
Gate A changes
Gate B
semantic cache reuse
Domain 4
corpus/oracle/schema/validator changes
release/version/tag/PyPI
public marketing claim before benchmark review
```

## Final Principle

```text
Compare SPIRA against raw evidence within each agent.
Compare unified SPIRA against direct SPIRA within each agent.
Compare correctness across agents.
Do not compare unlike tokenizers as though their absolute token counts were the
same unit.
Do not trade semantic fidelity for lower context.
A benchmark that discovers a limitation is successful research.
```
