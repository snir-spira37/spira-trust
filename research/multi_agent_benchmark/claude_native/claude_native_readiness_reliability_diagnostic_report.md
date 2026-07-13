# Claude Native Readiness Reliability Diagnostic Report

## Status

```text
CLAUDE_NATIVE_READINESS_RELIABILITY_DIAGNOSTIC_COMPLETE
UNSCORED_DIAGNOSTIC_SESSIONS_ONLY
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: haiku
session count: 30
schema valid: 30 / 30
correct: 15 / 30
usage available: 30 / 30
OUTPUT_NOT_OBJECT: 0
tool permission denials: 1
false PROCEED: 0
workspace mutations: 0
forbidden tool calls: 0
```

## Cell Summary

- pytest_result synthetic_clean_success arm B CRITICAL_ARM_B: correct=9/10 schema=10/10 output_not_object=0 tool_permission_denial=1
- pytest_result synthetic_clean_success arm A FAILED_ARM_A_PYTEST: correct=0/5 schema=5/5 output_not_object=0 tool_permission_denial=0
- python_artifact 0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4 arm A FAILED_ARM_A_PYTHON_ARTIFACT: correct=1/5 schema=5/5 output_not_object=0 tool_permission_denial=0
- terraform_plan auth_no_changes arm A FAILED_ARM_A_TERRAFORM: correct=0/5 schema=5/5 output_not_object=0 tool_permission_denial=0
- pytest_result synthetic_clean_success arm C MATCHED_ARM_C_CONTROL: correct=5/5 schema=5/5 output_not_object=0 tool_permission_denial=0

## Errors

- none

## Boundary

```text
These are unscored diagnostic sessions.
Primary, holdout, and carryover benchmark sessions were not started.
No readiness acceptance is granted by this diagnostic.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
