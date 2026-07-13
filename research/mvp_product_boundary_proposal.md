# SPIRA MVP Product Boundary Proposal

## Status

```text
MVP_PRODUCT_BOUNDARY_PROPOSAL_LOCKED
PRODUCT_BOUNDARY_PROPOSAL_ONLY
MVP_IMPLEMENTATION_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
VERSION_BUMP_NOT_AUTHORIZED
TAG_NOT_AUTHORIZED
PYPI_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
TERRAFORM_PRODUCER_NOT_AUTHORIZED
```

## Purpose

This document proposes a bounded MVP product boundary after the completed
multi-domain research program and the accepted negative Domain 3 closeout.

It is not an implementation plan and does not authorize release activity.

## Research Basis

The MVP boundary is based on three research outcomes:

```text
Domain 1:
Python wheel artifact evidence validated on the frozen 1,954-wheel corpus.

Gate A:
Generic proof-assembly boundary accepted.
Domain 1 identity preserved 1,954 / 1,954 during Gate A acceptance.

Domain 2:
Python pytest test-result evidence validated against an accepted frozen corpus,
accepted independent oracle, accepted validator, and accepted producer.
```

Domain 3 is included only as a boundary-setting negative result:

```text
Domain 3 / Terraform:
research attempt completed negatively at corpus materialization.
architectural hypothesis not evaluated.
Terraform excluded from MVP.
```

## Proposed MVP Scope

The MVP should include only capabilities supported by accepted evidence:

```text
Domain 1 product basis:
Python wheel artifact evidence
accepted Unification Proof behavior
bounded action contract
claim inclusion / mutation rejection evidence
NOT_EVALUATED and BLOCK preservation

Domain 2 research capability:
Python pytest test/build failure evidence
accepted dual identity model
accepted oracle and validator
accepted producer against the frozen 38-case corpus
```

Domain 2 may be presented as a validated research capability or experimental
bounded evidence domain. It should not be represented as a broad CI platform.

## Explicitly Out of MVP Scope

The MVP must exclude:

```text
Terraform Plan evidence
Terraform producer
Terraform oracle
Terraform corpus
Kubernetes evidence
live infrastructure state
Gate B status/cache/rerun generalization
semantic cache reuse
Domain 4
orchestrator / SPIRA OS
universal Context Firewall claim
software safety claim
infrastructure safety claim
security scanner claim
cost or compliance claim
```

## Domain 1 Boundary

Domain 1 may support product-facing claims only inside the accepted corpus and
contract:

```text
frozen 1,954-wheel corpus
zero correctness failures in final corpus closure
accepted action contract preserved
deterministic proof construction for identical canonical inputs and frozen context
claim inclusion verification
claim mutation rejection
NOT_EVALUATED semantics
BLOCK semantics
```

It must not claim:

```text
SBOM correctness in the external world
software package safety
vulnerability detection
universal supply-chain coverage
```

## Domain 2 Boundary

Domain 2 may support a bounded statement:

```text
SPIRA can process Python pytest test-result evidence against the accepted
38-case corpus and independent oracle with 38 / 38 claim fidelity, action
equivalence, scope_identity fidelity, and result_identity fidelity.
```

It must not claim:

```text
general CI-log summarization
universal pytest support
test correctness
software correctness
cache/reuse safety
```

## Domain 3 Boundary

Domain 3 must be described as:

```text
negative closeout
corpus not materialized
oracle not reached
producer not reached
architecture hypothesis not evaluated
```

The reason is:

```text
LOCAL TOOLING PRECONDITION NOT MET
Terraform CLI unavailable
authentic local Terraform-generated corpus stratum not materializable
```

The MVP must not include Terraform.

A future Terraform retry requires a separate owner decision and a new
authorization path. It must not be folded into this MVP proposal.

## Gate B Boundary

Gate B remains excluded:

```text
status/cache/rerun generalization: NOT_AUTHORIZED
semantic cache reuse: NOT_AUTHORIZED
epoch/staleness resolution: NOT_AUTHORIZED
```

The MVP may mention the known boundary:

```text
unification_id is contextual identity for exact canonical claims, decision,
subject, and frozen context inputs.
```

It must not claim:

```text
same regenerated evidence -> same identity
semantic cache safety
cross-time reuse safety
```

## Product Claim Language

Permitted bounded statement:

```text
SPIRA has validated a shared unification proof architecture across two accepted
evidence domains, with Domain 1 as the product basis and Domain 2 as a bounded
validated research capability.
```

Required qualifier:

```text
within the tested contracts, frozen corpora, and accepted oracles.
```

Forbidden statements:

```text
SPIRA proves software is safe.
SPIRA proves infrastructure is safe.
SPIRA is a universal Context Firewall.
SPIRA provides semantic cache reuse.
SPIRA supports Terraform.
SPIRA supports Kubernetes.
SPIRA OS / orchestrator exists.
```

## MVP Readiness Gate

This proposal does not decide MVP readiness.

Before MVP implementation or release, a separate review must decide:

```text
MVP_PRODUCT_BOUNDARY_ACCEPTED
MVP_PRODUCT_BOUNDARY_NEEDS_REVISION
MVP_PRODUCT_BOUNDARY_REJECTED
```

Only after boundary acceptance may a separate implementation or release
authorization be considered.

## Next Required Artifact

```text
research/mvp_product_boundary_proposal_review.md
```

## Final Boundary

```text
MVP implementation: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
Terraform retry: NOT_AUTHORIZED
```
