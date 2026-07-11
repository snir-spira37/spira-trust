# SPIRA Counterfactual Session Replay Methodology

## Status

```text
METHODOLOGY_LOCKED_BEFORE_REPLAY
```

## Research Program Boundary

This methodology belongs to the broader SPIRA Local Agent Efficiency research
program.

It does not change the product claim or scope of SPIRA Trust.

```text
SPIRA Trust:
Python artifact evidence
-> deterministic verification
-> compact action contract
-> exact-context reuse
-> fail-closed rerun planning
```

```text
Broader research program:
existing local tools
+ compact deterministic contracts
+ internal orchestration
-> potential session-wide context reduction
```

The broader program is a research hypothesis. It is not a current SPIRA Trust
capability or public product claim.

## Research Question

Can a local orchestration layer materially reduce total coding-session context
by replacing large raw tool outputs with smaller, sufficient, deterministic
responses at the moment those outputs first enter the conversation history?

The experiment must account for two forms of saving:

```text
1. Immediate saving:
   fewer fresh tokens when the event first enters context.

2. Propagated saving:
   a smaller event remains in the cached conversation prefix across later
   model calls until it is removed, compacted, or truncated.
```

## Core Hypothesis

Large raw outputs from deterministic tools may be replaced by smaller structured
contracts without changing the agent's ability to perform the next required
action.

If the replacement enters the history in place of the raw output, the saving may
propagate through subsequent cached-input calls.

The experiment tests this hypothesis. It does not assume it is true.

## Session Selection

The first replay uses one preselected validated session:

```text
session type: program completion
project class: SPIRA evidence-tooling development
selection reason: longest validated session, chosen to make accumulated history effects observable
```

The session is not claimed to represent general coding-agent work.

Because it comes from an evidence-heavy SPIRA project, its tool-answerable share
may be higher than in ordinary software-development sessions.

No session may be replaced after results are observed merely because another
session produces a more favorable saving ratio.

## Existing Baseline

The replay uses the recorded session as the factual baseline:

```text
actual provider-reported usage
actual tool events
actual event order
actual compaction markers
actual model-call boundaries
actual raw visible output sizes
```

The baseline is not regenerated or altered.

## Unit of Analysis

The primary unit is a model-visible event.

An event may include:

```text
tool result
file read
search result
Git output
test output
artifact evidence
workspace-state output
environment output
injected fixed context
compaction summary
```

Each event receives:

```text
event_id
session_id
timestamp or sequence position
source tool
safe command class
safe path class
raw visible bytes
first model call containing the event
last model call before removal or compaction
tool-answerability class
replacement tool or adapter
replacement measurement status
sufficiency confidence
classification confidence
addressability
```

Raw transcript content, source code, prompts, tool outputs, credentials,
personal paths, and API keys must not appear in published results.

## Tool-Answerability Classes

### A. `EXACT_EXISTING_TOOL`

A currently available deterministic tool can answer the relevant question
directly.

Examples:

```text
SPIRA trust / graph / status / cache / plan-rerun
Git status / diff summary / log / blame
LSP definitions / references / call hierarchy
ripgrep or structural code search
pytest/JUnit result query
workspace inventory and digest query
environment-version query
```

Requirements:

```text
- the tool exists at replay time;
- it can be run on the frozen relevant state;
- its compact output is captured and measured;
- no hypothetical output size is allowed;
- the output must pass sufficiency review.
```

### B. `EXACT_EXISTING_ADAPTER`

A currently runnable deterministic adapter transforms an existing tool's raw
output into a smaller structured contract.

Examples:

```text
test failure contract
build-state contract
code-change digest
dependency-state reconciliation
task-checkpoint query
```

Requirements are the same as Class A.

If the adapter does not exist and cannot be run at replay time, the event must
not remain in Class B.

It moves to Class C.

### C. `BOUNDED_SUMMARY`

A smaller structured response appears possible, but no existing deterministic
tool or adapter currently produces it.

Its compact size is therefore modeled rather than measured.

Requirements:

```text
- the output schema must be specified;
- the size assumption must be labeled MODELED;
- the event is excluded from the lower and realistic bounds;
- it may appear only in the upper research bound;
- sufficiency must still be reviewed.
```

### D. `NOT_TOOL_ANSWERABLE`

The event cannot reasonably be replaced by deterministic local tooling.

Examples:

```text
creative code generation
architectural judgment
ambiguous product decisions
user-intent interpretation
open-ended reasoning
trade-offs without a mechanical answer
```

These events remain fully in the counterfactual history.

They are not treated as failed optimization opportunities.

## Replacement Size Rule

`compact_target_tokens` must never be an unsupported guess in Classes A or B.

For each Class A or B event:

```text
1. run the actual replacement tool or adapter;
2. capture its actual compact output;
3. record its UTF-8 byte size;
4. record its token count when the provider tokenizer is available;
5. otherwise derive modeled token attribution through the locked allocation method;
6. preserve the raw and compact output hashes;
7. do not preserve the raw content in public results.
```

Required fields:

```yaml
replacement_measurement:
  status: MEASURED
  tool_name: string
  tool_version: string
  command_fingerprint: sha256
  input_state_fingerprint: sha256
  raw_output_sha256: sha256
  compact_output_sha256: sha256
  raw_visible_bytes: integer
  compact_visible_bytes: integer
  tokenizer_status: string
  measured_or_modeled_tokens: number
```

For Class C:

```text
replacement_measurement.status: MODELED
```

A Class C estimate must never be presented as an observed saving.

## Token Attribution

Provider-reported session usage is factual.

Per-event contribution is attributed through a model.

```text
Provider-reported usage:
ACTUAL

Event-level token attribution:
MODELED
```

The default allocation method is:

```text
PROPORTIONAL_TO_MODEL_VISIBLE_UTF8_BYTES
```

For each model call:

```text
allocated_fresh_tokens(event)
=
provider_reported_fresh_tokens_for_call
*
event_visible_bytes
/
total_new_visible_bytes_for_call
```

If a model-specific tokenizer is available and validated for the session
provider/model, tokenized event sizes may replace byte-proportional allocation.

The output must state which method was used.

## Sufficiency Audit

A smaller answer is not counted as a valid replacement merely because it is
smaller.

The compact answer must be sufficient for the actual next action performed by
the agent.

Sufficiency is evaluated against the recorded transcript locally.

Transcript content may be inspected locally for this audit, but it must not be
copied into the result files.

### Sufficiency Levels

#### `HIGH`

The next action depends only on facts contained in the compact output.

The agent did not rely on raw-output details absent from the compact contract.

Examples:

```text
The agent only needed:
- which tests failed;
- whether the artifact changed;
- which files were modified;
- which symbol references exist;
- whether the gate says STOP or PROCEED.
```

#### `MEDIUM`

The compact response probably contains enough information, but some dependence
on omitted raw detail cannot be ruled out.

#### `LOW`

The agent relied on raw-output details not contained in the compact response.

Examples:

```text
specific traceback lines
exact compiler diagnostics
precise diff hunks
full surrounding source context
individual log messages used in diagnosis
```

#### `INSUFFICIENT`

The compact output clearly could not support the recorded next action.

### Scenario Inclusion

```text
Lower bound:
Class A only
replacement output MEASURED
sufficiency HIGH
classification HIGH

Realistic bound:
Classes A and B
replacement output MEASURED
sufficiency HIGH
classification HIGH or MEDIUM

Upper research bound:
Classes A, B, and C
sufficiency HIGH or MEDIUM
Class C compact size explicitly MODELED
```

`LOW` and `INSUFFICIENT` events are not counted as replaceable.

## Partial Drill-Down

An event that requires some raw details must not automatically be counted as
fully replaceable.

A partial replacement may be evaluated only when an actual drill-down mechanism
exists.

Example:

```text
compact test summary
+
actual command returning one selected traceback
```

The measured replacement size must include both:

```text
compact contract
+
actual drill-down output
```

Without an executable drill-down path, the event remains `LOW`,
`INSUFFICIENT`, or Class C.

## Context Lifetime and Reuse

A raw event does not remain in context forever.

Its propagated saving is capped by the event's actual context lifetime.

For every candidate event, record:

```text
first_visible_model_call
last_visible_model_call
reuse_count
termination_reason
reuse_confidence
```

Valid termination reasons:

```text
SESSION_END
EXPLICIT_COMPACTION
CONTEXT_TRUNCATION
REPLACED_BY_COMPACTION_SUMMARY
UNKNOWN_BOUNDARY
```

### Reuse Rule

```text
reuse_count
=
number of subsequent model calls in which the event remained part of the
conversation prefix before the first terminating boundary
```

The original fresh appearance is not included in `reuse_count`.

### Compaction Rule

At the first compaction event that absorbs or removes the raw event:

```text
- the raw event stops accumulating reuse;
- the compaction summary becomes a new event;
- the raw event is not counted after that boundary;
- no saving is projected beyond the boundary unless the smaller replacement
  is shown to affect the measured size of the compaction summary.
```

If the analyzer cannot determine whether a compaction removed the event:

```text
reuse_confidence: LOW
termination_reason: UNKNOWN_BOUNDARY
```

Such propagated savings are excluded from the lower bound.

They may be included only in the upper bound with explicit disclosure.

## Counterfactual Saving Formula

For each replaceable event:

```text
immediate_saving_i
=
raw_i - compact_i
```

```text
propagated_saving_i
=
(raw_i - compact_i) * reuse_i
```

```text
total_token_volume_saving_i
=
(raw_i - compact_i) * (1 + reuse_i)
```

Where:

```text
raw_i:
attributed token size of the original event

compact_i:
measured replacement size for Classes A/B,
modeled replacement size for Class C

reuse_i:
actual or bounded number of subsequent prefix appearances before compaction,
truncation, or session end
```

Negative savings remain in the results.

They must not be clamped to zero.

## Cost-Weighted View

Token volume and monetary cost are reported separately.

```text
cost_saving_i
=
(raw_i - compact_i) * fresh_input_price
+
(raw_i - compact_i) * reuse_i * cached_input_price
+
cache_creation_effect, when provider-reported and attributable
```

Pricing must be explicit by:

```text
provider
model
date
fresh input price
cached read price
cache creation price
output price
```

No universal cached-token discount is assumed.

If reliable pricing is unavailable, cost saving is `NOT_EVALUATED`.

## Decision-Quality View

The experiment must not report a saving without considering whether the
replacement preserves the required action.

For every replacement candidate, record:

```text
next_action_preserved
required_information_preserved
exact_action_language_preserved, when applicable
drill_down_required
sufficiency_confidence
```

An event with lower token volume but insufficient information is not a
successful replacement.

## Replay Scenarios

### Scenario 1 - Conservative Lower Bound

Includes only:

```text
EXACT_EXISTING_TOOL
MEASURED replacement
HIGH sufficiency
HIGH classification confidence
HIGH reuse confidence
```

### Scenario 2 - Realistic Bound

Includes:

```text
EXACT_EXISTING_TOOL
EXACT_EXISTING_ADAPTER
MEASURED replacement
HIGH sufficiency
HIGH or MEDIUM classification confidence
HIGH or MEDIUM reuse confidence
```

### Scenario 3 - Upper Research Bound

Includes:

```text
Classes A, B, and C
MEASURED and MODELED replacements
HIGH or MEDIUM sufficiency
HIGH or MEDIUM classification confidence
HIGH, MEDIUM, or disclosed LOW reuse confidence
```

The upper bound is a research ceiling.

It is not a product claim or build authorization.

## Required Metrics

For the session and for each scenario:

```text
actual total input tokens
actual fresh input tokens
actual cached input tokens
actual output tokens

candidate event count
replaceable event count
insufficient event count
unknown event count

raw candidate bytes/tokens
compact replacement bytes/tokens

immediate fresh saving
propagated cached-prefix saving
total token-volume saving
cost-weighted saving, if evaluated
context-window occupancy reduction

classification coverage
sufficiency coverage
reuse-horizon coverage
LOW-confidence share
UNKNOWN share
```

Primary ratio:

```text
counterfactual_total_input_reduction_pct
```

Secondary ratios:

```text
counterfactual_fresh_input_reduction_pct
counterfactual_cached_prefix_reduction_pct
cost_weighted_reduction_pct
```

## Validity Gates

The replay is invalid if any of the following occurs:

```text
parse errors > 0
unresolved duplicate usage
event allocation coverage < 85%
tool-answerability classification coverage < 85%
reuse-horizon coverage < 85% for the claimed scenario
replacement sizes for Classes A/B are not measured
sufficiency was not reviewed
compaction boundaries are ignored
raw transcript content appears in public outputs
secrets or personal absolute paths appear in outputs
```

An invalid replay produces:

```text
REPLAY_INVALID
```

It must not produce a decision about the 50% research target.

## Predeclared Decision Thresholds

### Lower bound below 10%

```text
NO_JUSTIFICATION_FOR_BROAD_ORCHESTRATOR_PILOT
```

The measured deterministic opportunity is too small to justify building a
broader system.

### Realistic bound below 20%

```text
WEAK_SESSION_WIDE_OPPORTUNITY
```

Do not build a broad orchestrator.

Narrow tool improvements may continue only when independently justified.

### Realistic bound from 20% to below 40%

```text
JUSTIFY_THREE_TOOL_ORCHESTRATOR_PILOT
```

A bounded pilot may connect no more than three existing tool families.

Recommended initial families:

```text
SPIRA artifact evidence
Git state
test-state parser
```

### Realistic bound from 40% to below 50%

```text
STRONG_COUNTERFACTUAL_SUPPORT
```

Proceed to a live A/B pilot, but do not claim 50% session-wide saving.

### Realistic bound at or above 50%

```text
COUNTERFACTUAL_TARGET_SUPPORTED
```

The result supports the research target counterfactually.

A live controlled A/B experiment is still required before a product or
performance claim.

### Only upper bound exceeds 50%

```text
INDETERMINATE_MODELED_UPPER_BOUND_ONLY
```

No build or public claim is authorized solely by the upper bound.

## Live Pilot Requirement

Counterfactual support is not final proof.

Any positive build decision must be followed by a live A/B experiment:

```text
same repository
same task
same model
same initial context
same tool permissions
fresh session for each arm
multiple repetitions
```

Arm A:

```text
work agent receives normal raw tool outputs
```

Arm B:

```text
internal orchestrator returns compact deterministic contracts
raw evidence available only through explicit drill-down
```

Measure:

```text
fresh input tokens
cached input tokens
total input tokens
output tokens
cost
wall-clock time
tool calls
task correctness
decision correctness
required-detail preservation
```

## Privacy

The replay may inspect transcript content locally only for sufficiency review
and context-lifetime determination.

Public and persisted results must not contain:

```text
prompt text
assistant text
source code
tool output
raw commands
raw file paths
home-directory paths
API keys
credentials
authorization headers
private repository content
```

Allowed persisted data:

```text
safe event classes
safe path classes
command classes
hashes
sizes
usage counts
timestamps or relative sequence numbers
classification labels
confidence labels
decision outcomes
```

## Reproducibility Outputs

The replay must produce:

```text
counterfactual_replay_manifest.json
tool_answerability_rules.json
replacement_measurements.json
event_classification.csv
sufficiency_audit.csv
compaction_boundaries.csv
reuse_horizon.csv
counterfactual_results.json
counterfactual_results.md
not_claimed.md
SHA256SUMS.txt
```

## Not Claimed

This replay does not claim that:

```text
- SPIRA Trust itself reduces total session tokens by 50%;
- every coding session resembles the selected SPIRA session;
- modeled Class C outputs exist as working tools;
- smaller context is always sufficient;
- provider cache behavior is fully reconstructed;
- token-volume saving equals monetary saving;
- a counterfactual result equals a live A/B result;
- a local orchestrator should be built regardless of the result;
- creative reasoning can be replaced by deterministic tools;
- the broader research program is a released SPIRA capability.
```

## Final Status Vocabulary

The replay must end with exactly one of:

```text
REPLAY_INVALID

NO_JUSTIFICATION_FOR_BROAD_ORCHESTRATOR_PILOT

WEAK_SESSION_WIDE_OPPORTUNITY

JUSTIFY_THREE_TOOL_ORCHESTRATOR_PILOT

STRONG_COUNTERFACTUAL_SUPPORT

COUNTERFACTUAL_TARGET_SUPPORTED

INDETERMINATE_MODELED_UPPER_BOUND_ONLY
```

## Core Research Principle

```text
Do not estimate a compact answer when an actual tool can be run.

Do not count a smaller answer when it would not have been sufficient.

Do not propagate a saving beyond the event's real compaction boundary.

Do not build the orchestrator unless the replay justifies it.
```

The long validated session is suitable as a pilot for accumulation effects, but
its result remains labeled as a SPIRA evidence-tooling case. Only after the
replay passes the validity gates and the predeclared thresholds is there
justification to consider connecting SPIRA, Git, and a test parser in a live
pilot.
