# SPIRA Formal Core V1 Python Typed-Evidence Boundary Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_AUTHORIZED

BOUNDARY_IMPLEMENTATION_ONLY

CANONICAL_TYPED_EVIDENCE_ENTRYPOINT_AUTHORIZED

PYTHON_FORMAL_CORE_V1_MODULE_AUTHORIZED

FORMAL_TEST_VECTOR_MIRROR_AUTHORIZED

BOUNDARY_TESTS_AUTHORIZED

BOUNDARY_RESULTS_AUTHORIZED

BOUNDARY_REPORT_AUTHORIZED

BOUNDARY_REVIEW_REQUIRED

NO_DOMAIN_ADAPTER_CHANGES

NO_RAW_PARSER_CHANGES

NO_RUNTIME_INTEGRATION

NO_PRODUCTION_HOT_PATH_CHANGE

NO_BENCHMARK_CHANGES

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Purpose

This document authorizes a narrow Python typed-evidence boundary for SPIRA
Formal Core V1.

It responds to the accepted differential-harness blocker:

```text
PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED
```

The goal is to expose an accepted Python entrypoint over canonical typed
evidence so a later differential harness can compare Python behavior to the
executable Lean reference core.

This is not production runtime integration.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION

PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_LEAN_EQUIVALENCE_PROTOCOL_ACCEPTED
```

## 3. Authorized Files

This phase may create or modify only:

```text
source/spira_core/formal_core_v1.py

tests/test_formal_core_v1_python_boundary.py

research/formal_core/spira_formal_core_v1_python_typed_evidence_boundary_results.json

research/formal_core/spira_formal_core_v1_python_typed_evidence_boundary_report.md

research/formal_core/spira_formal_core_v1_python_typed_evidence_boundary_review.md
```

No other Python production files may be changed.

## 4. Required Boundary Shape

The module must expose a canonical typed-evidence entrypoint, for example:

```text
evaluate_typed_evidence(document)
```

The input document must contain:

```text
domain_id
subject_id
schema_version
producer_id
evidence_validity
typed_claims
evidence_refs
proof_refs
policy_id
policy_schema_version
policy_required_claims
policy_blocking_rules
policy_not_claimed_rules
```

The output must expose a machine contract with:

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

## 5. Required Semantic Constraints

The boundary must preserve the Formal Core V1 distinctions:

```text
empty list != missing field

NOT_EVALUATED != PASS

not_claimed != false

empty blocking_items != unknown blocking status
```

It must fail closed for:

```text
missing required field

invalid evidence validity

incomplete evidence

conflicting evidence

version incompatibility

internal validation failure
```

No model output, presentation text, or telemetry may affect the decision.

## 6. Required Test Vectors

Tests must cover the same semantic vector families as the Lean executable
reference:

```text
valid proceed vector

blocking vector

required unknown vector

conflicting evidence vector

invalid evidence vector

version-incompatible vector
```

Boundary tests must also cover:

```text
missing explicit list fails closed

model/presentation fields ignored

required typed_claims field distinguishes empty from missing
```

## 7. Non-Authorization

This document does not authorize:

```text
Domain 1 adapter changes

Domain 2 adapter changes

Domain 3 adapter changes

raw parser changes

runtime integration

using Lean from Python

production hot-path changes

benchmark execution

merge to main

release/version/tag/PyPI
```

## 8. Required Review Result

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_REJECTED
```

Only accepted status may reopen the generic differential harness phase.
