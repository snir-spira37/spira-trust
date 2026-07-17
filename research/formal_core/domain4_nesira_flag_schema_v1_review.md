# SPIRA Domain 4 / Nesira Flag Schema V1 Review

## Verdict

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_ACCEPTED
```

This review accepts the V1 flag schema specification as a precise interface
between the Python Nesira Phase 1 adapter and a future Lean Domain 4 decision
core. It does not authorize Lean implementation, Python implementation,
fixtures, tests, Phase 2 implementation, public claims, or release work.

Reviewed artifact:

```text
research/formal_core/domain4_nesira_flag_schema_v1_spec.md
```

## Review Method

The review applied the adversarial checklist required by the authorization:

```text
one definition per flag
python_computes and lean_assumes semantic equivalence
explicit edge-case behavior
false_when coverage for safety-critical flags
tuple totality
cross-platform path semantics
no trust/signature/authorization flag leakage
V1 immutability
canonical tuple serialization
scope revision instead of invented behavior
```

## Findings

### 1. Single-Definition Discipline Is Satisfied

Each flag contains a `one_definition` that is also reflected in
`python_computes` and `lean_assumes`. The spec does not define separate Python
and Lean meanings. This prevents the main failure mode where Python computes one
semantic fact and Lean proves a different one.

Accepted:

```text
one_definition is the source of truth for each flag
```

### 2. Artifact Kind Is Required and Correct

The review specifically checked whether one boolean flag set can safely cover
both accepted Phase 1 artifact families. The spec correctly adds:

```text
artifact_kind:
  SEVERANCE_AUTHORIZATION
  LEGACY_ISOLATION_RESULT
```

This is necessary because `LEGACY_ISOLATION_RESULT` checks evidence files,
paths, symlinks, duplicates, regular-file status, and hashes, while
`SEVERANCE_AUTHORIZATION` does not read evidence-root files in Phase 1.

The spec's treatment is accepted:

```text
For SEVERANCE_AUTHORIZATION, evidence/path/hash flags are true by
non-applicability in V1.

This is not a claim that evidence-root files were checked.
```

Without this artifact-kind discriminator, `hash_ok` and `path_safe` would have
been ambiguous and the schema would have needed revision.

### 3. Safety-Critical Flags Are Properly Identified

The review accepts the safety-critical set:

```text
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
context_match
```

These are the adapter classifications where a false `true` could turn an unsafe
raw artifact into a structurally valid flag tuple. The spec requires mutation
pairs for all of them.

### 4. Hash Semantics Are Precise

The review checked for the Phase 1 packaging failure class: hashes accidentally
computed over copies, manifests, normalized text, or metadata instead of the
bytes actually evaluated.

The spec is accepted because it states:

```text
SHA-256(raw file bytes)
not manifest bytes
not path string
not JSON document
not normalized metadata
```

This closes the most important ambiguity around `hash_ok`.

### 5. Path Semantics Are Precise Enough for V1

The review accepts the `path_safe` definition because it explicitly covers:

```text
empty path
absolute POSIX path
leading backslash
UNC / network path
Windows drive-qualified path
traversal components
empty components
backslash-to-slash normalization
```

The spec correctly keeps filesystem resolution out of `path_safe` and assigns
that concern to `symlink_escape_absent`.

### 6. Symlink / Filesystem Trust Is Not Overclaimed

The spec does not pretend Lean proves OS path resolution. It says Python
classifies symlink escape and Lean assumes only the resulting flag. This matches
the accepted proof boundary.

Accepted:

```text
filesystem resolution is Python-side / empirical
Lean does not prove OS semantics
```

### 7. Tuple Totality and Canonical Serialization Are Sufficient

The spec requires a named record and deterministic JSON serialization:

```text
UTF-8 JSON
sorted keys
no timestamps
no host paths
no environment metadata
```

This is sufficient for the future conformance harness to enforce two-run
semantic equality and byte-for-byte tuple comparison.

### 8. No Trust or Authorization Flag Leaks Into V1

The review checked whether any flag encodes cryptographic trust, signer
authority, actual isolation, or permission to sever. None does.

Accepted:

```text
flags are structural / binding / evidence-integrity classifications only
```

Required companion artifact remains:

```text
domain4_nesira_not_proven_in_lean_ledger.md
```

### 9. Edge Cases Are Explicitly Covered

The spec explicitly covers:

```text
missing artifact / malformed artifact
empty object
empty evidence_manifest
malformed evidence_manifest item
missing evidence file
hash mismatch
directory instead of file
duplicate canonical path
symlink escape
resolve failure
unsupported schema version
context mismatch
missing expected context
expired temporal binding
tool error
```

The review accepts this coverage for schema freeze purposes.

### 10. No Product Behavior Is Invented

The spec does not define the final decision table. It only defines flag
semantics and decision-table roles. Precedence and action projection remain in a
separate authorized sibling:

```text
domain4_nesira_decision_table_v1_spec.md
```

This preserves the authorization boundary.

## Non-Blocking Caveat

For `SEVERANCE_AUTHORIZATION`, the evidence/path/hash flags are true by
non-applicability. This is acceptable for V1 only because `artifact_kind` is part
of the tuple and because the spec states that no evidence-root file check is
claimed for severance in Phase 1.

Future versions that add severance evidence-root checks must create a new schema
version rather than changing this interpretation in place.

## Accepted Next Steps

The next specification artifacts may proceed under the existing authorization:

```text
research/formal_core/domain4_nesira_decision_table_v1_spec.md
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.md
research/formal_core/domain4_nesira_conformance_harness_v1_spec.md
```

The recommended order is:

```text
1. not_proven_in_lean_ledger
2. decision_table_v1_spec
3. conformance_harness_v1_spec
```

The ledger should come first so the decision table and harness cannot drift into
trust, signer, or execution claims.

## Not Authorized

This review does not authorize:

```text
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
Phase 1 reopening
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
combined verdict integration
CLI or wheel exposure
public capability claims
release
```

## Status

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_ACCEPTED

SPIRA_NESIRA_DOMAIN4_FLAGS_V1_FROZEN
ARTIFACT_KIND_DISCRIMINATOR_ACCEPTED
SAFETY_CRITICAL_FLAG_SET_ACCEPTED
CANONICAL_TUPLE_SERIALIZATION_ACCEPTED
MUTATION_PAIR_REQUIREMENTS_ACCEPTED_FOR_SCHEMA_PURPOSES

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

