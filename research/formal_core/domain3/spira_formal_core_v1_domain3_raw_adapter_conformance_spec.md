# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Specification

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_SPEC_PROPOSED
SPECIFICATION_ONLY
RAW_TERRAFORM_JSON_PARSER_PROOF_NOT_CLAIMED
```

## 1. Purpose

This specification defines the next deterministic adapter boundary:

```text
raw Terraform Plan evidence
-> Domain 3 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

It does not implement or prove the adapter. It defines what a later implementation and conformance phase must prove or test.

## 2. In-Scope Raw Inputs

Domain 3 raw adapter conformance is limited to bounded Terraform Plan fixture evidence:

```text
plan.json
plan.json.invalid
main.tf when present as optional provenance
manifest-declared file hashes
embedded spira_optional_provenance fields
```

Out of scope for this phase:

```text
terraform execution correctness
provider behavior
live cloud state
cost estimation
security/compliance assessment
full Terraform schema proof
arbitrary JSON parser proof
operating-system or filesystem correctness
LLM or agent behavior
```

## 3. Input State Classification

The adapter must classify each raw plan bundle into exactly one top-level input state:

```text
SUPPORTED_NO_CHANGES
SUPPORTED_WITH_EFFECTIVE_CHANGES
PLAN_ERRORED
PLAN_NOT_APPLYABLE
PLAN_INCOMPLETE
FORMAT_UNSUPPORTED
JSON_INVALID
SENSITIVE_OR_UNKNOWN_VALUES_PRESENT
OPTIONAL_PROVENANCE_PRESENT
INTERNAL_ADAPTER_FAILURE
```

### 3.1 Supported No Changes

Required behavior:

```text
action = PROCEED
stop = false
reason_codes includes TERRAFORM_PLAN_NO_CHANGES
blocking_items = []
not_evaluated = []
```

### 3.2 Supported With Effective Changes

Effective changes include create, update, delete, replace, read, and any action sequence other than `[]` or `["no-op"]`.

Required behavior:

```text
action = STOP_BLOCKED
stop = true
reason_codes includes TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE or a more specific accepted reason
blocking_items preserves changed resource/action facts
PROCEED forbidden
```

### 3.3 Plan Errored

Required behavior:

```text
action = STOP_BLOCKED
reason_codes includes TERRAFORM_PLAN_ERRORED
PROCEED forbidden
```

### 3.4 Plan Not Applyable

If `applyable = false` and effective changes exist:

```text
action = STOP_BLOCKED
reason_codes includes TERRAFORM_PLAN_NOT_APPLYABLE
PROCEED forbidden
```

### 3.5 Plan Incomplete

If `complete = false` or required plan structure is absent:

```text
action = REPORT_NOT_EVALUATED
not_evaluated includes the incomplete plan fact
PROCEED forbidden
```

### 3.6 Format Unsupported

If the Terraform `format_version` major version is unsupported:

```text
action = REPORT_NOT_EVALUATED
reason_codes includes TERRAFORM_PLAN_FORMAT_UNSUPPORTED
not_evaluated records unsupported format
PROCEED forbidden
```

### 3.7 JSON Invalid

If the plan JSON cannot be parsed:

```text
action = RERUN_REQUIRED
reason_codes includes TERRAFORM_PLAN_JSON_INVALID
not_evaluated preserves JSON parse failure
PROCEED forbidden
```

### 3.8 Sensitive Or Unknown Values Present

Sensitive and unknown value paths must be preserved as evidence facts.

Required behavior:

```text
unknown_paths preserved
sensitive_paths preserved
not_evaluated includes unknown/sensitive facts when required for the decision
plaintext sensitive values must not appear in public contract fields
```

### 3.9 Optional Provenance Present

Optional provenance states must be represented as claims without turning provenance presence into a claim of infrastructure correctness.

Required behavior:

```text
optional provenance state preserved
not_claimed still includes APPLY_SUCCESS and infrastructure correctness/security/cost/compliance claims
```

### 3.10 Internal Adapter Failure

Required behavior:

```text
fail closed
PROCEED forbidden
error recorded outside the authoritative contract when needed
```

## 4. Required Typed Evidence Fields

The adapter output must be projectable into Formal Core V1 typed evidence with:

```text
domain_id = terraform_plan
subject_id
schema_version
producer_id
evidence_validity
typed_claims
evidence_refs
proof_refs
policy_id
policy_schema_version
policy_required_claims
policy_blocking_rules
policy_not_claimed_rules
```

The adapter must preserve:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
subject identity
context identity
unification identity
resource action lists
replace paths
unknown paths
sensitive paths
optional provenance states
```

## 5. Mapping Obligations

### 5.1 No Changes

If the plan is complete, supported, not errored, applyable, and has no effective resource changes:

```text
action = PROCEED
reason_codes includes TERRAFORM_PLAN_NO_CHANGES
not_claimed preserved
```

### 5.2 Resource Changes

If any effective change exists:

```text
blocking_items or explicit lists preserve changed resources
action = STOP_BLOCKED
PROCEED forbidden
```

### 5.3 Replace Paths

Replace paths must be preserved:

```text
path in raw replace_paths
=>
path in typed evidence / explicit list / machine contract evidence facts
```

### 5.4 Unknown Paths

Unknown values must not become PASS:

```text
unknown path observed
=>
not_evaluated or typed unknown claim preserved
```

### 5.5 Sensitive Paths

Sensitive paths must be preserved without leaking plaintext sensitive values:

```text
sensitive path observed
=>
sensitive path identity preserved
plaintext sensitive value absent from public contract fields
```

### 5.6 Unsupported Or Invalid Format

Unsupported format and invalid JSON must fail closed:

```text
invalid JSON -> RERUN_REQUIRED
unsupported format -> REPORT_NOT_EVALUATED
PROCEED forbidden
```

### 5.7 Not Claimed

The adapter must preserve Domain 3 boundaries:

```text
APPLY_SUCCESS
INFRASTRUCTURE_COMPLIANCE
INFRASTRUCTURE_CORRECTNESS
INFRASTRUCTURE_COST
INFRASTRUCTURE_SECURITY
LIVE_STATE_FRESHNESS
```

These boundaries must not be converted into false negatives or positive claims.

## 6. Fixture Corpus Required Before Implementation

A later fixture authorization should materialize at least:

```text
3 no-change plans
3 create/update/delete plans
3 replace plans with replace_paths
2 errored plans
2 not-applyable plans
2 incomplete plans
2 unsupported format plans
2 invalid JSON plans
3 unknown path plans
3 sensitive path plans
2 optional provenance plans
2 duplicate resource-address plans
2 internal adapter failure simulations
```

Each fixture must include expected:

```text
input_state
typed evidence projection
Formal Core contract
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
resource action lists
replace_paths
unknown_paths
sensitive_paths
```

## 7. Differential Conformance Plan

A later implementation must compare:

```text
existing Terraform Plan producer output
new typed-evidence adapter output
Formal Core V1 Python reference output
accepted Domain 3 conformance corpus
new raw-adapter fixtures
```

Acceptance requires:

```text
no false PROCEED
no resource action list loss
no replace path loss
no unknown path loss
no sensitive path loss
no not_claimed loss
no evidence/proof identity loss
invalid JSON and unsupported formats fail closed
existing accepted Domain 3 conformance still passes
full pytest passes
```

## 8. Claim Boundary

Allowed after this specification:

```text
SPIRA has specified a Domain 3 raw-adapter conformance boundary for mapping bounded Terraform Plan evidence into Formal Core V1 typed evidence.
```

Disallowed:

```text
SPIRA has formally proved raw Terraform JSON parsing.
SPIRA has proved Terraform execution, provider behavior, cloud state, security, compliance, cost, or apply success.
SPIRA is release-ready based on this specification.
```

## 9. Recommended Next Authorization

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That next step should materialize the fixture corpus only. It should still not change the Domain 3 adapter implementation or claim parser proof.
