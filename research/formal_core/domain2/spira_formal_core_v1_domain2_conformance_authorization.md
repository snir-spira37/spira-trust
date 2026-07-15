# SPIRA Formal Core V1 Domain 2 Conformance Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_AUTHORIZED

DOMAIN_2_ONLY

FORMAL_DOMAIN2_TYPED_SEMANTICS_AUTHORIZED

DOMAIN2_LEAN_DEFINITIONS_AUTHORIZED

DOMAIN2_LEAN_PROOFS_AUTHORIZED

DOMAIN2_PYTHON_ADAPTER_DIFFERENTIAL_EVALUATION_AUTHORIZED

ACCEPTED_DOMAIN2_CORPUS_FROZEN

ACCEPTED_DOMAIN2_ORACLE_FROZEN

MUTATION_PAIR_EVALUATION_AUTHORIZED

RESULTS_REPORT_REVIEW_REQUIRED

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

This document authorizes bounded Domain 2 conformance work for SPIRA Formal
Core V1.

Domain 2 is bounded local pytest result evidence.

The phase must keep two claims separate:

```text
A. Domain 2 typed-evidence semantics formally proved.

B. Existing Python Domain 2 producer differentially conformant on the frozen
   accepted corpus.
```

It must not merge these into a stronger claim.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_PLAN_ACCEPTED
```

## 3. Authorized Files

Lean files:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain2/Proofs.lean
```

Python research harness:

```text
tools/run_formal_core_v1_domain2_conformance.py
```

Research outputs:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_results.json
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_report.md
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_review.md
```

The top-level Lean module may be updated only to import Domain 2 modules.

## 4. Frozen Inputs

The phase may read but must not modify:

```text
research/test_build_failure_contract/corpus_manifest_v1.json

research/test_build_failure_contract/oracle_v1.json

source/spira_core/test_build_failure_producer.py

source/spira_core/test_build_failure_oracle_validator.py
```

## 5. Formal Domain 2 Language

Model at least:

```text
tests passed

tests failed

collection error

execution error

conflicting evidence

malformed evidence

required information unknown

version incompatibility
```

## 6. Required Domain 2 Proof Obligations

The phase must prove at least:

```text
failed tests prevent PROCEED

collection/execution conflict prevents PROCEED

required unknown prevents PROCEED

valid clean success produces the accepted bounded action

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

and require exact equality among:

```text
accepted oracle

accepted Python producer

Formal Core V1 typed-evidence projection
```

If the frozen corpus contains a different count, the harness must report the
actual count and stop with `NEEDS_REVISION` rather than changing the corpus.

## 8. Required Accepted Statuses

The review may accept only if:

```text
DOMAIN_2_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED
```

It must explicitly state:

```text
raw pytest/JUnit parser formally proved: no
```

unless a later verified-parser track proves it.

## 9. Non-Authorization

This document does not authorize:

```text
Domain 2 adapter changes

raw parser changes

oracle changes

corpus changes

Domain 1 conformance

Domain 3 conformance

runtime integration

benchmark execution

production claim

merge to main

release/version/tag/PyPI
```
