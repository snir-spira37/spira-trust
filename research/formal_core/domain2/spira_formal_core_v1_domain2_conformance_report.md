# SPIRA Formal Core V1 Domain 2 Conformance Report

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_NEEDS_REVISION

DOMAIN2_ORACLE_ACTION_OUTSIDE_FORMAL_CORE_V1_ACTION_ALGEBRA

FORMAL_DOMAIN2_LEAN_IMPLEMENTATION_NOT_EXECUTED

PYTHON_ADAPTER_DIFFERENTIAL_EVALUATION_NOT_EXECUTED

CORPUS_MODIFIED_FALSE

ORACLE_MODIFIED_FALSE

DOMAIN_ADAPTER_MODIFIED_FALSE
```

## 1. Scope

This report covers the Domain 2 conformance phase authorized by:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_authorization.md
```

## 2. Finding

The frozen Domain 2 oracle contains an action that is outside the accepted
Formal Core V1 action algebra.

Accepted Formal Core V1 action algebra:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

Frozen Domain 2 oracle action distribution:

```text
STOP_BLOCKED: 23
REPORT_NOT_EVALUATED: 11
REPORT_WITH_NOTES: 2
PROCEED: 1
RERUN_REQUIRED: 1
```

The unsupported action is:

```text
REPORT_WITH_NOTES
```

Cases:

```text
synthetic_skipped_test
synthetic_xfail
```

Both cases have:

```text
reason_codes:
TEST_NOTES

stop:
false
```

## 3. Why This Blocks Conformance

The Domain 2 conformance authorization requires exact equality among:

```text
accepted oracle
accepted Python producer
Formal Core V1 typed-evidence projection
```

Mapping `REPORT_WITH_NOTES` silently to `PROCEED` or adding it to the action
algebra would change the accepted specification or the comparison policy.

That is not authorized in this phase.

## 4. Preserved Artifacts

No changes were made to:

```text
research/test_build_failure_contract/corpus_manifest_v1.json
research/test_build_failure_contract/oracle_v1.json
source/spira_core/test_build_failure_producer.py
source/spira_core/test_build_failure_oracle_validator.py
```

No Domain 2 Lean implementation or differential evaluation was executed after
the blocker was found.

## 5. Required Next Step

The next step must be a separate amendment or policy decision:

```text
FORMAL_CORE_V1_ACTION_ALGEBRA_OR_DOMAIN2_ACTION_MAPPING_AMENDMENT_REQUIRED
```

Possible bounded options:

```text
1. Add REPORT_WITH_NOTES to Formal Core V1 action algebra through a reviewed amendment.

2. Define a reviewed Domain 2 action-mapping layer where REPORT_WITH_NOTES is
   represented as PROCEED plus reason_codes = [TEST_NOTES], without changing
   the authoritative stop state.

3. Exclude note-only cases from Domain 2 V1 conformance through a reviewed
   corpus-scope amendment.
```

No option may be applied silently inside this conformance attempt.
