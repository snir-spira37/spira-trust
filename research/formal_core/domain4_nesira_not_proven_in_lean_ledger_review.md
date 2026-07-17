# SPIRA Domain 4 / Nesira NOT_PROVEN_IN_LEAN Ledger Review

## Verdict

```text
DOMAIN4_NESIRA_NOT_PROVEN_IN_LEAN_LEDGER_ACCEPTED
```

This review accepts the Domain 4 / Nesira NOT_PROVEN_IN_LEAN ledger and its
machine-readable JSON companion. It does not authorize Lean implementation,
Python implementation, fixtures, tests, decision-table implementation, Phase 2
implementation, public claims, or release work.

Reviewed artifacts:

```text
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.md
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.json
```

## Review Checklist

The review checked:

```text
1. All world -> flags claims are outside Lean proof scope.
2. NP-APPLIC-01 covers every flag that is N/A for any artifact_kind.
3. The positive claim is limited to flags -> contract.
4. No trust/signature/execution claim leaked into the proved side.
5. Every ledger ID is unique and stable.
6. The applicability matrix matches SPIRA_NESIRA_DOMAIN4_FLAGS_V1.
7. The JSON companion matches the Markdown ledger.
```

## Findings

### 1. Core Boundary Is Correct

The ledger correctly states:

```text
Lean proves: flags -> contract
Lean does not prove: world -> flags
```

This is the essential boundary for Domain 4. The proof may only reason over
typed flags that have already been classified by Python.

### 2. Adapter Faithfulness Is Properly Excluded

The ledger includes:

```text
NP-ADAPTER-01 through NP-ADAPTER-07
```

These entries cover JSON parsing, DSSE decoding, filesystem reads, symlink
resolution, SHA-256 over correct bytes, path canonicalization, and flag
faithfulness. This prevents a future Lean proof from being over-read as proof
that Python classified the world correctly.

### 3. Trust and Execution Claims Are Properly Excluded

The ledger includes:

```text
NP-TRUST-01 through NP-TRUST-06
```

These entries cover signatures, signer identity, signer authority, severance
authorization, permission to sever, and actual isolation execution. They remain
outside Domain 4 Phase 1 formal proof scope.

### 4. NP-APPLIC-01 Correctly Handles N/A Equals True

The review specifically tested the known semantic hazard:

```text
hash_ok = true for SEVERANCE_AUTHORIZATION
```

The ledger correctly prevents this from being read as:

```text
hash check performed
```

Instead it means only:

```text
hash check not applicable to SEVERANCE_AUTHORIZATION in V1
```

This guard is accepted and must be referenced by the future decision table.

### 5. Applicability Matrix Matches the Flag Schema

The matrix correctly marks the evidence-root file checks as applicable only for
`LEGACY_ISOLATION_RESULT`:

```text
evidence_present
hash_ok
path_safe
symlink_escape_absent
duplicate_path_free
directory_not_file_absent
```

It correctly marks `temporal_binding_ok` as applicable to
`SEVERANCE_AUTHORIZATION` and N/A for `LEGACY_ISOLATION_RESULT` in V1.

Accepted:

```text
artifact_kind branch required before consuming N/A flags
```

### 6. Positive Claim Is Properly Narrow

The ledger permits only a future conditional claim:

```text
Given faithful flags, the decision table is safe and deterministic.
```

It does not permit:

```text
Nesira is formally proved end to end
Python adapter is proved faithful
signatures are verified
isolation happened
severance is authorized
release is ready
```

### 7. JSON Companion Is Accepted

The JSON companion provides stable IDs and an applicability matrix suitable for
future machine checks. The review accepts it as the authoritative
machine-readable sibling of the Markdown ledger.

Future specs should reference ledger IDs such as:

```text
NP-APPLIC-01
NP-ADAPTER-05
NP-TRUST-03
```

instead of duplicating prose.

## Accepted Next Step

The next specification artifact may proceed under the existing authorization:

```text
research/formal_core/domain4_nesira_decision_table_v1_spec.md
```

The decision table must:

```text
branch on artifact_kind before consuming N/A flags
reference NP-APPLIC-01 for all N/A-true cases
avoid trust/signature/execution claims
keep PROCEED unrepresentable in Phase1Action
derive precedence from accepted Phase 1 semantics
stop with SCOPE_REVISION_REQUIRED if precedence is not determined
```

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
DOMAIN4_NESIRA_NOT_PROVEN_IN_LEAN_LEDGER_ACCEPTED

SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1_FROZEN
NP_ADAPTER_IDS_ACCEPTED
NP_TRUST_IDS_ACCEPTED
NP_APPLIC_01_ACCEPTED
NP_META_IDS_ACCEPTED
APPLICABILITY_MATRIX_ACCEPTED
MACHINE_READABLE_LEDGER_ACCEPTED

DECISION_TABLE_SPECIFICATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE1_REOPEN_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

