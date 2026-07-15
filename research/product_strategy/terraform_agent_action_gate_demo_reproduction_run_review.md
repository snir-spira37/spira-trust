# Terraform Agent Action Gate Demo Reproduction Run Review

## Review Status

```text
DEMO_REPRODUCTION_REVIEW_COMPLETE
DEMO_REPRODUCTION_NEEDS_REVISION
NO_RESULT_ACCEPTANCE
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_RELEASE
NO_OUTREACH
```

## Review Question

Can the accepted Terraform Agent Action Gate demo be reproduced from the repository using the documented fixtures, hashes, commands, and script without hidden state or manual output repair?

## Findings

### F1 - Required Harness Command Does Not Pass

Severity: blocking

The documented command was run twice:

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

Both runs returned exit code `1`. The generated conformance result status was:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_NEEDS_REVISION
```

The failing gate was:

```text
full_pytest_pass: false
```

This prevents `DEMO_REPRODUCTION_ACCEPTED` under the authorized acceptance criteria.

### F2 - External Reproduction Package Manifest Hash Mismatch

Severity: blocking

The full pytest failure was traced to:

```text
tests/test_formal_core_v1_external_reproduction_package.py::test_external_reproduction_package_manifest_hashes_match
```

The external reproduction package manifest has three mismatches against the current repository files:

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_review.md
```

This is a reproducibility/package-integrity blocker. It does not show that the three selected demo paths are semantically wrong, but it does show that the current documented reproduction route is not clean.

### F3 - Selected Demo Paths Reproduce Semantically

Severity: informational

The selected Domain 3 paths reproduced the intended semantics across two runs:

```text
STOP_BLOCKED:
PASS

REPORT_NOT_EVALUATED:
PASS

RERUN_REQUIRED:
PASS

invalid JSON soft pass:
not observed
```

The focused tests passed:

```text
12 passed
```

JSON validation and `git diff --check` also passed.

## Boundary Review

No prohibited work was performed:

```text
product code change: no
formal core change: no
schema change: no
adapter change: no
producer change: no
fixture change: no
new CLI: no
wrapper: no
runtime interception: no
agent integration: no
domain expansion: no
release: no
outreach: no
```

The review also found no invented public CLI, fake runtime, MCP/API/database gate, or backup/restore/approval demo claim.

## Verdict

```text
DEMO_REPRODUCTION_NEEDS_REVISION
```

The current run cannot be accepted because a required command fails in the current repository state. The immediate revision target is the external reproduction package manifest/hash mismatch for the Domain 3 conformance artifacts.

## Required Next Step

```text
DEMO_REPRODUCTION_REVISION_REQUIRED
```

After revision, rerun the full `DEMO_REPRODUCTION_RUN_REQUIRED` flow from a clean worktree. Do not proceed to `PUBLIC_DEMO_PACKAGE_AUTHORIZATION_REQUIRED` until the documented harness command returns PASS and the review accepts the reproduction.
