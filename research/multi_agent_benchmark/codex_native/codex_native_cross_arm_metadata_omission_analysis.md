# Codex Native Cross-Arm Metadata Omission Analysis

## Status

```text
CODEX_NATIVE_CROSS_ARM_METADATA_OMISSION_ANALYSIS_COMPLETE
EXISTING_RESULTS_ONLY
NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
CODEX_PRIMARY_NOT_AUTHORIZED
```

This analysis uses only the already committed Codex Native readiness and
diagnostic artifacts. It does not rerun Codex, reclassify any result, alter the
comparator, or change prompts, inputs, schema, oracle, MVP code, or producers.

## Scope

The authorized scope is the single positive pytest case where the same metadata
omission pattern was observed across direct and unified SPIRA contracts:

```text
domain: pytest_result
case: synthetic_clean_success
arms: B and C
```

Expected metadata:

```text
reason_codes:
TESTS_PASSED

not_claimed:
producer_correctness
software_safety
```

## Source Artifacts

```text
readiness results:
research/multi_agent_benchmark/codex_native/codex_native_readiness_results.json
sha256: 6d63140452095527abc70a4ba82ee4199713e64e93aeedd5671379e99f3ce93e

failure analysis:
research/multi_agent_benchmark/codex_native/codex_native_readiness_failure_analysis.json
sha256: 0920275b00520d513e38574ac4090751580aff91b6d35d7fb8546c8259f3f04b

reliability diagnostic:
research/multi_agent_benchmark/codex_native/codex_native_readiness_reliability_diagnostic_results.json
sha256: 5a8613c389748964d51b7438de799f5049636c709699ceca76d9df42b28623ce

Arm B frozen input:
research/multi_agent_benchmark/frozen_inputs/pytest_result/synthetic_clean_success/arm_B.json
sha256: 71fd835fbb3ba6de2d49bc4bbfdaee693a4005bece17e37fdbfb6dc5110553d8

Arm C frozen input:
research/multi_agent_benchmark/frozen_inputs/pytest_result/synthetic_clean_success/arm_C.json
sha256: 8e4cadcc3ed6ab9116b2603abb20a909c8eba6ab5256afc67bb999abacb71203
```

## What Happened

The original readiness failure occurred in Arm B:

```text
Arm B original readiness:
expected reason_codes: ["TESTS_PASSED"]
observed reason_codes: []

expected not_claimed: ["producer_correctness", "software_safety"]
observed not_claimed: []

action preserved: true
stop state preserved: true
blocking_items preserved: true
not_evaluated preserved: true
false PROCEED: false
schema valid: true
usage available: true
```

The reliability diagnostic then showed:

```text
Arm B:
10 / 10 exact

Arm C:
4 / 5 exact
1 / 5 same metadata omission class
```

The Arm C diagnostic failure was not a safety failure:

```text
action preserved: true
stop state preserved: true
blocking_items preserved: true
not_evaluated preserved: true
false PROCEED: false
schema valid: true
usage available: true
```

But it was still a strict contract failure:

```text
expected reason_codes: ["TESTS_PASSED"]
observed reason_codes: ["READING_INPUT"]

expected not_claimed: ["producer_correctness", "software_safety"]
observed not_claimed: []
```

Both failures returned schema-valid JSON objects that described the act of
reading or evaluating `frozen_input.json`, rather than the final oracle-exact
SPIRA contract result.

## Four-Layer Finding

### 1. SPIRA Source Contract

```text
status: PASS
```

Both frozen contracts contained the required metadata.

Arm B:

```text
reason_codes location:
evidence_surface.direct_domain_contract.policy_action.reason_codes

not_claimed location:
evidence_surface.direct_domain_contract.not_claimed
```

Arm C:

```text
reason_codes location:
evidence_surface.unified_mvp_contract.reason_codes

not_claimed location:
evidence_surface.unified_mvp_contract.not_claimed
```

The same shared proof identifiers were present:

```text
producer_contract_hash:
39e93a9ec8e090dfacc89ae715e7f882cc55fafa718efe3349f70506697b58e3

result_identity_sha256:
41faa8cc93583874449197ea874c2afe2097362b8b931a596ce6e1eee7b92dfc

scope_identity_sha256:
69bf76b5f4c8cf9ed3b0ca2412f700c8f350571899d22426484e37eccb54100c
```

### 2. Contract Transfer To The Model

```text
status: PASS_WITH_PRESENTATION_DIFFERENCES
```

The metadata was visible to the model in both arms. Arm B nests the action
metadata under `policy_action`; Arm C places it at the unified contract top
level. That is a presentation difference, but both are explicit.

The shared prompt also instructed the model to preserve:

```text
reason_codes
NOT_EVALUATED entries
blocking items
evidence/proof references
not_claimed boundaries
```

### 3. Model Action Understanding

```text
status: PASS
```

In the original Arm B failure and the Arm C diagnostic failure, Codex preserved:

```text
PROCEED
stop=false
blocking_items=[]
not_evaluated=[]
false PROCEED=0
```

The model understood the operational decision.

### 4. Model Contract Reconstruction

```text
status: FAIL_INTERMITTENT
```

The model did not reconstruct the full contract metadata deterministically. It
sometimes emitted a valid object about reading/evaluating the input instead of
the final SPIRA decision contract.

This is not a path/order/normalization issue. The omitted values are contractual
content:

```text
TESTS_PASSED
producer_correctness
software_safety
```

## Schema Finding

The schema worked as a structural gate but not as an oracle-content gate.

```text
schema requires reason_codes field: true
schema requires not_claimed field: true
schema allows empty reason_codes array: true
schema allows empty not_claimed array: true
schema allows arbitrary reason code strings: true
schema encodes case-specific oracle content: false
```

Therefore:

```text
schema-valid
!=
oracle-exact
```

This is not a schema defect. It is a known boundary: JSON Schema can require
fields and types, while the comparator must enforce case-specific oracle
content.

## Cause Assessment

### Model Serialization Variability

```text
MODEL_SERIALIZATION_VARIABILITY_CONFIRMED
```

Evidence:

```text
The original Arm B omission did not reproduce in 10 / 10 repetitions.
The same omission class appeared once in 5 matched Arm C repetitions.
Most identical presentations succeeded; one emitted status-like JSON.
```

Codex understood the action but was not a deterministic serializer of every
contract field.

### Global Contract Presentation Ambiguity

```text
CONTRACT_PRESENTATION_AMBIGUITY_REMAINS_CANDIDATE
```

The successful-case metadata appears less operationally salient than STOP/BLOCK
metadata. The shared prompt asks for exact preservation, but the observed
failures suggest that positive-case rationale and not-claimed boundaries can be
dropped when the model focuses on the act of reading the input or on the
operational action.

This analysis does not prove a deterministic presentation defect because the
same frozen presentations usually succeeded.

### Prompt Contract Preservation Weakness

```text
PROMPT_CONTRACT_PRESERVATION_WEAKNESS_REMAINS_CANDIDATE
```

The prompt already required exact preservation, but it did not prevent a
schema-valid interim/status output. Any prompt amendment must be global across
Claude, Codex, DeepSeek, and future tracks. No prompt change is authorized here.

### Comparator Or Oracle Defect

```text
COMPARATOR_OR_ORACLE_DEFECT_NOT_CONFIRMED
```

The expected values are present in both frozen inputs. The comparator identified
real missing/substituted content, not a harmless order-only or normalization
difference.

## Terminal Findings

```text
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

## Architectural Implication

The strongest conclusion is architectural:

```text
SPIRA machine contract:
stable source of truth

LLM-generated reconstruction:
not a deterministic serializer of that source of truth
```

For product design, this supports a separation:

```text
machine-readable SPIRA contract
→ passed through mechanically

LLM explanation
→ generated separately and treated as commentary
```

The LLM may understand and explain the decision while still failing strict
metadata reproduction. Therefore a future product flow should not require the
model to regenerate the machine contract as the authoritative artifact.

## Next Gate

No primary benchmark is authorized.

Possible next decisions are:

```text
1. Open a global contract-presentation amendment discussion.
2. Keep the current strict contract and classify Codex Native as not ready for primary.
3. Design a future product protocol where the machine contract is passed through
   mechanically and the model only explains it.
```

Any change to prompt, comparator, schema, oracle, input presentation, or scoring
policy requires separate global authorization.
