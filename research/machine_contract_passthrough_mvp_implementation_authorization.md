# Machine Contract Passthrough MVP Implementation Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_AUTHORIZED

PASSTHROUGH_MVP_IMPLEMENTATION_AUTHORIZATION_ONLY

ENVELOPE_SCHEMA_V1_FROZEN

ENVELOPE_VALIDATOR_ACCEPTED

FORTY_THREE_FIXTURES_FROZEN

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_FROZEN

AUTHORITATIVE_MACHINE_CONTRACT_PASSTHROUGH_AUTHORIZED

NON_AUTHORITATIVE_MODEL_EXPLANATION_CHANNEL_AUTHORIZED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_AUTHORIZED

LOCAL_INTEGRATION_TESTS_AUTHORIZED

MVP_IMPLEMENTATION_REPORT_AUTHORIZED

IMPLEMENTATION_REVIEW_REQUIRED

LIVE_AGENT_SESSIONS_NOT_AUTHORIZED

RUNNER_CHANGES_NOT_AUTHORIZED

PROMPT_CHANGES_NOT_AUTHORIZED

RESULT_RECLASSIFICATION_NOT_AUTHORIZED

REVISED_READINESS_NOT_AUTHORIZED

PRIMARY_BENCHMARK_NOT_AUTHORIZED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a narrow local MVP implementation of the accepted
machine-contract passthrough architecture.

The implementation may connect the accepted unified MVP path to:

```text
authoritative machine_contract passthrough

non-authoritative model_explanation channel

deterministic contradiction_analysis

accepted passthrough envelope validator
```

The implementation must preserve the accepted SPIRA machine contract as the
source of truth. The model explanation must not regenerate, replace, weaken, or
rewrite the machine contract.

## 2. Authorization Basis

This authorization follows:

```text
MVP_PRODUCT_BOUNDARY_PASSTHROUGH_AMENDMENT_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_ACCEPTED
```

Accepted foundation:

```text
Domain 1:
Python artifact evidence

Domain 2:
bounded local pytest result evidence

Domain 3:
bounded local Terraform Plan JSON evidence

Shared:
typed claims
Gate A proof assembly
authoritative machine-contract passthrough
non-authoritative model explanation
fail-closed contradiction analysis
mechanical contract identity checks
explanation compliance reporting
```

## 3. Authorized Work

Only the following implementation work is authorized:

```text
1. Build a passthrough envelope from an accepted Domain 1 / Domain 2 /
   Domain 3 unified machine contract.

2. Preserve machine_contract mechanically as authoritative.

3. Mark model_explanation as non-authoritative.

4. Accept a bounded model explanation input or local placeholder explanation
   only as explanation content, not as a decision source.

5. Compute deterministic contradiction_analysis.

6. Run the accepted passthrough envelope validator.

7. Fail closed when:
   - machine_contract identity changes;
   - action / stop / reason_codes / blocking_items / NOT_EVALUATED /
     not_claimed changes;
   - evidence or proof identity changes;
   - model_explanation contradicts the machine contract;
   - sensitive markers or sensitive values are exposed;
   - telemetry attempts to carry decision authority.

8. Add focused local integration tests.

9. Produce machine-readable implementation results.

10. Produce implementation report and implementation review.
```

The MVP implementation may use existing accepted producers and the existing
unified MVP interface. It must not change their semantics.

## 4. Authorized Files

Implementation may create or update only:

```text
source/spira_core/mvp_unified.py

tools/run_mvp_unified_local.py

tests/test_mvp_unified.py

tests/test_machine_contract_passthrough_mvp.py

research/machine_contract_passthrough_mvp_implementation_results.json

research/machine_contract_passthrough_mvp_implementation_report.md

research/machine_contract_passthrough_mvp_implementation_review.md
```

The implementation may import and call:

```text
tools/validate_machine_contract_passthrough_envelope.py
```

It must not modify that accepted validator unless a separate authorization is
written and accepted.

If any other file is required, implementation must stop for authorization
revision before changing that file.

## 5. Frozen Inputs And Semantics

The following are frozen and must not be modified:

```text
research/machine_contract_passthrough_envelope_schema_v1.schema.json

research/machine_contract_passthrough_envelope_validator_spec.md

research/machine_contract_passthrough_fixtures/

research/machine_contract_passthrough_fixtures/fixture_manifest.json

tools/validate_machine_contract_passthrough_envelope.py

tests/test_machine_contract_passthrough_envelope_validator.py

Domain 1 accepted behavior and baseline

Domain 2 corpus / oracle / validator / producer semantics

Domain 3 corpus / oracle / validator / producer semantics

Gate A proof assembly semantics

SPIRA_DECISION_SEMANTICS_V2

action/status enums

NOT_EVALUATED semantics

not_claimed boundary semantics

old Claude Native results

old Codex Native results
```

The implementation must not rebaseline, rewrite, normalize, loosen, or repair
accepted artifacts to make passthrough output pass.

## 6. Required Envelope Semantics

Every passthrough MVP envelope must contain:

```text
machine_contract

model_explanation

contradiction_analysis

telemetry
```

`machine_contract` must remain:

```text
authoritative: true
model_writable: false
representation: EMBEDDED_AND_HASH_BOUND
canonicalization: CANONICAL_JSON
```

`model_explanation` must remain:

```text
authoritative: false
model_produced: true
```

or, for deterministic local placeholder explanations:

```text
authoritative: false
model_produced: true
```

The placeholder may be used only for local integration tests. It must not be
reported as a live model explanation.

`contradiction_analysis` must remain:

```text
authoritative_for_machine_contract: false
model_writable: false
produced_by: VALIDATOR_DETERMINISTIC or MECHANICAL_CHECK
```

`telemetry` must remain:

```text
decision_authority: NONE
```

## 7. Mechanical Identity Gates

The implementation must prove that the passthrough envelope preserves:

```text
canonical contract hash

source contract hash

schema/version

domain

subject or case identity

action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed

evidence references

proof references

producer identity

unified wrapper identity, where applicable
```

Any mismatch must return a non-pass status and fail closed.

## 8. Contradiction Gates

The implementation must fail closed for contradictions including:

```text
MODEL_EXPLANATION_CONTRADICTS_MACHINE_CONTRACT
MODEL_EXPLANATION_OVERRIDES_MACHINE_ACTION
MODEL_EXPLANATION_UNSAFE_CONTINUATION
MODEL_EXPLANATION_DROPS_BLOCKER
MODEL_EXPLANATION_ADDS_UNSUPPORTED_BLOCKER
MODEL_EXPLANATION_REWRITES_REASON_CODE_NON_EQUIVALENTLY
MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS
MODEL_EXPLANATION_CLAIMS_NOT_CLAIMED_BOUNDARY
MODEL_EXPLANATION_FABRICATES_EVIDENCE
MODEL_EXPLANATION_FABRICATES_PROOF_REFERENCE
MODEL_EXPLANATION_WEAKENS_RERUN_REQUIRED
MODEL_EXPLANATION_IGNORES_EVIDENCE_CONFLICT
MODEL_EXPLANATION_EXPOSES_SENSITIVE_VALUE
MODEL_EXPLANATION_FOLLOWS_INSTRUCTION_IN_EVIDENCE
```

The model explanation must never be able to override:

```text
machine action
stop state
reason_codes
blocking_items
NOT_EVALUATED
not_claimed
evidence identity
proof identity
```

## 9. Required Local Tests

The implementation can be reported as pass only if focused local tests prove:

```text
valid Domain 1 passthrough envelope validates

valid Domain 2 passthrough envelope validates

valid Domain 3 passthrough envelope validates

machine_contract hash mutation fails closed

action mutation fails closed

reason_codes mutation fails closed

blocking_items mutation fails closed

NOT_EVALUATED mutation fails closed

not_claimed mutation fails closed

evidence/proof identity mutation fails closed

model explanation overriding STOP fails closed

model explanation converting NOT_EVALUATED to PASS fails closed

model explanation claiming not_claimed boundary fails closed

sensitive marker exposure fails closed

telemetry decision authority fails closed

accepted 43-fixture validator still passes

Domain 1 / Domain 2 / Domain 3 existing MVP tests still pass

full pytest passes
```

## 10. Required Machine-Readable Results

The implementation must produce:

```text
research/machine_contract_passthrough_mvp_implementation_results.json
```

The results must include:

```text
schema
schema_version
status
domain1_passthrough
domain2_passthrough
domain3_passthrough
machine_contract_identity_preservation
validator_result
contradiction_gate_result
sensitive_value_gate_result
telemetry_gate_result
fixture_validator_regression
focused_tests
full_pytest
live_sessions_executed: false
efficiency_claim_authorized: false
release_authorized: false
errors
```

The only successful implementation status is:

```text
MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_PASS
```

## 11. Required Report And Review

The implementation must produce:

```text
research/machine_contract_passthrough_mvp_implementation_report.md

research/machine_contract_passthrough_mvp_implementation_review.md
```

The report must document:

```text
authorization chain
files changed
passthrough envelope construction
machine-contract identity checks
model-explanation boundary
contradiction analysis behavior
validator invocation
Domain 1 / Domain 2 / Domain 3 local integration coverage
focused test results
full pytest result
explicit non-authorization boundaries
```

The review must end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_NEEDS_REVISION

MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_REJECTED
```

Even `ACCEPTED` does not authorize live sessions, revised readiness, primary
benchmark, or release.

## 12. Stop Conditions

Implementation must stop with a non-pass status if any of these occur:

```text
Schema V1 must change

accepted validator must change

fixture corpus must change

Domain 1 / Domain 2 / Domain 3 producer semantics must change

Gate A semantics must change

new action or claim-status enum is required

SPIRA_DECISION_SEMANTICS_V2 must change

Gate B behavior is required

semantic cache reuse is required

live model calls are required

runner or prompt changes are required

any machine_contract identity mismatch remains

any contradiction is not fail-closed

any sensitive value leaks

full pytest fails
```

Allowed non-pass statuses:

```text
MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_INCOMPLETE

MACHINE_CONTRACT_PASSTHROUGH_MVP_IMPLEMENTATION_FAILED

MACHINE_CONTRACT_PASSTHROUGH_MVP_AUTHORIZATION_REVISION_REQUIRED
```

## 13. Explicit Non-Authorization

This document does not authorize:

```text
new Claude sessions

new Codex sessions

DeepSeek sessions

revised readiness

primary benchmark

holdout

carryover

runner changes

prompt changes

model configuration changes

result reclassification

old Claude/Codex result changes

Gate B

Domain 4

semantic cache reuse

live Terraform state

terraform apply

Kubernetes

orchestrator / SPIRA OS

software safety claim

infrastructure safety claim

cost or compliance claim

public efficiency claim

merge to main

release

version bump

tag

PyPI publication
```

## Final Boundary

```text
MVP passthrough implementation: AUTHORIZED

local deterministic integration tests: AUTHORIZED

accepted validator invocation: AUTHORIZED

implementation review: REQUIRED

live agent testing: NOT_AUTHORIZED

revised readiness: NOT_AUTHORIZED

primary benchmark: NOT_AUTHORIZED

release/version/tag/PyPI: NOT_AUTHORIZED
```
