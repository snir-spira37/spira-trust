# SPIRA Formal Core V1 Domain 3 Production Adapter Alignment Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZED
```

## Purpose

This authorization opens an offline alignment check between:

```text
existing Domain 3 Terraform Plan production adapter
accepted Domain 3 conformance corpus
accepted Domain 3 synthetic raw-adapter fixtures
Formal Core V1 action/list preservation semantics
```

The work must not change the production adapter.

## Scope

Authorized:

```text
EXISTING_PRODUCTION_ADAPTER_EVALUATION_ONLY
EXISTING_DOMAIN3_CORPUS_REEVALUATION
ACCEPTED_SYNTHETIC_FIXTURE_CONFORMANCE_REEVALUATION
FORMAL_CORE_ACTION_LIST_PRESERVATION_COMPARISON
FOCUSED_TESTS
FULL_PYTEST
RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_domain3_production_adapter_alignment.py
tests/test_formal_core_v1_domain3_production_adapter_alignment.py
research/formal_core/domain3/spira_formal_core_v1_domain3_production_adapter_alignment_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_production_adapter_alignment_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_production_adapter_alignment_review.md
```

## Boundaries

Not authorized:

```text
source/spira_core/terraform_plan_producer.py changes
source/spira_core/terraform_plan_oracle_validator.py changes
production adapter changes
oracle changes
corpus changes
fixture changes
Lean changes
proof script changes
Python core changes
MVP / passthrough changes
live agent sessions
benchmark execution
result reclassification
raw Terraform JSON parser proof claim
Terraform execution proof claim
production claim
release
```

## Acceptance Gates

Acceptance requires:

```text
production Domain 3 conformance accepted
40 / 40 production corpus cases pass
10 / 10 mutation pairs pass
validator PASS
synthetic fixture harness accepted
31 / 31 synthetic fixtures pass
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
resource action list loss = 0
replace path loss = 0
unknown path loss = 0
sensitive path loss = 0
focused tests PASS
full pytest PASS
no production adapter source changes
```

Successful completion may support only a production-adapter alignment claim for the existing bounded Terraform Plan corpus and synthetic fixture suite. It must not claim arbitrary raw Terraform Plan JSON parser proof, Terraform execution proof, provider correctness, cloud-state freshness, cost correctness, security, compliance, apply success, production readiness, or release readiness.
