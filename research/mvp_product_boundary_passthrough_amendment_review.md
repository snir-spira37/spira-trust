# MVP Product Boundary Passthrough Amendment Review

## Status

```text
MVP_PRODUCT_BOUNDARY_PASSTHROUGH_AMENDMENT_ACCEPTED

AUTHORITATIVE_MACHINE_CONTRACT_PASSTHROUGH_INCLUDED

NON_AUTHORITATIVE_MODEL_EXPLANATION_INCLUDED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_INCLUDED

MECHANICAL_CONTRACT_IDENTITY_CHECKS_INCLUDED

EXPLANATION_COMPLIANCE_REPORTING_INCLUDED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_PRESERVED

OLD_CLAUDE_AND_CODEX_RESULTS_PRESERVED

NEW_ENVELOPE_SCHEMA_AUTHORIZATION_REQUIRED

NEW_CONTRADICTION_FIXTURE_AUTHORIZATION_REQUIRED

IMPLEMENTATION_AUTHORIZATION_REQUIRED

IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review evaluates:

```text
research/mvp_product_boundary_passthrough_amendment_proposal.md
```

It does not authorize:

```text
source-code changes

MVP implementation

new envelope schema

new fixture corpus

producer changes

prompt changes

comparator changes

oracle changes

result reclassification

new Claude sessions

new Codex sessions

DeepSeek sessions

primary benchmark execution

holdout

carryover

merge to main

release

version bump

tag

PyPI publication
```

## Review Question 1

```text
Should the MVP boundary be amended to include authoritative
machine-contract passthrough?
```

Verdict:

```text
YES
```

The accepted architecture and benchmark-policy reviews require the product
boundary to include a mechanical passthrough channel. The MVP must preserve the
SPIRA machine contract as the authoritative artifact rather than asking the
model to regenerate it.

Accepted MVP component:

```text
authoritative machine-contract passthrough
```

The channel must preserve:

```text
contract hash

schema/version

domain

subject or case identity, where applicable

action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence references

proof references

producer contract identity

unified wrapper identity, where applicable
```

## Review Question 2

```text
Should the MVP include a separate non-authoritative model explanation channel?
```

Verdict:

```text
YES
```

The MVP boundary must separate the authoritative machine contract from the
model explanation. The explanation may help humans or agents understand the
contract, but it is not the contract.

Accepted MVP component:

```text
non-authoritative model explanation
```

The model explanation may include:

```text
plain-language rationale

summary of blockers

bounded remediation suggestions

questions for human review

description of exposed evidence

next-step suggestions within the machine contract
```

It must not replace:

```text
machine action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence/proof identity
```

## Review Question 3

```text
Should fail-closed contradiction analysis be part of the MVP boundary?
```

Verdict:

```text
YES
```

The MVP boundary must include fail-closed contradiction analysis. If the model
explanation conflicts with the machine contract, the machine contract wins.

Accepted MVP component:

```text
fail-closed contradiction analysis
```

Minimum contradiction classes:

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

Critical contradictions must fail closed.

## Review Question 4

```text
Are mechanical contract identity checks required before implementation?
```

Verdict:

```text
YES
```

The MVP boundary requires mechanical checks for:

```text
source contract hash preserved

schema/version preserved

domain preserved

subject/case identity preserved

action preserved

stop / continue preserved

reason_codes preserved

blocking_items preserved

NOT_EVALUATED preserved

not_claimed preserved

evidence references preserved

proof references preserved

producer identity preserved

unified wrapper identity preserved, where applicable
```

These checks must be deterministic and must not depend on model-generated
serialization.

## Review Question 5

```text
Does the amendment preserve Domain 1, Domain 2, Domain 3, and Gate A
semantics?
```

Verdict:

```text
YES
```

The amendment preserves the accepted semantics:

```text
Domain 1 accepted behavior and baseline history

Domain 2 corpus, oracle, validator, and producer semantics

Domain 3 corpus, oracle, validator, and producer semantics

Gate A proof assembly semantics

SPIRA_DECISION_SEMANTICS_V2

action/status enums

NOT_EVALUATED semantics

not_claimed boundary semantics

evidence/proof identity semantics
```

No rebaseline, oracle change, producer semantic change, or Gate A refactor is
authorized.

## Review Question 6

```text
Does the amendment preserve old Claude and Codex results without
reclassification?
```

Verdict:

```text
YES
```

The review preserves the old benchmark results:

```text
Claude Native strict B/C gate:
not accepted

Claude Native primary strict contract acceptance:
not achieved

Codex Native strict metadata readiness:
not ready

Codex primary under the old policy:
not authorized
```

Those results remain valid evidence that model-generated regeneration is not a
reliable 100% source-of-truth channel.

The new product boundary does not convert those historical results to PASS.

## Review Question 7

```text
Which future artifacts must be authorized before implementation?
```

Verdict:

```text
SEPARATE AUTHORIZATIONS REQUIRED
```

The following remain required:

```text
machine/explanation envelope schema

envelope validator

mechanical passthrough integrity checker

explanation compliance comparator

contradiction fixture corpus

MVP implementation plan

focused regression tests

revised readiness protocol

revised live benchmark protocol
```

None are authorized by this review.

## Review Question 8

```text
Does this amendment change release scope?
```

Verdict:

```text
NO
```

The MVP boundary is amended conceptually, but release remains blocked.

This review does not authorize:

```text
merge to main

version bump

tag

GitHub Release

PyPI publication

public launch claim
```

## Review Question 9

```text
What sequence of schema, fixture, and implementation authorizations is
required next?
```

Verdict:

```text
ORDERED AUTHORIZATION CHAIN REQUIRED
```

The accepted next sequence is:

```text
MVP boundary passthrough amendment review
-> envelope/schema authorization
-> envelope/schema draft
-> envelope/schema review
-> contradiction fixture authorization
-> contradiction fixture materialization
-> fixture review
-> MVP passthrough implementation authorization
-> implementation
-> focused tests
-> revised readiness authorization
-> revised readiness execution
-> revised readiness review
-> revised live benchmark authorization
-> revised live benchmark execution
-> revised live benchmark review
-> release proposal, if justified
```

This review completes only the first step in that chain.

## Accepted Product Boundary

The amended MVP product boundary is:

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

The following remain excluded:

```text
Gate B / semantic cache reuse

cross-time staleness automation

live Terraform infrastructure

terraform apply

Kubernetes / Domain 4

orchestrator

safety / compliance / cost claims

release scope
```

## Final Verdict

```text
MVP_PRODUCT_BOUNDARY_PASSTHROUGH_AMENDMENT_ACCEPTED

AUTHORITATIVE_MACHINE_CONTRACT_PASSTHROUGH_INCLUDED

NON_AUTHORITATIVE_MODEL_EXPLANATION_INCLUDED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_INCLUDED

MECHANICAL_CONTRACT_IDENTITY_CHECKS_INCLUDED

EXPLANATION_COMPLIANCE_REPORTING_INCLUDED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_PRESERVED

OLD_CLAUDE_AND_CODEX_RESULTS_PRESERVED

NEW_ENVELOPE_SCHEMA_AUTHORIZATION_REQUIRED

NEW_CONTRADICTION_FIXTURE_AUTHORIZATION_REQUIRED

IMPLEMENTATION_AUTHORIZATION_REQUIRED

IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Next Artifact

The next artifact should be:

```text
research/machine_contract_passthrough_envelope_schema_authorization.md
```

It should authorize only the design and review of a versioned
machine/explanation envelope schema. It must not authorize implementation or
live sessions.
