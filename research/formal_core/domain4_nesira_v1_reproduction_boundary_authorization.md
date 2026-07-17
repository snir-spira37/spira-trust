# Domain 4 / Nesira V1 Reproduction Boundary Authorization

## Verdict

```text
DOMAIN4_NESIRA_V1_REPRODUCTION_BOUNDARY_AUTHORIZED
```

This document authorizes the narrow boundary-resolution gate required after the
Domain 4 / Nesira Python harness implementation review found that full pytest
was blocked by the Formal Core V1 external reproduction package.

This is not a request to rehash one file. It is a request to resolve the
boundary between:

```text
Formal Core V1 external reproduction package
```

and:

```text
later Domain4 / Nesira Lean imports in the shared SpiraFormalCore.lean
aggregator
```

## Root Cause

The accepted Formal Core V1 external reproduction package is V1-scoped. Its
manifest, inventory, expected results, claims-and-boundaries, and SHA256SUMS do
not include Domain4.

The accepted Domain4 Lean implementation added Domain4 imports to:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
```

That shared aggregator is locked by the V1 external reproduction package. As a
result, the package hash check fails after Domain4, and a narrow hash refresh
would be misleading because the package would build/import Domain4 without
declaring Domain4 in the package inventory or claims.

## Recommended Resolution: Option A

```text
KEEP_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_V1_SCOPED
```

Option A keeps the accepted V1 external reproduction deliverable scoped to the
accepted Formal Core V1 surface:

```text
Domain 1
Domain 2
Domain 3
shared V1 core
accepted V1 adapter/conformance artifacts
```

Domain4 remains a later Phase 2 / `NOT_CLAIMED` research extension and must not
be folded into the V1 external reproduction package through the shared
aggregator.

## Option A Authorized Work

The implementation gate may perform only the minimum changes needed to keep the
V1 external reproduction package stable when later domains are added:

```text
create a V1-specific Lean root / aggregator for the external reproduction package
or adjust the V1 package verification target to import explicit V1 modules
instead of the shared growing SpiraFormalCore.lean aggregator

update the V1 external reproduction package tests / verify scripts only as
needed to use the V1-scoped target

verify that Domain4 is not included in the V1 package inventory, claims, or
expected-results

rerun full pytest
```

The intended invariant is:

```text
adding Domain4, Domain5, or later research domains must not silently change the
accepted Formal Core V1 external reproduction package.
```

## Option A Acceptance Gates

```text
V1 package remains V1-scoped: PASS
Domain4 excluded from V1 reproduction package inventory: PASS
Domain4 excluded from V1 package claims: PASS
V1 verification target does not import Domain4: PASS
V1 package hash checks: PASS
Domain4 Lean build remains independently valid: PASS
Domain4 Python harness remains green: PASS
full pytest: PASS
git diff --check: PASS
whole-tree path/secret scan for changed artifacts: PASS
```

## Option A Stop Conditions

```text
If separating the V1 verification target changes V1 theorem semantics:
  SCOPE_REVISION_REQUIRED

If the fix requires changing Domain4 Lean proofs or Phase 1 code:
  STOP

If Domain4 must be included in the V1 package to make tests pass:
  STOP and switch to Option B authorization
```

## Option B Alternative

Option B is permitted only through a separate, heavier authorization:

```text
REGENERATE_EXTERNAL_REPRODUCTION_PACKAGE_WITH_DOMAIN4_INCLUDED
```

That would require a full new deliverable:

```text
artifact_manifest refresh
proof_and_axiom_inventory refresh
expected_results refresh
FORMAL_CLAIMS_AND_BOUNDARIES refresh with Domain4 NOT_CLAIMED / Phase 2 boundary
SHA256SUMS refresh
verify_all refresh
package review
cold external reproduction
```

Option B must not be performed as a shortcut hash refresh.

## Explicitly Not Authorized By This Proposal

```text
narrow rehash of SpiraFormalCore.lean only
silent inclusion of Domain4 in the V1 reproduction package
Domain4 Lean proof changes
Phase 1 validator changes
Domain4 Python harness behavior changes
Phase 2 implementation
signature verification
signer authority checks
isolation execution
permission to sever
public capability claim
release
```

## Status

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_INTERNAL_ACCEPTED
FINAL_HARNESS_REVIEW_BLOCKED_BY_V1_REPRODUCTION_BOUNDARY

RECOMMENDED_NEXT:
DOMAIN4_NESIRA_V1_REPRODUCTION_BOUNDARY_ACCEPTANCE_REVIEW
```
