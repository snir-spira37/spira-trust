# SPIRA Formal Core V1 Domain 2 Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_NEEDS_REVISION

DOMAIN2_ORACLE_ACTION_OUTSIDE_FORMAL_CORE_V1_ACTION_ALGEBRA

DOMAIN_2_FORMAL_TYPED_SEMANTICS_NOT_ACCEPTED

DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_NOT_ACCEPTED

CORPUS_PRESERVED

ORACLE_PRESERVED

DOMAIN_ADAPTERS_PRESERVED

ACTION_ALGEBRA_OR_MAPPING_AMENDMENT_REQUIRED

DOMAIN_3_NOT_AUTHORIZED

DOMAIN_1_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Review Scope

This review covers the attempted Domain 2 conformance phase.

Reviewed artifacts:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_results.json
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_report.md
```

## 2. Decision

Domain 2 conformance is not accepted.

The phase needs revision because the frozen Domain 2 oracle contains:

```text
REPORT_WITH_NOTES
```

but Formal Core V1 currently accepts only:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

## 3. Why This Is Not a Failure of Lean

This is not a failed proof and not a Lean implementation failure.

The mismatch was found before Domain 2 Lean semantics or Python adapter
differential evaluation were executed.

The issue is a specification/conformance boundary mismatch:

```text
Domain 2 accepted oracle action space
!=
Formal Core V1 accepted action algebra
```

## 4. Preserved Negative Finding

The negative finding is preserved.

No corpus, oracle, adapter, theorem, or action algebra was changed to force a
pass.

## 5. Required Next Step

A separate amendment is required before Domain 2 conformance can continue:

```text
FORMAL_CORE_V1_ACTION_ALGEBRA_OR_DOMAIN2_ACTION_MAPPING_AMENDMENT_REQUIRED
```

The amendment must decide whether:

```text
REPORT_WITH_NOTES becomes a Formal Core V1 action;
REPORT_WITH_NOTES maps to PROCEED plus TEST_NOTES metadata;
or note-only cases are outside Domain 2 Formal Core V1 conformance scope.
```

Until that decision is accepted:

```text
Domain 2 conformance: BLOCKED
Domain 3 conformance: BLOCKED
Domain 1 conformance: BLOCKED
runtime integration: BLOCKED
production claim: BLOCKED
release: BLOCKED
```
