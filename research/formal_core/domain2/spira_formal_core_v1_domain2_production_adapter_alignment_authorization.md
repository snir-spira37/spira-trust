# SPIRA Formal Core V1 Domain 2 Production Adapter Alignment Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_PRODUCTION_ADAPTER_ALIGNMENT_AUTHORIZED
```

## Purpose

This authorization opens an offline alignment check between:

```text
existing Domain 2 production adapter
accepted Domain 2 conformance corpus
accepted Domain 2 synthetic raw-adapter fixtures
Formal Core V1 typed-evidence semantics
```

The work must not change the production adapter.

## Scope

Authorized:

```text
EXISTING_PRODUCTION_ADAPTER_EVALUATION_ONLY
EXISTING_DOMAIN2_CORPUS_REEVALUATION
ACCEPTED_SYNTHETIC_FIXTURE_CONFORMANCE_REEVALUATION
FORMAL_CORE_REFERENCE_COMPARISON
FOCUSED_TESTS
FULL_PYTEST
RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_domain2_production_adapter_alignment.py
tests/test_formal_core_v1_domain2_production_adapter_alignment.py
research/formal_core/domain2/spira_formal_core_v1_domain2_production_adapter_alignment_results.json
research/formal_core/domain2/spira_formal_core_v1_domain2_production_adapter_alignment_report.md
research/formal_core/domain2/spira_formal_core_v1_domain2_production_adapter_alignment_review.md
```

## Boundaries

Not authorized:

```text
source/spira_core/test_build_failure_producer.py changes
source/spira_core/test_build_failure_oracle_validator.py changes
production adapter changes
oracle changes
corpus changes
fixture changes
Lean changes
proof script changes
MVP / passthrough changes
live agent sessions
benchmark execution
result reclassification
raw parser proof claim
production claim
release
```

## Acceptance Gates

Acceptance requires:

```text
production Domain 2 conformance accepted
38 / 38 production corpus cases pass
6 / 6 mutation pairs pass
synthetic fixture harness accepted
26 / 26 synthetic fixtures pass
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
focused tests PASS
full pytest PASS
no production adapter source changes
```

Successful completion may support only a production-adapter alignment claim for the existing bounded corpus and synthetic fixture suite. It must not claim arbitrary raw pytest/JUnit parser proof.
