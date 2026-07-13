# Claude Native Authentication Remediation Authorization

## Status

```text
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATION_AUTHORIZED
AUTHENTICATION_REMEDIATION_ONLY
CLAUDE_NATIVE_C0_RERUN_NOT_YET_AUTHORIZED
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The Claude native C0 review accepted a factual blocked result:

```text
CLAUDE_NATIVE_C0_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
CLAUDE_NATIVE_AUTHENTICATION_NOT_READY
CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED
```

The Claude Code executable is installed and pinned:

```text
Claude Code version:
2.1.206

Claude Code binary SHA-256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2
```

The only authorized question is whether the local Claude Code native
authentication state can be made visible to the benchmark runner without
starting readiness or benchmark execution.

## Scope

This authorization permits only authentication remediation and a non-scored
authentication/model smoke.

Allowed actions:

```text
inspect current Claude Code native auth state
verify whether an existing login/session is available
use the pinned Claude Code executable
run a non-scored prompt with no benchmark evidence
record safe model/version/usage metadata
record raw stdout/stderr hashes outside the repository
produce machine-readable remediation results and report
```

If an Anthropic API key is explicitly provided later, a process-local key may
be used for this remediation only. No key may be written to the repository.

## Allowed Files

```text
tools/run_claude_native_auth_remediation.py
tests/test_claude_native_auth_remediation.py
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_results.json
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_report.md
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_raw_private_manifest.json
```

Raw stdout/stderr must remain outside the repository.

## Forbidden

This authorization forbids:

```text
Claude native C0 rerun
readiness sessions
primary / holdout / carryover benchmark sessions
sending benchmark cases to the model
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing MVP code
changing producers
changing Gate A
weakening thresholds
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Success Gate

The remediation may end with:

```text
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED
CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_PASS
CLAUDE_NATIVE_USAGE_ACCOUNTING_SMOKE_AVAILABLE
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
```

## Failure Gates

The remediation may also end with exactly one of:

```text
CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY
CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_FAILED
CLAUDE_NATIVE_AUTH_REMEDIATION_INCOMPLETE
CLAUDE_NATIVE_AUTH_REMEDIATION_AUTHORIZATION_REVISION_REQUIRED
```

## Required Validation

After remediation:

```text
focused auth-remediation tests
JSON validation
benchmark asset validator
secret/private-path scan
full pytest
frozen asset diff check
```

## Next Required Artifact

After remediation:

```text
research/multi_agent_benchmark/claude_native/claude_native_authentication_remediation_review.md
```

Only if the remediation is accepted may a later document authorize a fresh
Claude native C0 rerun from P1.
