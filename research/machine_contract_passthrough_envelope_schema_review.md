# Machine Contract Passthrough Envelope Schema Review

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_ACCEPTED

MACHINE_EXPLANATION_ENVELOPE_SCHEMA_V1_ACCEPTED

VALIDATOR_SPECIFICATION_ACCEPTED

EMBEDDED_AND_HASH_BOUND_MACHINE_CONTRACT_ACCEPTED

CANONICAL_JSON_EQUALITY_REQUIRED

AUTHORITATIVE_MACHINE_CONTRACT_SECTION_ACCEPTED

NON_AUTHORITATIVE_MODEL_EXPLANATION_SECTION_ACCEPTED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_SECTION_ACCEPTED

SEPARATE_TELEMETRY_SECTION_ACCEPTED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_PRESERVED

OLD_CLAUDE_AND_CODEX_RESULTS_PRESERVED

IMPLEMENTATION_NOT_AUTHORIZED

VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED

FIXTURE_MATERIALIZATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review evaluates:

```text
research/machine_contract_passthrough_envelope_schema_v1.schema.json

research/machine_contract_passthrough_envelope_validator_spec.md
```

It does not authorize implementation, fixtures, readiness, primary benchmark
execution, or release.

## Schema Structure Review

Accepted.

The schema defines the required top-level sections:

```text
machine_contract

model_explanation

contradiction_analysis

telemetry
```

The trust boundary is explicit:

```text
machine_contract.authoritative == true

machine_contract.model_writable == false

model_explanation.authoritative == false

contradiction_analysis.model_writable == false

telemetry.decision_authority == NONE
```

## Machine Contract Design Review

Accepted.

The schema chooses:

```text
representation:
EMBEDDED_AND_HASH_BOUND

canonicalization:
CANONICAL_JSON
```

This is the correct design for the MVP boundary. It keeps the product local and
self-contained while still requiring hash-bound equality to the source contract.

The schema requires:

```text
source_contract_sha256

canonical_contract_sha256

embedded_contract

contract schema/version

decision semantics version

domain

action

stop

reason_codes

blocking_items

not_evaluated

not_claimed

evidence/proof references

producer identity
```

The future validator must prove equality; the schema correctly establishes the
shape and required fields.

## Model Explanation Design Review

Accepted.

The schema marks the model explanation as:

```text
authoritative: false
model_produced: true
```

It supports both:

```text
TEXT_ONLY
STRUCTURED_TEXT
```

This is sufficient for V1 because the product boundary requires explanation
separation, not a final natural-language quality rubric.

The schema correctly avoids making explanation fields authoritative.

## Contradiction Analysis Design Review

Accepted.

The schema includes the accepted contradiction taxonomy and severity levels.

It also ensures critical or safety/scope contradictions require:

```text
fail_closed_required: true
```

The validator specification adds the necessary semantic requirement:

```text
contradiction_analysis.fail_closed is true when any critical contradiction is present
```

The schema and spec together satisfy the fail-closed design requirement.

## Telemetry Design Review

Accepted.

Telemetry is separated from decision content.

The schema requires:

```text
usage.status

tools.status

timing.status
```

with:

```text
AVAILABLE
NOT_EXPOSED
NOT_EVALUATED
```

This prevents missing telemetry from being interpreted as zero. The validator
specification correctly requires numeric values only when the corresponding
status is `AVAILABLE`.

## Sensitive-Value Boundary Review

Accepted.

The schema requires:

```text
sensitive_values_excluded: true
sensitive_structural_paths_allowed: true
redacted_references_allowed: true
```

The validator specification requires sensitive-value absence across all
sections:

```text
machine_contract
model_explanation
contradiction_analysis
telemetry
```

This preserves the Domain 3 Terraform sensitive-value boundary.

## Backward Compatibility Review

Accepted.

The schema and validator specification do not require:

```text
Domain 1 rebaseline

Domain 2 oracle change

Domain 3 oracle change

producer semantic change

Gate A refactor

Gate B
```

They preserve:

```text
Domain 1 semantics
Domain 2 semantics
Domain 3 semantics
Gate A semantics
SPIRA_DECISION_SEMANTICS_V2
action/status enums
NOT_EVALUATED semantics
not_claimed boundary semantics
evidence/proof identity semantics
```

## Validator Specification Review

Accepted.

The validator specification covers:

```text
schema validity

authority boundary checks

canonical hash recomputation

explicit field preservation

decision semantics checks

contradiction analysis checks

explanation compliance checks

telemetry checks

sensitive-value checks

backward compatibility checks
```

It properly defines:

```text
PASS
FAIL
TOOL_ERROR
```

and keeps validator implementation blocked.

## Review Questions Answered

```text
1. Is machine_contract embedded in full or bound by hash/reference?
   -> Both embedded and hash-bound.

2. How is equality to the source contract proven?
   -> Canonical JSON equality plus hash recomputation.

3. Is model_explanation text-only or structured?
   -> V1 supports TEXT_ONLY and STRUCTURED_TEXT.

4. Which contradiction classes are critical fail-closed gates?
   -> Classes with FAIL_CLOSED_CRITICAL or SAFETY_OR_SCOPE_VIOLATION severity.

5. How is contradiction represented without giving the model authority
   over the machine result?
   -> contradiction_analysis is not authoritative for the machine contract,
      is not model-writable, and cannot alter machine_contract.

6. Which fields are required and which are nullable?
   -> Required fields are defined by JSON Schema. Unavailable telemetry uses
      explicit status values rather than ambiguous nulls.

7. How is backward compatibility preserved?
   -> Existing domain semantics, Gate A, decision semantics, and action/status
      enums remain frozen.

8. How are Terraform sensitive values excluded?
   -> Sensitive values are excluded by policy and checked by future validator;
      only structural paths or redacted references are permitted.

9. Which schema version and decision semantics version are locked?
   -> schema_version 1 and SPIRA_DECISION_SEMANTICS_V2.

10. What will the future validator check?
    -> The validator specification enumerates structural, semantic, hash,
       contradiction, telemetry, and sensitive-value checks.
```

## Historical Results Preservation

Accepted.

The schema review does not reclassify:

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

## Final Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_ACCEPTED

MACHINE_EXPLANATION_ENVELOPE_SCHEMA_V1_ACCEPTED

VALIDATOR_SPECIFICATION_ACCEPTED

EMBEDDED_AND_HASH_BOUND_MACHINE_CONTRACT_ACCEPTED

CANONICAL_JSON_EQUALITY_REQUIRED

AUTHORITATIVE_MACHINE_CONTRACT_SECTION_ACCEPTED

NON_AUTHORITATIVE_MODEL_EXPLANATION_SECTION_ACCEPTED

FAIL_CLOSED_CONTRADICTION_ANALYSIS_SECTION_ACCEPTED

SEPARATE_TELEMETRY_SECTION_ACCEPTED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_PRESERVED

OLD_CLAUDE_AND_CODEX_RESULTS_PRESERVED

IMPLEMENTATION_NOT_AUTHORIZED

VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED

FIXTURE_MATERIALIZATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

RELEASE_NOT_AUTHORIZED
```

## Next Artifact

The next artifact should be:

```text
research/machine_contract_passthrough_contradiction_fixture_authorization.md
```

It should authorize only the design/materialization of contradiction fixtures
for the accepted envelope and policy. It must not authorize MVP implementation
or live sessions.
