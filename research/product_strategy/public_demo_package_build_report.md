# Public Demo Package Build Report

## Status

```text
PUBLIC_DEMO_PACKAGE_ACCEPTED
```

## Scope

The build created a Domain 3 Terraform Plan public demo package only. It did not change product code, formal core code, schemas, adapters, producers, fixtures, action semantics, or release state.

## Package

```text
package root: research/product_strategy/public_demo_package
zip filename: spira_terraform_agent_action_gate_public_demo_19c0e99.zip
zip sha256: 0ba107aa2b6acef99ad9519f2e68b438b0452606306b001eb357a953a89a06cb
fixture packaging mode: copied_byte_for_byte_with_source_hash_provenance
upload note: sidecar file outside ZIP payload to avoid self-referential ZIP hash
```

## Included Demo Paths

- `STOP_BLOCKED` from `create_update_delete_01`
- `REPORT_NOT_EVALUATED` from `incomplete_plan_01`
- `RERUN_REQUIRED` from `invalid_json_01`

## Verification Summary

```text
authorized fixtures only: True
authorized actions only: True
authorized reason codes only: True
fixture hashes match source: True
semantic build repeatability: True
zip byte reproducibility: True
demo paths verified: True
conformance passed: True
focused pytest passed: True
full pytest passed: True
package smoke tests passed: True
JSON validation passed: True
Lean reproduction status: NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## Boundaries

The package preserves the positioning boundary:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

It does not claim arbitrary tool-call, MCP, API, database, backup/restore, approval-evidence, runtime-interception, release, or production-final capability.

## Blockers

```json
[]
```

## Next Step

```text
COLD_PUBLIC_DEMO_REVIEW_REQUIRED
```
