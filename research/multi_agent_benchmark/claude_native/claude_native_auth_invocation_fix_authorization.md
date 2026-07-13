# Claude Native Auth Invocation Fix Authorization

## Status

```text
CLAUDE_NATIVE_AUTH_INVOCATION_FIX_AUTHORIZED
AUTH_INVOCATION_FIX_ONLY
CHEAP_MODEL_PIN_AUTHORIZED
CLAUDE_NATIVE_C0_RERUN_NOT_YET_AUTHORIZED
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The previous remediation showed:

```text
interactive Claude Code:
logged in

Claude native --print with --bare:
Not logged in

Claude native --print without --bare:
authenticated smoke works
```

The blocker is therefore an invocation defect in the Claude native benchmark
runners, not a missing Claude installation.

## Authorized Fix

The fix may change only:

```text
tools/run_claude_native_auth_remediation.py
tools/run_claude_native_c0.py
tests/test_claude_native_auth_remediation.py
tests/test_claude_native_c0.py
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_results.json
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_report.md
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_raw_private_manifest.json
```

Allowed changes:

```text
remove --bare from Claude native non-interactive invocations
prefer the WinGet Links claude.exe shim when available
do not override CLAUDE_CONFIG_DIR for Claude Pro login-based auth
pin the Claude native technical-probe model to haiku
rerun only the auth remediation smoke
update auth remediation results and report
```

The model choice is intentionally cost-bounded:

```text
requested model:
haiku
```

This does not authorize changing benchmark cases, prompts, schemas, MVP code,
producers, or thresholds.

Because the local Claude native track uses Claude Code's login-based
authentication, the benchmark runner may use the existing user-level Claude
Code auth store. Session isolation must still be enforced by:

```text
--no-session-persistence
fresh session-id
no benchmark cases during remediation
```

## Success Gate

```text
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED
CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_PASS
CLAUDE_NATIVE_USAGE_ACCOUNTING_SMOKE_AVAILABLE
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
```

## Still Not Authorized

```text
Claude native C0 rerun
readiness sessions
primary / holdout / carryover benchmark sessions
benchmark case execution
MVP changes
efficiency claim
merge to main
release / version / tag / PyPI
```

After this fix, a separate review must accept the remediation before a fresh
Claude native C0 rerun may be authorized.
