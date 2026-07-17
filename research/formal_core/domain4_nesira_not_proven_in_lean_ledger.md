# SPIRA Domain 4 / Nesira NOT_PROVEN_IN_LEAN Ledger

## Status

```text
LEDGER_ID: SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
LEDGER_VERSION: 1
FROZEN: true
DOCUMENT_TYPE: CLAIM_BOUNDARY_LEDGER
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
DECISION_TABLE: NOT_AUTHORIZED_IN_THIS_DOCUMENT
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This ledger binds every future Domain 4 / Nesira Lean claim. Any statement about
Domain 4 / Nesira formal proof that is not accompanied by this ledger is an
overclaim.

## Core Boundary

```text
Lean proves:
flags -> contract

Lean does not prove:
world -> flags
```

Everything on the `world -> flags` side belongs in this ledger. The Python
adapter may classify raw artifacts into typed flags; Lean may only reason over
those already-classified flags.

## Positive Claim Allowed by This Ledger

The future positive claim, if later proved in Lean, is limited to:

```text
Given faithful SPIRA_NESIRA_DOMAIN4_FLAGS_V1 flags, the Domain 4 decision table:

- cannot produce PROCEED because PROCEED is unrepresentable in Phase1Action
- cannot mark hash-mismatch or unsafe-path classifications as structurally valid
- is deterministic for every legal flag tuple
- preserves explicit contractual boundaries such as not_claimed / not_evaluated

The proof, if implemented and accepted later, is checked in Lean 4.32.0,
sorry-free and dependency-free.
```

Nothing beyond that statement is authorized by this ledger.

## NOT_PROVEN IDs

### Adapter Faithfulness

```text
NP-ADAPTER-01: JSON parsing correctness
NP-ADAPTER-02: DSSE envelope / payload decoding correctness
NP-ADAPTER-03: filesystem reads, file existence, and file type classification
NP-ADAPTER-04: symlink resolution on Windows and POSIX
NP-ADAPTER-05: SHA-256 computed over the correct bytes
NP-ADAPTER-06: path normalization and canonicalization correctness
NP-ADAPTER-07: faithfulness of each computed flag to the real artifact
```

These items may be tested by conformance harnesses and mutation pairs. They are
not proved by Lean.

### Trust, Authority, and Execution

```text
NP-TRUST-01: cryptographic signature validity
NP-TRUST-02: signer identity
NP-TRUST-03: signer authority
NP-TRUST-04: severance authorization
NP-TRUST-05: permission to sever
NP-TRUST-06: actual isolation execution or independent observation
```

These are not in Domain 4 Phase 1 proof scope. They require separate Phase 2
research and authorization.

### Applicability

```text
NP-APPLIC-01: a non-applicable flag set to true must not be read as "check
performed." It means only "not applicable in V1 for this artifact_kind."
```

This item is required because `SPIRA_NESIRA_DOMAIN4_FLAGS_V1` uses one named
flag tuple for both accepted Phase 1 artifact families. Some evidence-file flags
are applicable to `LEGACY_ISOLATION_RESULT` and non-applicable to
`SEVERANCE_AUTHORIZATION`.

### Meta Claims

```text
NP-META-01: a Lean proof of the decision table is not "Nesira is formally
proved" end to end
NP-META-02: not independent certification
NP-META-03: not production readiness
NP-META-04: not release readiness
NP-META-05: not public wheel, CLI, or product capability availability
```

## Applicability Matrix

```text
flag                         SEVERANCE_AUTHORIZATION        LEGACY_ISOLATION_RESULT
schema_valid                 applicable                     applicable
evidence_present             N/A -> true, NP-APPLIC-01      applicable
hash_ok                      N/A -> true, NP-APPLIC-01      applicable
path_safe                    N/A -> true, NP-APPLIC-01      applicable
symlink_escape_absent        N/A -> true, NP-APPLIC-01      applicable
duplicate_path_free          N/A -> true, NP-APPLIC-01      applicable
directory_not_file_absent    N/A -> true, NP-APPLIC-01      applicable
context_match                applicable                     applicable
temporal_binding_ok          applicable                     N/A -> true, NP-APPLIC-01
evaluated                    applicable                     applicable
```

## Binding Rule for Future Decision Table

The future `domain4_nesira_decision_table_v1_spec.md` must branch on
`artifact_kind` before consuming a flag that is non-applicable for that
artifact family.

In particular:

```text
hash_ok = true for SEVERANCE_AUTHORIZATION
does not mean
"hash check performed"
```

It means only:

```text
evidence-root hash checking is not applicable to SEVERANCE_AUTHORIZATION in V1.
```

The same rule applies to all N/A entries in the applicability matrix.

## Machine-Readable Companion

The machine-readable companion for this ledger is:

```text
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.json
```

Future specs should reference ledger entries by ID rather than by prose copy.

## Not Authorized

This ledger does not authorize:

```text
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
decision-table implementation
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
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1_SPECIFIED

NOT_PROVEN_LEDGER_ONLY
WORLD_TO_FLAGS_OUT_OF_LEAN_SCOPE
NP_APPLIC_01_GUARD_SPECIFIED
APPLICABILITY_MATRIX_SPECIFIED
MACHINE_READABLE_LEDGER_COMPANION_SPECIFIED

DECISION_TABLE_NOT_AUTHORIZED_IN_THIS_DOCUMENT
LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PYTHON_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

