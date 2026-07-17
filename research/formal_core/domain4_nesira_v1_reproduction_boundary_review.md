# Domain 4 / Nesira V1 Reproduction Boundary Review

## Verdict

```text
DOMAIN4_NESIRA_V1_REPRODUCTION_BOUNDARY_ACCEPTED
```

## Summary

Option A was implemented. The Formal Core V1 external reproduction package
remains V1-scoped and no longer imports or builds Domain4 through its V1
verification path.

The fix does not fold Domain4 into the V1 external reproduction package claims.
Domain4 remains a later research extension and is still independently buildable
through the separate full Lake build path.

## Implemented Boundary

```text
SpiraFormalCore          -> V1-scoped Lean target
SpiraFormalCoreDomain4   -> separate Domain4 Lean target
verify_all               -> lake build SpiraFormalCore
full lake build           -> builds both targets
```

## Acceptance Gates

```text
V1 target excludes Domain4: PASS
full Lake build includes Domain4: PASS
V1 external reproduction verify_all.ps1: PASS
source artifact manifest hashes: PASS
SHA256SUMS: PASS
Domain4 Python harness: DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
full pytest: 286 passed
post-V1-verify full pytest: 286 passed
```

## Boundary Preserved

```text
Domain4 is not included in the V1 package inventory.
Domain4 is not included in the V1 package claims.
Domain4 is not silently reclassified as a Formal Core V1 deliverable.
```

## Still Not Authorized

```text
Phase 2 implementation
signature verification
signer authority checks
isolation execution
permission to sever
public capability claim
release
```
