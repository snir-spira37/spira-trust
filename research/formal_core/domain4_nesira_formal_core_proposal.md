# SPIRA Domain 4 / Nesira Formal Core — Proposal

## 0. Status

```text
DOCUMENT_TYPE: RESEARCH_PROPOSAL
PHASE: PHASE_2_RESEARCH
AUTHORIZATION: NOT_AUTHORIZED
IMPLEMENTATION: NOT_IMPLEMENTED
LEAN_PROOF: NOT_PROVEN
PUBLIC_CAPABILITY_CLAIM: NOT_CLAIMED
```

Nothing in this document is proven, implemented, released, or authorized. This is a
proposal to be reviewed before any Lean code, Python code, or schema is written.
It does not modify, extend, or re-open the locked Phase 1 result
`SPIRA_NESIRA_PHASE1_COLD_EXTERNAL_REPRODUCTION_ACCEPTED` (delivery `af88cba` via
`69fcc28`). Phase 1 remains exactly as accepted.

## 1. Motivation

Phase 1 established, by external cold reproduction, that the Nesira validator checks
structure, binding, evidence integrity, and safe evidence paths, and is fail-closed
(never `PROCEED`, always `stop`). Those checks are validated **empirically** (tests,
fixtures, mutation pairs) — the decision behaviour is observed to be correct on the
covered inputs.

This proposal adds one thing and only one thing: a **machine-checked proof of the
decision core** — the mapping from already-classified evidence flags to the machine
contract/action. It does not attempt to prove the parser, filesystem, signature stack,
or runner. It moves the central safety claim ("a valid-looking document can never
become `PROCEED` in Phase 1") from "reproduced on fixtures" to "true for all inputs to
the decision core, by construction and proof."

The lesson from the Phase 1 round applies here too: the value is not "does it work,"
it is "can an independent party verify it without trusting our machine or our word."
A Lean proof is exactly that kind of artifact — it is re-checkable by anyone with
`lake build` and zero knowledge of our environment.

## 2. Scope — what Lean will prove

Lean proves properties of a pure decision function over typed flags:

```text
NesiraCore : Flags → Policy → MachineContract
```

Proposed theorems (names mirror the existing Formal Core V1 style):

```text
hash_mismatch_not_valid          : hash_ok = false        → status ≠ VALID
unsafe_path_not_valid            : path_safe = false       → status ≠ VALID
symlink_escape_not_valid         : symlink_escape_absent=f → status ≠ VALID
duplicate_path_not_valid         : duplicate_path_free = f → status ≠ VALID
directory_evidence_not_valid     : directory_not_file = f  → status ≠ VALID
missing_evidence_not_valid       : evidence_present = false→ status ≠ VALID
binding_mismatch_reruns          : context_match = false   → action = RERUN_REQUIRED
structurally_valid_still_no_proceed : all checks valid     → action ≠ PROCEED
core_never_proceeds              : ∀ f p, action ≠ PROCEED (subsumed by the type; see §6)
core_deterministic               : extensional determinism of NesiraCore (see §7)
not_claimed_preserved            : the not_claimed set is preserved end to end
```

These are the same shapes already proven for Domain 1/2/3 (`blocking_decideAction_not_proceed`,
`required_unknown_decideAction_not_proceed`, `assembleContract_preserves_notClaimed`,
`core_extensional_determinism`, `failClosedAction_not_proceed`). Domain 4 is an
**extension of the existing `SpiraFormalCore` package**, not a new Lean project.

## 3. Non-scope — NOT_PROVEN_IN_LEAN ledger

This ledger is frozen from day one to prevent the proof from ever being over-claimed.
Lean **does not** prove any of the following; they remain empirical / out of the formal
model:

```text
- JSON parsing correctness
- DSSE envelope / payload decoding correctness
- filesystem behaviour (existence, reads)
- symlink resolution correctness on Windows and Linux
- SHA-256 computed over the correct bytes
- cryptographic signature trust
- signer identity and signer authority
- actual isolation execution and independent observation
- permission to sever
- public wheel / CLI packaging
- release readiness
- FAITHFULNESS of Python's flag classification
    (i.e. that Python's computed flags reflect the real artifact)
    — covered only by the conformance harness in §9, NOT by proof
```

The last line is the crux and must never be dropped: the proof is only meaningful to
the extent that Python hands the core flags that faithfully describe the raw artifact.
That faithfulness is an **empirical** claim carried by the harness, not a theorem.

## 4. The proof / adapter boundary

```text
Python adapter:
    raw JSON / DSSE / filesystem / paths / hashes  →  typed Flags

Lean Domain 4 / Nesira:
    typed Flags + Policy  →  MachineContract (status, action, reason codes, sets)

Conformance harness:
    proves EMPIRICALLY, on fixtures + mutation pairs,
    that Python produces the flags Lean assumes — and flips them when it must.
```

Lean proves the decision table over the flags. Python computes the flags. The harness
is the load-bearing bridge between the two; without it the proof floats above reality.

## 5. Frozen flag schema (v1)

The flag set is the contract on which everything else depends. It must be **frozen and
versioned** (like the Phase 1 schemas) before any proof or harness work begins. Each
flag is `Bool` unless noted, and carries a precise definitional contract that Python
must satisfy and Lean assumes.

```text
schema: SPIRA_NESIRA_DOMAIN4_FLAGS_V1
```

| flag | meaning (the contract Python must satisfy) |
|---|---|
| `schema_valid` | artifact matches the frozen structural contract for its type |
| `evidence_present` | every declared evidence entry resolves to an existing regular file inside the evidence root |
| `hash_ok` | for every declared evidence file, SHA-256 of the file's **raw bytes** equals the manifest digest (hash is over the evidence file, not the manifest) |
| `path_safe` | no evidence path is absolute, drive-relative, UNC, or contains traversal after canonicalization |
| `symlink_escape_absent` | no evidence path resolves, via symlink, outside the evidence root |
| `duplicate_path_free` | no two evidence entries canonicalize to the same path |
| `directory_not_file_absent` | no evidence entry points at a directory instead of a file |
| `context_match` | subject, candidate, environment, profile/policy match the externally supplied expected context |
| `temporal_binding_ok` | revision / expiry / scope invariants hold |
| `evaluated` | the validator ran and evaluated structure — **structural only**; never implies trust |

Notes:
- `evaluated = true` must never be read as "trust evaluated." Its meaning is fixed to
  "structural evaluation performed." This is the same trap flagged in Phase 1 and is
  frozen here explicitly.
- The flag set must be **total**: the decision function is defined for every
  combination, so no combination can fall through to an undefined (and possibly unsafe)
  default.

## 6. `Phase1Action` — `PROCEED` is unrepresentable

Rather than prove "the function never returns `PROCEED`," make `PROCEED` impossible to
express in this phase's action type:

```text
inductive Phase1Action
  | VALID_STRUCTURAL_ONLY   -- maps to REPORT_NOT_EVALUATED downstream
  | INVALID                 -- maps to STOP_BLOCKED
  | REPORT_NOT_EVALUATED
  | RERUN_REQUIRED
```

There is no `PROCEED` constructor. A future Phase 2 trust layer that legitimately needs
`PROCEED` introduces it in a **separate** type, gated by signer/runner evidence that
does not exist yet. This makes `core_never_proceeds` a type-level fact, not a proof
obligation — a future programmer error cannot even compile a `PROCEED` in Phase 1.

`VALID_STRUCTURAL_ONLY` must still map downstream to `REPORT_NOT_EVALUATED` with
`stop = true`, because structural validity is not authorization.

## 7. Decision table and precedence (determinism)

Safety (`≠ PROCEED`) is handled by the type in §6. But the contract and the two-run
equality property also require **determinism**: given identical flags, exactly one
action and one reason-code set. So the decision function needs a defined **precedence**
when several flags are bad simultaneously, and a proof that it is deterministic
(the analog of the existing `core_extensional_determinism`).

Proposed precedence (fail-closed, most-severe first — to be **derived from the accepted
Phase 1 specification, not invented**; Phase 1 Python already implements this mapping):

```text
1. schema_valid = false
   OR any of {hash_ok, path_safe, symlink_escape_absent,
              duplicate_path_free, directory_not_file_absent} = false
        → status = INVALID          → action = INVALID (STOP_BLOCKED)
2. else context_match = false OR temporal_binding_ok = false
        → status = RERUN_REQUIRED   → action = RERUN_REQUIRED
3. else evidence_present = false
        → status = NOT_EVALUATED    → action = REPORT_NOT_EVALUATED
4. else (all checks pass)
        → status = VALID_STRUCTURAL_ONLY → action = REPORT_NOT_EVALUATED
```

If the accepted Phase 1 specification does not uniquely determine this ordering, the
proposal **stops** for scope revision rather than inventing it — the same discipline as
Phase 1 (`SCOPE_REVISION_REQUIRED`).

## 8. Safety-critical flags

A false-`true` on these flags is the one adapter failure mode that could defeat the
fail-closed guarantee (the core would compute a correct action over an incorrect flag).
They are tagged and treated as a mandatory gate:

```text
SAFETY_CRITICAL_ADAPTER_CONFORMANCE:
    hash_ok
    path_safe
    symlink_escape_absent
    duplicate_path_free
    directory_not_file_absent
    context_match
```

Because Phase 1 is fail-closed, most adapter bugs cause a false `STOP`/`NOT_EVALUATED`
(safe). These flags are the exception: an adapter that wrongly reports one of them as
`true` is the only way to manufacture a structural `VALID` that should not exist. Their
conformance tests are safety gates, not mere correctness tests.

## 9. Conformance harness — Python ↔ Lean

The harness proves flag **values** on fixtures. It does not prove flag **semantics**.
To close that gap as far as empirically possible, the discipline is:

```text
For every safety-critical flag:
    a mutation pair whose minimal change is exactly at the point the flag must react,
    and Python MUST flip the flag (and therefore the action) for that mutation.
```

Examples:

```text
hash_ok            : flip one evidence byte → hash_ok must go false → INVALID
path_safe          : inject "../" / absolute / UNC → path_safe false → INVALID
symlink_escape     : evidence symlink pointing outside root → false → INVALID
duplicate_path     : two entries canonicalizing equal → false → INVALID
directory_not_file : point an entry at a directory → false → INVALID
context_match      : perturb subject/candidate/env → false → RERUN_REQUIRED
```

The harness runs twice and asserts byte-identical semantic outcomes (no timestamps /
environment metadata in decision content) — the same two-run equality already required
in Phase 1.

## 10. Relationship to existing Formal Core V1

- Add `SpiraFormalCore/Domain4/{Evidence,Policy,Decision,Proofs}.lean` alongside the
  existing Domain 1/2/3 modules; extend `SpiraFormalCore/Proofs/All.lean`.
- Reuse the existing `ExplicitList`, `MachineContract`, `not_claimed`, and
  `decideAction` machinery. Do **not** create a second Lean package.
- Pinned toolchain stays `leanprover/lean4:v4.32.0`; keep the package dependency-free so
  `lake build` remains offline and re-checkable by an external reviewer.
- Add a Domain 4 raw-adapter conformance harness paralleling the Domain 3 one, so the
  Python flags are checked against the Lean model on fixtures.

## 11. Sequencing and gates

```text
1. Review and accept THIS proposal (research/authorization).
2. Freeze SPIRA_NESIRA_DOMAIN4_FLAGS_V1 (versioned schema artifact).
3. Freeze the NOT_PROVEN_IN_LEAN ledger (§3).
4. Define the decision table + precedence; confirm it is derivable from the accepted
   Phase 1 spec (else stop: SCOPE_REVISION_REQUIRED).
5. Only after review: implement Domain4 Lean modules + proofs.
6. Build the Python ↔ Lean conformance harness with a mutation pair per safety-critical
   flag (§8, §9).
7. Adversarial review, then external cold reproduction (lake build + harness) from a
   fresh clone — same bar as Phase 1.
```

No Lean or Python is written before step 1 is accepted. Steps 5–7 are a separate
authorization, not part of this proposal.

## 12. Integration boundary

```text
- This work does not alter the locked Phase 1 result or its delivery artifacts.
- The Domain 4 core does not wire itself into the combined verdict.
- No new public capability is claimed; nothing enters the public wheel or CLI.
- A Lean proof of the decision table is NOT a claim that Nesira is "formally proved" —
  the NOT_PROVEN_IN_LEAN ledger (§3) travels with any such statement.
```

## 13. Open questions for review

```text
- Is the flag set in §5 complete and minimal for the two Phase 1 artifact types?
- Does the accepted Phase 1 spec uniquely fix the precedence in §7?
- Should VALID_STRUCTURAL_ONLY and NOT_EVALUATED remain distinct statuses, or collapse,
  given both map to REPORT_NOT_EVALUATED?
- Is a Domain 4 conformance harness sufficient, or do we also want property-based
  generation of flag tuples to exercise the decision table exhaustively?
```

## 14. Bottom line

```text
Prove the decision table, not the parser, filesystem, signature stack, or runner.
Make PROCEED unrepresentable in Phase 1 rather than merely absent.
Freeze the flag schema and the NOT_PROVEN_IN_LEAN ledger before proving anything.
Bridge Python and Lean with a mutation pair per safety-critical flag.
This is a Phase 2 research path — not a change to the locked Phase 1.
```
