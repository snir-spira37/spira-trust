# SPIRA Agent Action Gate Positioning Review

## Status

```text
POSITIONING_ACCEPTED
DOCUMENTATION_ONLY
NO_PRODUCT_BEHAVIOR_CHANGE
NO_SCHEMA_CHANGE
NO_FORMAL_CORE_CHANGE
NO_DOMAIN_EXPANSION
NO_COMPETITOR_MAPPING
NO_OUTREACH
NO_RELEASE
```

## Document Reviewed

```text
research/product_strategy/spira_agent_action_gate_positioning.md
```

## Review Objective

This review determines whether the positioning document accurately represents the current SPIRA product boundary and implementation, and whether it can serve as the accepted basis for future competitor mapping and messaging.

This was a review-only pass. No product code, schema, formal core, adapter, producer, benchmark, release, or domain behavior was changed.

## Implementation Sources Checked

```text
source/spira_core/formal_core_v1.py
source/spira_core/terraform_plan_producer.py
formal/spira_formal_core_v1/SpiraFormalCore/Contract.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain3/Decision.lean
tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

## Fixture And Schema Sources Checked

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_fixture_manifest.json
```

The review checked the Python contract shape, the Lean `MachineContract` shape, the Domain 3 formal action semantics, the raw-adapter conformance mapping, and representative accepted fixtures.

## Findings By Severity

### Critical

None.

### High

None.

### Medium

None.

### Low

One wording issue was corrected before acceptance: the Domain 3 demonstration used generic "audit artifact" wording. That could be read as inventing a new demo-specific audit schema. The document now says the demo must use an existing accepted machine-readable result artifact or evidence output, and must not invent a new audit schema for presentation.

## Current-Domain Boundary

The document accurately limits current capability to:

```text
Domain 1: package artifacts
Domain 2: test evidence
Domain 3: Terraform plan evidence
```

It explicitly does not claim current support for:

```text
arbitrary tool calls
arbitrary MCP actions
arbitrary database actions
arbitrary API actions
backup / restore evidence
approval evidence
universal agent governance
```

Roadmap items are marked as future adapters, not current product capability.

## Domain 3 Demo Integrity

The authoritative demo path is valid:

```text
Terraform plan JSON
-> Domain 3 adapter
-> typed Terraform evidence
-> machine contract
-> STOP_BLOCKED or REPORT_NOT_EVALUATED
-> existing machine-readable result artifact + bounded explanation
```

The document correctly distinguishes malformed JSON:

```text
malformed Terraform plan JSON -> RERUN_REQUIRED
```

The representative blocked contract values were verified against the accepted Domain 3 raw-adapter fixture:

```text
action: STOP_BLOCKED
stop: true
reason_codes: TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE
blocking_items: resource change requires review
not_evaluated: []
not_claimed:
  APPLY_SUCCESS
  INFRASTRUCTURE_COMPLIANCE
  INFRASTRUCTURE_CORRECTNESS
  INFRASTRUCTURE_COST
  INFRASTRUCTURE_SECURITY
  LIVE_STATE_FRESHNESS
evidence_refs:
  plan.json:create_update_delete_01
  manifest:create_update_delete_01
proof_refs:
  domain3_raw_adapter_fixture:create_update_delete_01
```

No invented action name, reason code, contract field, evidence reference pattern, proof reference pattern, CLI output, or unbuilt adapter is required by the demo.

## Action Semantics

The positioning document preserves the implementation semantics:

```text
effective Terraform resource change -> STOP_BLOCKED
valid but insufficient / incomplete / unsupported evidence -> REPORT_NOT_EVALUATED
malformed Terraform plan JSON -> RERUN_REQUIRED
```

The document does not collapse `REPORT_NOT_EVALUATED` into approval and does not treat `RERUN_REQUIRED` as a generic non-evaluated result.

## Policy And SPIRA Boundary

The core positioning statement is accepted:

```text
Policy says what an agent is allowed to do.
SPIRA checks whether the supported evidence justifies doing it now.
```

The document does not claim that SPIRA replaces IAM, authorization, agent identity, tool scoping, runtime policy enforcement, or organizational allowlists.

## Model Authority Boundary

The document preserves the accepted authority split:

```text
model may explain
model may summarize
model may identify missing evidence
model may not decide
model may not override
model may not upgrade blocked or non-evaluated evidence
model may not invent evidence
```

This is consistent with the accepted passthrough architecture: the model explanation is downstream of the machine contract and has no decision authority.

## Formal And Parser Boundaries

The document does not overclaim:

```text
formally proven Terraform parser: not claimed
universal safe agent action: not claimed
all agent actions governed: not claimed
production approval: not claimed
full end-to-end formal proof: not claimed
```

It correctly separates formal-core claims, adapter conformance, parser correctness, upstream artifact correctness, production readiness, and release approval.

## Claim Classification

```text
Artifact-backed evidence gate:
  positioning interpretation supported by current implementation and accepted evidence

Package / test / Terraform current domains:
  directly supported by current implementation and accepted evidence

Policy versus SPIRA distinction:
  positioning interpretation consistent with implementation boundaries

Model non-authority:
  supported by accepted passthrough and formal-core evidence

Domain 3 Terraform demo:
  directly supported by existing implementation and fixtures

Backup / restore / approval / database / API / MCP:
  roadmap or not claimed

Universal agent governance:
  not claimed

Formal parser correctness:
  not claimed

Production release readiness:
  not claimed
```

## Verification

```text
git diff --check
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
```

Both checks passed.

## Verdict

```text
POSITIONING_ACCEPTED
```

The positioning document is accurate enough to become the authoritative current-capability positioning baseline for SPIRA Agent Action Gate messaging.

This acceptance does not authorize competitor mapping, outreach, demo implementation, release, domain expansion, product behavior changes, schema changes, formal-core changes, or new action adapters.

## Next Step

```text
COMPETITOR_MAPPING_AUTHORIZATION_REQUIRED
```
