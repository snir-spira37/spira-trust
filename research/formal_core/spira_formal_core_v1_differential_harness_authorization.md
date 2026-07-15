# SPIRA Formal Core V1 Differential Harness Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_AUTHORIZED

RESEARCH_ONLY_GENERIC_HARNESS_AUTHORIZED

CANONICAL_TYPED_EVIDENCE_INPUTS_ONLY

LEAN_REFERENCE_EVALUATION_AUTHORIZED

EXISTING_ACCEPTED_PYTHON_BEHAVIOR_REQUIRED

PYTHON_TYPED_EVIDENCE_ENTRYPOINT_DISCOVERY_AUTHORIZED

FIELD_BY_FIELD_COMPARISON_AUTHORIZED

MISMATCHES_FAIL_CLOSED

RESULTS_REPORT_REVIEW_REQUIRED

PRODUCTION_PYTHON_INTEGRATION_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a research-only generic differential harness for SPIRA
Formal Core V1.

The harness may compare:

```text
canonical typed evidence -> accepted Python behavior
canonical typed evidence -> executable Lean reference core
```

It must not compare raw parsers and must not claim Python correctness.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_LEAN_EQUIVALENCE_PROTOCOL_ACCEPTED
```

## 3. Critical Precondition

The harness must use an existing accepted Python behavior over canonical typed
evidence.

It must not invent a new Python decision core merely to match Lean.

If no accepted Python typed-evidence entrypoint exists, the phase must return:

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION

PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED
```

and stop.

## 4. Authorized Files

This phase may create:

```text
tools/run_formal_core_v1_differential_harness.py

research/formal_core/spira_formal_core_v1_differential_harness_results.json

research/formal_core/spira_formal_core_v1_differential_harness_report.md

research/formal_core/spira_formal_core_v1_differential_harness_review.md
```

It may not modify production Python modules.

## 5. Required Comparison Fields

For every evaluated case, the harness must compare:

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

The comparison must use semantic field equality.

It must not use hash equality alone as a substitute for semantic equality.

## 6. Required Generic Gates

The phase may be accepted only if:

```text
accepted Python typed-evidence entrypoint: AVAILABLE

all formal test vectors equal: 100%

all error vectors fail closed: 100%

list-order differences: 0

missing-field differences: 0

identity differences: 0

nondeterministic repeats: 0
```

If the Python entrypoint is not available, the phase must stop as
`NEEDS_REVISION`, not as a Lean failure.

## 7. Non-Authorization

This document does not authorize:

```text
Python source behavior changes

new Python formal-core implementation

Domain 1/2/3 conformance

runtime integration

production release

benchmark execution

merge to main

release/version/tag/PyPI
```

## 8. Required Review Result

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_REJECTED
```

Only accepted status may open Domain 2 conformance authorization.
