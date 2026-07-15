# SPIRA Agent Action Gate Demo Script Authorization Review

## Status

```text
DEMO_SCRIPT_AUTHORIZATION_ACCEPTED
AUTHORIZATION_AND_BOUNDARY_REVIEW_ONLY
FINAL_DEMO_SCRIPT_NOT_CREATED
NO_DEMO_IMPLEMENTATION
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_OUTREACH
NO_RELEASE
```

## Document Reviewed

```text
research/product_strategy/demo_script_authorization.md
```

## Authoritative Starting Point

```text
positioning_commit:
da2e99d35e029f0d231e98a517ef87fe9528dde6

competitor_mapping_authorization_commit:
fe9047488438b40d0a0adf592123c7074acc38a7

competitor_mapping_execution_commit:
45fe70b40c45601510559cda25dd05f533c21cf8

accepted_gates:
POSITIONING_ACCEPTED
COMPETITOR_MAPPING_AUTHORIZATION_ACCEPTED
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
```

## Review Objective

This review determines whether the demo-script authorization safely permits a future public/technical SPIRA Agent Action Gate demo script without expanding current product capability.

This review does not create the final demo script and does not implement a demo.

## Authorized Demo Scope

The authorization correctly limits the future demo to:

```text
Domain 3 - Terraform plan evidence
Terraform plan JSON
existing Domain 3 raw adapter
typed Terraform evidence
existing formal core
existing machine-readable result contract
bounded model explanation with no decision authority
```

The authorization does not allow backup, restore, approval, database, API, MCP gateway, agent identity, IAM, or arbitrary tool-call evidence.

## Authorized Result Paths

The authorization correctly separates:

```text
Path A:
blocked resource/effective change -> STOP_BLOCKED

Path B:
valid/recognized but insufficiently evaluated evidence -> REPORT_NOT_EVALUATED

Path C:
malformed or invalid Terraform JSON -> RERUN_REQUIRED
```

Representative fixtures exist:

```text
STOP_BLOCKED:
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json

REPORT_NOT_EVALUATED:
research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json

RERUN_REQUIRED:
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
```

The authorization requires the future script to bind values to the exact fixture or generated result used.

## Model Authority Boundary

The authorization preserves:

```text
model may explain
model may summarize blockers
model may identify missing or invalid evidence
model may suggest the next evidence-producing step
model may not decide
model may not override
model may not upgrade STOP_BLOCKED, REPORT_NOT_EVALUATED or RERUN_REQUIRED into permission
model may not invent evidence
```

The model explanation must be labeled:

```text
EXPLANATION_ONLY
```

## Product Boundary

The authorization requires each demo section to be labeled as:

```text
CURRENT IMPLEMENTATION
CONCEPTUAL INTEGRATION BOUNDARY
ROADMAP ONLY
```

This prevents a conceptual orchestration diagram from becoming a current product claim.

## Reproducibility Gate

The authorization requires the future demo script to include:

```text
exact fixture or input path
exact command
expected exit code
expected result artifact path
expected action
expected reason code
expected blocking item or evaluation state
toolchain requirements
failure behavior
no hidden manual edits
disclosure if output is pre-generated rather than live
```

This is sufficient to force the future demo script to be technically reproducible from the repository.

## Forbidden Claims

The authorization explicitly forbids claims that SPIRA:

```text
governs every AI-agent action
is the only pre-action gate
is unique in Terraform gating
replaces OPA, Sentinel, HCP Terraform or Spacelift
replaces APort/OAP or Microsoft AGT
intercepts arbitrary MCP calls
performs agent identity or IAM
formally proves the Terraform parser
guarantees infrastructure safety
independently authorizes production deployment
supports backup/restore/approval evidence today
is externally certified without an accepted result
```

This preserves the competitor mapping conclusions.

## Findings By Severity

### Critical

None.

### High

None.

### Medium

None.

### Low

None.

## Acceptance Conditions

```text
Domain 3 only: PASS
Terraform plan JSON only: PASS
existing schema only: PASS
existing fixtures or reproducible generated plan only: PASS
no invented artifact: PASS
no runtime interception claim: PASS
no arbitrary tool-call claim: PASS
no MCP/API/database/backup/approval claim: PASS
model explanation separated from decision authority: PASS
STOP_BLOCKED / REPORT_NOT_EVALUATED / RERUN_REQUIRED separated: PASS
exact fixtures and commands required for final script: PASS
current / conceptual / roadmap labels required: PASS
competitor mapping boundaries preserved: PASS
no outreach: PASS
no pitch: PASS
no demo implementation: PASS
no product change: PASS
no release: PASS
```

## Verdict

```text
DEMO_SCRIPT_AUTHORIZATION_ACCEPTED
```

The authorization is accepted as a boundary and methodology document for a future SPIRA Agent Action Gate demo script.

It does not authorize writing the final demo script in this round.

## Next Authorized Step

```text
DEMO_SCRIPT_EXECUTION_REQUIRED
```
