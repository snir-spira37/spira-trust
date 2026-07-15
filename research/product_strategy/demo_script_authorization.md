# SPIRA Agent Action Gate Demo Script Authorization

## Status

```text
DEMO_SCRIPT_AUTHORIZATION_PROPOSED
AUTHORIZATION_METHOD_BOUNDARY_ONLY
FINAL_DEMO_SCRIPT_NOT_AUTHORIZED_IN_THIS_ROUND
DEMO_IMPLEMENTATION_NOT_AUTHORIZED
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

current_required_step:
DEMO_SCRIPT_AUTHORIZATION_REQUIRED
```

This document authorizes only the scope, methodology, fixture boundaries, reproducibility requirements, and review gates for a future SPIRA Agent Action Gate demo script.

It does not authorize writing the final demo script, implementing a demo, changing product behavior, changing schemas, expanding domains, performing outreach, or releasing anything.

## Authoritative Positioning

The future demo script must use the accepted positioning:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

The following boundary must appear near the positioning:

```text
SPIRA currently evaluates supported artifact-backed evidence.
SPIRA does not replace agent identity, IAM, arbitrary action authorization,
MCP gateways, arbitrary tool-call enforcement, API/database runtime
enforcement, or general agent monitoring.
```

## Authorized Demo Domain

The only authorized demo domain is:

```text
Domain 3 - Terraform plan evidence
```

The authorized demo flow is:

```text
Terraform plan JSON
-> existing Domain 3 raw adapter
-> typed Terraform evidence
-> existing formal core
-> existing machine-readable result contract
-> bounded model explanation with no decision authority
```

The demo may describe an AI-assisted software workflow that proposes or prepares `terraform apply`.

The demo must not claim that SPIRA itself intercepts Terraform, executes Terraform, performs MCP interception, or enforces a live agent runtime. It may show a conceptual integration boundary only if clearly labeled:

```text
CONCEPTUAL INTEGRATION BOUNDARY
```

## Authorized Input Type

The authorized input is:

```text
existing Terraform plan JSON fixture or reproducible generated Terraform plan JSON
```

The final demo script must identify the exact input path.

It must not use:

```text
backup evidence
restore evidence
approval records
database action evidence
API action evidence
MCP gateway events
agent authorization tokens
runtime interception logs
```

## Authorized Result Actions

The future script may demonstrate only these actions, and only when backed by existing implementation or fixtures:

```text
STOP_BLOCKED
REPORT_NOT_EVALUATED
RERUN_REQUIRED
```

No other action name may appear unless verified against existing code and schema in a separate accepted review.

## Authorized Demo Paths

### Path A - Blocked Resource Or Effective Change

Use an existing Domain 3 fixture or reproducible generated plan where a Terraform resource/effective change is classified as blocking under the accepted Domain 3 contract.

Representative accepted fixture:

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
```

Expected result:

```text
action: STOP_BLOCKED
reason_codes: TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE
blocking_items: resource change requires review
```

The final demo script must not assume these values apply to all fixtures. It must bind them to the exact fixture or generated result being shown.

### Path B - Valid But Not Sufficiently Evaluated Evidence

Use an existing Domain 3 fixture or reproducible generated plan where the input is structurally valid or recognized but the accepted contract returns:

```text
REPORT_NOT_EVALUATED
```

Representative accepted fixtures include:

```text
research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json
research/formal_core/domain3/raw_adapter_fixtures/unsupported_format/unsupported_format_01.json
research/formal_core/domain3/raw_adapter_fixtures/unknown_path/unknown_path_01.json
research/formal_core/domain3/raw_adapter_fixtures/sensitive_path/sensitive_path_01.json
```

The final demo script must identify the exact fixture and result state used. It must not invent a generic "missing evidence" scenario unless the existing implementation produces that state for the selected fixture.

### Path C - Invalid Or Malformed Input

Use an existing Domain 3 fixture or reproducible generated plan where malformed or invalid Terraform JSON returns:

```text
RERUN_REQUIRED
```

Representative accepted fixture:

```text
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
```

Expected result:

```text
action: RERUN_REQUIRED
reason_codes: TERRAFORM_PLAN_JSON_INVALID
not_evaluated: Terraform plan JSON parse failed
```

The final demo script must not present invalid JSON as `REPORT_NOT_EVALUATED`.

## Model Authority Boundary

The future demo must show explicitly:

```text
The model may:
- explain the machine contract
- summarize blocking items
- identify missing or invalid evidence
- suggest the next evidence-producing step

The model may not:
- decide the action independently
- override STOP_BLOCKED
- convert REPORT_NOT_EVALUATED into permission
- convert RERUN_REQUIRED into permission
- invent evidence
- remove blocking items
- claim that the action is safe
- claim that SPIRA executed or intercepted the action unless that is actually implemented
```

Model output must be labeled as:

```text
EXPLANATION_ONLY
```

## Authorized Demo Artifacts

The future demo may use only:

```text
existing Terraform plan JSON fixture or reproducible generated plan
existing machine-readable Domain 3 result
existing evidence output
existing reason_codes
existing blocking_items
existing not_evaluated
existing not_claimed
existing evidence_refs
existing proof_refs where present
bounded natural-language explanation derived from the existing result
```

The future demo must not invent:

```text
new audit schema
agent authorization token
MCP gateway event
runtime interception log
policy approval record
backup/restore evidence
human approval artifact
database transaction evidence
```

## Required Labeling

Every demo section must be labeled as one of:

```text
CURRENT IMPLEMENTATION
CONCEPTUAL INTEGRATION BOUNDARY
ROADMAP ONLY
```

These labels must not be mixed.

## Reproducibility Requirements

The final demo script must include:

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
statement that no hidden manual edits are used
statement when output is pre-generated rather than live
```

The script must be reproducible by a technical reviewer from the repository.

## Required Future Demo Script Structure

The future final demo script must include:

```text
1. Problem statement
2. Policy versus evidence distinction
3. Current capability boundary
4. Agent-assisted Terraform scenario
5. Exact input artifact
6. SPIRA evaluation command
7. Machine-readable result
8. Model explanation with no authority
9. Blocked / not-evaluated / rerun distinction
10. Evidence output
11. What SPIRA did
12. What SPIRA did not do
13. Reproduction instructions
14. Roadmap boundary
15. Closing positioning sentence
```

## Forbidden Demo Claims

The future demo script must not say or imply:

```text
SPIRA governs every AI-agent action
SPIRA is the only pre-action gate
SPIRA is unique in Terraform gating
SPIRA replaces OPA, Sentinel, HCP Terraform or Spacelift
SPIRA replaces APort/OAP or Microsoft AGT
SPIRA intercepts arbitrary MCP calls
SPIRA performs agent identity or IAM
SPIRA formally proves the Terraform parser
SPIRA guarantees infrastructure safety
SPIRA independently authorizes production deployment
SPIRA supports backup/restore/approval evidence today
SPIRA is externally certified unless a corresponding accepted result exists
```

## Competitor Mapping Boundaries Preserved

The future demo must reflect the accepted competitor mapping:

```text
SPIRA is not positioned as the only pre-action gate.
SPIRA is not positioned as uniquely capable of Terraform plan gating.
```

The authorized demonstration is narrower:

```text
artifact-backed evidence
-> typed evidence
-> deterministic machine contract
-> explicit non-evaluation and not-claimed boundaries
-> model cannot override
```

## Required Future Outputs

This authorization, if accepted, allows a later round to create:

```text
research/product_strategy/terraform_agent_action_gate_demo_script.md
research/product_strategy/terraform_agent_action_gate_demo_script_results.json
research/product_strategy/terraform_agent_action_gate_demo_script_review.md
research/product_strategy/terraform_agent_action_gate_demo_script_review_results.json
```

No final demo script is authorized in this round.

## Review Requirements

This authorization must receive a separate review.

Required review outputs:

```text
research/product_strategy/demo_script_authorization_review.md
research/product_strategy/demo_script_authorization_review_results.json
```

Allowed review verdicts:

```text
DEMO_SCRIPT_AUTHORIZATION_ACCEPTED
DEMO_SCRIPT_AUTHORIZATION_NEEDS_REVISION
DEMO_SCRIPT_AUTHORIZATION_REJECTED_SCOPE_OVERREACH
```

## Final Status

```text
DEMO_SCRIPT_AUTHORIZATION_PROPOSED
DOMAIN_3_ONLY
TERRAFORM_PLAN_JSON_ONLY
EXISTING_SCHEMA_ONLY
EXISTING_FIXTURES_OR_REPRODUCIBLE_GENERATED_PLAN_ONLY
NO_DEMO_SCRIPT_CREATED
NO_DEMO_IMPLEMENTATION
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_OUTREACH
NO_RELEASE
```
