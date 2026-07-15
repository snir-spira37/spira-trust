# SPIRA Formal Core V1 Domain 2 Conformance Rerun Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_RERUN_AUTHORIZED

DOMAIN_2_ONLY

ACCEPTED_REPORT_WITH_NOTES_MAPPING_REQUIRED

FORMAL_DOMAIN2_TYPED_SEMANTICS_AUTHORIZED

DOMAIN2_LEAN_DEFINITIONS_AUTHORIZED

DOMAIN2_LEAN_PROOFS_AUTHORIZED

DOMAIN2_PYTHON_ADAPTER_DIFFERENTIAL_EVALUATION_AUTHORIZED

DOMAIN2_CONFORMANCE_HARNESS_AUTHORIZED

ACCEPTED_DOMAIN2_CORPUS_FROZEN

ACCEPTED_DOMAIN2_ORACLE_FROZEN

MUTATION_PAIR_EVALUATION_AUTHORIZED

RESULTS_REPORT_REVIEW_REQUIRED

FORMAL_CORE_V1_ACTION_ALGEBRA_FROZEN

DOMAIN_1_NOT_AUTHORIZED

DOMAIN_3_NOT_AUTHORIZED

RAW_PARSER_PROOF_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

PRODUCTION_RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a rerun of Domain 2 conformance after acceptance of:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_action_mapping_amendment_review.md
```

The previous Domain 2 conformance attempt stopped with:

```text
DOMAIN2_ORACLE_ACTION_OUTSIDE_FORMAL_CORE_V1_ACTION_ALGEBRA
```

That blocker is now resolved by an accepted conformance-boundary mapping:

```text
REPORT_WITH_NOTES
-> PROCEED + TEST_NOTES
```

The old negative result remains preserved and is not reclassified.

## 2. Authorization Basis

The rerun is authorized only because the following are accepted:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN2_ACTION_MAPPING_AMENDMENT_ACCEPTED
```

## 3. Authorized Files

Lean files:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Proofs.lean
```

The top-level Lean module may be updated only to import Domain 2 modules.

Python research harness:

```text
tools/run_formal_core_v1_domain2_conformance.py
```

Research outputs:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_results.json
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_report.md
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_review.md
```

## 4. Frozen Inputs

The rerun may read but must not modify:

```text
research/test_build_failure_contract/corpus_manifest_v1.json

research/test_build_failure_contract/oracle_v1.json

source/spira_core/test_build_failure_producer.py

source/spira_core/test_build_failure_oracle_validator.py

source/spira_core/formal_core_v1.py
```

## 5. Required Mapping

Domain 2 action comparison must use the accepted mapping:

```text
PROCEED -> PROCEED

REPORT_WITH_NOTES -> PROCEED with TEST_NOTES preserved

STOP_BLOCKED -> STOP_BLOCKED

RERUN_REQUIRED -> RERUN_REQUIRED

REPORT_NOT_EVALUATED -> REPORT_NOT_EVALUATED
```

`REPORT_WITH_NOTES` may project to `PROCEED` only if:

```text
stop = false

reason_codes contains TEST_NOTES

blocking_items = []

not_evaluated = []
```

Any violation must fail the conformance rerun.

## 6. Required Domain 2 Proof Obligations

The rerun must prove or restate through machine-checked Lean the bounded Domain
2 obligations:

```text
failed tests prevent PROCEED

collection/execution conflict prevents PROCEED

required unknown prevents PROCEED

valid clean success produces PROCEED

note-only outcomes produce PROCEED while preserving TEST_NOTES

not_claimed boundaries are preserved

malformed/incompatible evidence fails closed
```

Proofs must contain:

```text
no sorry
no admit
no custom axiom
no sorryAx
```

## 7. Differential Corpus Gates

The research harness must evaluate:

```text
38 / 38 accepted Domain 2 cases

6 / 6 mutation pairs
```

and compare:

```text
accepted oracle

accepted Python producer

Formal Core V1 typed-evidence projection
```

under the accepted `REPORT_WITH_NOTES -> PROCEED + TEST_NOTES` mapping.

Required gates:

```text
38 / 38 cases evaluated

38 / 38 formal projection matches accepted mapped oracle

38 / 38 Python producer matches accepted mapped oracle

2 / 2 REPORT_WITH_NOTES cases project to PROCEED

2 / 2 REPORT_WITH_NOTES cases preserve TEST_NOTES

0 TEST_NOTES drops

0 blocking-to-proceed mappings

0 not_evaluated-to-proceed mappings

0 malformed-to-proceed mappings

0 identity drops

0 evidence/proof reference drops

6 / 6 mutation pairs evaluated
```

## 8. Required Accepted Statuses

The review may accept only if:

```text
DOMAIN_2_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED

DOMAIN_2_REPORT_WITH_NOTES_MAPPING_ACCEPTED_IN_CONFORMANCE
```

It must explicitly state:

```text
raw pytest/JUnit parser formally proved: no
```

unless a later verified-parser track proves it.

## 9. Non-Authorization

This document does not authorize:

```text
Formal Core V1 shared action algebra changes

Domain 2 adapter changes

raw parser changes

oracle changes

corpus changes

Domain 1 conformance

Domain 3 conformance

runtime integration

benchmark execution

new live sessions

production claim

merge to main

release/version/tag/PyPI
```
