# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Specification Review

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_SPEC_ACCEPTED
SPECIFICATION_ONLY
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO
DOMAIN_1_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_AUTHORIZATION_REQUIRED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 1 raw-adapter conformance specification is accepted as a specification-only artifact.

It defines the bounded Python artifact evidence boundary:

```text
raw Python artifact evidence
-> tested / untrusted Domain 1 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

No implementation change, parser proof, Lean proof, fixture materialization, live agent session, benchmark execution, production claim, or release is authorized by this review.

## Accepted Boundary

The accepted raw input scope is limited to:

```text
artifact bytes or synthetic artifact byte hash
wheel / ZIP container metadata summary
dist-info RECORD entries
dist-info METADATA summary
optional SBOM or provenance summary
manifest-declared artifact and file hashes
accepted Domain 1 identity-baseline records
```

The following remain outside the proof and conformance boundary:

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

## Accepted Input States

The specification appropriately requires top-level classification for:

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

These states cover the accepted Domain 1 baseline, identity-preservation obligations, parser uncertainty, proof binding, missing context, and fail-closed behavior.

## Preservation Requirements

The specification correctly treats identity fields and explicit lists as semantic contract data.

The later adapter and conformance harness must preserve:

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

The accepted legacy mapping remains:

```text
ASK_HUMAN -> REPORT_NOT_EVALUATED
```

This does not change the Formal Core V1 action algebra.

## Fail-Closed Obligations

The accepted specification preserves the core safety rule:

```text
blocked or uncertain Python artifact evidence must not produce unsafe PROCEED
```

The later fixture and conformance stages must verify fail-closed behavior for:

```text
RECORD missing or malformed
artifact hash mismatch
claims root mismatch
SBOM missing when required
previous-version or context unknown
unsupported format
incomplete evidence
private or sensitive path exposure
internal adapter failure
```

## Not-Claimed Boundary

The accepted Domain 1 boundaries are:

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

These must not be converted into positive claims or false negatives.

## Fixture Plan Acceptance

The proposed fixture plan is accepted as the minimum fixture materialization target for the next authorization:

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

Each fixture must include explicit expected outcomes. Fixtures without expected typed evidence and expected machine contract must not be accepted.

## Explicitly Not Accepted

This review does not accept or authorize:

```text
DOMAIN_1_ADAPTER_IMPLEMENTATION_CHANGE
RAW_WHEEL_ZIP_PARSER_CHANGE
RECORD_OR_SBOM_PARSER_CHANGE
LEAN_DEFINITION_CHANGE
LEAN_PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
NEW_FIXTURE_MATERIALIZATION
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_PROOF_CLAIM
PACKAGE_SAFETY_CLAIM
PRODUCTION_CLAIM
RELEASE
```

## Next Authorized Step Required

The next step must be a separate authorization:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That authorization may materialize the bounded fixture corpus and expected outcomes. It must still not change the Domain 1 adapter implementation or claim raw wheel / ZIP / RECORD / SBOM parser proof.
