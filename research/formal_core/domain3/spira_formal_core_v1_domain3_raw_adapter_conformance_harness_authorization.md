# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Harness Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_HARNESS_AUTHORIZED
```

## Purpose

This authorization opens a deterministic reference/conformance harness for the accepted Domain 3 raw Terraform Plan adapter fixture corpus.

The harness may evaluate synthetic raw fixtures against the accepted Domain 3 raw-adapter mapping specification. It must not change the production Domain 3 adapter.

## Scope

Authorized:

```text
REFERENCE_FIXTURE_ADAPTER_HARNESS_ONLY
SYNTHETIC_RAW_TERRAFORM_FIXTURE_TO_TYPED_EVIDENCE_PROJECTION
EXPECTED_CONTRACT_COMPARISON
FIXTURE_HASH_VALIDATION
RESOURCE_ACTION_REPLACE_UNKNOWN_SENSITIVE_LIST_VALIDATION
FOCUSED_TESTS
FULL_PYTEST
RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
tests/test_formal_core_v1_domain3_raw_adapter_conformance.py
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_review.md
```

## Boundaries

Not authorized:

```text
source/spira_core/terraform_plan_producer.py changes
source/spira_core/terraform_plan_oracle_validator.py changes
production adapter changes
raw Terraform JSON parser implementation change
raw Terraform JSON parser proof claim
Terraform execution proof claim
Lean changes
proof script changes
Python core changes
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
31 / 31 fixtures evaluated
31 / 31 fixture hashes match manifest
31 / 31 projected typed evidence matches expected typed evidence
31 / 31 contracts match expected contracts
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
evidence/proof identity loss = 0
resource action list loss = 0
replace path loss = 0
unknown path loss = 0
sensitive path loss = 0
focused tests PASS
full pytest PASS
```

Even if accepted, this harness only proves conformance of the synthetic fixture mapping. It does not prove arbitrary raw Terraform Plan JSON parsing, Terraform execution, provider behavior, cloud state, cost, security, compliance, or apply success.
