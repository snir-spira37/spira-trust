# SPIRA Agent Action Gate Public Demo Package Authorization

## Document Status

```text
PUBLIC_DEMO_PACKAGE_AUTHORIZATION_PROPOSED
AUTHORIZATION_AND_PACKAGE_DESIGN_ONLY
NO_PUBLIC_PACKAGE_BUILD
NO_OUTREACH
NO_VIDEO_PRODUCTION
NO_RELEASE
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
```

## Authoritative Inputs

```text
positioning_commit:
da2e99d35e029f0d231e98a517ef87fe9528dde6

competitor_mapping_commit:
45fe70b40c45601510559cda25dd05f533c21cf8

demo_authorization_commit:
2ef6f559433f1a2e0bb8c503a4b35af745e8c6a2

demo_script_commit:
bfed6f7774c48a17361ac0a2298fb9073b891ebc

demo_reproduction_revision_commit:
d731c6e719322cdb2e2c276b0c200eacb26f6e40

accepted_demo_reproduction_commit:
2b1fab6920232ec69a2af002aedbc138cd49e1a1
```

Accepted gates:

```text
POSITIONING_ACCEPTED
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
DEMO_SCRIPT_AUTHORIZATION_ACCEPTED
DEMO_SCRIPT_ACCEPTED
DEMO_REPRODUCTION_REVISION_ACCEPTED
DEMO_REPRODUCTION_ACCEPTED
```

## Purpose

Authorize the design and boundaries of a future public demo package for the SPIRA Agent Action Gate.

This authorization does not build the package. It defines what the future package may contain, what public claims it may make, how evidence must be labeled, and what must remain out of scope.

## Required Positioning

The future public demo package must use this positioning:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

Required boundary:

```text
SPIRA currently evaluates supported artifact-backed evidence.
```

SPIRA does not currently replace:

```text
agent identity
IAM
arbitrary tool-call authorization
MCP gateways
runtime interception
arbitrary API or database enforcement
human production approval
infrastructure policy products such as OPA, Sentinel, or HCP Terraform
```

## Authorized Demo Scope

The public demo package is limited to:

```text
Domain 3 - Terraform Plan evidence
```

Authorized fixtures:

```text
create_update_delete_01
incomplete_plan_01
invalid_json_01
```

Authorized actions:

```text
STOP_BLOCKED
REPORT_NOT_EVALUATED
RERUN_REQUIRED
```

Authorized reason codes:

```text
TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE
TERRAFORM_PLAN_INCOMPLETE
TERRAFORM_PLAN_JSON_INVALID
```

Authorized blocking / not-evaluated text:

```text
resource change requires review
terraform plan incomplete
Terraform plan JSON parse failed
```

No additional fixture, action, reason code, schema, adapter, producer, or domain is authorized.

## Authorized Package Contents

The future public demo package may include at most:

```text
README_DEMO.md
PUBLIC_DEMO_SCRIPT.md
REPRODUCE_DEMO.md
demo_reproduction_manifest.json
demo_expected_results.json
fixtures/
outputs/
SHA256SUMS
CLAIMS_AND_BOUNDARIES.md
COLD_DEMO_REVIEW_TASK.md
```

`fixtures/` may include only the three authorized demo fixtures if copying them does not weaken provenance. If duplication is not appropriate, the package must instead use repository-relative paths or public repository URLs pinned to exact commits.

`outputs/` may include recorded reference excerpts only if they are clearly labeled as recorded reference outputs and not presented as newly generated during a viewer's run.

## Required Public Files

### README_DEMO.md

Must explain:

```text
what SPIRA does
what the demo shows
what is not claimed
prerequisites
exact reproduction command
expected results
troubleshooting
links to exact authoritative commits
```

### PUBLIC_DEMO_SCRIPT.md

Must be based on the accepted 90-120 second Terraform demo script. It must preserve:

```text
CURRENT IMPLEMENTATION
CONCEPTUAL INTEGRATION BOUNDARY
ROADMAP ONLY
EXPLANATION_ONLY
```

### REPRODUCE_DEMO.md

Must include:

```text
exact working directory
exact commands
exact fixture paths
exact expected actions
exact reason codes
exact expected exit behavior
expected generated outputs
Windows/POSIX differences when applicable
```

### demo_reproduction_manifest.json

Must include:

```text
source commit
fixture paths
fixture SHA256
commands
prerequisites
expected semantic results
expected outputs
result classifications
verification date
```

### demo_expected_results.json

Must describe expected results for only the three authorized demo paths.

### CLAIMS_AND_BOUNDARIES.md

Must include these labels:

```text
FORMALLY_PROVED_IN_LEAN
EMPIRICALLY_REPRODUCED
CONFORMANCE_VALIDATED
TEST_SUITE_VALIDATED
DOCUMENTED_CURRENT_IMPLEMENTATION
CONCEPTUAL_INTEGRATION_BOUNDARY
ROADMAP_ONLY
NOT_EVALUATED_IN_THIS_ENVIRONMENT
NOT_CLAIMED
```

### COLD_DEMO_REVIEW_TASK.md

Must instruct an external reviewer to reproduce the demo independently and check:

```text
package SHA256
fixture hashes
documented commands
three expected outcomes
no soft PASS for invalid JSON
focused tests
full tests when dependencies are available
what was not evaluated in the reviewer environment
```

## Required Commands

The package must use only real commands that were tested:

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
python -m pytest
python -m pytest tests/test_formal_core_v1_external_reproduction_package.py
```

The package must not present:

```text
spira evaluate ...
```

or any other public CLI that does not exist in the current repository. If `spira evaluate` is mentioned, it may only appear as an explicit negative statement that the current demo does not use an invented public CLI.

## Required Layer Separation

### CURRENT IMPLEMENTATION

The package may present:

```text
Terraform plan JSON
Domain 3 adapter
typed evidence representation
machine-readable result
STOP_BLOCKED
REPORT_NOT_EVALUATED
RERUN_REQUIRED
existing evidence/proof references
```

### CONCEPTUAL INTEGRATION BOUNDARY

The package may describe only as conceptual:

```text
CI/CD pipeline consumes the result
authorized agent workflow consumes the result
external enforcement stops the next action
```

It must not claim that this external enforcement is already a built-in runtime product capability.

### ROADMAP ONLY

The package must mark these as roadmap only:

```text
direct MCP interception
arbitrary tool-call enforcement
arbitrary API/database action adapters
backup/restore evidence
approval evidence
universal runtime governance
unified public action-gate CLI, if not yet implemented
```

## Formal Proof Boundary

The package may say:

```text
SPIRA includes a machine-checked Formal Core V1 implemented in Lean.

The accepted formal package contains machine-checked proofs for bounded decision properties.
```

The package must also state:

```text
Demo reproduction:
DEMO_REPRODUCTION_ACCEPTED

Formal package Lean reproduction in the accepted demo environment:
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

The package must not say:

```text
the entire product is mathematically proven safe
the Terraform parser is formally proved
all adapters are formally proved
every AI action is mathematically verified
Lean was reproduced during the accepted demo reproduction run
DEMO_REPRODUCTION_ACCEPTED means Lean reproduction passed
```

Prior Lean/Lake PASS evidence may be referenced only as separate evidence with exact commit and artifact references. It must not be merged into the accepted demo reproduction result.

## Authorized Public Claims

The future package may make these claims only when tied to exact evidence artifacts or commits:

```text
The three Domain 3 demo outcomes were reproduced twice with matching semantic results.
Invalid Terraform JSON did not receive a soft PASS.
The focused and full Python test suites passed in the accepted reproduction environment.
The accepted reproduction used existing fixtures, actions, reason codes and schemas.
The demo did not require a product, adapter, schema or fixture change.
SPIRA's formal decision core contains machine-checked Lean proofs for bounded properties.
The model is explanation-only and does not own the machine action in the formal architecture.
```

## Prohibited Public Claims

The package must not claim:

```text
SPIRA guarantees Terraform safety
SPIRA formally proves Terraform
SPIRA governs all AI agents
SPIRA is the only pre-action gate
SPIRA is unique in Terraform policy
SPIRA replaces OPA, Sentinel, HCP Terraform, or Spacelift
SPIRA replaces IAM or MCP gateways
SPIRA intercepts arbitrary actions
SPIRA is independently certified
SPIRA is production-final
the complete system was formally verified end-to-end
DEMO_REPRODUCTION_ACCEPTED means Lean reproduction passed
```

## Security And Privacy Requirements

The future package must require:

```text
secret scan
no API keys
no tokens
no credentials
no private repository URLs
no local Windows absolute paths
no usernames embedded in public files
no machine-specific temp paths
no environment-specific secrets
no sensitive Terraform values
no source artifacts outside the authorized public scope
```

Every path in the package must be:

```text
repository-relative
archive-relative
or a public repository URL pinned to an exact commit
```

## Portability Requirements

The future package must require:

```text
forward-slash ZIP paths
LF-normalized generated text
Windows and POSIX instructions where supported
explicit Python version
explicit dependencies
deterministic semantic comparison
no reliance on untracked files
no reliance on an existing local virtual environment without disclosure
no hidden generated outputs
no local absolute links
```

## Acceptance Criteria For Future Package Build

The future build step must verify:

```text
package SHA256 present
SHA256SUMS present
all package hashes match
fixture hashes match
expected results match actual reproduction
no soft PASS for invalid JSON
focused tests pass
full tests pass when dependencies are available
secret scan passes
local absolute path scan passes
no unsupported public claims
no invented CLI
no domain expansion
no release
no outreach
```

## Authorization Verdict

```text
PUBLIC_DEMO_PACKAGE_AUTHORIZATION_ACCEPTED
```

## Next Step

```text
PUBLIC_DEMO_PACKAGE_BUILD_REQUIRED
```

The next step may build the package under this authorization. It may not publish, release, perform outreach, produce a public video, or launch a landing page without later accepted authorization.
