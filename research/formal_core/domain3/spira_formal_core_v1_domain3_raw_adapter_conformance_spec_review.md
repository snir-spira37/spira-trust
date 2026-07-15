# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Specification Review

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_SPEC_ACCEPTED
SPECIFICATION_ONLY
RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO
DOMAIN_3_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_AUTHORIZATION_REQUIRED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 3 raw-adapter conformance specification is accepted as a specification-only artifact.

It defines the bounded Terraform Plan evidence boundary:

```text
raw Terraform Plan evidence
-> tested / untrusted Domain 3 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

No implementation change, parser proof, Lean proof, live agent session, benchmark execution, production claim, or release is authorized by this review.

## Accepted Boundary

The accepted raw input scope is limited to:

```text
plan.json
plan.json.invalid
main.tf when present as optional provenance
manifest-declared file hashes
embedded spira_optional_provenance fields
```

The following remain outside the proof and conformance boundary:

```text
terraform execution correctness
provider behavior
live cloud state
cost estimation
security/compliance assessment
full Terraform schema proof
arbitrary JSON parser proof
operating-system or filesystem correctness
LLM or agent behavior
```

This preserves the Formal Core V1 architecture: raw parsing and adapter extraction are tested and bounded, while the core contract decision remains the formal target.

## Accepted Input States

The specification appropriately requires a top-level classification for:

```text
SUPPORTED_NO_CHANGES
SUPPORTED_WITH_EFFECTIVE_CHANGES
PLAN_ERRORED
PLAN_NOT_APPLYABLE
PLAN_INCOMPLETE
FORMAT_UNSUPPORTED
JSON_INVALID
SENSITIVE_OR_UNKNOWN_VALUES_PRESENT
OPTIONAL_PROVENANCE_PRESENT
INTERNAL_ADAPTER_FAILURE
```

These states are sufficient for the next fixture phase because they cover:

```text
safe no-change plans
resource-change blockers
errored plans
non-applyable plans
incomplete plans
unsupported formats
malformed JSON
unknown and sensitive values
optional provenance
adapter-internal failure
```

## Preservation Requirements

The specification correctly treats explicit lists and references as semantic contract data, not presentation formatting.

The later adapter and conformance harness must preserve:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
subject identity
context identity
unification identity
resource action lists
replace paths
unknown paths
sensitive paths
optional provenance states
```

The following distinctions remain mandatory:

```text
NOT_EVALUATED is not PASS
not_claimed is not false
empty blocking_items is not unknown blocking status
unknown values are not successful evaluation
sensitive path identity is not plaintext sensitive value disclosure
optional provenance is not infrastructure correctness
```

## Fail-Closed Obligations

The accepted specification preserves the core safety rule:

```text
blocking or uncertain Terraform evidence must not produce unsafe PROCEED
```

The later fixture and conformance stages must verify fail-closed behavior for:

```text
effective resource changes
plan errors
not-applyable plans
incomplete plans
unsupported format versions
invalid JSON
unknown values
sensitive values
internal adapter failures
```

In all such cases, `PROCEED` must be forbidden unless the accepted Domain 3 policy explicitly defines a safe no-change condition.

## Sensitive Value Boundary

The sensitive-value requirement is accepted with an important boundary:

```text
sensitive path identity must be preserved
plaintext sensitive values must not appear in public contract fields
```

The next fixture corpus must include synthetic sensitive values only. It must not introduce real credentials, private infrastructure identifiers, or live cloud secrets.

## Fixture Plan Acceptance

The proposed fixture plan is accepted as the minimum fixture materialization target for the next authorization:

```text
3 no-change plans
3 create/update/delete plans
3 replace plans with replace_paths
2 errored plans
2 not-applyable plans
2 incomplete plans
2 unsupported format plans
2 invalid JSON plans
3 unknown path plans
3 sensitive path plans
2 optional provenance plans
2 duplicate resource-address plans
2 internal adapter failure simulations
```

Each fixture must include expected typed evidence and expected Formal Core contract fields. Fixtures without explicit expected outcomes must not be accepted.

## Differential Plan Acceptance

The differential conformance plan is accepted.

The future conformance phase must compare:

```text
existing Terraform Plan producer output
new typed-evidence adapter output
Formal Core V1 Python reference output
accepted Domain 3 conformance corpus
new raw-adapter fixtures
```

Acceptance must require:

```text
no false PROCEED
no resource action list loss
no replace path loss
no unknown path loss
no sensitive path loss
no not_claimed loss
no evidence/proof identity loss
invalid JSON and unsupported formats fail closed
existing accepted Domain 3 conformance still passes
full pytest passes
```

## Explicitly Not Accepted

This review does not accept or authorize:

```text
DOMAIN_3_ADAPTER_IMPLEMENTATION_CHANGE
RAW_TERRAFORM_JSON_PARSER_CHANGE
LEAN_DEFINITION_CHANGE
LEAN_PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
NEW_FIXTURE_MATERIALIZATION
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_TERRAFORM_JSON_PARSER_PROOF_CLAIM
PRODUCTION_CLAIM
RELEASE
```

## Next Authorized Step Required

The next step must be a separate authorization:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That authorization may materialize the bounded fixture corpus and expected outcomes. It must still not change the Domain 3 adapter implementation or claim a formal raw Terraform JSON parser proof.
