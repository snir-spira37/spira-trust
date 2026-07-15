# Terraform Agent Action Gate Demo Script

## Document Status

```text
DEMO_SCRIPT_PROPOSED_FOR_REVIEW
DOCUMENTATION_AND_REPRODUCTION_ONLY
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_OUTREACH
NO_RELEASE
```

## Authoritative Commits

```text
positioning_commit:
da2e99d35e029f0d231e98a517ef87fe9528dde6

competitor_mapping_commit:
45fe70b40c45601510559cda25dd05f533c21cf8

demo_authorization_commit:
2ef6f559433f1a2e0bb8c503a4b35af745e8c6a2
```

## Intended Audience

Technical founders, platform engineers, AI-agent infrastructure teams, security engineers, and infrastructure owners evaluating AI-assisted software operations.

## Required Positioning

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

Boundary:

```text
SPIRA evaluates supported artifact-backed evidence.
SPIRA does not currently claim arbitrary tool-call authorization, general MCP interception,
agent identity management, IAM replacement, arbitrary API/database enforcement,
universal runtime governance, or universal infrastructure safety.
```

## Primary Public Demo - 90 To 120 Seconds

### Scene 1 - Opening Problem

**Label:** `CONCEPTUAL INTEGRATION BOUNDARY`

Narration:

> An AI-assisted workflow can be authorized to prepare or propose `terraform apply`.
> But authorization alone does not prove that the current Terraform plan justifies execution.

On screen:

```text
Policy question:
May this workflow propose terraform apply?

Evidence question:
Does this specific Terraform plan justify doing it now?
```

### Scene 2 - Policy Versus Evidence

**Label:** `CURRENT IMPLEMENTATION`

Narration:

> Policy says what an agent is allowed to do.
> SPIRA checks whether supported evidence justifies doing it now.

On screen:

```text
Terraform plan JSON
-> Domain 3 adapter
-> typed evidence
-> deterministic machine contract
```

### Scene 3 - Exact Input Artifact

**Label:** `CURRENT IMPLEMENTATION`

Narration:

> This demo uses an existing Domain 3 fixture from the repository. It is a Terraform plan JSON case with an effective resource change.

Input:

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
```

Fixture SHA256:

```text
49c622e62c5255b3ec05214640fd679a89228b83ee1bb10a7ce01e258d37adbe
```

### Scene 4 - Exact Execution

**Label:** `CURRENT IMPLEMENTATION`

Narration:

> There is no invented `spira evaluate` CLI in this demo. The existing repository command is the Domain 3 raw-adapter conformance harness.

Command:

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

Expected exit code:

```text
0
```

Expected status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
```

### Scene 5 - Machine-Readable Result

**Label:** `CURRENT IMPLEMENTATION`

Narration:

> SPIRA converts the supported Terraform artifact into typed evidence and a machine-readable result contract. For this fixture, the contract blocks automatic proceed.

On screen:

```text
EXCERPT FROM VERIFIED RESULT
```

```json
{
  "action": "STOP_BLOCKED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"
  ],
  "blocking_items": [
    "resource change requires review"
  ],
  "not_evaluated": [],
  "not_claimed": [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS"
  ],
  "evidence_refs": [
    "plan.json:create_update_delete_01",
    "manifest:create_update_delete_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:create_update_delete_01"
  ]
}
```

### Scene 6 - Bounded Explanation

**Label:** `EXPLANATION_ONLY`

Narration:

> The model can explain this contract. It cannot decide or override it.

Model explanation example:

```text
SPIRA evaluated the Terraform plan artifact and found an effective resource
change. Under the accepted Domain 3 contract, that change requires review
before automatic proceed. The result is STOP_BLOCKED. This does not prove
apply success, infrastructure compliance, infrastructure correctness, cost,
security, or live-state freshness.
```

Forbidden model wording:

```text
The change is probably safe, so proceed anyway.
```

### Scene 7 - Enforcement Boundary

**Label:** `CONCEPTUAL INTEGRATION BOUNDARY`

Narration:

> An external authorized workflow can consume this machine contract and stop the next action. This demo does not claim that SPIRA is a universal runtime interceptor or an MCP gateway.

On screen:

```text
SPIRA output:
STOP_BLOCKED

External workflow:
do not continue to apply
```

### Scene 8 - Closing

**Label:** `CURRENT IMPLEMENTATION`

Narration:

> SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions. Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.

## Three-Path Result Table

| Path | Fixture | Action | Stop | Reason Codes | Blocking / Evaluation State |
| --- | --- | --- | --- | --- | --- |
| A | `create_update_delete_01` | `STOP_BLOCKED` | `true` | `TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE` | `resource change requires review` |
| B | `incomplete_plan_01` | `REPORT_NOT_EVALUATED` | `true` | `TERRAFORM_PLAN_INCOMPLETE` | `not_evaluated: terraform plan incomplete` |
| C | `invalid_json_01` | `RERUN_REQUIRED` | `true` | `TERRAFORM_PLAN_JSON_INVALID` | `not_evaluated: Terraform plan JSON parse failed` |

## Technical Reproduction Appendix

### Prerequisites

```text
Python 3.12+
repository checkout
```

### Working Directory

```text
repository root
```

### Exact Command

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

This is an existing repository harness, not a new public product CLI.

### Expected Harness Output

```json
{
  "status": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED",
  "counts": {
    "fixture_count": 31,
    "fixture_hash_mismatch_count": 0,
    "typed_evidence_mismatch_count": 0,
    "contract_mismatch_count": 0,
    "false_proceed_count": 0,
    "blocking_item_loss_count": 0,
    "not_evaluated_loss_count": 0,
    "not_claimed_loss_count": 0,
    "evidence_proof_identity_loss_count": 0
  }
}
```

The command also writes the existing conformance results file:

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
```

The demo-specific verification output for this script is:

```text
research/product_strategy/terraform_agent_action_gate_demo_verified_results.json
```

### Path A - STOP_BLOCKED

Fixture:

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
```

Expected and verified:

```json
{
  "action": "STOP_BLOCKED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"
  ],
  "blocking_items": [
    "resource change requires review"
  ],
  "not_evaluated": [],
  "evidence_refs": [
    "plan.json:create_update_delete_01",
    "manifest:create_update_delete_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:create_update_delete_01"
  ]
}
```

### Path B - REPORT_NOT_EVALUATED

Fixture:

```text
research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json
```

Expected and verified:

```json
{
  "action": "REPORT_NOT_EVALUATED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_PLAN_INCOMPLETE"
  ],
  "blocking_items": [],
  "not_evaluated": [
    "terraform plan incomplete"
  ],
  "evidence_refs": [
    "plan.json:incomplete_plan_01",
    "manifest:incomplete_plan_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:incomplete_plan_01"
  ]
}
```

This is not `PROCEED` because the required claim was not evaluated. It is not `STOP_BLOCKED` because the selected fixture's result state is incomplete evaluation rather than a blocking resource change.

### Path C - RERUN_REQUIRED

Fixture:

```text
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
```

Expected and verified:

```json
{
  "action": "RERUN_REQUIRED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_PLAN_JSON_INVALID"
  ],
  "blocking_items": [],
  "not_evaluated": [
    "Terraform plan JSON parse failed"
  ],
  "evidence_refs": [
    "plan.json:invalid_json_01",
    "manifest:invalid_json_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:invalid_json_01"
  ]
}
```

This is not `REPORT_NOT_EVALUATED`. The input is malformed Terraform plan JSON, so the accepted result is `RERUN_REQUIRED`.

## What SPIRA Did

```text
CURRENT IMPLEMENTATION
```

SPIRA evaluated an existing supported Terraform plan fixture through the accepted Domain 3 evidence path and preserved the resulting machine-readable action contract.

## What SPIRA Did Not Do

```text
CURRENT IMPLEMENTATION
```

SPIRA did not:

```text
execute Terraform
intercept a live agent runtime
intercept MCP calls
perform IAM or identity management
approve production deployment
evaluate backup, restore or approval evidence
evaluate arbitrary API or database actions
claim universal infrastructure safety
prove the Terraform parser correct
```

## Roadmap Boundary

```text
ROADMAP ONLY
```

Future adapters may evaluate backup status, restore tests, approval records, database actions, API actions, or MCP events only after separate domain declarations, fixtures, schemas, validators, conformance evaluation, review, and acceptance.

## Prohibited Claims

This demo script must not be used to claim:

```text
SPIRA governs every AI-agent action.
SPIRA is the only pre-action gate.
SPIRA is unique in Terraform gating.
SPIRA replaces OPA, Sentinel, HCP Terraform, Spacelift, APort/OAP or Microsoft AGT.
SPIRA intercepts arbitrary MCP calls.
SPIRA formally proves the Terraform parser.
SPIRA guarantees infrastructure safety.
SPIRA independently authorizes production deployment.
```

## not_claimed

The demo does not claim:

```text
APPLY_SUCCESS
INFRASTRUCTURE_COMPLIANCE
INFRASTRUCTURE_CORRECTNESS
INFRASTRUCTURE_COST
INFRASTRUCTURE_SECURITY
LIVE_STATE_FRESHNESS
arbitrary tool-call enforcement
general MCP runtime enforcement
backup/restore/approval coverage
database/API action coverage
universal production safety
```

## Final Demo Closing Statement

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.
Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

## Final Status

```text
DEMO_SCRIPT_PROPOSED_FOR_REVIEW
THREE_PATHS_VERIFIED
DOMAIN_3_ONLY
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_OUTREACH
NO_RELEASE
```
