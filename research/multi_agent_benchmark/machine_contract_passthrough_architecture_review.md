# Machine Contract Passthrough Architecture Review

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ARCHITECTURE_ACCEPTED

AUTHORITATIVE_MACHINE_CONTRACT_CHANNEL_ACCEPTED

SEPARATE_NON_AUTHORITATIVE_LLM_EXPLANATION_CHANNEL_ACCEPTED

MODEL_REGENERATION_REJECTED_AS_SOURCE_OF_TRUTH

BENCHMARK_POLICY_REVISION_REQUIRED

MVP_BOUNDARY_AMENDMENT_REQUIRED

IMPLEMENTATION_NOT_AUTHORIZED

CLAUDE_RESULTS_PRESERVED

CODEX_RESULTS_PRESERVED

NO_RESULT_RECLASSIFICATION

NO_NEW_LIVE_SESSIONS

PRIMARY_BENCHMARKS_UNDER_OLD_POLICY_BLOCKED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review evaluates:

```text
research/multi_agent_benchmark/
machine_contract_passthrough_architecture_proposal.md
```

It does not authorize:

```text
source-code changes

MVP changes

producer changes

schema changes

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
Is the evidence sufficient to reject model regeneration
as the authoritative contract channel?
```

Verdict:

```text
YES
```

The evidence from Claude Native and Codex Native is sufficient to reject
language-model regeneration as the authoritative channel for SPIRA contracts.

Claude Native showed that, even when Arms B and C eliminated `false PROCEED`,
strict metadata reproduction was not perfect:

```text
Arm B direct-contract strict fidelity:
57 / 60

Arm C unified-contract strict fidelity:
51 / 60

Arm B/C false PROCEED:
0
```

Codex Native showed the same architectural boundary in a different form:

```text
action understanding:
PASS

safety:
PASS

schema validity:
PASS

usage accounting:
PASS

strict metadata reconstruction:
NOT 100%
```

The accepted Codex cross-arm analysis found:

```text
MODEL_SERIALIZATION_VARIABILITY_CONFIRMED
SCHEMA_ENFORCES_STRUCTURE_NOT_ORACLE_CONTENT
MODEL_INSTANCE_CONTENT_OMISSION_CONFIRMED
COMPARATOR_OR_ORACLE_DEFECT_NOT_CONFIRMED
```

That is enough to conclude that a probabilistic model may understand and obey a
contract while still failing to reproduce every machine field exactly.

The source of truth must therefore be the original machine contract, not a
model-generated substitute contract.

## Review Question 2

```text
Is machine passthrough compatible with the accepted
Domain 1, Domain 2, Domain 3, and Gate A semantics?
```

Verdict:

```text
YES, WITH BOUNDARIES
```

Machine passthrough is compatible with the accepted SPIRA semantics because it
preserves rather than replaces the deterministic contract artifacts already
accepted in the research chain.

Compatibility requires that the passthrough channel preserve:

```text
Domain 1 accepted behavior and baseline

Domain 2 corpus, oracle, validator, and producer semantics

Domain 3 corpus, oracle, validator, and producer semantics

Gate A proof assembly semantics

action and claim-status enums

SPIRA_DECISION_SEMANTICS_V2

explicit NOT_EVALUATED states

not_claimed boundaries

evidence and proof references

contract identity and hashes
```

The review does not authorize any refactor or rebaseline of those components.

## Review Question 3

```text
Can the authoritative and explanatory channels be separated
without weakening evidence provenance?
```

Verdict:

```text
YES, IF MACHINE IDENTITY IS PRESERVED AND AUDITABLE
```

The separation is accepted only if the machine channel remains independently
auditable. A future implementation must preserve at least:

```text
source contract hash

contract schema/version

domain

case or subject identifier, where applicable

action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence references

proof references

producer identity or contract hash

unified wrapper identity, if applicable
```

The explanatory channel may reference the contract, but it must not become the
contract.

## Review Question 4

```text
What contradiction and override gates are required?
```

Verdict:

```text
FAIL-CLOSED CONTRADICTION GATES REQUIRED
```

A future policy must define explicit contradiction gates. At minimum:

```text
MODEL_EXPLANATION_CONTRADICTS_MACHINE_CONTRACT

MODEL_EXPLANATION_UNSAFE_CONTINUATION

MODEL_EXPLANATION_DROPS_BLOCKER

MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS

MODEL_EXPLANATION_CLAIMS_NOT_CLAIMED_BOUNDARY

MODEL_EXPLANATION_FABRICATES_EVIDENCE

MODEL_EXPLANATION_OVERRIDES_MACHINE_ACTION
```

All such contradictions must fail closed or be surfaced as explicit review
findings. The model explanation must never be used to weaken:

```text
STOP

BLOCK

RERUN_REQUIRED

NOT_EVALUATED

not_claimed

evidence/proof identity
```

Precedence is accepted as:

```text
SPIRA machine contract
>
model explanation
>
free-form agent suggestion
```

## Review Question 5

```text
What new schema or envelope is needed?
```

Verdict:

```text
NEW ENVELOPE REQUIRED, NOT AUTHORIZED HERE
```

The proposal correctly avoids defining a final schema. A future authorization
must define a versioned envelope that separates:

```text
machine_contract

model_explanation

contradiction_analysis

usage/tool telemetry

drilldown/audit references
```

The envelope must make it impossible to confuse model explanation fields with
authoritative SPIRA contract fields.

The exact schema, validator, comparator updates, and benchmark harness changes
are not authorized by this review.

## Review Question 6

```text
How should the global benchmark protocol be revised?
```

Verdict:

```text
REVISION REQUIRED
```

The existing benchmark asked:

```text
Can the model regenerate the entire contract exactly?
```

That remains valid historical evidence and must not be reclassified.

A revised benchmark should ask:

```text
Can the system preserve the machine contract mechanically,
and can the model explain and obey it without contradiction?
```

The revised protocol must remain global across agents:

```text
Claude Native

Codex Native

DeepSeek Direct, if authorized

all future agent tracks
```

No agent-specific relaxation is accepted.

## Review Question 7

```text
Which existing benchmark assets can remain frozen?
```

Verdict:

```text
MOST SOURCE ASSETS SHOULD REMAIN FROZEN
```

The following should remain preserved unless a separate global amendment proves
otherwise:

```text
accepted Domain 1, Domain 2, and Domain 3 corpora

accepted Domain 2 and Domain 3 oracles

accepted producers

accepted Gate A semantics

global Arm A policy history

Claude and Codex historical result artifacts
```

New assets will likely be required for:

```text
machine/explanation envelope

contradiction fixtures

passthrough integrity checks

explanation compliance comparator

revised benchmark reports
```

## Review Question 8

```text
Which new cases are required to test explanation contradiction?
```

Verdict:

```text
NEW CONTRADICTION CASES REQUIRED
```

At minimum, future tests should include explanations that attempt to:

```text
recommend PROCEED when machine action is STOP

ignore a blocker

add a blocker not present in the machine contract

claim NOT_EVALUATED evidence passed

claim producer_correctness or software_safety when not_claimed says otherwise

fabricate evidence or proof references

weaken RERUN_REQUIRED

rewrite reason_codes into non-equivalent text

contradict a Terraform sensitive/unknown path boundary

contradict a pytest evidence conflict boundary
```

Those cases are not authorized by this review; they require a separate
benchmark-policy revision and asset authorization.

## Review Question 9

```text
Does the architecture require an MVP boundary amendment?
```

Verdict:

```text
YES
```

The accepted MVP boundary assumed a unified local evidence product, but the
machine-contract passthrough split changes the product contract surface. A
separate MVP boundary amendment must decide whether the MVP will expose:

```text
machine_contract

model_explanation

contradiction gates

mechanical passthrough identity

explanation audit status
```

This review does not amend the MVP boundary.

## Review Question 10

```text
What implementation and migration authorizations are required?
```

Verdict:

```text
SEPARATE AUTHORIZATIONS REQUIRED
```

At minimum, the future chain should be:

```text
benchmark policy revision proposal
-> benchmark policy review
-> MVP boundary amendment proposal
-> MVP boundary amendment review
-> passthrough envelope/schema authorization
-> implementation authorization
-> focused tests
-> revised readiness authorization
-> revised live benchmark authorization
-> acceptance review
```

No implementation, benchmark rerun, or release is authorized by this review.

## Historical Results Preservation

The review explicitly preserves:

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

Those results answered a different question:

```text
Can the model regenerate the entire contract exactly?
```

They remain valid and must not be converted to PASS.

## Accepted Architecture Statement

```text
SPIRA machine contract:
authoritative deterministic evidence channel

LLM explanation:
non-authoritative explanatory channel

Model-regenerated contract:
rejected as source of truth
```

The accepted architectural rule is:

```text
The model may explain the SPIRA contract.
The model may not replace the SPIRA contract.
```

## Final Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_ARCHITECTURE_ACCEPTED

AUTHORITATIVE_MACHINE_CONTRACT_CHANNEL_ACCEPTED

SEPARATE_NON_AUTHORITATIVE_LLM_EXPLANATION_CHANNEL_ACCEPTED

MODEL_REGENERATION_REJECTED_AS_SOURCE_OF_TRUTH

BENCHMARK_POLICY_REVISION_REQUIRED

MVP_BOUNDARY_AMENDMENT_REQUIRED

IMPLEMENTATION_NOT_AUTHORIZED

CLAUDE_RESULTS_PRESERVED

CODEX_RESULTS_PRESERVED

NO_RESULT_RECLASSIFICATION

NO_NEW_LIVE_SESSIONS

PRIMARY_BENCHMARKS_UNDER_OLD_POLICY_BLOCKED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Next Artifact

The next artifact should be a separate benchmark policy revision proposal, for
example:

```text
research/multi_agent_benchmark/
machine_contract_passthrough_benchmark_policy_revision_proposal.md
```

That proposal should define the revised benchmark question, revised arms,
machine-contract integrity gates, explanation-compliance gates, contradiction
taxonomy, and required new fixtures.

It must not authorize implementation or live sessions by itself.
