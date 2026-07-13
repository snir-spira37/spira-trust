# Terraform Plan Oracle Validator Specification

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_LOCKED
VALIDATOR_SPECIFICATION_ONLY
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Scope

This specification defines the validator contract for the accepted Terraform
Plan oracle schema:

```text
schema:
research/terraform_plan_contract/oracle_schema_v1.schema.json

schema verdict:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

accepted corpus:
research/terraform_plan_contract/corpus_manifest_v1.json

accepted corpus manifest sha256:
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

The validator is an oracle-quality gate. It is not a Terraform producer, not an
oracle author, and not a Gate B cache/reuse mechanism.

## Inputs

The validator must receive:

```text
1. oracle JSON bytes
2. Oracle Schema V1
3. accepted corpus manifest
4. accepted corpus case files
5. accepted corpus materialization results
```

The validator must not read producer output. If producer output is supplied as
an input or discovered in the oracle authoring path, validation must fail.

## Processing Order

The required order is:

```text
1. parse oracle JSON bytes as UTF-8 JSON
2. validate the document against Oracle Schema V1
3. bind the document to the accepted corpus manifest
4. recompute all recomputable file and identity hashes
5. validate case/reference integrity
6. validate mutation relationship integrity
7. validate canonical ordering and strict-list equivalence
8. validate Terraform resource action semantics
9. validate replace_paths, unknown_paths, and sensitive_paths
10. validate optional provenance states
11. validate policy/action and NOT_EVALUATED semantics
12. emit machine-readable validation output
```

Any failure before the semantic checks must still be reported as an oracle
document validation failure, not as a tool failure.

## Parse and Schema Validation

Malformed JSON must produce:

```text
verdict: FAIL
status: ORACLE_VALIDATION_FAILED
error_code: JSON_PARSE_FAILED
```

It must not produce:

```text
verdict: TOOL_ERROR
```

`TOOL_ERROR` is reserved for internal validator failures, such as an exception
inside the validator implementation, an unreadable schema file, or an unexpected
runtime error.

Schema validation must be full Oracle Schema V1 validation. A hand-written
top-level shape check is not sufficient.

The validator must enforce:

```text
required fields
additionalProperties: false
const
enum
patterns
array cardinality
uniqueItems
if/then/allOf conditions
$ref resolution
```

## Corpus Binding

The validator must verify:

```text
corpus_manifest_sha256 ==
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c

case_count == 40
oracle case IDs == accepted manifest case IDs
mutation relationship IDs == accepted manifest mutation pair IDs
```

No oracle case may refer to a case outside the accepted corpus. No accepted
corpus case may be missing from the oracle.

For every corpus file named in the manifest, the validator must recompute the
SHA-256 over the exact file bytes and compare it with the manifest. A mismatch
must fail validation.

## Canonical JSON Contract

Whenever the validator computes a hash over structured oracle data, it must use:

```text
encoding: UTF-8
JSON keys: sorted
separators: comma and colon only, no insignificant whitespace
set-like arrays: sorted and unique before hashing
hash format: lowercase 64-character SHA-256
```

The validator must not change these rules after seeing oracle results.

## Hash Recalculation

The validator must recompute and validate:

```text
manifest file hashes
case subject.sha256 from exact plan.json or plan.json.invalid bytes
configuration/provenance SHA-256 values when the bound source bytes are present
canonical expected_claims bytes
claims Merkle root used for proof assembly
canonical policy/action bytes
context_sha256 from the Domain 3 context projection
unification_id_expected from the accepted Gate A assembly inputs
```

The Domain 3 context projection is:

```text
domain_tag: SPIRA_TERRAFORM_PLAN_CONTEXT_V1
corpus_manifest_sha256
case_id
subject.type
subject.sha256
optional_provenance
evidence file hash map from the accepted manifest
```

The unification identity input set is:

```text
subject identity
canonical expected_claims
claims Merkle root
context_sha256
policy_action
decision_semantics_version
```

If any required canonical bytes are unavailable, the validator must fail closed:

```text
CANONICAL_BYTES_NOT_AVAILABLE
ORACLE_VALIDATION_FAILED
```

It must not accept a hash merely because the string is syntactically a SHA-256
digest.

## Case Integrity

The validator must enforce:

```text
CASE_ID_UNIQUENESS
CASE_ID_EXISTS_IN_ACCEPTED_MANIFEST
CASE_FILE_EXISTS
CASE_FILE_HASH_MATCHES_MANIFEST
CASE_PLAN_VALIDITY_MATCHES_MANIFEST
PRODUCER_OUTPUT_NOT_OBSERVED
```

For malformed JSON cases, the subject identity is still computed over the exact
`plan.json.invalid` bytes. Claims derived from invalid evidence may be
`NOT_EVALUATED`, but the case itself remains part of the oracle.

## Claim Validation

Every expected claim must satisfy:

```text
claim_id unique within the case
claim_id prefixed with terraform_plan.
claim_type belongs to Oracle Schema V1
status belongs to PASS / FAIL / BLOCK / NOT_EVALUATED
subject matches the case subject
evidence locators point to accepted case files
evidence locators use valid JSON pointers
evidence locators are safe_to_publish when present
```

The validator must verify that evidence locators are resolvable for valid JSON
files. For malformed JSON evidence, the validator may accept the root locator or
a metadata locator but must not pretend that an invalid JSON pointer was
resolved inside unparseable JSON.

## Resource Action-Sequence Validation

For Terraform Plan JSON evidence, the validator must derive resource action
sequences from `resource_changes[*].change.actions`.

The validator must check:

```text
create claim <-> ["create"]
update claim <-> ["update"]
delete claim <-> ["delete"]
read claim   <-> ["read"]
noop claim   <-> ["no-op"]
replace claim <-> ["delete","create"] or ["create","delete"]
```

The order of replacement action sequences is identity-bearing. The validator
must not normalize:

```text
["delete","create"]
```

into:

```text
["create","delete"]
```

or vice versa.

## Strict Explicit Lists

The validator must recompute these lists from the plan evidence and expected
claims:

```text
create_resources
update_resources
delete_resources
replace_resources
read_resources
noop_resources
replace_paths
unknown_paths
sensitive_paths
not_evaluated
```

The recomputed lists must equal `explicit_lists` exactly after canonical
sorting. This is a strict-list contract:

```text
missing item -> FAIL
extra item -> FAIL
wrong order after canonical sorting -> FAIL
duplicate item -> FAIL
```

## replace_paths Consistency

`replace_paths` must be derived from Terraform replacement evidence. A resource
listed in `replace_resources` with explicit replacement paths must contribute
those paths to the canonical `replace_paths` list.

The validator must fail if:

```text
replace action exists but expected replace facts are missing
replace_paths contains a path not supported by evidence
replace_paths omits an evidence-supported path
replace_paths uses a non-canonical JSON pointer
```

If Terraform evidence provides a replacement action but no path-level reason,
the validator must preserve that distinction rather than invent a path.

## unknown_paths Representation

`unknown_paths` must be derived from Terraform planned-unknown structures, such
as `after_unknown`.

The validator must fail if:

```text
PLANNED_VALUE_UNKNOWN is emitted with status other than NOT_EVALUATED
unknown_paths includes a path not present in unknown evidence
unknown evidence exists but is omitted from unknown_paths
unknown paths are represented as raw values instead of JSON pointers
```

Unknown planned values are structural facts. The validator must not infer the
unknown runtime value.

## Sensitive Structural Paths

Sensitive evidence is structural only. The validator must enforce:

```text
SENSITIVE_PATH_PRESENT -> NOT_EVALUATED
sensitive_paths are JSON pointers
sensitive_paths do not expose secret values
claim string values do not contain obvious secret-like sentinels
```

The validator must scan oracle strings and public evidence fields for common
secret indicators:

```text
secret
password
token
private key
credential
api key
access key
```

This scan is not a proof that no secret exists, but any hit must fail closed
unless it is a known synthetic sentinel intentionally represented only as a
blocked or not-evaluated structural path.

## Optional Provenance

Optional provenance entries must use only:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

The validator must enforce:

```text
BOUND -> sha256 or fingerprint required
NOT_PROVIDED -> no sha256 and no fingerprint
NOT_APPLICABLE -> no sha256 and no fingerprint
```

When a BOUND field references corpus bytes, the validator must recompute the
hash. When a BOUND field is a fingerprint rather than a file hash, the
fingerprint must be recomputed from its declared canonical input. If the
canonical input is unavailable, validation must fail closed.

## Policy and Action Consistency

The validator must enforce:

```text
decision_semantics_version == SPIRA_DECISION_SEMANTICS_V2
stop:false -> PROCEED or REPORT_WITH_NOTES
stop:true -> STOP_BLOCKED, RERUN_REQUIRED, or REPORT_NOT_EVALUATED
reason_codes sorted and unique
```

It must also check the policy/action binding against the claim statuses:

```text
invalid JSON evidence -> RERUN_REQUIRED or REPORT_NOT_EVALUATED
evidence conflict -> RERUN_REQUIRED
errored or incomplete plan -> STOP_BLOCKED or REPORT_NOT_EVALUATED
blocked policy-relevant resource change -> STOP_BLOCKED
clean no-change plan -> PROCEED or REPORT_WITH_NOTES
```

The validator must not claim that infrastructure is correct, safe, compliant,
or cheap. Those topics remain outside the oracle boundary.

## Mutation Relationships

The validator must enforce:

```text
MUTATION_PAIR_ID_UNIQUENESS
BASE_CASE_ID_EXISTS
MUTATED_CASE_ID_EXISTS
DECLARED_DELTA_MATCHES_ACCEPTED_MANIFEST
EXPECTED_CLAIMS_RELATION_MATCHES_CASES
EXPECTED_CLAIMS_ROOT_RELATION_MATCHES_RECOMPUTED_ROOTS
EXPECTED_UNIFICATION_ID_RELATION_MATCHES_RECOMPUTED_IDS
```

For order-only mutations, the validator must verify that the expected relation
matches the locked manifest and the recomputed canonical claim identity.

## Relationship Symmetry

Relationship checks must be symmetric at evaluation time:

```text
SAME(a,b) == SAME(b,a)
DIFFERENT(a,b) == DIFFERENT(b,a)
```

The oracle schema stores each mutation pair once. The validator must still
evaluate both directions logically and report any asymmetric interpretation as a
validation failure.

## Not-Claimed Boundaries

The validator must require the oracle document to preserve the excluded claims:

```text
INFRASTRUCTURE_CORRECTNESS
INFRASTRUCTURE_SECURITY
INFRASTRUCTURE_COST
INFRASTRUCTURE_COMPLIANCE
APPLY_SUCCESS
LIVE_STATE_FRESHNESS
GATE_B_REUSE
TERRAFORM_PROVIDER_SAFETY
KUBERNETES_SUPPORT
DOMAIN_4
MVP_INCLUSION
RELEASE
```

If any expected answer attempts to assert one of these as proven, validation
must fail.

## Machine-Readable Output

The validator must emit JSON with:

```text
schema: SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE_VALIDATION_RESULT
schema_version: 1
verdict: PASS | FAIL | TOOL_ERROR
status:
  DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATION_PASS
  ORACLE_VALIDATION_FAILED
  ORACLE_VALIDATOR_TOOL_ERROR
case_count
validated_case_count
mutation_relationship_count
schema_validation
corpus_binding
hash_recomputation
strict_list_equivalence
resource_action_validation
optional_provenance_validation
policy_action_validation
mutation_relationship_validation
producer_output_observed
errors
warnings
```

Each error must include:

```text
error_code
case_id, when applicable
pair_id, when applicable
json_pointer, when applicable
message
```

## Required Negative Fixtures

A future implementation must include negative fixtures for:

```text
malformed JSON oracle document
Schema V1 nested required-field violation
forbidden additional property
invalid enum
missing accepted corpus case
extra non-corpus case
case file hash mismatch
subject hash mismatch
context hash mismatch
unification_id mismatch
hash-only identity without canonical bytes
unresolvable evidence locator
duplicate claim_id
non-canonical explicit list
replace_paths mismatch
unknown_paths mismatch
sensitive value exposed as ordinary string
BOUND provenance without recomputable bytes
invalid stop/action pair
mutation pair references missing case
mutation relation mismatch
producer output observed
```

## Success Criteria

The only validator success condition is:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATION_PASS
```

It requires:

```text
Schema V1: PASS
accepted corpus binding: PASS
40 / 40 cases validated
10 / 10 mutation relationships validated
all recomputable hashes match
strict explicit lists match
resource action sequences match evidence
replace_paths match evidence
unknown_paths match evidence
sensitive structural paths are not value leaks
optional provenance states are consistent
policy/action binding is consistent
producer output observed: false
errors: 0
```

## Non-Authorization

This specification does not authorize:

```text
validator implementation
oracle population
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```
