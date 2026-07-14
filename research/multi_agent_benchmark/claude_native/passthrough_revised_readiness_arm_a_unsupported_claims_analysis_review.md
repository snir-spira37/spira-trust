# Claude Native Passthrough Revised Readiness Arm A Unsupported Claims Analysis Review

## Verdict

```text
CLAUDE_NATIVE_PASSTHROUGH_ARM_A_UNSUPPORTED_CLAIMS_ANALYSIS_ACCEPTED

ARM_A_UNSUPPORTED_CLAIMS_PROJECTION_FALSE_POSITIVE_CONFIRMED
MODEL_BOUNDARY_SELF_REPORT_MISREAD_AS_VIOLATION
UNSUPPORTED_CLAIMS_FIELD_SEMANTIC_AMBIGUITY_CONFIRMED
GLOBAL_OUTPUT_FIELD_AMENDMENT_REQUIRED
GENUINE_ARM_A_UNSUPPORTED_CLAIM_NOT_CONFIRMED

RESULT_RECLASSIFICATION_NOT_AUTHORIZED
NEW_LIVE_SESSIONS_NOT_AUTHORIZED
CODEX_READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review covers only:

```text
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_arm_a_unsupported_claims_analysis.json
research/multi_agent_benchmark/claude_native/passthrough_revised_readiness_arm_a_unsupported_claims_analysis.md
```

The analysis stayed inside scope:

```text
existing failed Arm A cell only: yes
new live sessions: 0
raw private output committed: no
raw private path committed: no
result reclassification: no
prompt changes: no
schema changes: no
validator changes: no
runner changes: no
MVP changes: no
```

## Findings

The review accepts that Claude did not make a genuine unsupported safety claim
in the inspected explanation text.

The explanation stated that evaluation was incomplete, that multiple policies
were not evaluated, that the worst claim status was `NOT_EVALUATED`, and that
human review was required before proceeding.

Those statements preserve the safety floor. They do not assert:

```text
software_safety
package_safety
universal_supply_chain_coverage
```

The non-empty `unsupported_claims` list was a model self-report of boundaries
not claimed, not evidence that the explanation crossed those boundaries.

## Accepted Root Cause

The accepted root cause is:

```text
ARM_A_UNSUPPORTED_CLAIMS_PROJECTION_FALSE_POSITIVE_CONFIRMED
MODEL_BOUNDARY_SELF_REPORT_MISREAD_AS_VIOLATION
```

The Arm A evaluator treated any non-empty `unsupported_claims` list as a hard
failure, even when the explanation text did not assert those claims.

The review also accepts:

```text
UNSUPPORTED_CLAIMS_FIELD_SEMANTIC_AMBIGUITY_CONFIRMED
```

The prompt text can be read as asking the model to list claims it is not allowed
to make, while the runner interprets any listed value as a claim that was
actually made.

## Rejected Interpretation

This review rejects:

```text
GENUINE_ARM_A_UNSUPPORTED_CLAIM_CONFIRMED
```

The inspected explanation text does not claim safety or coverage. It explicitly
requires more review before proceeding.

## Required Next Gate

A separate global output-field/evaluator amendment authorization is required
before any fix.

That future authorization should decide whether to:

```text
rename unsupported_claims to unsupported_claims_made,
add a separate not_claimed_or_not_supported_boundaries field,
make unsupported-claim failures depend on deterministic explanation-text checks,
or revise the prompt/schema so the model cannot confuse boundaries with violations.
```

The amendment must be global for Claude, Codex, and future tracks. It must not
be a Claude-only exception.

## Final State

```text
Claude readiness rerun: NEEDS_REVISION
Codex readiness rerun: NOT STARTED
new live sessions: NOT AUTHORIZED
result reclassification: NOT AUTHORIZED
global output-field amendment: AUTHORIZATION REQUIRED
primary benchmark: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
