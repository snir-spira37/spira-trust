# SPIRA MVP Product Boundary Amendment Proposal Review

## Status

```text
MVP_PRODUCT_BOUNDARY_AMENDMENT_ACCEPTED
MVP_BOUNDARY_REVIEW_COMPLETE
THREE_DOMAIN_RESEARCH_COMPLETE_WITH_BOUNDS
MVP_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT
MVP_IMPLEMENTATION_NOT_AUTHORIZED
UNIFIED_REAL_AGENT_BENCHMARK_REQUIRED_BEFORE_EFFICIENCY_CLAIM
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
artifact: research/mvp_product_boundary_amendment_proposal.md
review_type: SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
prior_boundary: MVP_PRODUCT_BOUNDARY_ACCEPTED
domain3_closeout: DOMAIN_3_RESEARCH_COMPLETE_WITH_BOUNDS
```

## Review Question

```text
Should the accepted MVP product boundary be amended to include Domains 1-3 as
a unified local evidence product boundary, while keeping implementation,
release, Gate B, and efficiency claims separately gated?
```

## Verdict

```text
MVP_PRODUCT_BOUNDARY_AMENDMENT_ACCEPTED
```

The amendment is accepted as a product-boundary decision only. It does not
authorize code, merge to main, release, version bump, tag, PyPI publication,
Gate B, Domain 4, semantic cache reuse, live infrastructure claims, or public
efficiency claims.

## Research Basis Review

The proposal correctly reflects the accepted research basis:

```text
Domain 1:
Python artifact evidence validated on the frozen 1,954-wheel corpus.

Domain 2:
pytest result evidence validated against accepted corpus, schema, validator,
independent oracle, and producer.

Domain 3:
Terraform Plan JSON evidence validated against accepted corpus, schema,
validator, independent oracle, and producer.

Shared boundary:
typed claims
accepted Gate A proof assembly
bounded deterministic action contract
proof and drill-down surface
```

The proposal also preserves the correct Gate A sequence:

```text
Gate A introduced a generic assembly boundary.
Domain 1 identity was preserved under the accepted Gate A review.
Domains 2 and 3 used the accepted generic boundary with independent truth
layers and accepted producers.
```

It does not claim that the original pre-Gate-A interface was reused unchanged
across all domains.

## Product Boundary Review

The amended MVP boundary is accepted as:

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

This is a bounded local evidence-product boundary, not a live orchestration
platform.

## Shared Product Shape Review

The proposal correctly describes the common product shape:

```text
Domain Producers
  - Python artifact producer
  - pytest result producer
  - Terraform Plan producer

        -> typed claims

Shared SPIRA Unification Core
  - accepted Gate A proof assembly
  - contextual unification_id
  - bounded policy/action contract

        -> proof + action + drill-down
```

This is sufficiently clear to support a future implementation authorization
document.

## Domain-Specific Boundary Review

Domain 1 remains bounded to:

```text
Python wheel artifact evidence
accepted Unification Proof behavior
bounded action contract
claim inclusion / mutation rejection evidence
NOT_EVALUATED preservation
BLOCK preservation
Domain 1 identity baseline
```

Domain 2 is bounded to:

```text
Python pytest result evidence
accepted dual identity model
accepted corpus
accepted Oracle Schema V7
accepted validator
accepted independent oracle
accepted producer
```

Domain 3 is bounded to:

```text
Terraform Plan JSON evidence
accepted 40-case corpus
accepted Oracle Schema V1
accepted validator
accepted independent oracle
accepted producer
```

The proposal correctly does not expand Domain 2 into general CI support and
does not expand Domain 3 into live Terraform state, `terraform apply`, cloud
credentials, remote backends, or infrastructure correctness.

## Identity Boundary Review

The proposal preserves:

```text
unification_id = contextual proof identity
```

It correctly rejects:

```text
semantic-result identity for unification_id
cache key for reuse
cross-time staleness guarantee
proof of regenerated-evidence equivalence
```

Domain 2's `result_identity` remains a bounded policy-independent semantic
identity inside the Domain 2 test-result contract. It is not authorized for Gate
B cache or reuse.

## Gate B and Exclusion Review

The proposal keeps these out of the MVP:

```text
Gate B status/cache/rerun generalization
semantic result cache
cross-time staleness resolution
live Terraform state
terraform apply
remote backends
cloud credentials
Kubernetes
Domain 4
orchestrator / SPIRA OS
universal Context Firewall claim
software safety claim
infrastructure safety claim
security scanner claim
cost optimization claim
compliance claim
release/version/tag/PyPI
```

This is accepted.

## Product Claim Review

The permitted product claim is accepted:

```text
SPIRA has validated a shared unification proof architecture across three
accepted evidence domains: Python artifacts, pytest result evidence, and
Terraform Plan JSON.
```

The required qualifier is present:

```text
within the tested contracts, frozen corpora, accepted oracles, and accepted
producer implementations.
```

The proposal correctly forbids:

```text
software safety claims
infrastructure safety claims
Terraform apply success claims
universal Context Firewall claims
semantic cache reuse claims
live Kubernetes support claims
SPIRA OS / orchestrator claims
measured live agent efficiency claims
```

## Unified Benchmark Review

The proposal correctly separates correctness research from live product
efficiency.

It requires a future separately authorized benchmark before any public
efficiency claim:

```text
raw evidence
vs
domain compact contracts
vs
unified SPIRA product flow
```

Required preservation gates are accepted:

```text
action preserved
reason_codes preserved
NOT_EVALUATED preserved
BLOCK preserved
zero false PROCEED
zero safety overclaim
evidence drill-down preserved
```

The proposal correctly avoids promising a savings percentage in advance.

## Implementation and Release Review

Acceptance of this boundary amendment does not authorize implementation.

A future MVP implementation authorization remains required and must define:

```text
allowed files
forbidden files
included product commands or surfaces
Domain 1 / Domain 2 / Domain 3 integration boundaries
regression gates
oracle/evaluator reuse boundaries
Gate A unchanged checks
public compatibility requirements
release exclusions
rollback conditions
```

The public product remains unchanged until separate release authorization.

## What This Acceptance Means

This acceptance means:

```text
The MVP product boundary may now be defined as a unified local evidence product
over Domains 1-3, using the accepted shared Gate A proof-assembly boundary and
bounded action/proof/drill-down contract.
```

## What This Acceptance Does Not Mean

This acceptance does not mean:

```text
the integrated MVP has been implemented
the public product supports Domains 2 or 3
a release is authorized
a version bump is authorized
Gate B is authorized
semantic cache reuse is safe
Terraform live infrastructure is supported
live agent efficiency has been measured
```

## Next Authorized Artifact

The next artifact may be a narrow implementation authorization:

```text
research/mvp_implementation_authorization.md
```

It must not authorize release/version/tag/PyPI by default. Any release decision
requires a separate gate after implementation, regression, and benchmark review.

## Final Boundary

```text
MVP product boundary amendment: ACCEPTED
MVP implementation: NOT_AUTHORIZED
unified real-agent benchmark: REQUIRED_BEFORE_EFFICIENCY_CLAIM
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
semantic cache reuse: NOT_AUTHORIZED
live infrastructure: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
merge to main: NOT_AUTHORIZED
```
