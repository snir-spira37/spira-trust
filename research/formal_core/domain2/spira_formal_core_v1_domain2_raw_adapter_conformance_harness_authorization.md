# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Harness Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_HARNESS_AUTHORIZED
```

## Purpose

This authorization opens a deterministic reference/conformance harness for the accepted Domain 2 raw-adapter fixture corpus.

The harness may evaluate synthetic raw fixtures against the accepted mapping specification. It must not change the production Domain 2 adapter.

## Scope

Authorized:

```text
REFERENCE_FIXTURE_ADAPTER_HARNESS_ONLY
SYNTHETIC_RAW_FIXTURE_TO_TYPED_EVIDENCE_PROJECTION
FORMAL_CORE_REFERENCE_EVALUATION
EXPECTED_CONTRACT_COMPARISON
FIXTURE_HASH_VALIDATION
FOCUSED_TESTS
FULL_PYTEST
RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_domain2_raw_adapter_conformance.py
tests/test_formal_core_v1_domain2_raw_adapter_conformance.py
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_results.json
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_report.md
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_review.md
```

## Boundaries

Not authorized:

```text
source/spira_core/test_build_failure_producer.py changes
source/spira_core/test_build_failure_oracle_validator.py changes
production adapter changes
raw parser proof claim
Lean changes
proof script changes
MVP / passthrough changes
fixture changes
live agent sessions
benchmark execution
result reclassification
production claim
release
```

## Acceptance Gates

Acceptance requires:

```text
26 / 26 fixtures evaluated
26 / 26 fixture hashes match manifest
26 / 26 projected typed evidence matches expected typed evidence
26 / 26 Formal Core contracts match expected contracts
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
evidence/proof identity loss = 0
focused tests PASS
full pytest PASS
```

Even if accepted, this harness only proves conformance of the synthetic fixture mapping. It does not prove arbitrary raw pytest/JUnit parsing.
