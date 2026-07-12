# Test/Build Failure Contract Public Run Materialization Authorization

Status:

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_AUTHORIZED
PUBLIC_RUN_MATERIALIZATION_AUTHORIZATION_ONLY
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Accepted corpus review:

```text
5b21a4a Review Domain 2 corpus materialization
DOMAIN_2_CORPUS_NEEDS_REVISION
CORPUS_REVIEW_COMPLETE
```

This document authorizes only the narrow public-run materialization revision
required by the corpus review. It does not authorize oracle population,
producer implementation, Gate B, Domain 3, or release activity.

## Purpose

The accepted corpus review found that the synthetic stratum and mutation pairs
are acceptable, but the public real-world stratum is currently only:

```text
PUBLIC_REPRODUCIBLE_INSTRUCTION_SET
```

not yet:

```text
PUBLIC_REPRODUCIBLE_RUN_CORPUS
```

The purpose of this authorization is to materialize the 8 public cases as
actual reproducible run evidence, or to record stable hashes of regenerated
public run outputs when raw output publication is withheld after privacy or
licensing review.

## Authorized Scope

For each of the 8 public cases, this authorization permits only:

```text
repository and commit verification
Python / pytest / dependency pinning
structured argv command execution
documented execution environment capture
pytest console byte capture
JUnit XML capture when available
pytest process exit-code capture
capture-completeness metadata
SHA-256 for each captured source
privacy scan
path scan
secret scan
manifest/report/results update
```

The revision may update only corpus materialization artifacts:

```text
research/test_build_failure_contract/corpus/
research/test_build_failure_contract/corpus_manifest_v1.json
research/test_build_failure_contract/corpus_materialization_report.md
research/test_build_failure_contract/corpus_materialization_results.json
tools/materialize_test_build_failure_corpus.py
```

If another file is required, work must stop and a new authorization document
must be committed before changing it.

## Public Case Set

The authorized public cases are exactly the 8 public instruction cases already
present in the materialized corpus:

```text
public_click_import
public_click_param
public_flask_clean
public_flask_param
public_flask_unicode_path
public_requests_assertion
public_requests_clean
public_requests_long_traceback
```

No public case may be silently replaced, removed, or added under this
authorization.

## Required Evidence Per Public Case

Each public case must record enough information to distinguish instructions
from actual run evidence.

Required identity and environment fields:

```text
repository_url
pinned_commit
source_revision_verification
python_version_contract
pytest_version
dependency_install_command
dependency_lock_or_constraints_hash, if available
package_manager_command
plugin_discovery_policy
environment_variable_policy
structured argv command
working_directory_policy
```

Required captured run sources:

```text
console output bytes
pytest process exit code
JUnit XML bytes, when available
capture completeness metadata
source SHA-256 hashes
source byte lengths
source media types
```

If JUnit XML is not available for a case, the case must state that explicitly
with a fail-closed reason. The console output and exit code remain required.

## Publication Modes

The public run output may use one of two publication modes.

### Published Raw Run Evidence

Raw run outputs may be committed only if privacy, path, secret, and licensing
review allow publication.

The manifest must distinguish:

```text
instruction_hashes
raw_run_output_hashes
raw_run_output_publication_status: PUBLISHED
```

### Withheld Raw Run Evidence With Stable Hashes

If raw output publication is withheld, the run outputs must still be
materialized before oracle population and their hashes must be recorded.

The manifest must distinguish:

```text
instruction_hashes
raw_run_output_hashes
raw_run_output_publication_status: WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW
reproduction_instructions
capture_completeness
```

This mode is acceptable only if the hashes identify actual captured public run
outputs. Hashes of instruction files or metadata are not sufficient.

## Dependency Pinning Requirement

The existing public instructions record repository, commit, Python, pytest and
command. That is not sufficient for corpus acceptance.

Each public case must record a deterministic dependency environment sufficient
for independent replay:

```text
install command
requirements or constraints source
requirements or constraints SHA-256, if present
lockfile SHA-256, if present
package manager and version when available
plugin inclusion/exclusion policy
environment variables that affect pytest collection or execution
network access policy during test execution
```

If the dependency environment cannot be pinned enough for independent replay,
the case must not be treated as materialized.

## Stop Conditions

Any of the following must stop the public-run materialization and produce a
revision-required or incomplete result:

```text
repository commit unavailable
source revision mismatch
dependencies cannot be pinned
run is not reproducible under the recorded environment
console output missing
exit code missing
required JUnit XML declared available but missing
capture incomplete without explicit reason
source hash mismatch
private path detected in publishable output
secret detected in publishable output
license or privacy review blocks publication and no stable output hash is recorded
attempt to replace a public case silently
attempt to add oracle expected answers
attempt to run or inspect a producer
```

Stop status:

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_INCOMPLETE
```

or, if the corpus cannot be repaired within this authorization:

```text
DOMAIN_2_CORPUS_REVISION_REQUIRED
```

No data may be completed by assumption. No case may be swapped after observing
materialization results.

## Required Updates

The materialization revision must update:

```text
corpus_manifest_v1.json
corpus_materialization_report.md
corpus_materialization_results.json
```

The manifest and report must explicitly distinguish:

```text
instruction files
metadata files
materialized run output files
withheld materialized run output hashes
publication status
capture completeness
dependency environment
```

The revision must preserve:

```text
oracle_expected_answers: NOT_POPULATED
producer_output_seen: false
```

for every corpus case.

## Required Validation

Before committing the public-run materialization revision, the following must
pass:

```text
38 unique case IDs
30 synthetic cases preserved
8 public cases preserved
3 public projects preserved
6 declared mutation pairs preserved
all source hashes recompute
public run output hashes present for all 8 public cases
dependency environment recorded for all 8 public cases
JSON validation passes
privacy scan passes
path scan passes
secret scan passes
oracle expected answers absent
producer outputs absent
```

## Not Authorized

This authorization does not permit:

```text
oracle population
oracle expected answers
producer implementation
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3 work
core changes
schema changes
validator changes
release/version/tag/PyPI publication
```

## Completion Statuses

The public-run materialization revision must end in exactly one of:

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZED
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_INCOMPLETE
DOMAIN_2_CORPUS_REVISION_REQUIRED
PUBLIC_RUN_MATERIALIZATION_AUTHORIZATION_REVISION_REQUIRED
```

If successful, the next required artifact is a public-run materialization
review. Success does not authorize oracle population.

## Final Authorization

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_AUTHORIZED
PUBLIC_RUN_MATERIALIZATION_AUTHORIZATION_ONLY
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```
