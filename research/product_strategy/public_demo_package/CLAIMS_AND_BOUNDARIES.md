# Claims And Boundaries

## FORMALLY_PROVED_IN_LEAN

SPIRA Formal Core V1 contains Lean proofs for bounded decision properties inside the formal model:

- bounded formal decision properties
- blockers do not become `PROCEED` within the formal model
- required non-evaluation does not become `PROCEED`
- machine action is not controlled by model explanation
- explicit contract fields are preserved according to the formal theorem statements

This package does not claim end-to-end proof of Terraform parsing, all adapters, Python runtime behavior, operating-system behavior, or all production integrations.

## EMPIRICALLY_REPRODUCED

- Three Domain 3 Terraform Plan paths
- Two semantically matching reproduction runs
- Invalid JSON did not receive a soft PASS
- Domain 3 conformance PASS
- Focused tests PASS
- Full pytest 270 passed
- Package integrity PASS

## CONFORMANCE_VALIDATED

- Domain 3 raw adapter alignment
- Existing fixtures and expected results
- Action and reason-code fidelity

## CURRENT IMPLEMENTATION

- Terraform plan JSON evaluation
- Domain 3 adapter
- typed evidence
- machine-readable contract
- existing result fields
- model explanation-only boundary

## CONCEPTUAL INTEGRATION BOUNDARY

- CI/CD or an authorized workflow consumes the result
- The external system stops or proceeds based on the result
- SPIRA is not claimed as a universal runtime interceptor

## ROADMAP ONLY

- arbitrary tool calls
- general MCP enforcement
- API/database action adapters
- backup/restore evidence
- approval evidence
- universal agent governance
- unified public action-gate CLI, unless implemented and authorized later

## NOT_EVALUATED_IN_THIS_ENVIRONMENT

Demo reproduction:

```text
DEMO_REPRODUCTION_ACCEPTED
```

Formal package Lean reproduction in the accepted demo environment:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## NOT_CLAIMED

- universal Terraform safety
- formal proof of Terraform parser
- formal proof of all adapters
- full end-to-end mathematical safety
- production-final status
- independent certification
- uniqueness as a Terraform gate
- replacement for OPA, Sentinel, HCP Terraform, Spacelift, IAM or MCP gateways
- arbitrary tool-call authorization
- arbitrary MCP action authorization
- arbitrary database/API operation authorization
- runtime interception of universal agent actions
