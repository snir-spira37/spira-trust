# SPIRA Formal Core V1 Integration Boundary Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_AUTHORIZED

LOCAL_INTEGRATION_BOUNDARY_REVIEW_ONLY

FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED_REQUIRED

PASSTHROUGH_MVP_IMPLEMENTATION_ACCEPTED_REQUIRED

MVP_IMPLEMENTATION_ACCEPTED_REQUIRED

AUTHORITY_CHAIN_REVIEW_AUTHORIZED

MVP_ROUTER_REGRESSION_AUTHORIZED

PASSTHROUGH_VALIDATOR_REGRESSION_AUTHORIZED

FORMAL_CORE_PROOF_PACKAGE_REPRODUCTION_AUTHORIZED

CLAIM_BOUNDARY_RECONCILIATION_AUTHORIZED

RESULTS_REPORT_REVIEW_REQUIRED

RAW_ADAPTER_PROOFS_NOT_AUTHORIZED

RUNTIME_PROOF_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a bounded local integration boundary review after the
Formal Core V1 proof package.

The review must answer:

```text
Does the accepted Formal Core V1 typed-evidence proof package connect cleanly
to the accepted local MVP passthrough architecture without expanding the claim
to raw parsers, runtime, live agents, production, or release?
```

## 2. Authorized Files

Python integration harness:

```text
tools/run_formal_core_v1_integration_boundary.py
```

Research outputs:

```text
research/formal_core/spira_formal_core_v1_integration_boundary_results.json
research/formal_core/spira_formal_core_v1_integration_boundary_report.md
research/formal_core/spira_formal_core_v1_integration_boundary_review.md
```

No other file changes are authorized.

## 3. Required Inputs

The harness and review must read but not modify:

```text
research/formal_core/spira_formal_core_v1_proof_package_review.md
research/formal_core/spira_formal_core_v1_claim_boundary_summary.md
research/formal_core/spira_formal_core_v1_all_domains_conformance_review.md
research/machine_contract_passthrough_mvp_implementation_review.md
research/mvp_implementation_review.md
research/machine_contract_passthrough_envelope_validator_implementation_review.md
research/machine_contract_passthrough_fixtures/fixture_manifest.json
source/spira_core/mvp_unified.py
tools/evaluate_mvp_unified.py
tools/validate_machine_contract_passthrough_envelope.py
tools/run_formal_core_v1_proof_package.py
```

## 4. Authorized Checks

The integration harness may run:

```text
python tools/run_formal_core_v1_proof_package.py

python tools/evaluate_mvp_unified.py

python -m pytest tests/test_machine_contract_passthrough_mvp.py

python -m pytest tests/test_machine_contract_passthrough_envelope_validator.py

python -m pytest tests/test_mvp_unified.py

python -m pytest tests/test_formal_core_v1_python_boundary.py
```

The harness may verify that the accepted status strings are present in the
required review artifacts.

## 5. Required Authority Chain

The review must preserve this authority order:

```text
typed evidence accepted by domain boundary
>
Formal Core V1 machine contract semantics
>
authoritative machine contract passthrough
>
deterministic validator / evaluator
>
non-authoritative model explanation / presentation
>
free-form agent suggestion
```

The review must reject any claim that model output, reports, UI, telemetry, or
benchmark runner self-report can override the Formal Core / machine-contract
decision channel.

## 6. Acceptance Gates

The integration boundary may be accepted only if:

```text
Formal Core V1 proof package: ACCEPTED

MVP implementation: ACCEPTED

Passthrough MVP implementation: ACCEPTED

Envelope validator implementation: ACCEPTED

MVP evaluation: PASS

passthrough MVP tests: PASS

validator tests: PASS

MVP tests: PASS

Formal Core boundary tests: PASS

authority chain: COMPLETE

claim boundary: PRESERVED

raw parser proof claim: ABSENT

production claim: ABSENT

release authorization: ABSENT
```

## 7. Explicitly Not Authorized

This authorization does not permit:

```text
source code changes outside the integration harness

MVP semantic changes

validator changes

Formal Core theorem changes

domain adapter changes

raw parser proofs

benchmark runner changes

Claude / Codex / DeepSeek sessions

production integration

merge to main

release

version bump

tag

PyPI publish
```

## 8. Review Outcomes

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_REJECTED
```

Acceptance means only that the local proof package, local MVP passthrough
architecture, local validator, and local router share a consistent authority
boundary. It does not authorize production or release.
