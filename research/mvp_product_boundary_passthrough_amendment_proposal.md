# MVP Product Boundary Passthrough Amendment Proposal

## Status

```text
MVP_PRODUCT_BOUNDARY_PASSTHROUGH_AMENDMENT_PROPOSED

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

NO_IMPLEMENTATION_AUTHORIZATION

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This proposal amends the accepted MVP product boundary to reflect the accepted
machine-contract passthrough architecture and the accepted passthrough benchmark
policy.

It defines what the unified local MVP should include conceptually after the
architecture change:

```text
authoritative machine-contract passthrough
+
non-authoritative model explanation
+
fail-closed contradiction gates
```

This is a product-boundary proposal only.

It does not authorize:

```text
implementation

schema creation

fixture creation

runner changes

prompt changes

comparator changes

oracle changes

new live sessions

primary benchmark execution

release
```

## 2. Prior MVP Boundary

The previously accepted MVP boundary covered a unified local evidence product
over:

```text
Domain 1 - Python artifact evidence

Domain 2 - bounded local pytest result evidence

Domain 3 - bounded local Terraform Plan JSON evidence
```

with shared:

```text
typed claims

Gate A unification assembly

deterministic action

proof and drill-down references
```

The prior boundary excluded:

```text
Gate B / semantic cache reuse

cross-time staleness automation

live Terraform infrastructure

terraform apply

Kubernetes / Domain 4

orchestrator

safety / compliance / cost claims
```

Those exclusions remain in force.

## 3. Reason For Amendment

Claude Native and Codex Native benchmark evidence showed that language models
can understand and obey the SPIRA decision while still failing to reproduce all
contract metadata exactly.

The accepted architecture review concluded:

```text
SPIRA machine contract:
authoritative deterministic evidence channel

LLM explanation:
non-authoritative explanatory channel

model-regenerated contract:
rejected as source of truth
```

The accepted benchmark-policy review then changed the benchmark target from:

```text
Can the model regenerate the entire SPIRA contract exactly?
```

to:

```text
Can the system preserve the authoritative SPIRA machine contract mechanically,
and can the model explain and obey that contract without contradiction,
unsafe override, or unsupported claim?
```

The MVP product boundary must therefore be amended before any implementation.

## 4. Proposed MVP Inclusion

The amended MVP should include the following conceptual product capabilities.

### 4.1 Authoritative Machine-Contract Passthrough

The MVP should pass the accepted SPIRA machine contract mechanically through
the product flow without model regeneration.

The machine contract remains authoritative for:

```text
domain

subject / case identity, where applicable

contract schema and version

contract hash

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

The model must not be able to rewrite this channel.

### 4.2 Separate Model Explanation Channel

The MVP should expose a distinct non-authoritative explanation channel.

The model explanation may include:

```text
plain-language rationale

summary of blockers

bounded remediation suggestions

questions for human review

description of exposed evidence

next-step suggestions within the machine contract
```

The model explanation must not replace:

```text
machine action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence/proof identity
```

### 4.3 Fail-Closed Contradiction Analysis

The MVP should include contradiction analysis between the machine contract and
the model explanation.

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

### 4.4 Mechanical Contract Identity Checks

The MVP boundary should include mechanical checks that verify:

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

These checks must not depend on model-generated serialization.

### 4.5 Explanation Compliance Reporting

The MVP boundary should include reporting that separates:

```text
machine_contract_integrity

model_explanation_compliance

contradiction_findings

telemetry

not_claimed boundaries

NOT_EVALUATED preservation
```

The report must make clear that the machine contract is authoritative and the
model explanation is not.

## 5. Proposed Product Trust Boundary

The amended MVP trust boundary is:

```text
SPIRA machine contract
>
model explanation
>
free-form agent suggestion
```

When the model explanation contradicts the machine contract:

```text
the machine contract wins
```

When contradiction is detected:

```text
the contradiction is reported
and the workflow fails closed where safety/scope is affected
```

## 6. Domain Scope Preserved

The amended MVP remains scoped to the already accepted evidence domains:

```text
Domain 1:
Python artifact evidence

Domain 2:
bounded local pytest result evidence

Domain 3:
bounded local Terraform Plan JSON evidence
```

The amendment does not add:

```text
Domain 4

Kubernetes

live Terraform state

terraform apply

Gate B

semantic cache reuse

orchestrator

release scope
```

## 7. Semantics Preserved

The amendment must preserve:

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
authorized by this proposal.

## 8. Historical Benchmark Results Preserved

The amendment does not reclassify old benchmark results.

The following remain preserved:

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

## 9. Required Future Artifacts

The amended MVP boundary requires separate future authorizations for:

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

None of these are authorized here.

## 10. Proposed Envelope Shape

The eventual MVP output may need to expose a structure similar to:

```json
{
  "machine_contract": {
    "authoritative": true,
    "contract_hash": "<frozen hash>",
    "action": "STOP",
    "reason_codes": ["..."],
    "blocking_items": ["..."],
    "not_evaluated": ["..."],
    "not_claimed": ["..."],
    "evidence_references": ["..."],
    "proof_references": ["..."]
  },
  "model_explanation": {
    "authoritative": false,
    "text": "...",
    "remediation_suggestions": ["..."]
  },
  "contradiction_analysis": {
    "contradictions": [],
    "fail_closed": false
  },
  "telemetry": {
    "usage_available": true
  }
}
```

This is illustrative only.

The exact schema is not authorized by this proposal.

## 11. Non-Claims

This proposal does not claim that:

```text
the passthrough MVP is implemented

the envelope schema exists

contradiction fixtures exist

model explanations are always correct

all contradiction risks are eliminated

efficiency has been proven

Claude results should be reclassified

Codex results should be reclassified

Codex primary is authorized

DeepSeek direct is authorized

release is authorized
```

## 12. Required Review Questions

A separate review must decide:

```text
1. Should the MVP boundary be amended to include authoritative
   machine-contract passthrough?

2. Should the MVP include a separate non-authoritative model explanation
   channel?

3. Should fail-closed contradiction analysis be part of the MVP boundary?

4. Are mechanical contract identity checks required before implementation?

5. Does the amendment preserve Domain 1, Domain 2, Domain 3, and Gate A
   semantics?

6. Does the amendment preserve old Claude and Codex results without
   reclassification?

7. Which future artifacts must be authorized before implementation?

8. Does this amendment change release scope?

9. What sequence of schema, fixture, and implementation authorizations is
   required next?
```

## 13. Proposed Verdict

```text
MVP_PRODUCT_BOUNDARY_PASSTHROUGH_AMENDMENT_PROPOSED

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

NO_IMPLEMENTATION_AUTHORIZATION

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
research/mvp_product_boundary_passthrough_amendment_review.md
```

The review may accept, reject, or require revision of this boundary amendment.

It must not authorize implementation, schema creation, fixture creation, live
sessions, or release unless separate authorizations are created afterward.
