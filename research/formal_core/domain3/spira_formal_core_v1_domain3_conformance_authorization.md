# SPIRA Formal Core V1 Domain 3 Conformance Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_AUTHORIZED

DOMAIN_3_ONLY

DOMAIN2_CONFORMANCE_ACCEPTED_REQUIRED

FORMAL_DOMAIN3_TYPED_SEMANTICS_AUTHORIZED

DOMAIN3_LEAN_DEFINITIONS_AUTHORIZED

DOMAIN3_LEAN_PROOFS_AUTHORIZED

DOMAIN3_PYTHON_ADAPTER_DIFFERENTIAL_EVALUATION_AUTHORIZED

DOMAIN3_CONFORMANCE_HARNESS_AUTHORIZED

ACCEPTED_DOMAIN3_CORPUS_FROZEN

ACCEPTED_DOMAIN3_ORACLE_FROZEN

MUTATION_PAIR_EVALUATION_AUTHORIZED

RESULTS_REPORT_REVIEW_REQUIRED

FORMAL_CORE_V1_ACTION_ALGEBRA_FROZEN

DOMAIN_1_NOT_AUTHORIZED

RAW_TERRAFORM_JSON_PARSER_PROOF_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

PRODUCTION_RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes bounded Domain 3 conformance work for SPIRA Formal
Core V1.

Domain 3 is bounded Terraform Plan evidence.

The phase must keep two claims separate:

```text
A. Domain 3 typed-evidence semantics formally proved.

B. Existing Python Domain 3 producer differentially conformant on the frozen
   accepted corpus.
```

It must not merge these into a stronger raw-parser or production claim.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED

DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED

DOMAIN_3_TERRAFORM_PLAN_PRODUCER_ACCEPTED
```

## 3. Authorized Files

Lean files:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain3/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain3/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain3/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain3/Proofs.lean
```

The top-level Lean module may be updated only to import Domain 3 modules.

Python research harness:

```text
tools/run_formal_core_v1_domain3_conformance.py
```

Research outputs:

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_review.md
```

## 4. Frozen Inputs

The phase may read but must not modify:

```text
research/terraform_plan_contract/corpus_manifest_v1.json

research/terraform_plan_contract/cases/

research/terraform_plan_contract/oracle_v1.json

source/spira_core/terraform_plan_producer.py

source/spira_core/terraform_plan_oracle_validator.py

source/spira_core/formal_core_v1.py
```

## 5. Formal Domain 3 Language

Model at least:

```text
terraform plan valid JSON

malformed JSON

unsupported format

errored plan

incomplete plan

applyable false with effective changes

effective resource changes

no effective changes

unknown planned values

sensitive paths

not_claimed boundaries
```

## 6. Required Domain 3 Proof Obligations

The phase must prove at least:

```text
effective resource changes prevent PROCEED

errored plans prevent PROCEED

applyable:false with effective changes prevents PROCEED

malformed JSON produces RERUN_REQUIRED / non-PROCEED

unsupported format produces REPORT_NOT_EVALUATED / non-PROCEED

incomplete plans preserve NOT_EVALUATED and prevent PROCEED

valid no-change plans produce PROCEED

not_claimed boundaries are preserved

sensitive/unknown paths are represented in explicit not_evaluated metadata
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
40 / 40 accepted Domain 3 cases

10 / 10 mutation pairs
```

and compare:

```text
accepted oracle

accepted Python producer

Formal Core V1 Domain 3 typed-evidence projection
```

Required gates:

```text
40 / 40 cases evaluated

40 / 40 formal projection matches accepted oracle

40 / 40 Python producer matches accepted oracle

0 false PROCEED

0 blocking-to-proceed mappings

0 not_evaluated-to-proceed mappings

0 malformed-to-proceed mappings

0 sensitive value leaks

0 instruction overrides

0 identity drops

0 evidence/proof reference drops

10 / 10 mutation pairs evaluated
```

## 8. Required Accepted Statuses

The review may accept only if:

```text
DOMAIN_3_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_3_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED
```

It must explicitly state:

```text
raw Terraform JSON parser formally proved: no
```

unless a later verified-parser track proves it.

## 9. Non-Authorization

This document does not authorize:

```text
Formal Core V1 shared action algebra changes

Domain 3 adapter changes

raw Terraform parser changes

oracle changes

corpus changes

Domain 1 conformance

runtime integration

benchmark execution

new live sessions

production claim

merge to main

release/version/tag/PyPI
```
