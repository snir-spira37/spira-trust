# SPIRA Nesira Phase 1 External Reproduction Package Build Report

Verdict:

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_PACKAGE_ACCEPTED
```

## Source

```text
accepted Phase 1 source commit: 6d06bdc8de1b2db3585c509e7917c5644e62eb5f
external reproduction authorization commit: b851ed0d04b58a7f526346929580543b02b47815
package mode: clone-based
```

## Boundary

The package prepares external reproduction of the narrow Phase 1 claim:

```text
SPIRA validates structure, binding, evidence integrity, and safe evidence paths
for SEVERANCE_AUTHORIZATION and LEGACY_ISOLATION_RESULT.
```

It does not claim cryptographic signature trust, signer identity or authority,
actual isolation execution, permission to sever, product integration, public
capability availability, production readiness, or release approval.

## Builder Checks

```text
focused Phase 1 tests: 11 passed
full pytest: 281 passed
compileall: PASS
public wheel build: PASS
protected surface diffs: 0
two focused semantic runs identical: True
```

## Metrics

```json
{
  "PROCEED_paths": 0,
  "directories_accepted_as_evidence_files": 0,
  "duplicate_canonical_evidence_paths_accepted": 0,
  "false_VALID_mutation_pairs": 0,
  "hash_mismatches_accepted": 0,
  "local_absolute_paths_leaked_in_results": 0,
  "negative_invariant_detection": "100%",
  "positive_fixtures_structurally_accepted": "6/6",
  "positive_fixtures_yielding_PROCEED": 0,
  "stop_false_paths": 0,
  "unsafe_evidence_paths_accepted": 0
}
```

## ZIP

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_6d06bdc.zip
SHA256: 66493d0e1b99c0d072129051e7c87706687bd1740bcbeb6f20fbb17886b322af
SHA256SUMS after extraction: True
ZIP path safety: True
```

No cold external reproduction was performed in this step.
