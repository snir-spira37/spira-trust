# Terraform Agent Action Gate Demo Reproduction Run Review

## Review Status

```text
DEMO_REPRODUCTION_REVIEW_COMPLETE
DEMO_REPRODUCTION_ACCEPTED
PUBLIC_DEMO_PACKAGE_AUTHORIZATION_REQUIRED_NEXT
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_RELEASE
NO_OUTREACH
```

## Review Question

Can the accepted Terraform Agent Action Gate demo be reproduced after the package-integrity revision using the documented fixtures, hashes, commands, and script without hidden state or manual output repair?

## Findings

### F1 - Package Integrity Restored

Severity: pass

The reproduction package passed integrity checks before and after the Domain 3 conformance runs:

```text
artifact manifest hash mismatches: 0
missing artifacts: 0
duplicate paths: 0
secret scan hits: 0
forbidden Lean token matches: 0
```

No hash drift recurred after repeated Domain 3 generated-output runs.

### F2 - Demo Paths Reproduced

Severity: pass

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

### F3 - Required Tests Passed

Severity: pass

The required Python and package checks passed:

```text
Domain 3 conformance: PASS twice
focused pytest: PASS
full pytest: PASS, 270 passed
package smoke tests: PASS
JSON validation: PASS
git diff --check: PASS
```

### F4 - Lean/Lake Not Evaluated In This Environment

Severity: boundary

Lean/Lake was not available in the local environment:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

This was not promoted to a PASS. Full Lean reproduction remains for an environment with the declared Lean/Lake toolchain available.

### F5 - Documentation Matches The Reproduction

Severity: pass

The demo script matches the reproduced fixtures, commands, actions, reason codes, blockers, `not_evaluated` values, output paths, and labels:

```text
CURRENT IMPLEMENTATION
CONCEPTUAL INTEGRATION BOUNDARY
ROADMAP ONLY
EXPLANATION_ONLY
```

The `spira evaluate` phrase appears only as an explicit negative statement that the demo does not use an invented CLI.

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

The historical failed reproduction from commit `03d92b97304f61b77e58b058875a277abb1df4c7` remains preserved in git history. The package-integrity revision from `d731c6e719322cdb2e2c276b0c200eacb26f6e40` remains a separate checkpoint.

## Demo Reproduction Verdict

```text
DEMO_REPRODUCTION_ACCEPTED
```

## Formal Package Lean Reproduction Status

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## Required Next Step

```text
PUBLIC_DEMO_PACKAGE_AUTHORIZATION_REQUIRED
```

Do not perform outreach, video production, landing-page publication, or release under this review.
