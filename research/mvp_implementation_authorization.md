# SPIRA MVP Implementation Authorization

## Status

```text
MVP_IMPLEMENTATION_AUTHORIZATION_LOCKED
AUTHORIZATION_REVIEW_REQUIRED_BEFORE_CODE
MVP_IMPLEMENTATION_NOT_YET_AUTHORIZED
RELEASE_NOT_AUTHORIZED
VERSION_BUMP_NOT_AUTHORIZED
TAG_NOT_AUTHORIZED
PYPI_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
TERRAFORM_RETRY_NOT_AUTHORIZED
```

## Authorization Chain

```text
Domain 3 negative closeout:
DOMAIN_3_TERRAFORM_PLAN_NEGATIVE_CLOSEOUT_ACCEPTED

MVP product boundary:
MVP_PRODUCT_BOUNDARY_ACCEPTED
```

This document defines the exact implementation scope that may be authorized
after review.

It does not itself authorize code changes. Implementation remains blocked until
a separate review returns:

```text
MVP_IMPLEMENTATION_AUTHORIZATION_ACCEPTED
```

## Exact MVP Scope

The MVP implementation may only align the public product surface with the
accepted MVP boundary.

The MVP includes:

```text
Domain 1 as the product basis:
Python wheel artifact evidence
accepted Unification Proof behavior
bounded action contract
claim inclusion verification
claim mutation rejection
NOT_EVALUATED preservation
BLOCK preservation

Domain 2 as a bounded validated research capability:
Python pytest test-result evidence
accepted 38-case corpus
accepted independent oracle
accepted validator
accepted producer
research-only positioning unless separately authorized for release
```

The MVP does not include:

```text
Terraform
Kubernetes
Gate B status/cache/rerun generalization
semantic cache reuse
epoch/staleness resolution
Domain 4
orchestrator / SPIRA OS
new public runtime domains
release/version/tag/PyPI activity
```

## Domain 1 Product Capabilities

Domain 1 may be product-facing only within its accepted boundaries:

```text
artifact trust / graph behavior for Python wheel evidence
Unification Proof for exact canonical claims, decision, subject, and frozen context
bounded action contract
claim inclusion and mutation rejection
NOT_EVALUATED and BLOCK semantics
```

Domain 1 must not be represented as:

```text
SBOM truth in the external world
software safety proof
vulnerability scanner
universal supply-chain verifier
```

## Domain 2 Research-Only Boundary

Domain 2 may be included only as a validated research capability.

Permitted language:

```text
validated against an accepted 38-case corpus and independent oracle
```

Forbidden language:

```text
production CI platform
universal pytest support
general test-log summarizer
release-ready public feature
cache/reuse capability
software correctness proof
```

No Domain 2 public CLI command, release-facing workflow, or product promise may
be added unless a later authorization explicitly promotes Domain 2 from
research capability to product feature.

## Allowed Files After Review Acceptance

If and only if this authorization is accepted by a separate review, a narrow MVP
implementation may modify only:

```text
README.md
docs/mvp_product_boundary.md
docs/unification_proof.md
docs/agent_integration.md
docs/ci_quickstart.md
source/spira_core/trust_cli.py
tests/test_mvp_product_boundary.py
```

File intent:

```text
README.md:
  align product claims with the accepted MVP boundary.

docs/mvp_product_boundary.md:
  publish the accepted MVP boundary for users.

docs/unification_proof.md:
  preserve bounded reproducibility and contextual identity language.

docs/agent_integration.md:
  keep agent-facing claims inside Domain 1 and accepted research boundaries.

docs/ci_quickstart.md:
  ensure CI language does not imply Gate B, Domain 2 release support, Terraform,
  Kubernetes, or universal safety.

source/spira_core/trust_cli.py:
  help text or command-description guardrails only.
  No new commands.
  No behavior changes to trust/graph/status/cache/plan-rerun/drift/rebaseline.

tests/test_mvp_product_boundary.py:
  regression tests that enforce public-claim boundaries and CLI help guardrails.
```

Any additional file requires a new authorization before modification.

## Forbidden Files and Areas

The MVP implementation must not modify:

```text
pyproject.toml
CHANGELOG.md
release/
dist/
.github/workflows/
schemas/
source/spira_core/unification_proof.py
source/spira_core/test_build_failure_producer.py
source/spira_core/test_build_failure_oracle_validator.py
source/spira_core/agent_cache.py
source/spira_core/agent_status.py
source/spira_core/rerun_planner.py
research/test_build_failure_contract/**
research/unification_proof_corpus/**
research/terraform_plan_contract/**
```

Forbidden changes:

```text
version bump
package metadata change
new public CLI command
new action enum
new claim status enum
decision semantics change
Gate A refactor
Gate B behavior
Domain 2 corpus/oracle/schema/validator changes
Terraform retry
Domain 4
release packaging
```

## Public Compatibility Requirements

Public product version `0.6.1` remains unchanged.

The implementation must preserve:

```text
spira-trust version output behavior
existing public command names
existing command exit semantics
existing JSON output schemas for runtime commands
existing Domain 1 behavior
accepted Gate A behavior
accepted Domain 2 research artifacts
```

No public compatibility claim may imply a new release.

## Regression Gates

A future implementation may be accepted only if all gates pass:

```text
focused MVP boundary tests: PASS
full pytest: PASS
git diff --check: PASS
public claim grep: PASS
forbidden claim grep: PASS
version unchanged: 0.6.1
pyproject.toml unchanged
release/tag/PyPI artifacts unchanged
Gate A files unchanged
Gate B files unchanged
Domain 2 corpus/oracle/schema/validator unchanged
Terraform artifacts unchanged
```

Required forbidden-claim grep must fail the implementation if public-facing docs
or CLI help claim:

```text
Terraform support
Kubernetes support
Gate B support
semantic cache safety
universal Context Firewall
software safety proof
infrastructure safety proof
compliance proof
SPIRA OS / orchestrator product
Domain 2 production CI platform
```

## Implementation Stop Conditions

Stop and record a revision-required result if implementation requires:

```text
modifying files outside the allowed list
changing runtime semantics
adding a public command
changing version/package metadata
changing release files
changing Gate A
opening Gate B
promoting Domain 2 to release feature
retrying Terraform
opening Domain 4
weakening product-claim boundaries
```

## Authorized Outcomes After Review

If this authorization is reviewed and accepted, the implementation phase may
end only with:

```text
MVP_IMPLEMENTATION_COMPLETE
MVP_IMPLEMENTATION_NEEDS_REVISION
MVP_IMPLEMENTATION_REJECTED
MVP_IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
```

`MVP_IMPLEMENTATION_COMPLETE` would not authorize release.

## Review Required

The next required artifact is:

```text
research/mvp_implementation_authorization_review.md
```

Possible review verdicts:

```text
MVP_IMPLEMENTATION_AUTHORIZATION_ACCEPTED
MVP_IMPLEMENTATION_AUTHORIZATION_NEEDS_REVISION
MVP_IMPLEMENTATION_AUTHORIZATION_REJECTED
```

Until that review is committed and accepted:

```text
no MVP code
no public product expansion
no merge/push requirement
no release
```
