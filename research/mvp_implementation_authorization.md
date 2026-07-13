# SPIRA MVP Implementation Authorization

## Status

```text
MVP_IMPLEMENTATION_AUTHORIZED
MVP_IMPLEMENTATION_AUTHORIZATION_ONLY
THREE_DOMAIN_MVP_BOUNDARY_ACCEPTED
UNIFIED_LOCAL_EVIDENCE_PRODUCT_AUTHORIZED
UNIFIED_REAL_AGENT_BENCHMARK_TOOLING_AUTHORIZED
RELEASE_NOT_AUTHORIZED
VERSION_BUMP_NOT_AUTHORIZED
TAG_NOT_AUTHORIZED
PYPI_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
Domain 1:
VALIDATED

Domain 2:
VALIDATED AGAINST ACCEPTED CORPUS AND INDEPENDENT ORACLE

Domain 3:
DOMAIN_3_RESEARCH_COMPLETE_WITH_BOUNDS

MVP product boundary amendment:
MVP_PRODUCT_BOUNDARY_AMENDMENT_ACCEPTED
```

The accepted MVP boundary is:

```text
Domain 1:
INCLUDED IN MVP

Domain 2:
INCLUDED IN MVP AS A BOUNDED LOCAL EVIDENCE PRODUCER

Domain 3:
INCLUDED IN MVP AS A BOUNDED LOCAL EVIDENCE PRODUCER

Gate B:
EXCLUDED

Domain 4:
EXCLUDED
```

## Purpose

This document authorizes a narrow implementation of a unified local MVP
interface across the three accepted evidence domains.

It does not authorize:

```text
release
merge to main
version bump
tag
PyPI publication
Gate B
Domain 4
semantic cache reuse
live infrastructure access
new product claims
```

## Authorized Work

Only the following implementation work is authorized:

```text
1. Unified local MVP entry point.
2. Domain 1 / Domain 2 / Domain 3 producer routing.
3. Common bounded action contract presentation.
4. Common proof and drill-down reference presentation.
5. Consistent NOT_EVALUATED propagation.
6. Consistent BLOCK propagation.
7. Evidence pointer surfacing.
8. MVP-focused tests.
9. Three-domain regression/evaluation report.
10. Unified real-agent benchmark tooling.
11. Benchmark report that measures without promising savings.
```

The MVP may orchestrate accepted domain producers and existing proof assembly.
It must not change their semantics.

## Allowed Files

Implementation may create or update only:

```text
source/spira_core/mvp_unified.py
tools/run_mvp_unified_local.py
tools/evaluate_mvp_unified.py
tools/benchmark_mvp_unified_agent.py
tests/test_mvp_unified.py
research/mvp_implementation_results.json
research/mvp_implementation_report.md
research/mvp_unified_benchmark_results.json
research/mvp_unified_benchmark_report.md
```

If implementation requires any file outside this list, work must stop and a new
authorization must be written before changing that file.

## Frozen Artifacts and Code

The following are frozen and must not be modified:

```text
Domain 1 accepted behavior and baseline
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
source/spira_core/unification_proof.py

Domain 2 corpus / oracle / validator / producer semantics
research/test_build_failure_contract/
source/spira_core/test_build_failure_oracle_validator.py
source/spira_core/test_build_failure_producer.py
tools/evaluate_test_build_failure_producer.py

Domain 3 corpus / oracle / validator / producer semantics
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/cases/
research/terraform_plan_contract/oracle_v1.json
research/terraform_plan_contract/oracle_schema_v1.schema.json
source/spira_core/terraform_plan_oracle_validator.py
source/spira_core/terraform_plan_producer.py
tools/evaluate_terraform_plan_producer.py

Core semantics
SPIRA_DECISION_SEMANTICS_V2
action enum
claim status enum
Gate A semantics
Gate B status/cache/rerun semantics
```

The MVP layer may call or route to accepted code. It may not rebaseline,
rewrite, loosen, normalize, or repair accepted artifacts to fit MVP output.

## Domain Boundaries

### Domain 1

The MVP may expose Domain 1 as:

```text
Python artifact evidence
accepted Unification Proof behavior
bounded action contract
proof and drill-down references
```

It must not alter Domain 1 identity construction or the accepted baseline.

### Domain 2

The MVP may expose Domain 2 as:

```text
bounded local pytest result evidence
accepted producer behavior
accepted policy-independent result_identity
accepted action/proof behavior
```

It must not claim:

```text
general CI support
test correctness
software correctness
semantic cache reuse
```

### Domain 3

The MVP may expose Domain 3 as:

```text
bounded local Terraform Plan JSON evidence
accepted producer behavior
accepted action/proof behavior
```

It must not require or claim:

```text
live Terraform state
terraform apply
remote backend
cloud credentials
provider download at evaluation time
infrastructure correctness
infrastructure security
cost correctness
compliance correctness
Kubernetes support
```

## Unified Interface Requirements

The unified local MVP interface must present, for each supported domain:

```text
domain identifier
subject identity
typed claims summary
bounded policy/action result
reason_codes
NOT_EVALUATED items
BLOCK items
proof identifier / unification reference
evidence drill-down pointers
not-claimed boundaries
```

It must preserve domain-specific evidence rather than flattening all domains
into an ambiguous generic summary.

## Required Regression Gates

The implementation can be reported as pass only if all gates pass:

```text
Domain 1 regressions: PASS
Domain 1 accepted baseline root unchanged:
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c

Domain 2 preserved:
38 / 38 oracle claim fidelity
38 / 38 action equivalence
38 / 38 scope_identity fidelity
38 / 38 result_identity fidelity
0 false PROCEED
0 mismatches

Domain 3 preserved:
40 / 40 claim fidelity
40 / 40 action equivalence
40 / 40 strict-list fidelity
40 / 40 evidence-pointer validity
10 / 10 mutation relationships
0 false PROCEED
0 mismatches

Shared gates:
explicit NOT_EVALUATED lists preserved
BLOCK preservation
proof/evidence pointers valid
0 sensitive-value leaks
0 instruction-injection overrides
Gate A unchanged check: PASS
Gate B untouched: PASS
full pytest: PASS
unified product interface tests: PASS
```

If the full Gate A 1,954-case isolated identity regression is not run during
MVP implementation, the report must state that clearly and may only claim an
authorized fallback:

```text
accepted Domain 1 baseline root unchanged
Gate A core worktree unchanged
Gate A full identity regression: NOT_RUN
```

The fallback must not be labeled as full Gate A identity regression.

## Unified Real-Agent Benchmark

Benchmark tooling is authorized as part of MVP implementation, but a benchmark
result is not an efficiency claim.

The benchmark must measure:

```text
raw evidence
vs
domain compact contracts
vs
unified SPIRA product flow
```

Across:

```text
Domain 1: Python artifact evidence
Domain 2: pytest result evidence
Domain 3: Terraform Plan JSON evidence
```

Required benchmark preservation gates:

```text
action preserved
reason_codes preserved
NOT_EVALUATED preserved
BLOCK preserved
zero false PROCEED
zero safety overclaim
evidence drill-down preserved
not-claimed boundaries preserved
```

Measurements may include:

```text
context size
tool-call count
evidence bytes surfaced to the agent
latency or wall-clock observations
human-review ergonomics
```

The benchmark must not promise or assume a savings percentage in advance. Any
public efficiency claim requires a later reviewed benchmark result and separate
release authorization.

## Machine-Readable Results

The implementation must produce:

```text
research/mvp_implementation_results.json
research/mvp_unified_benchmark_results.json
```

The implementation results must include:

```text
schema
schema_version
status
domain1_regression
domain2_regression
domain3_regression
false_proceed_count
mismatch_count
not_evaluated_preservation
block_preservation
evidence_pointer_validity
sensitive_value_leaks
instruction_override_count
gate_a_check
gate_b_touched
full_tests
unified_interface_tests
errors
```

The benchmark results must include:

```text
schema
schema_version
status
domains_measured
raw_evidence_measurements
domain_contract_measurements
unified_product_flow_measurements
preservation_gates
efficiency_claim_authorized: false
errors
```

## Required Reports

The implementation must produce:

```text
research/mvp_implementation_report.md
research/mvp_unified_benchmark_report.md
```

The reports must document:

```text
authorization chain
implemented unified entry point
Domain 1 / Domain 2 / Domain 3 routing
frozen artifacts checked
regression commands and results
benchmark commands and measurements
Gate A unchanged check
Gate B untouched confirmation
truth-layer artifacts unchanged
release boundary
terminal status
```

## Successful Status

The only successful implementation status is:

```text
MVP_IMPLEMENTATION_PASS
```

The only successful benchmark tooling status is:

```text
MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM
```

These statuses do not authorize release.

## Stop Conditions

Implementation must stop with a non-pass status if any of these occur:

```text
Domain 1 behavior or baseline must change
Domain 2 corpus/oracle/validator/producer semantics must change
Domain 3 corpus/oracle/validator/producer semantics must change
Gate A refactor or rebaseline is required
Gate B behavior is required
new action or claim-status values are required
SPIRA_DECISION_SEMANTICS_V2 must change
semantic cache reuse is required
live Terraform infrastructure is required
any domain regression mismatch remains
any false PROCEED appears
sensitive values are exposed
instruction-like evidence changes action
full pytest fails
```

Allowed non-pass statuses:

```text
MVP_IMPLEMENTATION_INCOMPLETE
MVP_IMPLEMENTATION_FAILED
MVP_IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
MVP_BOUNDARY_REVISION_REQUIRED
```

## Post-Implementation Review Requirement

Even if implementation reports:

```text
MVP_IMPLEMENTATION_PASS
```

the MVP is not accepted until a separate review records one of:

```text
MVP_IMPLEMENTATION_ACCEPTED
MVP_IMPLEMENTATION_NEEDS_REVISION
MVP_IMPLEMENTATION_REJECTED
```

Release remains blocked after implementation acceptance until a separate
release proposal and release review are completed.

## Non-Authorization

This document does not authorize:

```text
merge to main
release
version bump
tag
PyPI publication
Gate B
Domain 4
semantic cache reuse
live Terraform state
terraform apply
remote backend
cloud credentials
Kubernetes
orchestrator / SPIRA OS
universal Context Firewall claim
software safety claim
infrastructure safety claim
cost or compliance claim
public efficiency claim
```

## Final Boundary

```text
MVP implementation: AUTHORIZED
MVP review: REQUIRED AFTER IMPLEMENTATION
unified real-agent benchmark tooling: AUTHORIZED
unified efficiency claim: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
merge to main: NOT_AUTHORIZED
```
