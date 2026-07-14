# Machine Contract Passthrough Architecture Proposal

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ARCHITECTURE_PROPOSED

BENCHMARK_POLICY_REVISION_REQUIRED

AUTHORITATIVE_MACHINE_CONTRACT_CHANNEL_PROPOSED

SEPARATE_LLM_EXPLANATORY_CHANNEL_PROPOSED

NO_RESULT_RECLASSIFICATION

NO_NEW_LIVE_SESSIONS

NO_IMPLEMENTATION_AUTHORIZATION

CLAUDE_RESULTS_PRESERVED

CODEX_RESULTS_PRESERVED

PRIMARY_BENCHMARKS_UNDER_OLD_POLICY_BLOCKED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This proposal records an architectural conclusion produced by the Claude Native
and Codex Native benchmark tracks.

The existing benchmark policy required the language model to regenerate the
accepted SPIRA decision contract as structured output.

The benchmark evidence now shows that:

```text
the SPIRA source contract can be valid and complete;

the contract can be transferred to the model correctly;

the model can understand the required action and safety boundary;

yet the model may still omit, add, substitute, or rewrite
contract metadata when generating a new output object.
```

The proposed architecture therefore separates:

```text
the authoritative machine contract

from

the language-model explanation of that contract.
```

The proposal does not alter or reinterpret any completed benchmark result.

## 2. Evidence Basis

### 2.1 Claude Native

The completed Claude Native primary benchmark established:

```text
Arm A raw-evidence strict fidelity:
4 / 60

Arm A operational pass:
39 / 60

Arm A false PROCEED:
9

Arm B direct-contract strict fidelity:
57 / 60

Arm C unified-contract strict fidelity:
51 / 60

Arm B/C false PROCEED:
0
```

All twelve Arm B/C strict failures were limited to `blocking_items` drift:

```text
10 EXTRA_ITEM

2 ITEM_SUBSTITUTION

0 ORDER_ONLY
```

Across those failures:

```text
action preserved:
12 / 12

stop state preserved:
12 / 12

reason_codes preserved:
12 / 12

NOT_EVALUATED preserved:
12 / 12

false PROCEED:
0
```

No comparator or oracle defect was confirmed.

### 2.2 Codex Native

Codex Native readiness and diagnostic evidence established:

```text
Arm A operational readiness:
3 / 3

Arm C initial strict readiness:
3 / 3

Arm B initial strict readiness:
2 / 3

false PROCEED:
0

schema validity:
complete

usage accounting:
complete

isolation:
pass
```

The failed `pytest_result / synthetic_clean_success / Arm B` session omitted:

```text
reason_codes:
TESTS_PASSED

not_claimed:
producer_correctness
software_safety
```

A subsequent unscored diagnostic produced:

```text
Arm B:
10 / 10 exact

Arm C:
4 / 5 exact
```

The one Arm C failure omitted the same contractual metadata.

The accepted cross-arm analysis concluded:

```text
MODEL_SERIALIZATION_VARIABILITY_CONFIRMED

SCHEMA_ENFORCES_STRUCTURE_NOT_ORACLE_CONTENT

MODEL_INSTANCE_CONTENT_OMISSION_CONFIRMED

COMPARATOR_OR_ORACLE_DEFECT_NOT_CONFIRMED

CODEX_NATIVE_STRICT_METADATA_RELIABILITY_NOT_READY
```

## 3. Core Finding

The combined evidence supports the following architectural finding:

```text
SPIRA contract is reliable as machine evidence.

LLM regeneration of that contract
is not reliable at 100%.
```

This distinction applies even when:

```text
the model receives the correct contract;

the prompt requests exact preservation;

the output satisfies the JSON Schema;

the model selects the correct action;

the model preserves the safety decision;

the infrastructure and usage telemetry are valid.
```

A probabilistic language model must therefore not be treated as the
authoritative serializer of a deterministic machine contract.

## 4. Existing Architecture Problem

The existing benchmark interaction effectively asks the model to perform:

```text
SPIRA machine contract
-> model interpretation
-> model-generated replacement contract
-> comparator
```

This design creates an unnecessary regeneration boundary.

The source contract already contains the accepted machine values:

```text
action

stop state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed

evidence references

proof references
```

Requiring the language model to reproduce these fields introduces avoidable
risks:

```text
field omission

extra-item insertion

item substitution

natural-language rewriting

normalization drift

boundary loss

unsupported inference

inconsistent list serialization
```

These risks are separate from whether the model understood the operational
decision.

## 5. Proposed Architecture

The proposed architecture introduces two explicitly separate channels.

### 5.1 Authoritative Machine Contract Channel

The accepted SPIRA contract passes mechanically through the workflow without
language-model regeneration.

```text
SPIRA producer
-> accepted deterministic contract
-> unified contract wrapper, when applicable
-> immutable authoritative machine channel
-> agent or workflow enforcement
```

This channel remains the source of truth for:

```text
recommended action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence references

proof references

contract identity and hashes
```

The authoritative channel must not be rewritten by the language model.

The model must not be permitted to:

```text
remove contractual values

add contractual values

replace contractual values

reorder values when ordering is contractually significant

convert explicit NOT_EVALUATED into evaluated status

replace machine boundaries with free-form text

generate a substitute contract that overrides the source contract
```

### 5.2 LLM Explanatory Channel

The model receives the authoritative contract and may generate a separate
explanation.

```text
authoritative SPIRA contract
+
supporting evidence exposed within policy
-> LLM explanation
```

The explanatory channel may contain:

```text
plain-language explanation

human-readable rationale

recommended remediation sequence

summary of blocking conditions

description of evidence

questions for human review

bounded next-step suggestions
```

The explanatory channel is not authoritative.

It must not replace:

```text
the machine action

the machine stop state

the contractual reason codes

the explicit blocker list

NOT_EVALUATED

not_claimed boundaries

evidence and proof identities
```

## 6. Required Output Separation

A future agent-facing response should expose both channels distinctly.

Conceptual example:

```json
{
  "machine_contract": {
    "source": "SPIRA",
    "authoritative": true,
    "contract_hash": "<frozen hash>",
    "action": "STOP",
    "reason_codes": ["..."],
    "blocking_items": ["..."],
    "not_evaluated": ["..."],
    "not_claimed": ["..."],
    "evidence_references": ["..."]
  },
  "model_explanation": {
    "authoritative": false,
    "text": "The workflow must stop because...",
    "remediation_suggestions": ["..."]
  }
}
```

The exact schema is not authorized by this proposal.

The example illustrates the required trust boundary only.

## 7. Enforcement Principle

When the machine contract and model explanation disagree:

```text
the machine contract wins.
```

The workflow must never resolve a contradiction by accepting the
model-generated interpretation over the authoritative SPIRA contract.

Required precedence:

```text
SPIRA machine contract
>
model explanation
>
free-form agent suggestion
```

Examples:

```text
Machine contract says STOP,
model explanation says continue:
STOP remains authoritative.

Machine contract contains NOT_EVALUATED,
model explanation claims the layer passed:
the explanation is contradictory and must be rejected or flagged.

Machine contract contains two blockers,
model explanation mentions one:
both machine blockers remain active.
```

## 8. Proposed Benchmark Policy Revision

The existing benchmark asks whether a model can regenerate the complete
contract exactly.

That result remains valid historical evidence, but it should not remain the
sole acceptance model for the proposed architecture.

A revised benchmark should test two separate capabilities.

### 8.1 Machine Contract Integrity

Verify mechanically:

```text
the source contract is unchanged;

the contract hash is preserved;

the action is unchanged;

all explicit lists are unchanged;

NOT_EVALUATED is unchanged;

not_claimed boundaries are unchanged;

evidence and proof references are unchanged;

the authoritative channel cannot be modified by the model.
```

This gate must be deterministic and must not depend on model-generated
serialization.

### 8.2 Model Explanation Compliance

Evaluate whether the model explanation:

```text
agrees with the authoritative action;

does not recommend unsafe continuation;

does not contradict reason codes;

does not contradict blockers;

does not convert NOT_EVALUATED into PASS;

does not claim excluded safety or compliance conclusions;

does not fabricate evidence;

does not override the authoritative contract;

provides useful and bounded human-readable guidance.
```

Exact reproduction of the complete machine contract should no longer be
required from the explanatory channel unless a future task explicitly tests
model serialization reliability.

## 9. Proposed Future Benchmark Arms

A future revised protocol may preserve the existing research distinction while
changing the agent output boundary.

### Arm A - Raw Evidence Baseline

```text
raw evidence
-> model discovery and interpretation
-> operational decision and explanation
```

Measure:

```text
action accuracy

false PROCEED

unsupported inference

evidence discovery cost

tool calls

files opened

tokens

latency

fidelity distance from the accepted oracle
```

### Arm B - Direct Contract Passthrough

```text
direct domain contract
-> mechanical authoritative channel
+
model explanation
```

Measure:

```text
machine-contract integrity

explanation agreement

contradiction rate

unsafe recommendation rate

token and tool cost
```

### Arm C - Unified Contract Passthrough

```text
unified SPIRA contract
-> mechanical authoritative channel
+
model explanation
```

Measure:

```text
machine-contract integrity

unified routing integrity

explanation agreement

contradiction rate

unsafe recommendation rate

overhead relative to Arm B

cost-and-fidelity improvement relative to Arm A
```

## 10. Historical Result Preservation

This proposal does not alter completed results.

The following remain authoritative historical findings:

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

No prior result may be rewritten as PASS merely because the proposed
architecture would use a different acceptance boundary.

The old benchmark answered:

```text
Can the model regenerate the entire contract exactly?
```

The proposed benchmark would answer:

```text
Can the system preserve the machine contract mechanically,
and can the model explain and obey it without contradiction?
```

These are different research questions.

## 11. Global Scope

Any accepted architecture or benchmark amendment must apply equally to:

```text
Claude Native

Codex Native

DeepSeek Direct, if authorized

all future agent tracks
```

No Claude-specific or Codex-specific exception is permitted.

The amendment must not be optimized toward:

```text
Claude blocking_items drift

Codex clean-success metadata omission

a particular model family

a particular provider

a particular failed session
```

## 12. Security and Trust Implications

The passthrough architecture strengthens the trust boundary by ensuring:

```text
the deterministic evidence engine remains authoritative;

the probabilistic model cannot silently weaken a STOP decision;

explicit blockers cannot disappear from the machine channel;

NOT_EVALUATED cannot be rewritten as evaluated;

not_claimed boundaries remain visible;

the explanation can be audited independently;

contract and explanation can be compared for contradiction.
```

It also enables a new explicit signal:

```text
MODEL_EXPLANATION_CONTRADICTS_MACHINE_CONTRACT
```

Such a contradiction should fail closed.

## 13. Product Implication

The architectural role of SPIRA becomes:

```text
SPIRA verifies evidence.

SPIRA produces the authoritative bounded decision contract.

The workflow passes that contract mechanically.

The language model explains and acts within the contract.

The language model does not recreate the source of truth.
```

This preserves the product principle:

```text
AI agents generate artifacts.

SPIRA verifies artifacts.

SPIRA produces bounded machine decisions.

Humans and agents act within those decisions.
```

## 14. Non-Claims

This proposal does not establish that:

```text
the passthrough architecture is implemented;

the revised architecture is production-ready;

model explanations will always be correct;

all contradiction risks are eliminated;

token or latency savings are proven;

Claude or Codex results should be reclassified;

Codex primary is authorized;

DeepSeek direct is authorized;

the product is ready for release.
```

## 15. Required Review Questions

A separate review must decide:

```text
1. Is the evidence sufficient to reject model regeneration
   as the authoritative contract channel?

2. Is machine passthrough compatible with the accepted
   Domain 1, Domain 2, Domain 3, and Gate A semantics?

3. Can the authoritative and explanatory channels be separated
   without weakening evidence provenance?

4. What contradiction and override gates are required?

5. What new schema or envelope is needed?

6. How should the global benchmark protocol be revised?

7. Which existing benchmark assets can remain frozen?

8. Which new cases are required to test explanation contradiction?

9. Does the architecture require an MVP boundary amendment?

10. What implementation and migration authorizations are required?
```

## 16. Required Next Artifact

The next artifact, if this proposal is reviewed, should be:

```text
research/multi_agent_benchmark/
machine_contract_passthrough_architecture_review.md
```

The review may accept, reject, or require revision of the proposal.

It must not authorize implementation unless a separate implementation
authorization is created afterward.

## 17. Proposed Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_ARCHITECTURE_PROPOSED

AUTHORITATIVE_MACHINE_CONTRACT_CHANNEL_PROPOSED

SEPARATE_NON_AUTHORITATIVE_LLM_EXPLANATION_CHANNEL_PROPOSED

MODEL_REGENERATION_REMOVED_AS_PROPOSED_SOURCE_OF_TRUTH

BENCHMARK_POLICY_REVISION_REQUIRED

GLOBAL_CROSS_AGENT_SCOPE_REQUIRED

CLAUDE_RESULTS_PRESERVED

CODEX_RESULTS_PRESERVED

NO_RESULT_RECLASSIFICATION

NO_NEW_LIVE_SESSIONS

NO_IMPLEMENTATION_AUTHORIZATION

PRIMARY_BENCHMARKS_UNDER_OLD_POLICY_BLOCKED

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Final Boundary

This document proposes an architecture and a benchmark-policy direction only.

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

The next step after this proposal is a separate review only. The review must
decide whether the separation between an authoritative machine contract and a
model explanation is the correct architectural change before any code or
protocol implementation is touched.
