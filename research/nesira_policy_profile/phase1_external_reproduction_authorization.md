# SPIRA Nesira Policy Profile - Phase 1 External Reproduction Authorization

Status:

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_AUTHORIZATION
```

This document authorizes the methodology, boundary, required evidence,
acceptance metrics, and adversarial review requirements for a future cold
external reproduction of the accepted Nesira Phase 1 validator.

It does not authorize building the reproduction package yet, running the
external reproduction yet, starting Phase 2, changing product code, exposing the
validator in the public wheel, publishing a capability claim, or releasing.

## Authoritative Starting Point

```text
accepted_phase1_implementation_commit:
a6e69cf8ea17a1a7d8e188cf3da6735cbfa7a0aa

hygiene_clean_reproduction_source_commit:
c21abef47dd174284a5d1938182a633b93bd8785

accepted_phase1_verdict:
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED

current_required_step:
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_AUTHORIZATION_REQUIRED
```

The historical implementation and review sequence is:

```text
7d11be9a261cb3c61074a8932a8ba58a42b9ae81
-> remediation of the four High acceptance findings

a6e69cf8ea17a1a7d8e188cf3da6735cbfa7a0aa
-> clean acceptance rerun

c21abef47dd174284a5d1938182a633b93bd8785
-> hygiene-only redaction of local builder paths in historical logs
```

## Authorized Claim

The future reproduction may evaluate only this claim:

```text
SPIRA validates structure, binding, evidence integrity,
and safe evidence paths for the two supported Phase 1 artifact types.
```

The claim does not include:

```text
cryptographic signature verification
signer identity
signer authority
signer trust
actual isolation execution
independent isolation observation
severance authorization
permission to sever
production readiness
product integration
public capability availability
```

Every reproduction document and review must preserve this boundary:

```text
Phase 1 validates structure, binding, evidence integrity,
and safe evidence paths.

Phase 1 does not validate cryptographic signature trust,
signer identity or authority, actual isolation execution,
or permission to sever.
```

Positive fixtures must remain non-proceeding:

```text
recommended_agent_action != PROCEED
stop == true
```

No reproduction output may claim:

```text
signature verified
signer trusted
isolation trusted
severance authorized
safe to proceed
production approved
```

## Phase 1 Scope Under Reproduction

The future reviewer may test only these artifact types:

```text
SEVERANCE_AUTHORIZATION
LEGACY_ISOLATION_RESULT
```

The tested Phase 1 properties are:

```text
JSON/schema structure
DSSE envelope structure and payload decoding
subject binding
candidate binding
environment binding
policy/profile binding
revision and temporal binding
evidence existence
SHA256 integrity
safe evidence paths
traversal rejection
absolute-path rejection
drive-relative-path rejection
UNC-path rejection
symlink escape rejection
regular-file requirement
canonical duplicate-path rejection
deterministic fail-closed output
```

## Source of Reproduction

The future reproduction must start from the hygiene-clean reproduction source
commit:

```text
c21abef47dd174284a5d1938182a633b93bd8785
```

The accepted Phase 1 implementation verdict remains anchored in
`a6e69cf8ea17a1a7d8e188cf3da6735cbfa7a0aa`. The later `c21abef...` commit is
a forward-only artifact hygiene commit that redacts local builder paths from
tracked historical reports without changing validator code, schemas, tests, or
Phase 1 semantics.

It may use only one of two source modes:

1. Fresh clone pinned to the exact commit.
2. Clean worktree created from the exact commit.

If a clean worktree is used, the report must not call it an external clone.

The reviewer must record:

```text
reproduction type
repository URL
source commit
branch or detached HEAD
initial git status
operating system
Python version
dependency installation method
working directory
environment variables relevant to the run
```

## V1.1 Authorization Package Verification

The future reproduction must verify the corrected V1.1 authority package:

```text
SPIRA_NESIRA_POLICY_PROFILE_PHASE1_IMPLEMENTATION_AUTHORIZATION_V1_1.zip
```

Authoritative SHA256:

```text
14b19bbce4764778599b755ce614404ecc6875349c63a08efa9ad5439ef5370d
```

Required checks:

```text
ZIP SHA256
SHA256SUMS
path safety
JSON validity
accepted authorization verdict
forbidden-term absence
PROCEED allowed = false
```

If the V1.1 package is not available to the external reviewer, the
authorization-verification layer must be reported as `NOT_EVALUATED`, not
`PASS`.

## Protected Surfaces

The future reproduction must verify protected surfaces at the accepted Phase 1
commit against this baseline:

```text
df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe
```

Protected surfaces include:

```text
pyproject.toml
source/spira_core/attestation_verify.py
source/spira_core/agent_summary.py
source/spira_core/combined_verdict.py
source/spira_core/policy_pack.py
source/spira_core/rerun_planner.py
existing public schemas
existing action contracts
Formal Core files
tools/build_spira_trust_public.py
```

Any unauthorized diff in these surfaces must block reproduction acceptance.

## Fixture and Mutation Requirements

The future reproduction must report fixture-level and mutation-pair-level
results, not only aggregate counts.

Acceptance metrics:

```text
positive fixtures structurally accepted: 6/6
positive fixtures yielding PROCEED: 0/6

negative invariant detection: 100%
false VALID mutation pairs: 0

unsafe evidence paths accepted: 0
hash mismatches accepted: 0
directories accepted as evidence files: 0
duplicate canonical evidence paths accepted: 0
local absolute paths leaked in results: 0

PROCEED paths: 0
stop=false paths: 0
```

For each fixture, record:

```text
fixture path
SHA256
artifact type
expected status
expected action
expected stop
expected reason codes
expected not_evaluated
actual result
```

For each mutation pair, record:

```text
source fixture
mutated fixture
mutated invariant
expected distinction
actual distinction
```

## Path-Security Matrix

The future reproduction must cover at least these path-security cases:

```text
POSIX absolute:
/tmp/evidence.txt
/
/var/log/example

Windows drive-relative and absolute:
C:tmp/evidence.txt
C:
D:folder/file
C:\tmp\evidence.txt
C:/tmp/evidence.txt

UNC:
\\server\share\file
//server/share/file

Traversal and normalization:
../file
a/../../file
./file
a/../file
mixed slash variants

Filesystem objects:
nonexistent path
directory instead of file
symlink to file outside root
symlinked parent directory
duplicate canonical paths
evidence root itself
```

Every unsafe input must receive a deterministic validation result, not
`TOOL_ERROR`, unless a genuinely unexpected internal failure occurs.

## Hash and Binding Matrix

The future reproduction must cover:

```text
correct hash
malformed hash
wrong hash
wrong algorithm
changed evidence file
subject mismatch
candidate mismatch
environment mismatch
profile/policy mismatch
revision mismatch
temporal mismatch
duplicate identifiers
conflicting identifiers
expected-context mismatch
```

## Error Hygiene

The future reproduction must verify that outputs do not contain:

```text
absolute local paths
repository paths
usernames
temporary-directory paths
raw exception representations
stack traces
secrets
credentials
sensitive values
```

## Capability Absence Checks

The future reviewer must verify that Phase 1 did not implement:

```text
cryptographic signature verification
Sigstore trust verification
signer identity lookup
signer authority evaluation
isolation runner
subprocess-based isolation execution
Docker/container execution
sandbox execution
combined-verdict integration
agent-summary integration
CLI registration
public exports
Phase 2 code
cutover execution
release code
```

Keyword search alone is insufficient. The review must inspect imports,
functions, call sites, and public exports.

## Public Wheel Exclusion

The future reproduction must:

1. Build the public wheel with the existing public builder.
2. Compute the wheel SHA256.
3. Inspect the wheel archive.
4. Produce a complete inventory.
5. Verify that the new validator module is not included.
6. Verify that research schemas and fixtures are not included.
7. Verify that the public allowlist did not change.
8. Verify `unexpected public-wheel modules = 0`.

The reviewer must not rely only on a previous build report.

## Required Commands

The future package must lock exact commands, working directories, and expected
exit codes for at least:

```text
python -m compileall
focused Phase 1 pytest
all path-security tests
all hash-binding tests
all mutation tests
full pytest
public wheel build
wheel archive inspection
JSON validation
protected-surface diff
action/schema identity checks
git diff --check
```

## Two Independent Runs

The future reproduction must require two independent runs of the focused Phase
1 layer.

The reviewer must verify:

```text
semantic results identical
fixture outcomes identical
mutation outcomes identical
no new generated drift
no stale result reuse
```

If timestamps or environment metadata vary, those fields must be separated from
semantic decision content.

## Future Reproduction Package Outputs

After this authorization is accepted, a separate package-build step may create:

```text
phase1_external_reproduction_package/
README_REPRODUCTION.md
CLAIMS_AND_BOUNDARIES.md
REPRODUCE_PHASE1.md
phase1_reproduction_manifest.json
phase1_expected_results.json
SHA256SUMS
COLD_EXTERNAL_REVIEW_TASK.md
package build report/results
package build review/results
deterministic ZIP
external sidecar containing ZIP filename and SHA256
```

The ZIP SHA must not self-reference from inside the ZIP.

This authorization does not build those artifacts.

## Source Package Mode

The later package-build authorization must choose one source mode:

```text
self-contained source package
clone-based package
```

If self-contained:

```text
every source file must be hash-bound
no dependency on files outside the package
every fixture must be byte-identical to source
no local paths
no symlinks escaping package root
```

If clone-based:

```text
every path must exist in the pinned commit
repository URL and commit must be pinned
no use of external working-tree files
```

## Lean Boundary

Phase 1 does not add a new Lean proof.

The future reproduction must distinguish:

```text
existing Formal Core identity check
Phase 1 validator empirical reproduction
absence of a formal proof of the new validator
```

It must not claim:

```text
Phase 1 validator is formally proved
DSSE parser is formally proved
path validation is formally proved
end-to-end trust is formally proved
```

## Current Authorization Outputs

This authorization step creates only:

```text
phase1_external_reproduction_authorization.md
phase1_external_reproduction_authorization_review.md
phase1_external_reproduction_authorization_review_results.json
```

No reproduction package is built in this step.

## Current-Step Prohibitions

```text
PHASE2_NOT_AUTHORIZED
PRODUCT_INTEGRATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
REPRODUCTION_PACKAGE_BUILD_NOT_AUTHORIZED_IN_THIS_STEP
EXTERNAL_REPRODUCTION_EXECUTION_NOT_AUTHORIZED_IN_THIS_STEP
```

## Next Step After Acceptance

If this authorization is accepted, the next required step is:

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_REQUIRED
```
