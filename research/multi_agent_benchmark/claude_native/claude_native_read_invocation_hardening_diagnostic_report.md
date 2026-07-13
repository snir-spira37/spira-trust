# Claude Native Read Invocation Hardening Diagnostic Report

## Status

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_PASS
UNSCORED_DIAGNOSTIC_SESSIONS_ONLY
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: haiku
allowed tools added: Read,Glob,Grep
session count: 20
schema valid: 20 / 20
exact: 20 / 20
usage available: 20 / 20
JSON result envelope present: 20 / 20
structured_output present: 20 / 20
permission denials: 0
false PROCEED: 0
workspace mutations: 0
repository mutation observed: false
forbidden tool calls: 0
```

## Cell Summary

- pytest_result synthetic_clean_success arm B CRITICAL_ARM_B: exact=10/10 schema=10/10 envelope=10/10 structured=10/10 permission_denials=0
- pytest_result synthetic_clean_success arm C MATCHED_ARM_C: exact=5/5 schema=5/5 envelope=5/5 structured=5/5 permission_denials=0
- technical_probe read_nonce arm N/A READ_NONCE_TECHNICAL_PROBE: exact=5/5 schema=5/5 envelope=5/5 structured=5/5 permission_denials=0

## Errors

- none

## Boundary

```text
These are unscored hardening diagnostic sessions.
Primary, holdout, and carryover benchmark sessions were not started.
No readiness rerun is authorized by this diagnostic.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
