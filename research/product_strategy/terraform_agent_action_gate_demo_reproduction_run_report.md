# Terraform Agent Action Gate Demo Reproduction Run Report

## Document Status

```text
DEMO_REPRODUCTION_RUN_COMPLETE
DEMO_REPRODUCTION_ACCEPTED
REPRODUCTION_AND_VERIFICATION_ONLY
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_RELEASE
NO_OUTREACH
```

## Scope

This run reproduced the accepted Terraform Agent Action Gate demo after the package-integrity revision:

```text
revision_commit:
d731c6e719322cdb2e2c276b0c200eacb26f6e40

previous_failed_reproduction_commit:
03d92b97304f61b77e58b058875a277abb1df4c7
```

The reproduction used the accepted demo script, reproduction manifest, and verified-result artifact:

```text
research/product_strategy/terraform_agent_action_gate_demo_script.md
research/product_strategy/terraform_agent_action_gate_demo_reproduction_manifest.json
research/product_strategy/terraform_agent_action_gate_demo_verified_results.json
```

This was a clean-worktree reproduction, not an external fresh clone.

## Environment

```text
operating_system: Windows-10-10.0.19045-SP0
python_version: 3.12.10
working_directory: repository root
initial_git_status_clean: true
lake_available: false
lean_available: false
```

Formal package Lean reproduction status:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

This is not reported as a Lean PASS.

## Package Integrity Preflight

The external reproduction package passed integrity checks before the demo reproduction:

```text
artifact manifest hash mismatches: 0
missing artifacts: 0
duplicate paths: 0
secret scan hits: 0
forbidden Lean token matches: 0
package smoke tests: PASS
JSON validation: PASS
git diff --check: PASS
```

The Domain 3 generated artifacts remained hash-stable after repeated conformance runs. No runtime-timing hash drift recurred.

## Fixture Verification

The three selected Domain 3 fixtures existed and matched the manifest SHA256 values:

| Path | Fixture | Hash |
| --- | --- | --- |
| STOP_BLOCKED | `create_update_delete_01` | PASS |
| REPORT_NOT_EVALUATED | `incomplete_plan_01` | PASS |
| RERUN_REQUIRED | `invalid_json_01` | PASS |

## Semantic Reproduction

The three demo paths reproduced semantically across two runs:

| Path | Expected Action | Repeatability | Key Check |
| --- | --- | --- | --- |
| A | `STOP_BLOCKED` | PASS | `TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE`, `resource change requires review` |
| B | `REPORT_NOT_EVALUATED` | PASS | `TERRAFORM_PLAN_INCOMPLETE`, `terraform plan incomplete` |
| C | `RERUN_REQUIRED` | PASS | `TERRAFORM_PLAN_JSON_INVALID`, `Terraform plan JSON parse failed` |

The invalid JSON path did not soft-pass and did not return `PROCEED` or `REPORT_NOT_EVALUATED`.

## Commands Run

```powershell
python -m pytest tests/test_formal_core_v1_external_reproduction_package.py
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
python -m pytest tests/test_formal_core_v1_external_reproduction_package.py
python -m pytest
python -m json.tool research/product_strategy/terraform_agent_action_gate_demo_reproduction_manifest.json
python -m json.tool research/product_strategy/terraform_agent_action_gate_demo_verified_results.json
python -m json.tool research/product_strategy/demo_reproduction_revision_results.json
git diff --check
```

## Results

```text
Domain 3 conformance:
PASS twice

focused pytest:
PASS

full pytest:
PASS, 270 passed

package smoke tests:
PASS

package integrity:
PASS

JSON validation:
PASS

git diff --check:
PASS
```

## Documentation Check

The demo script matched the reproduced commands, fixtures, action names, reason codes, blockers, `not_evaluated` values, output paths, and labels.

The script mentions `spira evaluate` only to say that no such invented CLI is used in this demo. No fake agent runtime, MCP/API/database gate, runtime interception, release, or outreach claim was introduced.

## Demo Reproduction Result

```text
DEMO_REPRODUCTION_ACCEPTED
```

## Formal Package Lean Reproduction Status

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## Next Step

```text
PUBLIC_DEMO_PACKAGE_AUTHORIZATION_REQUIRED
```

This is not a release authorization. Do not perform outreach, video production, landing-page publication, or release in this step.
