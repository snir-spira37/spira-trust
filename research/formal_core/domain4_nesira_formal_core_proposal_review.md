# SPIRA Domain 4 / Nesira Formal Core Proposal Review

## Verdict

```text
DOMAIN4_NESIRA_FORMAL_CORE_PROPOSAL_ACCEPTED
```

This review accepts the Domain 4 / Nesira formal-core direction as a research
path only. It does not authorize Lean implementation, Python implementation,
schema changes, Phase 1 changes, product integration, public claims, Phase 2
release work, or any change to the accepted Nesira Phase 1 milestone.

## Accepted Scope

The proposal correctly defines Domain 4 as an extension of the existing
Formal Core V1 pattern:

```text
raw artifact / filesystem / JSON / hash work
-> tested Python adapter
-> typed flags
-> Lean-proved decision table
-> authoritative machine contract
```

The accepted proof boundary is:

```text
Lean proves:
typed flags + policy -> safe Phase 1 decision table

Lean does not prove:
raw parsing, filesystem behavior, hash computation, signatures,
signer authority, isolation execution, or Python flag faithfulness
```

This is the correct boundary. It preserves the Phase 1 achievement while
preventing an overclaim that "Nesira is formally proved" as an end-to-end
system.

## Key Findings

### 1. Domain 4 Should Reuse Formal Core V1

The proposal correctly avoids creating a new Lean project. Domain 4 should be
added beside the existing Domain 1, Domain 2, and Domain 3 modules and should
reuse the existing formal-core structure wherever possible.

Accepted:

```text
Domain4/Nesira as an extension of SpiraFormalCore
```

Rejected:

```text
a separate Nesira Lean project
a parallel contract algebra
a product integration shortcut
```

### 2. The Flag Boundary Is the Critical Artifact

The proposal correctly identifies the flag schema as the load-bearing contract
between Python and Lean. The next stage must freeze the flag interface before
any proof or harness is written.

Accepted next artifact:

```text
SPIRA_NESIRA_DOMAIN4_FLAGS_V1
```

The review agrees that the flag schema must include precise semantics, not only
field names. In particular, `hash_ok`, `path_safe`, `symlink_escape_absent`,
`duplicate_path_free`, `directory_not_file_absent`, and `context_match` are
safety-critical adapter claims.

### 3. `PROCEED` Should Be Type-Level Impossible in Phase 1

The proposal's strongest design choice is accepted:

```text
Phase1Action has no PROCEED constructor.
```

This is stronger than proving that `PROCEED` is not returned. In Phase 1,
structural validity must remain non-authoritative for severance permission.
Therefore even a fully valid Phase 1 document may only support a structural
result such as `VALID_STRUCTURAL_ONLY` / `REPORT_NOT_EVALUATED` with
`stop = true`.

Any future `PROCEED`-capable action type belongs to a separate Phase 2 trust
layer after signer authority, cryptographic verification, and isolation
execution have been specified and authorized.

### 4. `NOT_PROVEN_IN_LEAN` Is Required

The proposal correctly freezes a non-scope ledger from the beginning. This is
required for safe communication of the proof.

The following must remain explicitly outside the Lean claim:

```text
JSON / DSSE parsing
filesystem reads and path semantics
symlink resolution
SHA-256 over the correct bytes
signature trust
signer identity and authority
actual isolation execution
permission to sever
Python flag-classification faithfulness
```

The review accepts the proposal only with this ledger attached to all future
Domain 4 claims.

### 5. Deterministic Precedence Is Required

The proposal correctly separates safety from deterministic contract shape.
Because `PROCEED` is unrepresentable, the remaining risk is inconsistent
classification of multiple simultaneous non-pass conditions.

The decision table and precedence order must be derived from accepted Phase 1
semantics. If the Phase 1 specification does not determine the precedence
unambiguously, the next step must stop with:

```text
SCOPE_REVISION_REQUIRED
```

The review does not authorize inventing a new precedence order during Lean
implementation.

### 6. Mutation Pairs Are Mandatory for Safety-Critical Flags

The proposal correctly states that the harness proves values on fixtures, not
the semantics of Python's classification. Therefore every safety-critical flag
must have a dedicated mutation pair that forces the flag to flip.

Required mutation-pair coverage:

```text
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
context_match
```

Without these mutation pairs, the Lean proof would be formally correct but
insufficiently connected to the Python adapter.

## Accepted Next Step

The next authorized proposal stage is:

```text
research/formal_core/domain4_nesira_flag_schema_v1_authorization.md
```

That document should authorize specification work only:

```text
freeze SPIRA_NESIRA_DOMAIN4_FLAGS_V1
freeze NOT_PROVEN_IN_LEAN ledger
define decision-table precedence requirements
define safety-critical mutation-pair requirements
define Python-to-Lean conformance harness requirements
```

## Not Authorized

This review does not authorize:

```text
Lean definitions
Lean proof scripts
Python adapter changes
Nesira validator changes
Phase 1 changes
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
DOMAIN4_NESIRA_FORMAL_CORE_PROPOSAL_ACCEPTED

DOMAIN4_NESIRA_FLAG_SCHEMA_V1_AUTHORIZATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

