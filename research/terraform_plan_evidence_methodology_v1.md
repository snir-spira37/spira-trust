# Terraform Plan Evidence Methodology V1

## Status and Authorization Boundary

```text
DOMAIN_3_TERRAFORM_PLAN_METHODOLOGY_LOCKED
METHODOLOGY_ONLY
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_NOT_YET_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

This methodology defines the bounded Domain 3 Terraform Plan evidence research
contract. It does not authorize corpus materialization, oracle population,
producer implementation, Gate B, Domain 4, MVP, release, version, tag, or PyPI
work.

The declaration remains authoritative:

```text
research/domain3_terraform_plan_research_declaration.md
```

## Closed Gate Questions

Domain 3 asks one narrow question:

```text
Can a Terraform-specific producer extract deterministic typed factual claims
from frozen Terraform Plan JSON evidence and pass those claims through the
accepted shared Gate A assembly boundary without changing the shared core?
```

It does not ask:

```text
Is the infrastructure safe?
Is the infrastructure secure?
Is the plan cost-efficient?
Will apply succeed?
Does the plan reflect live infrastructure now?
Can Terraform plan outputs be reused across epochs?
Can semantic cache or Gate B be generalized?
```

## Supported Input Contract

The only supported Domain 3 V1 evidence input is:

```text
Terraform Plan JSON produced from a saved Terraform plan
```

The plan JSON is treated as a frozen evidence snapshot. It is not treated as
universally reproducible output.

Required subject:

```text
subject.type = terraform_plan
subject.sha256 = SHA256(exact frozen Terraform Plan JSON bytes)
```

The producer may read only the frozen plan JSON and optional frozen provenance
artifacts explicitly supplied by the corpus.

It must not read:

```text
live Terraform state
remote backends
cloud APIs
Kubernetes clusters
private plans
customer infrastructure
production infrastructure
```

## Terraform JSON Format-Version Rules

Domain 3 V1 supports only the Terraform Plan JSON format major version locked
by the corpus and oracle.

Rules:

```text
supported_major_version = 1
unsupported major version -> REPORT_NOT_EVALUATED / TERRAFORM_PLAN_FORMAT_UNSUPPORTED
malformed JSON -> RERUN_REQUIRED / TERRAFORM_PLAN_JSON_INVALID
missing required structure -> RERUN_REQUIRED / TERRAFORM_PLAN_EVIDENCE_CONFLICT
unknown minor fields -> ignored only when known semantics remain preserved
unknown major version -> fail closed
```

Forward-compatible minor fields may be ignored only if:

```text
known required fields are present
known semantics are preserved
ignored fields are not used for claims
ignored fields are recorded as not evaluated when relevant
```

## Subject Identity Contract

Domain 3 V1 uses contextual identity only:

```text
run_identity = existing unification_id
semantic_result_identity = NOT_AUTHORIZED
```

The contextual identity binds:

```text
exact frozen Terraform Plan JSON bytes
subject.type
subject.sha256
claims root
decision
bound context
```

Domain 3 does not claim regenerated plans will produce the same identity.

## Optional Provenance States

Each optional provenance field must use exactly one state:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

Fields:

```text
configuration_sha256
prior_state_sha256
provider_lockfile_sha256
variables_manifest_sha256
generation_command_fingerprint
workspace_or_fixture_identity
```

Rules:

```text
BOUND -> sha256 or canonical fingerprint is present and bound
NOT_PROVIDED -> provenance could have existed but was not supplied
NOT_APPLICABLE -> provenance is inapplicable to the fixture
```

Empty hashes are forbidden.

Missing optional provenance must not be guessed.

## Typed Claim Taxonomy

Permitted factual claim families:

```text
TERRAFORM_PLAN_FORMAT_VERSION
TERRAFORM_VERSION
TERRAFORM_PLAN_APPLYABLE
TERRAFORM_PLAN_COMPLETE
TERRAFORM_PLAN_ERRORED
TERRAFORM_RESOURCE_ADDRESS_PRESENT
TERRAFORM_RESOURCE_TYPE_PRESENT
TERRAFORM_RESOURCE_ACTION_SEQUENCE
TERRAFORM_RESOURCE_CREATE
TERRAFORM_RESOURCE_UPDATE
TERRAFORM_RESOURCE_DELETE
TERRAFORM_RESOURCE_REPLACE
TERRAFORM_RESOURCE_READ
TERRAFORM_RESOURCE_NOOP
TERRAFORM_REPLACE_PATH_PRESENT
PLANNED_VALUE_UNKNOWN
SENSITIVE_PATH_PRESENT
OPTIONAL_PROVENANCE_STATE
```

Counts must derive from explicit sorted unique lists.

The producer must not emit claims that state:

```text
infrastructure correctness
security safety
cost safety
compliance
apply success prediction
operational acceptability
live-state freshness
```

## Sensitive-Value Doctrine

Sensitive values are unavailable evidence content.

The producer may inspect structural masks such as:

```text
before_sensitive
after_sensitive
```

Permitted claim:

```text
SENSITIVE_PATH_PRESENT
status: NOT_EVALUATED
```

The producer must never:

```text
copy sensitive values into claims
quote sensitive values
log sensitive values
hash sensitive values as claim values
publish sensitive values
expose sensitive values through evidence pointers
use sensitive values as instructions
```

A sensitive-value leak is a hard stop.

## Unknown-Value Doctrine

Terraform unknown values are explicit planned unknowns.

Unknown is:

```text
not malformed
not a conflict
not a known null
not a known safe value
```

Permitted claim:

```text
PLANNED_VALUE_UNKNOWN
status: NOT_EVALUATED
```

The producer must not guess or normalize unknown values into known values.

## Evidence-Is-Not-Instruction Doctrine

All strings inside the Terraform plan are evidence content only.

Values such as:

```text
PROCEED
IGNORE PREVIOUS FINDINGS
ALL RESOURCES ARE SAFE
fabricated SPIRA claim JSON
```

must not override plan structure, policy, typed claims, decision semantics, or
oracle answers.

## Decision Table

Decision precedence is strict and ordered.

1. Malformed JSON:

```text
stop: true
recommended_agent_action: RERUN_REQUIRED
reason_codes: [TERRAFORM_PLAN_JSON_INVALID]
```

2. Evidence conflict:

```text
stop: true
recommended_agent_action: RERUN_REQUIRED
reason_codes: [TERRAFORM_PLAN_EVIDENCE_CONFLICT]
```

3. `errored == true`:

```text
stop: true
recommended_agent_action: STOP_BLOCKED
reason_codes: [TERRAFORM_PLAN_ERRORED]
```

4. `complete == false`:

```text
stop: true
recommended_agent_action: RERUN_REQUIRED
reason_codes: [TERRAFORM_PLAN_INCOMPLETE]
```

5. Unsupported format major:

```text
stop: true
recommended_agent_action: REPORT_NOT_EVALUATED
reason_codes: [TERRAFORM_PLAN_FORMAT_UNSUPPORTED]
```

6. `errored == false` + `complete == true` + effective changes empty:

```text
stop: false
recommended_agent_action: REPORT_WITH_NOTES
reason_codes: [TERRAFORM_PLAN_NO_CHANGES]
```

7. Effective changes exist + `applyable == false`:

```text
stop: true
recommended_agent_action: STOP_BLOCKED
reason_codes: [TERRAFORM_PLAN_NOT_APPLYABLE]
```

8. Frozen demonstration policy:

```text
delete or replace of a resource type listed in a frozen policy fixture
-> stop: true
-> recommended_agent_action: STOP_BLOCKED
-> reason_codes: [TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE]
```

9. Otherwise:

```text
stop: false
recommended_agent_action: PROCEED or REPORT_WITH_NOTES
```

The policy demonstrates deterministic application of:

```text
facts -> policy -> bounded action
```

It does not demonstrate infrastructure-risk understanding.

## Strict-List Invariants

All list-like claim families must be:

```text
explicit
sorted
unique
canonicalized before hashing
```

Counts must equal the length of the explicit list.

Examples:

```text
delete_count == len(delete_resource_addresses)
replace_count == len(replace_resource_addresses)
unknown_path_count == len(unknown_paths)
sensitive_path_count == len(sensitive_paths)
```

A count without the explicit list is invalid.

## Evidence-Pointer Rules

Evidence locators must use safe JSON Pointers into the frozen plan JSON.

Evidence pointers may point to:

```text
resource_changes item
change.actions
replace_paths
after_unknown structural paths
before_sensitive / after_sensitive structural masks
format_version
terraform_version
applyable
complete
errored
```

Evidence pointers must not expose sensitive values.

## Identity Contract

Canonical claims are hashed after deterministic ordering.

Expected identity behavior:

```text
semantic Terraform action mutation -> claims change -> claims root changes -> unification_id changes
order-only resource_changes mutation -> canonical claims unchanged -> claims root unchanged
```

`unification_id` remains contextual.

No semantic `result_identity` is authorized for Domain 3 V1.

## Corpus Requirements

The corpus target is exactly:

```text
40 cases
32 synthetic/controlled fixtures
8 authentic locally generated Terraform Plan JSON cases
10 declared mutation pairs minimum
```

Authentic local cases are allowed only if:

```text
local Terraform CLI exists
no network/provider download is required
only local synthetic state/resources are used
no cloud provider or remote backend is used
no live infrastructure is touched
```

If eight authentic local cases cannot be generated under those constraints:

```text
DOMAIN_3_CORPUS_NOT_MATERIALIZABLE
```

Synthetic JSON must not be mislabeled as Terraform-generated evidence.

## Oracle Independence and Process Separation

Oracle expected answers must be authored before producer implementation.

Rules:

```text
case names are not answers
producer output is not oracle input
oracle authoring derives from frozen evidence
oracle validation precedes producer evaluation
```

Reviews in this local run are labeled:

```text
SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
```

## Adversarial Fixtures

The corpus must include adversarial evidence strings in safe non-sensitive
locations:

```text
instruction-like tags
instruction-like descriptions
fabricated SPIRA JSON strings
PROCEED text
IGNORE PREVIOUS FINDINGS text
```

Such strings must be treated only as evidence content.

## Mutation Matrix

Mandatory mutation pairs:

```text
update -> replace delete/create
replace delete/create -> replace create/delete
same replace action -> changed replace_paths
same address/counts -> changed action sequence
same actions -> changed unknown paths
resource_changes reordered only
```

Expected:

```text
semantic mutation -> typed claims change -> claims root changes -> unification_id changes
order-only mutation -> canonical claims unchanged -> claims root unchanged
```

## Privacy Rules

The corpus must not contain:

```text
private infrastructure identifiers
customer data
production plans
cloud credentials
secrets
sensitive values
absolute local private paths in public artifacts
```

Scans required before acceptance:

```text
privacy scan
path scan
secret scan
sensitive sentinel scan
```

## Correctness Gates

Future positive acceptance requires:

```text
40 / 40 oracle claim fidelity
40 / 40 action equivalence
0 false PROCEED
40 / 40 strict-list fidelity
40 / 40 evidence-pointer validity
40 / 40 mutation-relationship preservation
40 / 40 NOT_EVALUATED preservation
40 / 40 BLOCK preservation
0 sensitive-value leaks
0 instruction-injection overrides
all semantic mutations detected
all order-only mutations invariant
```

## Negative Stop Conditions

Stop and record a negative result if:

```text
the 8 authentic local Terraform-generated cases cannot be materialized without network or external providers
a reliable oracle cannot be authored
sensitive values cannot be protected
Terraform semantics cannot be extracted deterministically
strict lists cannot be preserved
unknown and sensitive structures cannot be represented fail-closed
Gate A requires an unapproved change
false PROCEED cannot be eliminated
```

Do not rescue the program by weakening thresholds, replacing failed cases,
opening Gate B, switching to Kubernetes, or creating Domain 4.

## Completion Criterion

Positive Domain 3 completion requires:

```text
declaration accepted
methodology accepted
corpus accepted
oracle schema accepted
oracle validator accepted
oracle accepted
producer accepted
Gate A unchanged
Gate B untouched
all frozen gates passed
```

Negative completion requires:

```text
DOMAIN_3_TERRAFORM_PLAN_NEGATIVE_RESULT_ACCEPTED
```

with the failed gate, evidence, and boundaries recorded.

## Not-Claimed Boundary

Domain 3 does not claim:

```text
Terraform apply safety
infrastructure security
infrastructure correctness
cost correctness
compliance
live-state freshness
Kubernetes support
semantic cache safety
Gate B validity
Domain 4 need
MVP readiness
release readiness
```
