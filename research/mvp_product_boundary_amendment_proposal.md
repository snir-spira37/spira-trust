# SPIRA MVP Product Boundary Amendment Proposal

## Status

```text
MVP_PRODUCT_BOUNDARY_AMENDMENT_PROPOSAL_LOCKED
PRODUCT_BOUNDARY_AMENDMENT_PROPOSAL_ONLY
THREE_DOMAIN_RESEARCH_COMPLETE_WITH_BOUNDS
MVP_IMPLEMENTATION_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
VERSION_BUMP_NOT_AUTHORIZED
TAG_NOT_AUTHORIZED
PYPI_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
```

## Purpose

This document proposes an amendment to the previously accepted MVP product
boundary after the accepted Domain 3 Terraform Plan retry closeout.

It is not an implementation authorization, release authorization, benchmark
result, or merge authorization.

## Reason for Amendment

The prior MVP boundary excluded Terraform after the first Domain 3 run closed
negatively:

```text
Run 1:
NEGATIVE
reason: Terraform CLI / local tooling prerequisite unavailable
```

That negative closeout remains valid historical evidence.

After environment remediation, the separately authorized retry completed
positively:

```text
Retry 1:
POSITIVE
corpus accepted
oracle accepted
producer accepted

overall:
DOMAIN_3_RESEARCH_COMPLETE_WITH_BOUNDS
```

Therefore the MVP boundary can now be reconsidered on the basis of the accepted
three-domain research result.

## Research Basis

The amended product boundary is based on:

```text
Domain 1:
Python artifact evidence
validated on the frozen 1,954-wheel corpus

Domain 2:
pytest result evidence
validated against accepted corpus, schema, validator, independent oracle, and
producer

Domain 3:
Terraform Plan JSON evidence
validated against accepted corpus, schema, validator, independent oracle, and
producer

Shared:
typed claims
accepted Gate A generic proof-assembly boundary
bounded deterministic action contract
proof and drill-down surface
```

The correct architectural sequence remains:

```text
Gate A introduced a generic assembly boundary.
Domain 1 identity was preserved under the accepted Gate A review.
Domains 2 and 3 used the accepted generic boundary with independent truth
layers and accepted producers.
```

The proposal must not claim that the original pre-Gate-A interface was reused
unchanged across all domains.

## Proposed Amended MVP Boundary

The proposed amended MVP boundary is:

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

The amended MVP is a local evidence product, not a live orchestration platform.

## Unified MVP Shape

The proposed MVP shape is:

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

This is a product-boundary proposal for a unified evidence workflow over three
accepted domains.

## Domain 1 Product Boundary

Domain 1 may remain the product basis:

```text
Python wheel artifact evidence
accepted Unification Proof behavior
bounded action contract
claim inclusion / mutation rejection evidence
NOT_EVALUATED preservation
BLOCK preservation
Domain 1 identity baseline
```

It must remain bounded to the accepted corpus and contract.

It must not claim:

```text
software package safety
SBOM correctness in the external world
vulnerability detection
universal supply-chain coverage
```

## Domain 2 Product Boundary

Domain 2 may be included as a bounded local evidence producer:

```text
Python pytest result evidence
accepted dual identity model
accepted corpus
accepted Oracle Schema V7
accepted validator
accepted independent oracle
accepted producer
```

Permitted bounded claim:

```text
SPIRA can process Python pytest result evidence within the accepted corpus,
oracle, and producer contract.
```

It must not claim:

```text
general CI-log understanding
universal pytest support
test correctness
software correctness
semantic cache reuse safety
```

The Domain 2 `result_identity` remains a policy-independent semantic result
identity for the accepted test-result contract. It is not authorized for Gate B
cache or reuse.

## Domain 3 Product Boundary

Domain 3 may be included as a bounded local evidence producer:

```text
Terraform Plan JSON evidence
accepted 40-case corpus
accepted Oracle Schema V1
accepted validator
accepted independent oracle
accepted producer
```

Permitted bounded claim:

```text
SPIRA can process pinned Terraform Plan JSON evidence within the accepted
corpus, oracle, and producer contract.
```

It must not claim:

```text
Terraform infrastructure correctness
Terraform infrastructure security
Terraform cost correctness
Terraform compliance correctness
whether terraform apply would succeed
live-state freshness
provider safety
cloud safety
Kubernetes support
```

Terraform Plan JSON is treated as pinned evidence. The MVP must not require
live Terraform apply, remote backend access, cloud credentials, provider
downloads at evaluation time, or live infrastructure access.

## Shared Identity Boundary

The `unification_id` remains:

```text
contextual proof identity
```

It is not:

```text
semantic result identity
cache key for reuse
cross-time staleness guarantee
proof of regenerated-evidence equivalence
```

The product may state:

```text
identical canonical claims, decision, subject, and frozen context inputs
produce a reproducible unification_id
```

It must not state:

```text
same semantic outcome always produces the same unification_id
regenerated reports or plans always preserve identity
the identity is safe for semantic cache reuse
```

## Explicitly Out of MVP Scope

The amended MVP must still exclude:

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

## Product Claim Language

Permitted bounded statement:

```text
SPIRA has validated a shared unification proof architecture across three
accepted evidence domains: Python artifacts, pytest result evidence, and
Terraform Plan JSON.
```

Required qualifier:

```text
within the tested contracts, frozen corpora, accepted oracles, and accepted
producer implementations.
```

Permitted product-positioning statement:

```text
The MVP boundary may include a unified local evidence flow for Domains 1-3,
using typed claims, the accepted Gate A proof-assembly boundary, bounded
actions, proof output, and drill-down.
```

Forbidden statements:

```text
SPIRA proves software is safe.
SPIRA proves infrastructure is safe.
SPIRA predicts Terraform apply success.
SPIRA is a universal Context Firewall.
SPIRA provides semantic cache reuse.
SPIRA supports live Kubernetes evidence.
SPIRA OS / orchestrator exists.
SPIRA has measured live agent efficiency gains.
```

## Unified Real-Agent Benchmark Requirement

The three-domain research validates correctness within the accepted domain
contracts. It does not yet validate the efficiency or operational behavior of a
unified product flow with a live agent.

Before public release or any public efficiency claim, a separate MVP acceptance
benchmark must be authorized, run, and reviewed.

The benchmark should compare:

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

Required preservation gates:

```text
action preserved
reason_codes preserved
NOT_EVALUATED preserved
BLOCK preserved
zero false PROCEED
zero safety overclaim
evidence drill-down preserved
```

Measurements may include:

```text
context size
tool-call count
evidence bytes surfaced to the agent
latency or wall-clock observations
human-review ergonomics
```

The benchmark must not promise a savings percentage in advance. Any savings or
efficiency claim must be based on the measured benchmark result.

## Implementation Boundary

Acceptance of this amendment would not authorize code.

A separate MVP implementation authorization would still be required. It must
define:

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

## Release Boundary

This proposal does not authorize:

```text
merge to main
public product claim update
version bump
tag
PyPI publication
release notes
marketing copy
documentation that implies release support
```

The public product remains unchanged until separate release authorization.

## Review Required

The next artifact must be a review:

```text
research/mvp_product_boundary_amendment_proposal_review.md
```

The review must decide exactly one:

```text
MVP_PRODUCT_BOUNDARY_AMENDMENT_ACCEPTED
MVP_PRODUCT_BOUNDARY_AMENDMENT_NEEDS_REVISION
MVP_PRODUCT_BOUNDARY_AMENDMENT_REJECTED
```

## Final Boundary

```text
MVP product boundary amendment: PROPOSED
MVP implementation: NOT_AUTHORIZED
unified real-agent benchmark: REQUIRED_BEFORE_EFFICIENCY_CLAIM
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
semantic cache reuse: NOT_AUTHORIZED
live infrastructure: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
merge to main: NOT_AUTHORIZED
```
