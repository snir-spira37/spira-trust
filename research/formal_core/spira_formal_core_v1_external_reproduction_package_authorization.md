# SPIRA Formal Core V1 External Reproduction Package Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_AUTHORIZED

OFFLINE_REPRODUCTION_ONLY
NO_LIVE_AGENTS
NO_RESULT_RECLASSIFICATION

FORMAL_CORE_ARTIFACTS_INCLUDED
DOMAIN_1_2_3_ADAPTER_EVIDENCE_INCLUDED
FIXTURE_CORPORA_INCLUDED
PROOF_AND_AXIOM_INVENTORY_INCLUDED
TOOLCHAIN_LOCK_INCLUDED
REPRODUCIBLE_COMMANDS_REQUIRED
HASH_MANIFEST_REQUIRED
COLD_EXTERNAL_REVIEW_TASK_REQUIRED

PARSER_PROOF_NOT_CLAIMED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This authorization opens an offline external reproduction package for the accepted Formal Core V1 and all-domain adapter alignment checkpoint.

The package must allow an external reviewer to reproduce the deterministic evidence without Claude, Codex, DeepSeek, or any live agent sessions.

## Authorized Scope

Authorized:

```text
EXTERNAL_REPRODUCTION_PACKAGE_DIRECTORY
README_TASK
FORMAL_CLAIMS_AND_BOUNDARIES
EXPECTED_RESULTS
ARTIFACT_MANIFEST
SHA256SUMS
VERIFY_ALL_POWERSHELL
VERIFY_ALL_SHELL
PROOF_AND_AXIOM_INVENTORY
TOOLCHAIN_LOCK_SUMMARY
COLD_EXTERNAL_REVIEW_TASK
PACKAGE_REPORT_AND_REVIEW
PACKAGE_BUILD_SCRIPT
PACKAGE_SMOKE_TESTS
```

Authorized files and directories:

```text
tools/build_formal_core_v1_external_reproduction_package.py
tests/test_formal_core_v1_external_reproduction_package.py
research/formal_core/external_reproduction_package/
research/formal_core/spira_formal_core_v1_external_reproduction_package_results.json
research/formal_core/spira_formal_core_v1_external_reproduction_package_report.md
research/formal_core/spira_formal_core_v1_external_reproduction_package_review.md
```

## Required Package Contents

The package must include:

```text
README_TASK.txt
FORMAL_CLAIMS_AND_BOUNDARIES.md
expected_results.json
artifact_manifest.json
SHA256SUMS
verify_all.ps1
verify_all.sh
proof_and_axiom_inventory.json
toolchain_lock.json
COLD_EXTERNAL_REVIEW_TASK.md
```

The artifact manifest must cover at least:

```text
Lean source files
lean-toolchain
Lake files
Formal Core V1 specification/review artifacts
Domain 1 typed conformance results
Domain 1 raw fixtures and raw conformance results
Domain 2 typed conformance results
Domain 2 raw fixtures and raw conformance results
Domain 2 production alignment results
Domain 3 typed conformance results
Domain 3 raw fixtures and raw conformance results
Domain 3 production alignment results
all-domain adapter alignment review
reproduction scripts
```

## Reproduction Commands

The scripts must document and attempt, in order:

```text
toolchain verification
Lean build / proof check when Lean is available
axiom and no-sorry scan
fixture validation
Domain 1 conformance
Domain 2 conformance
Domain 3 conformance
raw adapter conformance for Domains 1-3
production adapter alignment for Domains 2-3
mutation checks
full pytest
secret/private-path scan
final manifest/hash verification
```

## Boundaries

Not authorized:

```text
live Claude sessions
live Codex sessions
live DeepSeek sessions
benchmark execution
holdout or carryover execution
new model calls
adapter implementation changes
Lean theorem changes
proof script changes
MVP / passthrough changes
parser proof claim
production readiness claim
release
version bump
tag
PyPI
```

## External Acceptance Questions

The cold external review task must ask:

```text
Can the reviewer reproduce all deterministic results?
Do the claims match the evidence exactly?
Is there a path to bypass the Formal Core?
Is any parser proof claimed by mistake?
Are TCB or assumptions hidden?
Does any PASS depend on undocumented manual judgment?
```

Successful package creation may support only an external-reproduction-ready claim for offline deterministic evidence. It must not authorize production, release, or renewed live-agent benchmarking.
