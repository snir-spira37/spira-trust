# Machine Contract Passthrough Envelope Schema Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_DESIGN_AUTHORIZED

VERSIONED_MACHINE_EXPLANATION_ENVELOPE_DESIGN_ONLY

AUTHORITATIVE_MACHINE_CONTRACT_SECTION_REQUIRED

NON_AUTHORITATIVE_MODEL_EXPLANATION_SECTION_REQUIRED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_SECTION_REQUIRED

SEPARATE_TELEMETRY_SECTION_REQUIRED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_FROZEN

OLD_CLAUDE_AND_CODEX_RESULTS_PRESERVED

SCHEMA_DRAFT_AUTHORIZED

SCHEMA_VALIDATOR_SPEC_AUTHORIZED

SCHEMA_REVIEW_REQUIRED

FIXTURE_MATERIALIZATION_NOT_AUTHORIZED

IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes design of a versioned machine/explanation envelope
schema for the accepted machine-contract passthrough MVP boundary.

The accepted product boundary now requires:

```text
authoritative machine-contract passthrough
+
non-authoritative model explanation
+
fail-closed contradiction analysis
+
mechanical contract identity checks
+
explanation compliance reporting
```

This authorization opens only the design/specification path for the envelope
schema and its validator specification.

It does not authorize implementation, fixture materialization, live sessions,
benchmark execution, result reclassification, or release work.

## 2. Authorized Artifacts

The following artifacts are authorized:

```text
research/machine_contract_passthrough_envelope_schema_v1.schema.json

research/machine_contract_passthrough_envelope_validator_spec.md

research/machine_contract_passthrough_envelope_schema_review.md
```

The schema review may accept, reject, or require revision of the schema and
validator specification.

No validator implementation is authorized by this document.

## 3. Required Envelope Sections

The schema design must define four top-level sections:

```text
machine_contract

model_explanation

contradiction_analysis

telemetry
```

The schema must make the trust boundary explicit:

```text
machine_contract:
authoritative

model_explanation:
non-authoritative

contradiction_analysis:
fail-closed gate evidence

telemetry:
execution and measurement provenance
```

## 4. Machine Contract Section

The `machine_contract` section must be authoritative.

It must include or mechanically bind to:

```text
contract hash

contract schema and version

decision semantics version

domain

subject identity or case identity, where applicable

action

stop / continue state

reason_codes

blocking_items

NOT_EVALUATED

not_claimed boundaries

evidence references

proof references

producer identity

producer contract hash, where applicable

unified wrapper identity, where applicable

source artifact references, where applicable
```

The design must decide whether the machine contract is:

```text
embedded in full
```

or:

```text
referenced by immutable hash and canonical source reference
```

or:

```text
both embedded and hash-bound
```

The draft must specify how equality to the source contract is checked:

```text
byte-for-byte equality

canonical JSON equality

canonical projection equality

or a strictly defined domain-specific projection
```

If a field is derived rather than copied, the derivation must be explicit.

## 5. Model Explanation Section

The `model_explanation` section must be non-authoritative.

It must be marked:

```text
authoritative: false
```

It may contain:

```text
plain-language rationale

summary of blockers

bounded remediation suggestions

questions for human review

description of exposed evidence

next-step suggestions within the machine contract
```

The schema design must decide whether this section is:

```text
text-only
```

or:

```text
structured object with rationale/remediation/summaries
```

The model explanation must not contain authoritative replacements for:

```text
action

stop / continue

reason_codes

blocking_items

NOT_EVALUATED

not_claimed

evidence references

proof references
```

If the explanation repeats machine-contract content for readability, the schema
must make clear that the repeated text is not authoritative.

## 6. Contradiction Analysis Section

The `contradiction_analysis` section must support fail-closed contradiction
classification.

It must support at least:

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

It must support severity levels such as:

```text
FAIL_CLOSED_CRITICAL

SAFETY_OR_SCOPE_VIOLATION

CONTRACT_CONTRADICTION

REMEDIATION_DETAIL_LOSS

QUALITY_ONLY
```

The section must include a deterministic `fail_closed` result or equivalent
field. Critical contradictions must require fail-closed behavior.

The schema design must ensure contradiction reporting cannot be used by the
model to alter the authoritative machine contract.

## 7. Telemetry Section

The `telemetry` section must be separate from decision content.

It should support:

```text
model identity

harness identity

agent track

session identity

usage telemetry

tool-call telemetry

timing, if measured directly

schema validation status

explanation compliance status

source artifact hashes

runner commit or harness version, where applicable
```

Telemetry must not change:

```text
machine action

stop / continue

reason_codes

blocking_items

NOT_EVALUATED

not_claimed

evidence/proof identity
```

If a telemetry field is unavailable, the schema must represent that explicitly
rather than inventing a value.

## 8. Sensitive-Value Boundary

The schema design must preserve the Domain 3 sensitive-value boundary.

Terraform sensitive values must not be exposed in:

```text
machine_contract

model_explanation

contradiction_analysis

telemetry
```

The schema must support sensitive structural paths or redacted references
without requiring sensitive value materialization.

## 9. Backward Compatibility Requirements

The schema design must preserve compatibility with accepted:

```text
Domain 1 semantics

Domain 2 semantics

Domain 3 semantics

Gate A proof assembly semantics

SPIRA_DECISION_SEMANTICS_V2

action/status enums

NOT_EVALUATED semantics

not_claimed boundary semantics

evidence/proof identity semantics
```

The schema must not require:

```text
Domain 1 rebaseline

Domain 2 oracle change

Domain 3 oracle change

producer semantic change

Gate A refactor

Gate B
```

## 10. Validator Specification Requirements

The authorized validator specification must describe how a future validator
would check at least:

```text
schema validity

required section presence

machine_contract authoritative flag

model_explanation non-authoritative flag

contract hash format

contract identity preservation

explicit-list preservation

NOT_EVALUATED preservation

not_claimed preservation

evidence/proof reference shape

contradiction class enum validity

fail_closed consistency

telemetry separation from decision content

sensitive-value absence

unknown / unavailable telemetry representation
```

The validator specification may define expected result categories such as:

```text
PASS

FAIL

TOOL_ERROR
```

But validator implementation is not authorized.

## 11. Required Design Questions

The schema draft and validator specification must answer:

```text
1. Is machine_contract embedded in full or bound by hash/reference?

2. How is equality to the source contract proven?

3. Is model_explanation text-only or structured?

4. Which contradiction classes are critical fail-closed gates?

5. How is contradiction represented without giving the model authority
   over the machine result?

6. Which fields are required and which are nullable?

7. How is backward compatibility with Domain 1, Domain 2, Domain 3,
   and Gate A preserved?

8. How are Terraform sensitive values excluded?

9. Which schema version and decision semantics version are locked?

10. What will the future validator check?
```

## 12. Frozen Boundaries

The following remain frozen:

```text
Domain 1 behavior and baseline history

Domain 2 corpus, oracle, validator, and producer semantics

Domain 3 corpus, oracle, validator, and producer semantics

Gate A proof assembly semantics

SPIRA_DECISION_SEMANTICS_V2

action/status enums

old Claude results

old Codex results

old benchmark artifacts
```

## 13. Explicit Non-Authorization

This document does not authorize:

```text
schema validator implementation

MVP implementation

changes to mvp_unified.py

runner changes

prompt changes

comparator changes

oracle changes

producer changes

fixture materialization

new Claude sessions

new Codex sessions

DeepSeek sessions

readiness

primary benchmark

holdout

carryover

result reclassification

efficiency claim

merge to main

release

version bump

tag

PyPI publication
```

## 14. Completion Gates

The authorized schema design phase completes only if:

```text
schema draft exists

validator specification exists

schema review exists

review accepts, rejects, or requests revision

no implementation occurred

no fixtures were materialized

no live sessions occurred

old results were preserved
```

## 15. Terminal Verdict Options For Schema Review

The schema review should end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_NEEDS_REVISION

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_REJECTED
```

Even `ACCEPTED` does not authorize implementation.

## Final Boundary

This authorization opens only:

```text
versioned envelope schema design

validator specification design

schema review
```

It does not open:

```text
implementation

fixtures

readiness

live benchmark

release
```
