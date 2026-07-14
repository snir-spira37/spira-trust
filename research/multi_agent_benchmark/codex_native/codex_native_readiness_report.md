# Codex Native Readiness Report

## Status

```text
CODEX_NATIVE_CONTRACT_READINESS_NOT_READY
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: gpt-5.5
resolved model ID: gpt-5.5
reasoning effort: xhigh
Codex CLI: codex-cli 0.130.0-alpha.5
session count: 9
schema valid: 9 / 9
correct: 5 / 9
Arm B strict: 2 / 3
Arm C strict: 3 / 3
Arm A operational pass: 3 / 3
JSONL result envelope: 9 / 9
structured output: 9 / 9
usage available: 9 / 9
false PROCEED: 0
workspace mutations: 0
forbidden tool calls: 0
```

## Sessions

- pytest_result synthetic_clean_success arm A: ready=True schema=True correct=False rc=0
- pytest_result synthetic_clean_success arm B: ready=False schema=True correct=False rc=0
- pytest_result synthetic_clean_success arm C: ready=True schema=True correct=True rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm A: ready=True schema=True correct=False rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm B: ready=True schema=True correct=True rc=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm C: ready=True schema=True correct=True rc=0
- terraform_plan auth_no_changes arm A: ready=True schema=True correct=False rc=0
- terraform_plan auth_no_changes arm B: ready=True schema=True correct=True rc=0
- terraform_plan auth_no_changes arm C: ready=True schema=True correct=True rc=0

## Errors

- CODEX_NATIVE_READINESS_NEEDS_REVISION

## Boundary

```text
Only the 9 authorized Codex readiness sessions were executed.
Codex primary, holdout, and carryover benchmark sessions were not started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
