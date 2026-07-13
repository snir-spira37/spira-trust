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
schema valid: 9 / 9
correct: 6 / 9
JSON result envelope: 9 / 9
structured_output: 9 / 9
usage available: 9 / 9
false PROCEED: 0
workspace mutations: 0
forbidden tool calls: 0
```

## Sessions

- pytest_result synthetic_clean_success arm A: ready=False schema=True correct=False rc=0
- pytest_result synthetic_clean_success arm B: ready=True schema=True correct=True rc=0
- pytest_result synthetic_clean_success arm C: ready=True schema=True correct=True rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm A: ready=False schema=True correct=False rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm B: ready=True schema=True correct=True rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm C: ready=True schema=True correct=True rc=0
- terraform_plan auth_no_changes arm A: ready=False schema=True correct=False rc=0
- terraform_plan auth_no_changes arm B: ready=True schema=True correct=True rc=0
- terraform_plan auth_no_changes arm C: ready=True schema=True correct=True rc=0

## Errors

- CLAUDE_NATIVE_READINESS_NEEDS_REVISION

## Boundary

```text
Only the 9 authorized readiness sessions were executed.
Primary, holdout, and carryover benchmark sessions were not started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
