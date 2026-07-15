# SPIRA Formal Core V1 Differential Harness Rerun Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_RERUN_AUTHORIZED

ACCEPTED_PYTHON_TYPED_EVIDENCE_ENTRYPOINT_FROZEN

LEAN_EXECUTABLE_REFERENCE_FROZEN

FORMAL_TEST_VECTORS_FROZEN

GENERIC_DIFFERENTIAL_HARNESS_REVISION_AUTHORIZED

FIELD_BY_FIELD_COMPARISON_REQUIRED

RESULTS_REPORT_REVIEW_REQUIRED

PYTHON_PRODUCTION_INTEGRATION_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a rerun and revision of the generic differential
harness after acceptance of the Python typed-evidence boundary.

The prior blocker was:

```text
PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED
```

That blocker is resolved by:

```text
spira_core.formal_core_v1.evaluate_typed_evidence
```

## 2. Authorized Files

This phase may modify:

```text
tools/run_formal_core_v1_differential_harness.py
```

It may regenerate:

```text
research/formal_core/spira_formal_core_v1_differential_harness_results.json

research/formal_core/spira_formal_core_v1_differential_harness_report.md

research/formal_core/spira_formal_core_v1_differential_harness_review.md
```

No production Python source files may be changed.

## 3. Required Comparison

The harness must evaluate the accepted Python typed-evidence boundary over the
formal test vector set and compare every semantic field to the Lean reference
semantics for the same vectors:

```text
action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
domain_id
subject_id
policy_id
schema_version
producer_id
contract_id
```

The Lean executable reference must also be run and must return:

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_PASS
```

## 4. Acceptance Gates

```text
accepted Python typed-evidence entrypoint: AVAILABLE

Lean executable reference: PASS

all formal test vectors equal: 100%

all error vectors fail closed: 100%

list-order differences: 0

missing-field differences: 0

identity differences: 0

nondeterministic repeats: 0

Python source changes outside authorized boundary: 0

domain adapter changes: 0
```

## 5. Non-Authorization

This document does not authorize:

```text
Domain 2 conformance

Domain 3 conformance

Domain 1 conformance

runtime integration

benchmark execution

production claim

merge to main

release/version/tag/PyPI
```
