# Terraform Agent Action Gate Demo Reproduction Run Report

## Document Status

```text
DEMO_REPRODUCTION_RUN_COMPLETE
DEMO_REPRODUCTION_NEEDS_REVISION
REPRODUCTION_AND_VERIFICATION_ONLY
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_RELEASE
NO_OUTREACH
```

## Scope

This run attempted to reproduce the accepted Terraform Agent Action Gate demo from commit:

```text
bfed6f7774c48a17361ac0a2298fb9073b891ebc
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
```

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

The invalid JSON path did not soft-pass and did not return `PROCEED`.

## Commands Run

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
python -m json.tool research/product_strategy/terraform_agent_action_gate_demo_reproduction_manifest.json
python -m json.tool research/product_strategy/terraform_agent_action_gate_demo_verified_results.json
python -m json.tool research/product_strategy/terraform_agent_action_gate_demo_script_review_results.json
git diff --check
```

## Results

```text
focused pytest:
PASS, 12 passed

JSON validation:
PASS

git diff --check:
PASS

Domain 3 semantic fixture conformance:
PASS for the selected demo paths

documented conformance harness command:
FAIL, exit code 1 in both runs
```

The documented harness command returned non-zero because its internal full pytest gate failed:

```text
full_pytest_pass: false
status: SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_NEEDS_REVISION
```

The failure was not a mismatch in the three demo paths. The failure was a hash mismatch in the external reproduction package manifest for three tracked Domain 3 conformance artifacts:

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_review.md
```

## Documentation Check

The demo script matched the reproduced commands, fixtures, action names, labels, and current implementation boundary. No invented `spira evaluate` CLI, fake agent runtime, MCP/API/database gate, runtime interception, release, or outreach claim was introduced.

## Verdict

```text
DEMO_REPRODUCTION_NEEDS_REVISION
```

The demo's three semantic paths are reproducible, but the required acceptance gate cannot be satisfied because the exact documented harness command does not return PASS from the current commit. The blocker is in the external reproduction package manifest/hash layer, not in the selected Domain 3 demo fixture semantics.

## Next Step

```text
DEMO_REPRODUCTION_REVISION_REQUIRED
```

Do not proceed to a public demo package until the external reproduction package manifest/hash mismatch is corrected or the reproduction instructions are revised and re-run.
