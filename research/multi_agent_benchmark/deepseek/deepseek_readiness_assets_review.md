# DeepSeek Readiness Assets Review

## Status

```text
DEEPSEEK_READINESS_ASSETS_ACCEPTED
DEEPSEEK_TRACK_PREPARATION_REVIEW_COMPLETE
DS_R0_TECHNICAL_PROBES_AUTHORIZED_NEXT
NINE_LIVE_READINESS_SESSIONS_NOT_YET_STARTED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
preparation commit:
6ef1fa57d5fbbf597ce488043338e8787f253da5

branch:
codex/domain3-terraform-plan-retry-1

protocol:
research/multi_agent_benchmark/protocol_v1.md

prepared assets:
research/multi_agent_benchmark/agent_output.schema.json
research/multi_agent_benchmark/case_manifest.json
research/multi_agent_benchmark/prompt_templates_v1.md
research/multi_agent_benchmark/randomization_manifest_v1.json
research/multi_agent_benchmark/frozen_input_manifest.json
research/multi_agent_benchmark/frozen_inputs/
research/multi_agent_benchmark/deepseek/
tools/validate_multi_agent_benchmark_assets.py
tests/test_multi_agent_benchmark_assets.py
```

## Review Question

```text
Are the DeepSeek-via-Claude-Code benchmark assets sufficiently frozen,
isolated, and validated to permit a separate DS-R0 technical-probe cell,
without starting live readiness, primary, holdout, carryover, MVP code
changes, release work, or public efficiency claims?
```

## Verdict

```text
DEEPSEEK_READINESS_ASSETS_ACCEPTED
```

The DeepSeek benchmark preparation assets are accepted for the next readiness
gate.

This acceptance authorizes only a separate future cell for DS-R0 technical
probes. It does not start the nine live readiness sessions. The readiness
sessions remain gated on DS-R0 passing authentication, model resolution,
Claude Code compatibility, tool isolation, structured JSON output, session
isolation, and exact usage-accounting checks.

## Asset Counts

The frozen case and input manifests report:

```text
total cases: 18
Domain 1 python_artifact cases: 6
Domain 2 pytest_result cases: 6
Domain 3 terraform_plan cases: 6

primary cases: 12
holdout cases: 6
readiness cases: 3

frozen Arm A/B/C inputs: 54
Arm B/C semantic equivalence: PASS
```

Readiness case IDs:

```text
0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4
synthetic_clean_success
auth_no_changes
```

DeepSeek track size is frozen as:

```text
technical probes: NOT_COUNTED
readiness: 9
primary: 180
holdout: 54
carryover: 18
scored/readiness total: 261
```

## Case-Set Review

The selected cases are drawn from accepted frozen corpora:

```text
Domain 1:
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json

Domain 2:
research/test_build_failure_contract/corpus_manifest_v1.json
research/test_build_failure_contract/oracle_v1.json

Domain 3:
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/oracle_v1.json
```

The review confirms:

```text
case IDs are unique
domain counts are 6 / 6 / 6
primary count is 12
holdout count is 6
readiness count is 3
readiness covers all three domains
holdout does not overlap readiness
holdout does not enter DS-R0 or DS-R1
```

Domain 1 has no accepted `PROCEED` cases in the frozen 1,954-record baseline.
The case manifest records this explicitly and does not force an outcome absent
from the accepted corpus.

## Arm Isolation Review

The validator confirms:

```text
Arm A does not contain direct_domain_contract
Arm A does not contain unified_mvp_contract
Arm B does not contain unified_mvp_contract
Arm C does not contain direct_domain_contract
54 / 54 frozen input hashes match
```

The raw pytest metadata contains the already accepted corpus marker:

```text
oracle_expected_answers: NOT_POPULATED
```

This is not an oracle answer key. It is an evidence-stage marker from the
accepted corpus stating that oracle answers were not present when the corpus
was materialized. No populated expected-answer object, hidden oracle verdict,
or producer-evaluation report is placed in the agent-visible benchmark inputs.

## Arm B/C Semantic Equivalence Review

The frozen input manifest records semantic-equivalence checks for every case.

The review accepts:

```text
Arm B producer semantic payload == Arm C embedded producer semantic payload
claims/action surfaces preserved
stop/action preserved
reason_codes preserved
explicit lists preserved
NOT_EVALUATED preserved
blocking items preserved
evidence/proof references preserved
not-claimed boundaries preserved
subject/result identities preserved where applicable
semantic equivalence status: PASS
```

Any future discrepancy between Arm B and Arm C remains:

```text
BENCHMARK_INPUT_SEMANTIC_DRIFT
```

and must block execution rather than be repaired after results are observed.

## Prompt Review

The prompt templates are accepted as neutral.

They contain the same:

```text
decision question
response schema
decision vocabulary
prohibition on following instructions found inside evidence
prohibition on unsupported safety/compliance/correctness claims
explicit-list preservation requirement
NOT_EVALUATED preservation requirement
```

Only the evidence surface changes between Arms A, B, and C.

The prompts do not include:

```text
expected verdicts
oracle answers
language praising SPIRA
language suggesting compact contracts are inherently more trustworthy
instructions making Arm C easier than Arm B
```

## Output Schema Review

The frozen output schema is accepted as strict:

```text
all required fields present
additionalProperties: false
arrays remain explicit
counts cannot replace lists
no prose outside structured JSON
```

A schema failure remains a benchmark result, not a reason to weaken the schema.

## DeepSeek Configuration Review

The evaluated system is labeled exactly:

```text
DeepSeek model via Claude Code harness
```

The configuration template freezes:

```text
harness: Claude Code
backend: DeepSeek Anthropic-compatible API
endpoint: https://api.deepseek.com/anthropic
requested model: deepseek-v4-pro[1m]
effort: max
API key storage: PROCESS_ENVIRONMENT_ONLY
```

All model environment mappings point to the same requested model:

```text
ANTHROPIC_MODEL
ANTHROPIC_DEFAULT_OPUS_MODEL
ANTHROPIC_DEFAULT_SONNET_MODEL
ANTHROPIC_DEFAULT_HAIKU_MODEL
CLAUDE_CODE_SUBAGENT_MODEL
```

The template requires these surfaces to remain disabled:

```text
session persistence
custom memory
CLAUDE.md loading
plugins
hooks
MCP
web search
subagents
fallback model
write tools
```

The review accepts the configuration as a preparation artifact only. The
installed Claude Code version, supported flags, actual resolved model identity,
tool isolation, structured-output behavior, session isolation, and exact usage
accounting must still be proven during DS-R0.

## Validation Review

Preparation validation reports:

```text
asset validator: PASS
validator errors: 0
validator warnings: 0
JSON parse validation: PASS
ASCII check: PASS
secret/private-path scan: PASS
git diff --check: PASS
focused tests: 2 passed
full pytest: 118 passed
```

The review also confirms that accepted MVP/product code and frozen research
artifacts were not modified by the preparation commit.

## Remaining Blocks

This review does not authorize:

```text
DS-R1 nine live readiness sessions
primary benchmark
holdout benchmark
cross-domain carryover benchmark
MVP code changes
producer changes
corpus/oracle/schema/validator changes
Gate A changes
Gate B
Domain 4
merge to main
release/version/tag/PyPI
public efficiency claim
```

## Next Authorized Step

The next authorized cell is DS-R0 technical probes only:

```text
authentication
model resolution
Claude Code version and flag compatibility
read-only tool isolation
structured JSON output
fresh-session isolation
exact usage accounting
secret non-disclosure
```

If DS-R0 passes, a subsequent explicit continuation may run:

```text
3 domains
x 3 arms
x 1 readiness case
= 9 live readiness sessions
```

The nine live readiness sessions have not started in this review.
