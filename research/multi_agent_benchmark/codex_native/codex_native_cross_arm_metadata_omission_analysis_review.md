# Codex Native Cross-Arm Metadata Omission Analysis Review

## Status

```text
CODEX_NATIVE_CROSS_ARM_METADATA_OMISSION_ANALYSIS_REVIEW_COMPLETE
CODEX_NATIVE_CROSS_ARM_METADATA_OMISSION_ANALYSIS_ACCEPTED

MODEL_SERIALIZATION_VARIABILITY_CONFIRMED
SCHEMA_ENFORCES_STRUCTURE_NOT_ORACLE_CONTENT
MODEL_INSTANCE_CONTENT_OMISSION_CONFIRMED
NO_SCHEMA_DEFECT_CONFIRMED
COMPARATOR_OR_ORACLE_DEFECT_NOT_CONFIRMED

CONTRACT_PRESENTATION_AMBIGUITY_REMAINS_CANDIDATE
PROMPT_CONTRACT_PRESERVATION_WEAKNESS_REMAINS_CANDIDATE

CODEX_NATIVE_STRICT_METADATA_RELIABILITY_NOT_READY
CODEX_PRIMARY_NOT_AUTHORIZED
```

## Review Scope

This review covers only:

```text
codex_native_cross_arm_metadata_omission_analysis.json
codex_native_cross_arm_metadata_omission_analysis.md
```

The review verifies that the analysis stayed within the authorization:

```text
EXISTING_RESULTS_ONLY
PYTEST_CLEAN_SUCCESS_ARM_B_AND_ARM_C_ONLY
NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
NO_PROMPT_CHANGE
NO_SCHEMA_CHANGE
NO_ORACLE_CHANGE
NO_COMPARATOR_CHANGE
NO_INPUT_CHANGE
```

## Evidence Chain

The analysis correctly uses the committed evidence chain:

```text
original Codex readiness:
Arm B failure in pytest_result / synthetic_clean_success

failure analysis:
genuine metadata omission, no comparator/oracle defect

reliability diagnostic:
Arm B exact 10 / 10
Arm C exact 4 / 5
same omission class observed once in Arm C
```

The analysis does not rely on raw private responses and does not expose private
paths or session credentials.

## Finding 1: Source Contract Was Not Defective

Accepted.

Both Arm B and Arm C frozen inputs contain:

```text
reason_codes:
TESTS_PASSED

not_claimed:
producer_correctness
software_safety
```

Arm B stores reason codes under:

```text
direct_domain_contract.policy_action.reason_codes
```

Arm C stores reason codes under:

```text
unified_mvp_contract.reason_codes
```

Both presentations are explicit. The source SPIRA contract is not shown to be
missing or contradictory.

## Finding 2: The Model Understood The Action

Accepted.

In the original failure and the diagnostic failure:

```text
PROCEED preserved
stop=false preserved
blocking_items=[] preserved
not_evaluated=[] preserved
false PROCEED=0
```

The readiness failure was not an action failure, safety failure, schema failure,
usage failure, or isolation failure.

## Finding 3: Strict Metadata Reconstruction Was Not Reliable

Accepted.

The missing values were real contractual content:

```text
TESTS_PASSED
producer_correctness
software_safety
```

The failures were not order-only, path-normalization-only, or duplicate-only
differences. Codex returned schema-valid objects that did not preserve the
oracle-specific metadata.

## Finding 4: Schema Validity Is Not Oracle Exactness

Accepted.

The output schema requires fields and array types, but it does not encode the
case-specific oracle values for every session. Therefore:

```text
schema-valid output
does not imply
oracle-exact output
```

This is not a schema defect. It confirms that the comparator remains necessary
for strict fidelity.

## Finding 5: Presentation Weakness Is A Candidate, Not A Proven Defect

Accepted.

The positive pytest case appears vulnerable to metadata omission because the
operational decision is simple:

```text
tests passed
no blockers
PROCEED
```

However, the same frozen inputs usually produced exact metadata:

```text
Arm B diagnostic: 10 / 10 exact
Arm C diagnostic: 4 / 5 exact
```

That means the evidence does not prove a deterministic presentation defect. It
does support a global presentation-amendment discussion if the project wants to
make positive-case metadata more salient.

## Finding 6: Codex Native Primary Remains Blocked

Accepted.

The readiness gate required strict B/C fidelity. The diagnostic did not restore
that gate; it showed cross-arm intermittent metadata omission instead.

Therefore:

```text
Codex primary: NOT AUTHORIZED
new live sessions: NOT AUTHORIZED
holdout: NOT AUTHORIZED
carryover: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```

## Product Implication

This review accepts the architectural implication:

```text
The SPIRA machine contract should remain the authoritative artifact.
The LLM should not be treated as a deterministic serializer of that artifact.
```

A future product design may mechanically pass through the SPIRA contract and
ask the model to explain it separately. That would be a new globally authorized
design change, not a reclassification of these benchmark results.

## Final Verdict

```text
CODEX_NATIVE_CROSS_ARM_METADATA_OMISSION_ANALYSIS_ACCEPTED
MODEL_SERIALIZATION_VARIABILITY_CONFIRMED
CODEX_NATIVE_STRICT_METADATA_RELIABILITY_NOT_READY
CODEX_PRIMARY_NOT_AUTHORIZED
```
