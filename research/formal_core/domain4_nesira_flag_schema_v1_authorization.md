# SPIRA Domain 4 / Nesira Flag Schema V1 Authorization

## Verdict

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_SPECIFICATION_AUTHORIZED
```

This authorization opens the next specification step for the accepted Domain 4
/ Nesira formal-core research path. It authorizes only the design and review of
the typed flag interface between the Python Nesira Phase 1 adapter and the
future Lean decision core.

It does not authorize Lean implementation, Lean proof scripts, Python adapter
changes, Nesira validator changes, Phase 1 changes, Phase 2 implementation,
product integration, public claims, or release work.

## Prior Accepted Inputs

This authorization depends on the accepted proposal and review:

```text
DOMAIN4_NESIRA_FORMAL_CORE_PROPOSAL_ACCEPTED

proposal:
research/formal_core/domain4_nesira_formal_core_proposal.md

proposal review:
research/formal_core/domain4_nesira_formal_core_proposal_review.md
```

The accepted proof boundary remains:

```text
Lean proves:
typed flags + policy -> safe Phase 1 decision table

Lean does not prove:
raw parsing, filesystem behavior, hash computation, signatures,
signer authority, isolation execution, or Python flag faithfulness
```

## Authorized Artifacts

The next step may create only specification and review artifacts:

```text
research/formal_core/domain4_nesira_flag_schema_v1_spec.md
research/formal_core/domain4_nesira_decision_table_v1_spec.md
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.md
research/formal_core/domain4_nesira_conformance_harness_v1_spec.md
research/formal_core/domain4_nesira_flag_schema_v1_review.md
```

The review may accept, reject, or require revision of the specification package.

## Required Flag Schema Content

The flag schema specification must define:

```text
schema id
schema version
flag names
flag types
precise semantic meaning of each flag
producer of each flag
whether the flag is safety-critical
which mutation pair proves adapter sensitivity
which Phase 1 fixture family exercises the flag
decision-table role
not_claimed / not_evaluated implications, if any
```

The schema must be total: every legal flag tuple must have a deterministic
decision-table outcome. No undefined tuple may fall through to a permissive
default.

## Minimum Required Flags

The specification must address at least these proposed flags:

```text
schema_valid
evidence_present
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
context_match
temporal_binding_ok
evaluated
```

The specification may propose additional flags only if it explains why the
accepted Phase 1 behavior cannot be modeled without them.

## Safety-Critical Flags

The following flags are provisionally safety-critical and must receive explicit
mutation-pair requirements:

```text
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
context_match
```

For each safety-critical flag, the conformance specification must require a
minimal mutation pair that forces the Python adapter to flip that flag and
therefore changes the deterministic outcome.

## Required Decision Table Properties

The decision-table specification must define:

```text
Phase1Action type
status values
action projection to the machine contract
stop value
reason-code precedence
blocking_items behavior
not_evaluated behavior
not_claimed preservation
deterministic precedence for simultaneous failures
```

The Phase 1 action type must not contain a `PROCEED` constructor:

```text
PROCEED_UNREPRESENTABLE_IN_PHASE1_ACTION_TYPE
```

Any future `PROCEED`-capable action type belongs only to a separately
authorized Phase 2 trust layer.

## Precedence Constraint

The precedence table must be derived from accepted Phase 1 semantics. If the
existing Phase 1 specification does not determine the order among simultaneous
failures, the specification review must return:

```text
SCOPE_REVISION_REQUIRED
```

The schema work is not authorized to invent a new product behavior.

## Required NOT_PROVEN_IN_LEAN Ledger

The ledger must explicitly preserve the following non-scope items:

```text
JSON parsing correctness
DSSE envelope / payload decoding correctness
filesystem behavior
symlink resolution correctness
SHA-256 computed over the correct bytes
cryptographic signature trust
signer identity and authority
actual isolation execution
permission to sever
public wheel / CLI packaging
release readiness
faithfulness of Python flag classification
```

The ledger must state that Python flag-classification faithfulness is covered
only by conformance tests and mutation pairs, not by Lean proof.

## Required Harness Specification

The conformance harness specification must define:

```text
Python adapter output shape
Lean model input shape
fixture inventory
mutation-pair inventory
two-run semantic equality requirement
expected result fields
false-valid counters
false-PROCEED counters
path/hash/context mutation counters
external reproduction requirements
```

The harness may be specified, but not implemented, in this stage.

## Not Authorized

This authorization does not authorize:

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

## Required Review Outcomes

The review must end in exactly one of:

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_ACCEPTED
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_NEEDS_REVISION
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_REJECTED
```

Even `ACCEPTED` does not authorize Lean or Python implementation. It only
permits a later implementation authorization request.

## Status

```text
DOMAIN4_NESIRA_FLAG_SCHEMA_V1_SPECIFICATION_AUTHORIZED

FLAG_SCHEMA_SPECIFICATION_AUTHORIZED
DECISION_TABLE_SPECIFICATION_AUTHORIZED
NOT_PROVEN_IN_LEAN_LEDGER_AUTHORIZED
CONFORMANCE_HARNESS_SPECIFICATION_AUTHORIZED
FLAG_SCHEMA_REVIEW_REQUIRED

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

