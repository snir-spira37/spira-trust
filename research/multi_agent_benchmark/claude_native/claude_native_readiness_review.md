# Claude Native Readiness Review

## Status

```text
CLAUDE_NATIVE_READINESS_NEEDS_REVISION
CLAUDE_NATIVE_READINESS_REVIEW_COMPLETE
SCHEMA_TRANSPORT_FIX_ACCEPTED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
blocked readiness commit:
8b54423

schema transport fix:
CLAUDE_NATIVE_READINESS_SCHEMA_TRANSPORT_FIX_AUTHORIZED

results:
research/multi_agent_benchmark/claude_native/claude_native_readiness_results.json

report:
research/multi_agent_benchmark/claude_native/claude_native_readiness_report.md
```

## Formal Results

```text
readiness sessions:
9 / 9 executed

schema valid:
8 / 9

correct:
5 / 9

usage available:
9 / 9

false PROCEED:
0

workspace mutations:
0

forbidden tool calls:
0
```

## Accepted Finding

The schema transport defect is closed.

```text
schema_transport:
INLINE_CANONICAL_JSON_WITHOUT_DRAFT_URI

schema_transport_semantics_changed:
false
```

The frozen output schema was not changed. The Claude CLI transport copy removes
only the top-level `$schema` draft URI that Claude Code rejected in the earlier
blocked run.

## Blocking Finding

Claude native readiness is not accepted.

Four readiness sessions did not preserve the expected contract:

```text
pytest_result synthetic_clean_success arm A:
reason_codes / not_claimed mismatch

pytest_result synthetic_clean_success arm B:
OUTPUT_NOT_OBJECT

python_artifact wheel readiness arm A:
blocking_items mismatch

terraform_plan auth_no_changes arm A:
reason_codes / not_evaluated / not_claimed mismatch
```

These are readiness correctness failures, not SPIRA product failures and not
schema transport failures.

## Boundary Preserved

```text
primary benchmark:
NOT STARTED

holdout / carryover:
NOT STARTED

MVP code:
UNCHANGED

benchmark cases/prompts/schema:
UNCHANGED

efficiency claim:
NOT AUTHORIZED
```

## Verdict

```text
CLAUDE_NATIVE_READINESS_NEEDS_REVISION
```

The Claude native track is not ready for primary benchmark execution. A
separate authorization is required before changing prompts, readiness case
selection, comparison policy, or the Claude invocation beyond the accepted
schema transport fix.
