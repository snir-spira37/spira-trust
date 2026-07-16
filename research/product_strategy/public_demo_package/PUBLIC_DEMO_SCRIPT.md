# Public Demo Script - Terraform Agent Action Gate

## Status

```text
PUBLIC_DEMO_PACKAGE_REFERENCE_SCRIPT
DOMAIN_3_ONLY
NO_FAKE_AGENT_RUNTIME
NO_INVENTED_CLI
RECORDED_REFERENCE_OUTPUTS_ARE_LABELED
```

## 90 To 120 Second Version

### 1. Opening Problem

An AI-assisted workflow may be allowed by policy to propose `terraform apply`. But permission to propose an action is not evidence that this specific Terraform plan is safe or justified now.

```text
Policy question:
May this workflow propose terraform apply?

Evidence question:
Does this supported Terraform plan justify doing it now?
```

### 2. Policy Versus Evidence

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.

```text
Terraform plan JSON
-> Domain 3 adapter
-> typed evidence
-> deterministic machine contract
```

### 3. Current Capability

This demo uses existing Domain 3 Terraform Plan fixtures and the existing Domain 3 research/conformance harness. It does not introduce backup evidence, restore evidence, approval evidence, arbitrary API enforcement, MCP enforcement, or a new agent runtime.

### 4. Terraform Plan Input

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
```

Fixture SHA256:

```text
49c622e62c5255b3ec05214640fd679a89228b83ee1bb10a7ce01e258d37adbe
```

### 5. Actual Existing Command

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

There is no invented `spira evaluate ...` command in this demo.

### 6. Machine-Readable Result

The existing harness verifies the expected machine contract for the selected fixtures. For `create_update_delete_01`, the expected result is:

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

### 7. STOP_BLOCKED Explanation

The resource change is not converted into a silent continue. The machine contract says `STOP_BLOCKED` and records the blocker:

```text
resource change requires review
```

### 8. Model Marked EXPLANATION_ONLY

The model may explain the contract, but it does not decide, override, or upgrade the machine action. The machine contract is the authoritative decision artifact.

### 9. Conceptual External Enforcement Boundary

A CI/CD system or authorized workflow can consume the machine-readable result and decide whether to stop or proceed. This demo does not claim universal runtime interception.

### 10. Closing Statement

SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions. It does not replace policy; it answers whether the supported evidence justifies doing the action now.
