# Claude Native Readiness Report

## Status

```text
CLAUDE_NATIVE_READINESS_NEEDS_REVISION
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: haiku
session count: 9
schema valid: 0 / 9
correct: 0 / 9
usage available: 0 / 9
false PROCEED: 0
workspace mutations: 0
forbidden tool calls: 0
```

## Sessions

- pytest_result synthetic_clean_success arm A: ready=False schema=False correct=False rc=1
- pytest_result synthetic_clean_success arm B: ready=False schema=False correct=False rc=1
- pytest_result synthetic_clean_success arm C: ready=False schema=False correct=False rc=1
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm A: ready=False schema=False correct=False rc=1
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm B: ready=False schema=False correct=False rc=1
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm C: ready=False schema=False correct=False rc=1
- terraform_plan auth_no_changes arm A: ready=False schema=False correct=False rc=1
- terraform_plan auth_no_changes arm B: ready=False schema=False correct=False rc=1
- terraform_plan auth_no_changes arm C: ready=False schema=False correct=False rc=1

## Errors

- CLAUDE_NATIVE_READINESS_NEEDS_REVISION
- CLAUDE_NATIVE_READINESS_USAGE_NOT_AVAILABLE

## Boundary

```text
Only the 9 authorized readiness sessions were executed.
Primary, holdout, and carryover benchmark sessions were not started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
