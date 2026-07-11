# Decision: Retire the 50% Session-Wide Token Reduction Target

## Status

```text
BROAD_SESSION_50_PERCENT_TARGET_RETIRED_SCOPE_MISMATCH
```

SPIRA Trust will not claim, target, or optimize toward a 50% reduction in total
coding-session tokens.

The target is retired for SPIRA Trust's current product scope:

```text
Python artifact evidence
-> deterministic verification
-> combined verdict
-> compact agent action contract
-> exact-context reuse
-> minimal rerun planning
```

This is not a product failure. It is a correction of a target that did not match
the measured structure of real agent sessions.

## Evidence

A privacy-preserving session analyzer was built and validated before
measurement. It used provider-reported usage counters and metadata-based event
attribution without saving transcript content, prompts, source code, tool
outputs, raw commands, credentials, or personal paths.

After adapter audit and correction, five preselected SPIRA development sessions
passed validation in `MEASUREMENT` mode.

```text
validated sessions:              5/5
median fresh input share:        4.327%
median cached input share:      95.673%
median P_fresh_now:              0.0%
metadata evidence hits:          0
```

The adapter audit identified and corrected real parsing and attribution
problems involving Codex `agent_message`, `patch_apply_end`, and duplicate or
streaming usage records. The release/build session was rerun after the adapter
correction and passed the predeclared coverage threshold. The threshold was not
lowered.

## Interpretation

The measurement found no fresh metadata events in the five sessions that were
classified as replaceable by SPIRA's existing capabilities.

Even under the impossible best case in which all fresh input disappeared, the
median total-session reduction would be bounded by the median fresh share:

```text
maximum fresh-only reduction: approximately 4.327%
```

A 50% total-session reduction would therefore require replacing a substantial
part of the cached conversation prefix, including some combination of:

- previously read source code
- model reasoning and responses
- user instructions
- system and repository instructions
- test and Git history
- compacted conversation state
- general development context

That would require a broad coding-session context-management product. It is
outside the scope of SPIRA Trust and will not be pursued merely to rescue the
retired target.

## What This Does Not Mean

The result does not show that SPIRA has no efficiency value.

It shows that artifact-evidence work was not a large enough share of the five
measured end-to-end development sessions to support a 50% session-wide token
claim.

SPIRA's measured value remains concentrated in the narrower workflow it was
designed to improve:

```text
artifact evidence -> deterministic action
```

## Revised Product Claim

SPIRA Trust is not designed or claimed to reduce total coding-session tokens by
50%.

SPIRA converts Python artifact evidence into a compact, deterministic action
contract for coding agents. It binds the decision to the exact artifact and
evidence context, reuses it only when context and result agree, plans the
minimum required reruns, and fails closed when state is missing, changed,
conflicting, or corrupted.

Measured results supporting this narrower claim include:

- 1.71x fewer prompt tokens than a decision-only baseline in the live-v2
  benchmark.
- 12.31x-32.66x fewer prompt tokens than broad evidence injection in the
  measured live-v2 cases.
- Correct STOP and exact `REPORT_NOT_EVALUATED` preservation in 6/6
  summary-path runs.
- Incorrect PROCEED in 6/6 broad-evidence runs under the original prompt.
- Approximately 28.94x faster warm exact-context reuse than cold verification
  in the frozen cache performance benchmark.
- Compact artifact status and cache responses of approximately 1KB.
- A compact rerun plan of approximately 1.85KB in the agent memory flow
  regression.
- A 34.7x median static context reduction across a surveyed corpus of 1,954
  Python wheels with embedded SBOMs.

The broad-evidence control matters. A prompt-only fix can teach a model that
non-empty `not_evaluated` means STOP, but it leaves the broad-evidence context
cost and exact action contract outside the deterministic artifact. In live-v2,
the two full-evidence arms consumed 15,033 and 40,305 prompt tokens and preserved
the exact `REPORT_NOT_EVALUATED` action in 0/6 runs. The agent summary avoided
both the broad-context cost and the need for each consumer to reconstruct
SPIRA's action semantics in its prompt.

## Revised Positioning

```text
SPIRA does not make the agent smarter.
It removes artifact-evidence decisions that the agent should not have to
reconstruct at runtime.
```

Or, more formally:

```text
SPIRA compiles artifact evidence into a small deterministic action contract
for coding agents.
```

## Not Claimed

This decision does not claim that:

- SPIRA reduces every coding session.
- All models behave like the measured DeepSeek runs.
- Broad evidence always causes an incorrect answer.
- The cache benchmark represents every machine or repository.
- Cached token volume is equivalent to provider cost.
- SPIRA measures or reduces physical energy or CO2.
- SPIRA replaces code review, tests, malware analysis, provenance verification,
  or human approval.

## Final Decision

```text
50% session-wide token target:
RETIRED

Reason:
SCOPE_MISMATCH_CONFIRMED_BY_MEASUREMENT

SPIRA artifact-evidence efficiency claim:
RETAINED_AND_SUPPORTED

Next product direction:
NO SCOPE EXPANSION TO RESCUE THE RETIRED TARGET
```
