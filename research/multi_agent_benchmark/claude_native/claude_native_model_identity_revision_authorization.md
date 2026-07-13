# Claude Native Model Identity Revision Authorization

## Status

```text
CLAUDE_NATIVE_MODEL_IDENTITY_REVISION_AUTHORIZED
MODEL_IDENTITY_RULE_REVISION_ONLY
CHEAP_MODEL_PIN_HAIKU_PRESERVED
CLAUDE_NATIVE_C0_RERUN_AUTHORIZED_AFTER_REVISION
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The Claude native C0 rerun made progress but stopped at model identity metadata:

```text
auth:
PASS

usage accounting:
AVAILABLE

requested model:
haiku

reported model:
null

terminal status:
CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED
```

The runner required a response-reported model field that Claude Code native JSON
output did not expose.

## Scope

This authorization permits only:

```text
inspect Claude Code JSON / stream-json metadata shape
define an explicit model identity confirmation rule for Claude native haiku
update the C0 runner and focused tests
rerun C0 from P1
update C0 results and report
```

The accepted cheap model pin remains:

```text
requested model:
haiku
```

## Allowed Model Identity Rule

The revised rule may accept model identity only if all are true:

```text
requested_model == haiku
Claude Code invocation includes --model haiku
Claude Code returncode == 0
auth_error_observed == false
usage accounting is available
no response metadata contradicts haiku
```

If Claude Code exposes a concrete model field, it must not contradict the
requested model.

## Allowed Files

```text
tools/run_claude_native_c0.py
tests/test_claude_native_c0.py
research/multi_agent_benchmark/claude_native/claude_native_c0_results.json
research/multi_agent_benchmark/claude_native/claude_native_c0_report.md
research/multi_agent_benchmark/claude_native/claude_native_c0_raw_private_manifest.json
```

## Forbidden

```text
readiness sessions
primary / holdout / carryover benchmark sessions
benchmark case execution
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing MVP code
changing producers
changing Gate A
changing thresholds
changing the model pin away from haiku
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Required Validation

After the revision and rerun:

```text
focused C0 tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```

## Next Required Artifact

After the revision:

```text
research/multi_agent_benchmark/claude_native/claude_native_model_identity_revision_review.md
```

Only if C0 passes and the review accepts it may a later document authorize the
nine Claude native readiness sessions.
