# Claude Native Auth Invocation Fix Review

## Status

```text
CLAUDE_NATIVE_AUTH_INVOCATION_FIX_ACCEPTED
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED
CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_PASS
CLAUDE_NATIVE_USAGE_ACCOUNTING_SMOKE_AVAILABLE
CHEAP_MODEL_PIN_ACCEPTED_AS_HAIKU
CLAUDE_NATIVE_C0_RERUN_AUTHORIZATION_REQUIRED_NEXT
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
fix commit:
c50a9d7

authorization:
research/multi_agent_benchmark/claude_native/claude_native_auth_invocation_fix_authorization.md

results:
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_results.json

report:
research/multi_agent_benchmark/claude_native/claude_native_auth_remediation_report.md
```

## Review Question

```text
Did the narrow invocation fix remediate Claude native authentication without
starting C0 rerun, readiness, or benchmark execution?
```

## Verdict

```text
CLAUDE_NATIVE_AUTH_INVOCATION_FIX_ACCEPTED
```

The fix is accepted.

The authentication blocker is closed for the Claude native track.

## What Changed

The fix was narrow:

```text
removed --bare from Claude native non-interactive invocations
stopped overriding CLAUDE_CONFIG_DIR for login-based Claude Pro auth
preferred the WinGet Links claude.exe shim when available
pinned the Claude native technical-probe model to haiku
```

The model pin is intentionally cost-bounded:

```text
requested model:
haiku
```

## Confirmed Result

```text
terminal status:
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED

returncode:
0

auth error observed:
false

usage accounting available:
true

benchmark cases sent:
0

readiness sessions:
0
```

## Boundary Preserved

```text
Claude native C0 rerun:
NOT PERFORMED

readiness sessions:
0

primary / holdout / carryover sessions:
0

benchmark cases sent:
0

MVP code changes:
0

prompt / case / schema changes:
0

efficiency claim:
NOT AUTHORIZED
```

## Validation

```text
focused Claude native tests:
8 passed

benchmark asset validator:
PASS

JSON validation:
PASS

secret / private-path scan:
PASS

full pytest:
143 passed

frozen asset diff check:
PASS
```

## Not Authorized

This review does not authorize:

```text
readiness sessions
primary / holdout / carryover benchmark sessions
benchmark case execution
changing benchmark assets
changing MVP code
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Next Required Artifact

The next artifact may be:

```text
research/multi_agent_benchmark/claude_native/claude_native_c0_rerun_authorization.md
```

It may authorize only a fresh Claude native C0 technical-probe rerun from P1
using the accepted `haiku` model pin and fixed invocation.

Only if that future C0 rerun passes may a later review consider authorizing
the nine Claude native readiness sessions.
