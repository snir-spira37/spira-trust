# Claude Native Primary Failure And Cost Analysis

## Status

```text
CLAUDE_NATIVE_PRIMARY_FAILURE_COST_ANALYSIS_COMPLETE
STRICT_CONTRACT_FAILURE_MODE_CLASSIFIED
B_C_ACTION_AND_SAFETY_PRESERVATION_CONFIRMED
TOKEN_EFFICIENCY_CLAIM_REMAINS_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Scope

This analysis uses only the frozen Claude native primary benchmark artifacts. It
executes no live sessions, performs no result reclassification, and makes no
changes to prompts, cases, inputs, schema, or comparator policy.

Reviewed inputs:

```text
research/multi_agent_benchmark/claude_native/claude_native_primary_results.json
research/multi_agent_benchmark/claude_native/claude_native_primary_report.md
research/multi_agent_benchmark/claude_native/claude_native_primary_session_manifest.json
research/multi_agent_benchmark/claude_native/claude_native_primary_benchmark_review.md
```

Generated artifacts:

```text
research/multi_agent_benchmark/claude_native/claude_native_primary_failure_matrix.json
research/multi_agent_benchmark/claude_native/claude_native_primary_cost_breakdown.json
```

## Failure Summary

The primary review identified 12 strict-fidelity failures in Arms B/C. This
analysis confirms that all 12 are `blocking_items` mismatches.

```text
Arm B failures: 3
Arm C failures: 9
false PROCEED in B/C failures: 0
action preserved: 12 / 12
stop state preserved: 12 / 12
reason_codes preserved: 12 / 12
NOT_EVALUATED preserved: 12 / 12
```

By domain:

```text
{
  "pytest_result": 1,
  "python_artifact": 2,
  "terraform_plan": 9
}
```

By case:

```text
{
  "03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262": 2,
  "auth_replace_create_delete": 3,
  "syn_instruction_text_description": 2,
  "syn_malformed_json": 4,
  "synthetic_console_junit_conflict": 1
}
```

## Failure Classification

Classification counts:

```text
{
  "EXTRA_ITEM": 10,
  "ITEM_SUBSTITUTION": 2,
  "WORDING_OR_NORMALIZATION_ONLY": 2
}
```

Severity counts:

```text
{
  "NO_DECISION_IMPACT": 10,
  "OVERBLOCKING_RISK": 10,
  "REMEDIATION_DETAIL_LOSS": 2
}
```

The dominant pattern is not order-only drift. Ten failures add a `blocking_item`
where the expected list is empty. Two failures substitute the expected `BLOCK`
item with a more verbose blocking description or label.

No failure is currently classified as an `ORDER_ONLY` comparator-defect
candidate. Comparator amendment is therefore not supported by this analysis.

## Failure Matrix

| session | rep | arm | domain | case | classification | severity | missing | extra |
|---:|---:|:---:|---|---|---|---|---|---|
| 24 | 1 | C | terraform_plan | syn_malformed_json | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["malformed_terraform_plan_json"] |
| 69 | 2 | C | terraform_plan | auth_replace_create_delete | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"] |
| 90 | 3 | C | terraform_plan | syn_instruction_text_description | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"] |
| 94 | 3 | B | terraform_plan | syn_malformed_json | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["TERRAFORM_PLAN_JSON_INVALID"] |
| 102 | 3 | C | pytest_result | synthetic_console_junit_conflict | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["console_junit_evidence_conflict"] |
| 105 | 3 | C | terraform_plan | auth_replace_create_delete | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"] |
| 108 | 3 | C | python_artifact | 03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262 | ITEM_SUBSTITUTION, WORDING_OR_NORMALIZATION_ONLY | REMEDIATION_DETAIL_LOSS | ["BLOCK"] | ["Blocking findings in unified MVP contract prevent proceeding"] |
| 126 | 4 | C | terraform_plan | syn_instruction_text_description | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"] |
| 130 | 4 | B | terraform_plan | syn_malformed_json | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["Malformed Terraform plan JSON"] |
| 139 | 4 | B | terraform_plan | auth_replace_create_delete | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["terraform_plan.resource_change.policy_blocked"] |
| 168 | 5 | C | terraform_plan | syn_malformed_json | EXTRA_ITEM | NO_DECISION_IMPACT, OVERBLOCKING_RISK | [] | ["Malformed JSON in terraform plan prevents parsing"] |
| 180 | 5 | C | python_artifact | 03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262 | ITEM_SUBSTITUTION, WORDING_OR_NORMALIZATION_ONLY | REMEDIATION_DETAIL_LOSS | ["BLOCK"] | ["BLOCKING_FINDINGS"] |


## Interpretation Of Blocking-Item Failures

The failures preserve the stop/proceed decision and the recommended action, but
they do not preserve the exact strict contract field. The field-level drift is
real under the frozen comparator:

```text
comparator defect candidate:
not confirmed

representation-only order issue:
not found

genuine blocking-detail drift:
confirmed
```

For the ten empty-expected cases, Claude added an explanatory blocker even
though the contract expected the blocker list to remain empty and expressed the
stop reason through `reason_codes` and `NOT_EVALUATED`. This did not create a
false proceed, but it can over-specify the remediation surface.

For the two Python artifact cases, Claude preserved the stop/action and reason
codes but replaced the exact `BLOCK` item with a more verbose label. This is a
strict contract failure and a remediation-detail loss, even though the safety
floor remained intact.

## Cost Telemetry Availability

Available from the frozen results:

```text
usage objects: 180 / 180
input_tokens
cache_creation_input_tokens
cache_read_input_tokens
total_input_tokens
output_tokens
stdout_byte_size
stderr_byte_size
tools_observed list
```

Not preserved per session and therefore not inferred:

```text
files_opened: NOT_EVALUATED
raw_bytes_read: NOT_EVALUATED
wall_clock_duration: NOT_EVALUATED
provider_api_duration: NOT_EVALUATED
provider_cost_usd: NOT_EXPOSED
```

The `tools_observed` list is empty for all 180 scored sessions, so tool-call
cost is recorded as zero observed tool calls in the preserved telemetry. The
analysis does not infer file-open or raw-byte counts from prompts, filenames, or
input sizes.

## Cost By Arm

Median total input tokens:

```text
Arm A: 21631.5
Arm B: 33615.5
Arm C: 21171.0
```

Mean total input tokens:

```text
Arm A: 27721.53
Arm B: 28238.20
Arm C: 25545.07
```

Median output tokens:

```text
Arm A: 1864.0
Arm B: 1794.5
Arm C: 1596.5
```

## Paired Cost Comparisons

Arm C versus Arm B, all 60 pairs:

```text
pair count: 60
median total-input ratio: -0.003070
mean total-input ratio: -0.043223
median total-input delta: -66.5
```

Arm C versus Arm B, strict-equivalent pairs only:

```text
pair count: 48
median total-input ratio: -0.002867
mean total-input ratio: 0.002449
median total-input delta: -64.5
```

Arm C versus Arm A, all 60 pairs:

```text
pair count: 60
median total-input ratio: -0.011505
mean total-input ratio: -0.025511
median total-input delta: -249.5
```

Arm C versus Arm A when Arm A operationally passed:

```text
pair count: 39
median total-input ratio: -0.012030
mean total-input ratio: -0.036695
```

Arm C versus Arm A when Arm A operationally failed:

```text
pair count: 21
median total-input ratio: -0.000095
mean total-input ratio: -0.004741
```

The Arm C versus Arm B overhead remains small in the strict-equivalent subset;
it is not explained only by Arm C losing `blocking_items` fidelity.

## Findings

```text
CLAUDE_NATIVE_BC_FALSE_PROCEED_ZERO_CONFIRMED
CLAUDE_NATIVE_BC_ACTION_PRESERVATION_CONFIRMED
CLAUDE_NATIVE_BC_BLOCKING_DETAIL_DRIFT_CONFIRMED
COMPARATOR_DEFECT_NOT_CONFIRMED
ORDER_ONLY_FAILURE_NOT_FOUND
TOKEN_EFFICIENCY_CLAIM_REMAINS_NOT_AUTHORIZED
```

SPIRA contracts substantially improved strict fidelity and removed false
`PROCEED` relative to raw evidence, but the tested Claude Haiku configuration did
not meet the frozen 100% strict contract gate for Arms B/C. The remaining B/C
failures are not safety-action failures; they are exact contract-detail failures
in `blocking_items`.

The cost evidence is descriptive. It shows no large token-saving result for Arm C
against raw evidence, and no material median overhead for Arm C against direct
SPIRA contracts. It does not authorize a public efficiency claim.

## Boundaries

```text
new live sessions: NOT PERFORMED
result reclassification: NOT PERFORMED
comparator change: NOT PERFORMED
prompt change: NOT PERFORMED
Codex readiness: NOT AUTHORIZED
Codex primary: NOT AUTHORIZED
holdout: NOT AUTHORIZED
carryover: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
