# SPIRA Domain 4 / Nesira Flag Schema V1 Specification

## Status

```text
DOCUMENT_TYPE: SPECIFICATION
SCHEMA_ID: SPIRA_NESIRA_DOMAIN4_FLAGS_V1
SCHEMA_VERSION: 1
FROZEN: true
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document specifies the typed flag interface for a future Domain 4 / Nesira
Formal Core. It is a specification only. It does not implement Lean, Python,
fixtures, tests, product integration, or release behavior.

## Immutability Policy

```text
SPIRA_NESIRA_DOMAIN4_FLAGS_V1 is immutable.

Any change to a flag name, type, field definition, semantics, canonicalization,
or required mutation-pair behavior requires a new schema version.

V1 must not be edited in place after acceptance.
```

## Core Principle

Each flag has one definition that serves both consumers:

```text
Python computes the flag according to the one definition.
Lean assumes the flag according to the same one definition.
```

If `python_computes` and `lean_assumes` cannot be read as the same semantic
claim, the flag is not ready to freeze.

## Tuple Shape

The Domain 4 flag tuple is a named record, not a positional list.

```text
record NesiraDomain4FlagsV1:
  schema_id: "SPIRA_NESIRA_DOMAIN4_FLAGS_V1"
  schema_version: 1
  artifact_kind: Phase1ArtifactKind
  schema_valid: Bool
  evidence_present: Bool
  hash_ok: Bool
  path_safe: Bool
  symlink_escape_absent: Bool
  duplicate_path_free: Bool
  directory_not_file_absent: Bool
  context_match: Bool
  temporal_binding_ok: Bool
  evaluated: Bool
```

`artifact_kind` is required because the two accepted Phase 1 artifact families
do not evaluate the same raw evidence:

```text
Phase1ArtifactKind =
  SEVERANCE_AUTHORIZATION
  LEGACY_ISOLATION_RESULT
```

`LEGACY_ISOLATION_RESULT` evaluates evidence file paths and hashes.
`SEVERANCE_AUTHORIZATION` evaluates DSSE / statement shape and context binding,
but does not read evidence files from an evidence root in Phase 1. Any future
severance evidence-file check requires a new schema version.

## Canonical Serialization

The canonical serialization of the flag tuple is:

```text
UTF-8 JSON
object keys sorted lexicographically
no insignificant whitespace
booleans encoded as JSON true / false
artifact_kind encoded as its exact enum string
no timestamps
no host paths
no environment metadata
no runtime duration
no provider/tool telemetry
```

The conformance harness must compare canonical serialized tuples byte-for-byte
across repeated runs.

## Tuple Totality

The future decision table must be defined for every possible combination of:

```text
artifact_kind x schema_valid x evidence_present x hash_ok x path_safe
x symlink_escape_absent x duplicate_path_free
x directory_not_file_absent x context_match x temporal_binding_ok x evaluated
```

No tuple may fall through to an undefined or permissive default.

## Flag Specification Template

Every flag below follows the required template:

```text
name
type
one_definition
python_computes
lean_assumes
canonicalization
true_when
false_when
safety_critical
artifact_applicability
mutation_pair
decision_table_role
edge_cases
```

## Flag: `schema_valid`

```text
name: schema_valid
type: Bool
safety_critical: false
artifact_applicability: both artifact kinds
```

one_definition:

```text
The artifact's in-scope Phase 1 structural contract is satisfied for its
artifact_kind, including required fields, supported schema/version identity,
and field types that Phase 1 validates before semantic binding checks.
```

python_computes:

```text
For SEVERANCE_AUTHORIZATION, Python decodes the DSSE payload as JSON and checks
the in-toto statement / severance predicate structural requirements that Phase 1
validates.

For LEGACY_ISOLATION_RESULT, Python checks the result schema identity,
schema_version, required fields, and field shapes that Phase 1 validates.
```

lean_assumes:

```text
If schema_valid = true, the artifact has passed the same in-scope structural
requirements described in one_definition. Lean does not assume raw JSON parsing
correctness; it assumes only this classified structural flag.
```

canonicalization:

```text
None in Lean. Python may parse JSON/DSSE before producing this flag, but parsing
is outside the Lean proof boundary.
```

true_when:

```text
All in-scope structural checks for the artifact_kind pass.
```

false_when:

```text
artifact is missing
artifact is not a mapping/object where one is required
JSON / DSSE payload cannot be decoded into the expected structure
required fields are absent
required fields have invalid types
schema identity or schema_version is malformed or unsupported
evidence_manifest item shape is invalid for LEGACY_ISOLATION_RESULT
```

edge_cases:

```text
malformed JSON -> schema_valid = false
empty object -> schema_valid = false
unsupported schema version -> schema_valid = false
empty evidence_manifest list is structurally valid if list type is valid;
  evidence_present handles whether evidence entries exist
```

mutation_pair:

```text
required but not safety-critical:
valid structural artifact -> remove required field -> schema_valid false
```

decision_table_role:

```text
schema_valid = false must produce a non-PROCEED Phase 1 action.
```

## Flag: `evidence_present`

```text
name: evidence_present
type: Bool
safety_critical: false
artifact_applicability: LEGACY_ISOLATION_RESULT for file evidence;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root file check
```

one_definition:

```text
Every evidence file that Phase 1 is required to read for this artifact_kind is
declared and exists as a regular in-root candidate before hash validation.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python normalizes each evidence_manifest path,
joins it to evidence_root, and checks that every declared evidence file exists
before hash validation.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root file existence
check in Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If evidence_present = true, all Phase 1 evidence files applicable to the
artifact_kind exist as candidates for validation. For SEVERANCE_AUTHORIZATION,
Lean assumes there are no evidence-root file checks in V1.
```

canonicalization:

```text
For LEGACY_ISOLATION_RESULT, path separators are normalized by replacing
backslash with slash before existence checks. Root resolution is a Python /
filesystem operation and is not proven in Lean.
```

true_when:

```text
LEGACY_ISOLATION_RESULT: every declared evidence path exists after the Phase 1
normalization and root join.

SEVERANCE_AUTHORIZATION: true because this artifact_kind has no Phase 1
evidence-root file existence check.
```

false_when:

```text
LEGACY_ISOLATION_RESULT: one or more declared evidence files are missing.
LEGACY_ISOLATION_RESULT: an evidence entry is required but cannot be checked
because its path does not resolve to an existing file candidate.
```

edge_cases:

```text
empty evidence_manifest list -> evidence_present = true but schema_valid may
  decide whether an empty manifest is structurally allowed; V1 does not infer
  trust from an empty list.
malformed evidence_manifest item -> schema_valid = false, evidence_present is
  not the primary failure.
path traversal / absolute path -> path_safe = false has precedence.
```

mutation_pair:

```text
LEGACY_ISOLATION_RESULT:
valid fixture -> remove one declared evidence file from evidence_root
  -> evidence_present false
```

decision_table_role:

```text
evidence_present = false must produce NOT_EVALUATED / REPORT_NOT_EVALUATED,
not VALID_STRUCTURAL_ONLY.
```

## Flag: `hash_ok`

```text
name: hash_ok
type: Bool
safety_critical: true
artifact_applicability: LEGACY_ISOLATION_RESULT for file evidence;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root file hash check
```

one_definition:

```text
Every Phase 1 evidence file whose bytes are in scope for this artifact_kind has
SHA-256(raw file bytes) equal to the digest declared for that evidence file.
The hash is over the evidence file bytes, not over the manifest, path string,
JSON document, or normalized metadata.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python reads each validated regular evidence file
as bytes and compares sha256(file_bytes).hexdigest() to the entry's declared
sha256.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root file hash check
in Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If hash_ok = true, all applicable Phase 1 evidence-file byte hashes match their
declared digests according to one_definition. Lean does not prove that Python
read the correct bytes.
```

canonicalization:

```text
No text encoding, newline conversion, JSON canonicalization, or path string is
included in the hash. Hash input is raw file bytes only.
```

true_when:

```text
LEGACY_ISOLATION_RESULT: every applicable evidence file hash matches.
SEVERANCE_AUTHORIZATION: true because no evidence-root file hash check exists
in Phase 1 V1.
```

false_when:

```text
LEGACY_ISOLATION_RESULT: any applicable evidence file's raw-byte SHA-256 differs
from its manifest digest.
LEGACY_ISOLATION_RESULT: bytes cannot be read after the file was otherwise
classified as present and regular; this may become TOOL_ERROR in Python, but
must not become structural VALID in the decision table.
```

edge_cases:

```text
hash computed over manifest instead of file bytes -> invalid implementation
empty file -> hash_ok true only if declared digest is SHA-256 of zero bytes
line-ending change -> hash_ok false unless digest matches changed raw bytes
missing file -> evidence_present false has precedence
directory instead of file -> directory_not_file_absent false has precedence
```

mutation_pair:

```text
valid LEGACY_ISOLATION_RESULT evidence file -> flip one byte of that file while
keeping the declared digest unchanged -> hash_ok false
```

decision_table_role:

```text
hash_ok = false must produce INVALID / STOP_BLOCKED.
```

## Flag: `path_safe`

```text
name: path_safe
type: Bool
safety_critical: true
artifact_applicability: LEGACY_ISOLATION_RESULT for evidence paths;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root path check
```

one_definition:

```text
Every Phase 1 evidence path applicable to this artifact_kind is a relative,
non-empty, non-drive-qualified, non-UNC, non-absolute path with no traversal or
empty component after backslash-to-slash normalization.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python replaces backslashes with slashes for
normalization, rejects raw paths beginning with slash or backslash, rejects
normalized paths beginning with double slash, rejects drive-qualified raw or
normalized paths, and rejects any normalized path component equal to '..' or
empty.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root path check in
Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If path_safe = true, all applicable Phase 1 evidence path strings satisfy the
path safety definition above. Lean does not prove platform filesystem behavior.
```

canonicalization:

```text
Backslash is replaced by slash before component analysis. No filesystem resolve
is part of path_safe; symlink/root resolution belongs to symlink_escape_absent.
```

true_when:

```text
every applicable evidence path is relative, non-empty, non-drive-qualified,
non-UNC, non-absolute, and traversal-free after normalization
```

false_when:

```text
empty path string
absolute POSIX path
leading backslash path
UNC or network path
Windows drive-qualified path such as C:foo or C:/foo
any '..' component after normalization
any empty component after normalization
```

edge_cases:

```text
"safe/../file" -> path_safe false
"safe//file" -> path_safe false
"C:relative" -> path_safe false
"C:/absolute" -> path_safe false
"\\\\server\\share\\file" -> path_safe false
"//server/share/file" -> path_safe false
```

mutation_pair:

```text
valid relative evidence path -> replace with '../outside.txt' or drive-qualified
path -> path_safe false
```

decision_table_role:

```text
path_safe = false must produce INVALID / STOP_BLOCKED.
```

## Flag: `symlink_escape_absent`

```text
name: symlink_escape_absent
type: Bool
safety_critical: true
artifact_applicability: LEGACY_ISOLATION_RESULT for evidence paths;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root symlink check
```

one_definition:

```text
No applicable evidence path resolves through a symlink or resolved path outside
the evidence root.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python resolves the candidate path and evidence
root, rejects the evidence if the resolved path is not within the resolved root,
and rejects a path that is itself a symlink.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root symlink check in
Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If symlink_escape_absent = true, all applicable evidence paths are classified as
not escaping the evidence root by the Python filesystem adapter. Lean does not
prove the OS-specific correctness of path resolution.
```

canonicalization:

```text
Filesystem resolution is performed by Python before classification. The
canonical tuple records only the boolean flag, not host paths.
```

true_when:

```text
every applicable evidence path resolves within evidence_root and the path is
not classified as a symlink escape
```

false_when:

```text
resolved evidence path lies outside evidence_root
evidence path is a symlink
resolve operation shows an escape through filesystem metadata
```

edge_cases:

```text
resolve failure -> not a Lean-level fact; Python may return TOOL_ERROR, and the
decision table must not yield structural VALID for tool errors
symlink support unavailable in a test environment -> conformance harness must
record NOT_EVALUATED for that mutation rather than claiming coverage
```

mutation_pair:

```text
valid evidence file -> replace with symlink to a file outside evidence_root
where supported -> symlink_escape_absent false
```

decision_table_role:

```text
symlink_escape_absent = false must produce INVALID / STOP_BLOCKED.
```

## Flag: `duplicate_path_free`

```text
name: duplicate_path_free
type: Bool
safety_critical: true
artifact_applicability: LEGACY_ISOLATION_RESULT for evidence paths;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root duplicate path check
```

one_definition:

```text
No two applicable evidence entries canonicalize to the same in-root evidence
path after normalization and resolution.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python computes each resolved path relative to the
resolved evidence root as a POSIX-style canonical path and rejects the manifest
if the same canonical path appears more than once.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root duplicate path
check in Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If duplicate_path_free = true, no applicable evidence file is counted twice
under different path spellings. Lean does not prove filesystem canonicalization.
```

canonicalization:

```text
resolved.relative_to(root).as_posix() is the Python-side canonical evidence
identity for this flag.
```

true_when:

```text
all applicable canonical evidence paths are unique
```

false_when:

```text
two or more applicable evidence entries resolve to the same canonical path
```

edge_cases:

```text
"file.txt" and "./file.txt" -> duplicate_path_free false if both resolve to the
same canonical path
exact duplicate entries -> duplicate_path_free false
hash mismatch on duplicate entries does not make the duplicate safe
```

mutation_pair:

```text
valid single evidence entry -> add a second entry that canonicalizes to the
same file -> duplicate_path_free false
```

decision_table_role:

```text
duplicate_path_free = false must produce INVALID / STOP_BLOCKED.
```

## Flag: `directory_not_file_absent`

```text
name: directory_not_file_absent
type: Bool
safety_critical: true
artifact_applicability: LEGACY_ISOLATION_RESULT for evidence paths;
  SEVERANCE_AUTHORIZATION has no Phase 1 evidence-root regular-file check
```

one_definition:

```text
No applicable evidence entry points to a directory or non-regular file where a
regular evidence file is required.
```

python_computes:

```text
For LEGACY_ISOLATION_RESULT, Python rejects evidence paths that exist but are
not regular files.

For SEVERANCE_AUTHORIZATION, Python performs no evidence-root regular-file
check in Phase 1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If directory_not_file_absent = true, every applicable evidence path classified
as present is a regular file, not a directory. Lean does not prove OS file type
classification.
```

canonicalization:

```text
Filesystem file-type classification is Python-side only.
```

true_when:

```text
every applicable present evidence path is a regular file
```

false_when:

```text
an applicable evidence path exists and points to a directory
an applicable evidence path exists and is otherwise not a regular file
```

edge_cases:

```text
missing file -> evidence_present false has precedence
symlink -> symlink_escape_absent false has precedence
directory with matching digest string -> still directory_not_file_absent false
```

mutation_pair:

```text
valid evidence file -> replace path target with a directory -> 
directory_not_file_absent false
```

decision_table_role:

```text
directory_not_file_absent = false must produce INVALID / STOP_BLOCKED.
```

## Flag: `context_match`

```text
name: context_match
type: Bool
safety_critical: true
artifact_applicability: both artifact kinds
```

one_definition:

```text
All Phase 1 context fields required for this artifact_kind match the external
expected/current context supplied to the validator.
```

python_computes:

```text
For SEVERANCE_AUTHORIZATION, Python compares subject_sha256, candidate_sha256,
legacy_dependency_id, operation, environment_id, evidence_sha256, policy_id,
source_commit, and state_version between the severance predicate and
expected_context.

For LEGACY_ISOLATION_RESULT, Python compares profile_id, environment_id,
candidate_sha256, and legacy_dependency_id against current_context and also
checks profile.profile_id against result.profile_id.
```

lean_assumes:

```text
If context_match = true, all in-scope identity and context binding fields for
the artifact_kind match the supplied context. Lean does not prove that the
external context was itself correct or authoritative.
```

canonicalization:

```text
Context values are compared as exact strings. No case folding, trimming, path
normalization, or semantic aliasing is allowed.
```

true_when:

```text
all required in-scope context fields are present in both artifact and external
context and compare exactly
```

false_when:

```text
any required context field mismatches
profile_id mismatches for LEGACY_ISOLATION_RESULT
artifact binds to a different candidate, subject, environment, policy, source,
state, or legacy dependency than the supplied context
```

edge_cases:

```text
missing external context field -> not_evaluated path, not context_match true
extra fields -> ignored unless Phase 1 explicitly binds them
string values differing only by case or whitespace -> context_match false
```

mutation_pair:

```text
valid fixture -> change one required context field in the supplied context or
artifact -> context_match false
```

decision_table_role:

```text
context_match = false must produce RERUN_REQUIRED / RERUN_REQUIRED.
```

## Flag: `temporal_binding_ok`

```text
name: temporal_binding_ok
type: Bool
safety_critical: false
artifact_applicability: SEVERANCE_AUTHORIZATION in Phase 1 V1;
  LEGACY_ISOLATION_RESULT has no accepted temporal binding check in V1
```

one_definition:

```text
All in-scope temporal constraints for this artifact_kind are satisfied at the
supplied validation time.
```

python_computes:

```text
For SEVERANCE_AUTHORIZATION, Python checks the accepted Phase 1 temporal
binding fields against now_utc.

For LEGACY_ISOLATION_RESULT, Python performs no temporal binding check in
Phase 1 V1; the flag is true by non-applicability for this artifact_kind.
```

lean_assumes:

```text
If temporal_binding_ok = true, all accepted temporal constraints applicable to
the artifact_kind have been classified as satisfied. Lean does not prove clock
correctness.
```

canonicalization:

```text
Python supplies the boolean classification. Wall-clock source, time parsing,
and timezone handling are outside Lean.
```

true_when:

```text
all applicable temporal constraints are satisfied, or no temporal constraints
are applicable to the artifact_kind in V1
```

false_when:

```text
applicable severance temporal binding is expired or otherwise outside its
accepted validity window
```

edge_cases:

```text
missing temporal field that is structurally required -> schema_valid false
malformed temporal field -> schema_valid false or temporal_binding_ok false,
depending on the accepted Phase 1 parser classification
clock not trusted -> NOT_PROVEN_IN_LEAN; not a Lean theorem
```

mutation_pair:

```text
valid severance fixture -> set temporal binding outside accepted window ->
temporal_binding_ok false
```

decision_table_role:

```text
temporal_binding_ok = false must produce RERUN_REQUIRED / RERUN_REQUIRED.
```

## Flag: `evaluated`

```text
name: evaluated
type: Bool
safety_critical: false
artifact_applicability: both artifact kinds
```

one_definition:

```text
The Phase 1 validator completed its in-scope structural evaluation path and
returned a classified result rather than a malformed-input rerun or internal
tool-error result. `evaluated` never means trust, authorization, or permission
to sever.
```

python_computes:

```text
Python sets evaluated according to whether the Phase 1 evaluation completed for
the artifact_kind. It must remain false for malformed JSON / malformed DSSE
entry paths and tool errors.
```

lean_assumes:

```text
If evaluated = true, Phase 1 structural evaluation completed. Lean does not
assume signer trust, isolation trust, or severance permission from evaluated.
```

canonicalization:

```text
No canonicalization. This is a boolean classification, not a timestamped event.
```

true_when:

```text
Phase 1 completed in-scope structural evaluation and produced a deterministic
classified result
```

false_when:

```text
malformed JSON prevents evaluation
malformed DSSE prevents severance payload evaluation
internal validator tool error prevents result availability
```

edge_cases:

```text
evaluated = true with validation_status VALID still does not authorize PROCEED
evaluated = false must not silently become VALID_STRUCTURAL_ONLY
```

mutation_pair:

```text
valid fixture -> malformed JSON bytes -> evaluated false
```

decision_table_role:

```text
evaluated = false must produce RERUN_REQUIRED or STOP_BLOCKED depending on the
future accepted decision-table specification; it must never produce a
PROCEED-capable action.
```

## Required Canonical Tuple Example

Example for a structurally valid isolation result with valid evidence:

```json
{"artifact_kind":"LEGACY_ISOLATION_RESULT","context_match":true,"directory_not_file_absent":true,"duplicate_path_free":true,"evaluated":true,"evidence_present":true,"hash_ok":true,"path_safe":true,"schema_id":"SPIRA_NESIRA_DOMAIN4_FLAGS_V1","schema_valid":true,"schema_version":1,"symlink_escape_absent":true,"temporal_binding_ok":true}
```

Example for a structurally valid severance authorization:

```json
{"artifact_kind":"SEVERANCE_AUTHORIZATION","context_match":true,"directory_not_file_absent":true,"duplicate_path_free":true,"evaluated":true,"evidence_present":true,"hash_ok":true,"path_safe":true,"schema_id":"SPIRA_NESIRA_DOMAIN4_FLAGS_V1","schema_valid":true,"schema_version":1,"symlink_escape_absent":true,"temporal_binding_ok":true}
```

For severance, evidence/path/hash flags are true by non-applicability in V1.
This is not a claim that evidence-root files were checked.

## Explicit Non-Claims

This flag schema does not prove or claim:

```text
cryptographic signature trust
signer identity
signer authority
actual isolation execution
permission to sever
correctness of JSON / DSSE parsing
correctness of filesystem operations
correctness of SHA-256 implementation
faithfulness of Python flag classification
public wheel exposure
release readiness
```

## Status

```text
SPIRA_NESIRA_DOMAIN4_FLAGS_V1_SPECIFIED

FLAG_SCHEMA_ONLY
DECISION_TABLE_NOT_SPECIFIED_HERE
NOT_PROVEN_IN_LEAN_LEDGER_REQUIRED_SEPARATELY
CONFORMANCE_HARNESS_REQUIRED_SEPARATELY
LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PYTHON_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

