# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Specification

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_SPEC_PROPOSED
SPECIFICATION_ONLY
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_PROOF_NOT_CLAIMED
```

## 1. Purpose

This specification defines the Domain 1 raw-adapter boundary:

```text
raw Python artifact evidence
-> Domain 1 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

It does not implement or prove the adapter. It specifies what a later fixture and conformance phase must test.

## 2. In-Scope Raw Inputs

Domain 1 raw adapter conformance is limited to bounded Python artifact fixture evidence:

```text
artifact bytes or synthetic artifact byte hash
wheel / ZIP container metadata summary
dist-info RECORD entries
dist-info METADATA summary
optional SBOM or provenance summary
manifest-declared artifact and file hashes
accepted Domain 1 identity-baseline records
```

Out of scope for this phase:

```text
arbitrary wheel / ZIP parser proof
arbitrary RECORD parser proof
arbitrary SBOM parser proof
PyPI correctness
package installation correctness
dependency resolution correctness
malware detection
software safety
package safety
license compliance
runtime behavior
filesystem correctness
LLM or agent behavior
```

## 3. Input State Classification

The adapter must classify each raw artifact bundle into exactly one top-level input state:

```text
SUPPORTED_IDENTITY_BASELINE_RECORD
SUPPORTED_ARTIFACT_IDENTITY_PRESENT
RECORD_PRESENT_AND_MATCHING
RECORD_MISSING_OR_MALFORMED
ARTIFACT_HASH_MISMATCH
CLAIMS_ROOT_MISMATCH
SBOM_PRESENT_UNVERIFIED
SBOM_MISSING
PREVIOUS_VERSION_OR_CONTEXT_UNKNOWN
FORMAT_UNSUPPORTED
INCOMPLETE_EVIDENCE
PRIVATE_OR_SENSITIVE_PATH_PRESENT
INTERNAL_ADAPTER_FAILURE
```

### 3.1 Supported Identity Baseline Record

Accepted Domain 1 baseline records must preserve:

```text
artifact_sha256
subject_sha256
canonical_claims_bytes_sha256
claims_merkle_root
context_sha256
canonical_decision_bytes_sha256
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
unification_id
reason_codes
not_evaluated
worst_claim_status
legacy recommended_agent_action
Formal Core action projection
```

Legacy `ASK_HUMAN` maps to:

```text
REPORT_NOT_EVALUATED
```

without adding `ASK_HUMAN` to the Formal Core V1 action algebra.

### 3.2 Supported Artifact Identity Present

If artifact and subject identity are present but required review context is unavailable:

```text
action = REPORT_NOT_EVALUATED
reason_codes includes REPORT_NOT_EVALUATED or HUMAN_REVIEW_REQUIRED
not_evaluated preserves missing context facts
PROCEED forbidden unless all policy-required checks are explicitly satisfied
```

### 3.3 RECORD Present And Matching

If RECORD entries are present and match declared file hashes:

```text
artifact identity claims preserved
record identity claims preserved
not_claimed still preserves package/software safety boundaries
```

This state alone does not imply software safety, dependency safety, or producer correctness.

### 3.4 RECORD Missing Or Malformed

Required behavior:

```text
action = REPORT_NOT_EVALUATED
reason_codes includes PYTHON_ARTIFACT_RECORD_MISSING_OR_MALFORMED
not_evaluated preserves RECORD parse/availability failure
PROCEED forbidden
```

### 3.5 Artifact Hash Mismatch

Required behavior:

```text
action = STOP_BLOCKED
reason_codes includes PYTHON_ARTIFACT_HASH_MISMATCH
blocking_items preserves mismatched identity
PROCEED forbidden
```

### 3.6 Claims Root Mismatch

Required behavior:

```text
action = STOP_BLOCKED
reason_codes includes PYTHON_ARTIFACT_CLAIMS_ROOT_MISMATCH
blocking_items preserves root mismatch
PROCEED forbidden
```

### 3.7 SBOM Present Unverified

Required behavior:

```text
SBOM presence preserved as evidence
SBOM correctness not claimed
not_claimed preserves dependency safety and package safety boundaries
```

### 3.8 SBOM Missing

Required behavior:

```text
action = REPORT_NOT_EVALUATED
not_evaluated includes missing SBOM when required by policy
PROCEED forbidden when policy requires SBOM evidence
```

### 3.9 Previous Version Or Context Unknown

Required behavior:

```text
action = REPORT_NOT_EVALUATED
not_evaluated includes missing previous-version or bounded-context facts
legacy ASK_HUMAN maps to REPORT_NOT_EVALUATED
PROCEED forbidden
```

### 3.10 Format Unsupported

Required behavior:

```text
action = REPORT_NOT_EVALUATED
reason_codes includes PYTHON_ARTIFACT_FORMAT_UNSUPPORTED
not_evaluated records unsupported format
PROCEED forbidden
```

### 3.11 Incomplete Evidence

Required behavior:

```text
action = REPORT_NOT_EVALUATED
not_evaluated preserves all required unavailable facts
PROCEED forbidden
```

### 3.12 Private Or Sensitive Path Present

Private local paths and sensitive markers must not leak into public contract fields.

Required behavior:

```text
private/sensitive path identity may be recorded only in safe classified form
plaintext local user path or secret marker absent from public contract fields
action != PROCEED when sensitive/private exposure affects required evidence
```

### 3.13 Internal Adapter Failure

Required behavior:

```text
fail closed
PROCEED forbidden
error recorded outside the authoritative contract when needed
```

## 4. Required Typed Evidence Fields

The adapter output must be projectable into Formal Core V1 typed evidence with:

```text
domain_id = python_artifact
subject_id
schema_version
producer_id
evidence_validity
typed_claims
evidence_refs
proof_refs
policy_id
policy_schema_version
policy_required_claims
policy_blocking_rules
policy_not_claimed_rules
```

The adapter must preserve:

```text
artifact identity
subject identity
claims root
context identity
decision identity
compact-reference identity
proof identity
unification identity
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
worst claim status
legacy action and Formal Core action projection
```

## 5. Mapping Obligations

### 5.1 Baseline Record Projection

For an accepted Domain 1 baseline record:

```text
legacy ASK_HUMAN -> REPORT_NOT_EVALUATED
legacy STOP_BLOCKED -> STOP_BLOCKED
legacy REPORT_NOT_EVALUATED -> REPORT_NOT_EVALUATED
legacy PROCEED -> PROCEED only if no blocker and no required unknown exists
```

### 5.2 Identity Preservation

All SHA-256 identity fields must be preserved exactly:

```text
artifact_sha256
subject_sha256
canonical_claims_bytes_sha256
claims_merkle_root
context_sha256
canonical_decision_bytes_sha256
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
```

### 5.3 No Silent Pass For Unknowns

If `not_evaluated` is non-empty:

```text
the item remains in typed evidence and machine contract
action != PROCEED unless policy explicitly marks it non-required
```

### 5.4 Blocking Prevents PROCEED

If an artifact mismatch, claims-root mismatch, or policy-active block exists:

```text
action = STOP_BLOCKED
PROCEED forbidden
blocking_items preserved
```

### 5.5 Not Claimed

The adapter must preserve Domain 1 boundaries:

```text
producer_correctness
software_safety
package_safety
dependency_safety
license_compliance
malware_absence
universal_supply_chain_coverage
runtime_behavior
```

These boundaries must not be converted into false negatives or positive claims.

## 6. Fixture Corpus Required Before Implementation

A later fixture authorization should materialize at least:

```text
3 accepted identity baseline records
3 artifact identity present records
3 RECORD present and matching records
3 RECORD missing or malformed records
3 artifact hash mismatch records
3 claims root mismatch records
2 SBOM present unverified records
2 SBOM missing records
3 previous-version/context unknown records
2 unsupported format records
2 incomplete evidence records
2 private/sensitive path records
2 internal adapter failure simulations
```

Each fixture must include expected:

```text
input_state
typed evidence projection
Formal Core contract
legacy action
Formal Core action
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
identity hash fields
unification_id
```

## 7. Differential Conformance Plan

A later implementation must compare:

```text
accepted Domain 1 identity baseline
new synthetic raw-adapter fixtures
raw fixture to typed-evidence projection
Formal Core V1 action/list preservation semantics
existing Domain 1 conformance runner
```

Acceptance requires:

```text
no false PROCEED
no identity hash loss
no reason_codes loss
no blocking_items loss
no NOT_EVALUATED loss
no not_claimed loss
no evidence/proof identity loss
no sensitive/private path leak
accepted Domain 1 baseline still passes
full pytest passes
```

## 8. Claim Boundary

Allowed after this specification:

```text
SPIRA has specified a Domain 1 raw-adapter conformance boundary for mapping bounded Python artifact evidence into Formal Core V1 typed evidence.
```

Disallowed:

```text
SPIRA has formally proved raw wheel / ZIP parsing.
SPIRA has proved RECORD parsing, SBOM parsing, PyPI correctness, package installation, dependency safety, malware absence, software safety, license compliance, or runtime behavior.
SPIRA is release-ready based on this specification.
```

## 9. Recommended Next Authorization

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That next step should materialize the fixture corpus only. It should still not change the Domain 1 adapter implementation or claim raw parser proof.
