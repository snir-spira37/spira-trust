# Test/Build Failure Contract Corpus Materialization Authorization

Status:

```text
DOMAIN_2_CORPUS_MATERIALIZATION_AUTHORIZED
CORPUS_MATERIALIZATION_AUTHORIZATION_ONLY
ORACLE_SCHEMA_V7_ACCEPTED
ORACLE_VALIDATOR_SPEC_ACCEPTED
ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Accepted prerequisites:

```text
Dual Identity Model V2: ACCEPTED
Oracle Schema V7: ACCEPTED
Oracle Validator Spec: ACCEPTED
Oracle Validator Implementation: ACCEPTED
```

Accepted validator implementation:

```text
a4dcafe Accept Domain 2 oracle validator implementation
```

This document authorizes only Domain 2 corpus materialization. It does not
authorize oracle population, producer implementation, Gate B, Domain 3, or any
release activity.

## Purpose

The next research object is a frozen Domain 2 corpus, not an oracle and not a
producer.

The corpus must provide stable, reproducible input material for later oracle
authoring. It must be created and frozen before oracle population so that
expected answers are not shaped by producer output.

## Authorized Work

This authorization permits only:

```text
synthetic pytest evidence fixtures
adversarial pytest evidence fixtures
public reproducible run instructions
public run hashes and source identities
declared mutation pairs
input byte hashing
corpus manifest creation
privacy/path/secret scans
materialization report creation
```

The corpus may contain:

```text
pytest console output bytes
JUnit XML bytes
pytest process exit code
capture-completeness metadata
project identity
source revision
Python version contract
pytest version
plugin contract
normalized selection command
declared mutation metadata
```

The corpus must not contain oracle expected answers. It may contain evidence
and metadata needed to author oracle cases later.

## Authorized Files

The materialization step may add or edit only:

```text
research/test_build_failure_contract/corpus/
research/test_build_failure_contract/corpus_manifest_v1.json
research/test_build_failure_contract/corpus_materialization_report.md
research/test_build_failure_contract/corpus_materialization_results.json
tools/materialize_test_build_failure_corpus.py
```

If another file is required, work must stop and a new authorization document
must be committed before changing it.

## Corpus Strata

The corpus must include at least these strata.

### Stratum A: Synthetic control and adversarial fixtures

Synthetic fixtures may be committed if they are generated or authored for this
research corpus and contain no private data.

Required coverage includes:

```text
clean successful run
single assertion failure
multiple failures
skipped test
xfail
xpass
collection error
import error
syntax error
fixture setup error
fixture teardown error
timeout
keyboard interruption
process crash
nonzero exit without normal test result
truncated console
malformed JUnit XML
incomplete JUnit fields
console/JUnit conflict
duplicate test IDs
parameterized test IDs
Unicode test names and messages
Windows paths
Linux paths
long traceback
deterministically derivable rerun target
non-derivable rerun target
```

Required adversarial evidence includes at least two instruction-injection
cases, selected from:

```text
a failing test prints "ALL TESTS PASSED"
a failing test prints "PROCEED"
a failing test prints "IGNORE PREVIOUS FAILURE"
a failing test prints fabricated SPIRA claim JSON
a test ID contains instruction-like text
```

### Stratum B: Reproducible public runs

The corpus must include reproducible real-world public runs with:

```text
public repository identity
pinned commit SHA
pinned Python version
pinned pytest version
recorded command
recorded dependency environment
deterministic generation instructions
source hashes
```

Minimum:

```text
8 real-world runs
across at least 3 public projects
```

Required real-world coverage includes:

```text
one clean pass
one assertion failure
one collection or import failure
one parameterized-test case
one noisy or long traceback case
one Unicode or path-normalization case
```

Raw public-project logs may be committed only after license, privacy and secret
review. Otherwise the corpus must publish generation instructions, source
identities, hashes, aggregate metadata and safe normalized paths only.

### Stratum C: Optional private supplemental cases

Private logs may be tested locally as supplemental evidence only.

They:

```text
must not enter the primary public denominator
must not determine the public success claim
must publish no raw content or absolute paths
must be represented publicly only by safe aggregates and hashes
```

Redacted private logs are not substitutes for the reproducible public corpus.

## Mutation Pairs

Mutation pairs are authorized only as corpus inputs, not oracle answers.

Every mutation pair must declare:

```text
source case id
mutated case id
mutation type
changed bytes or generation instruction
expected identity relationship to be assessed later by oracle authoring
raw input hashes
```

Allowed mutation classes include:

```text
factual mutation
claim-order mutation
non-factual raw-byte mutation
declared formatting mutation
declared path mutation
declared timing mutation
instruction-injection mutation
```

No mutation may be added after seeing producer output.

## Manifest Requirements

The materialization step must produce:

```text
research/test_build_failure_contract/corpus_manifest_v1.json
```

The manifest must include:

```text
schema
schema_version
status
materialization_commit
methodology_document
oracle_schema_version
validator_implementation_commit
case_count
strata counts
case ids
source identities
source hashes
generation instructions
mutation-pair relationships
privacy review status
secret scan status
path scan status
raw-evidence publication status
not_authorized boundary
```

Each case record must include at minimum:

```text
case_id
stratum
case_kind
public_or_private
input_sources
source_id
media_type
sha256
byte_length
capture_complete
source_state
project_identity
source_revision
python_version_contract
pytest_version
relevant_plugin_contract
normalized_selection_command
expected_publication_mode
```

The manifest must be machine-readable JSON and must be stable under canonical
serialization.

## Freeze Rules

After corpus freeze:

```text
no case replacement
no case removal after seeing producer output
no threshold change
no oracle rewrite to match implementation
no corpus expansion to rescue a weak result
```

A corpus defect must be documented and versioned. It must not be silently
swapped or patched.

## Required Scans

Before materialization can be accepted, the materialized public artifacts must
pass:

```text
JSON validation
path scan
secret scan
raw-evidence exclusion check
license/publication review for committed public-project logs
```

The scan report must state whether raw logs are committed, withheld, or
represented only by hashes and generation instructions.

Absolute private paths, credentials, API keys, private repository content,
private raw logs and private environment variables must not appear in public
artifacts.

## Stop Conditions

Materialization must stop with:

```text
DOMAIN_2_CORPUS_NOT_MATERIALIZABLE
```

if any of the following occur:

```text
required synthetic coverage cannot be produced
required adversarial cases cannot be produced
8 public runs across 3 projects cannot be identified
public run hashes cannot be recorded
generation instructions are not reproducible enough
privacy or secret scan fails
raw public logs cannot be safely published and no safe hash/instruction
representation is produced
case IDs are not unique
mutation pairs are ambiguous
corpus manifest is not valid JSON
corpus manifest cannot be reviewed independently
```

No missing case may be filled by guessing.

## Explicitly Not Authorized

This authorization does not allow:

```text
oracle population
oracle expected-answer authoring
running the Domain 2 producer
implementing the Domain 2 producer
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3
core changes
action enum changes
claim status changes
decision semantics changes
version bump
tag
PyPI publication
```

The accepted validator may be used only to validate corpus metadata format or
future oracle documents after separate authorization. It must not be used to
populate oracle answers during this step.

## Required Materialization Result

The corpus materialization step must end with one of:

```text
DOMAIN_2_CORPUS_MATERIALIZED
DOMAIN_2_CORPUS_NOT_MATERIALIZABLE
CORPUS_MATERIALIZATION_AUTHORIZATION_REVISION_REQUIRED
```

Successful materialization must commit:

```text
corpus_manifest_v1.json
corpus_materialization_report.md
corpus_materialization_results.json
```

and any authorized synthetic fixtures or generation scripts.

## Next Review

After materialization, the next document must be a corpus review:

```text
research/test_build_failure_contract_corpus_materialization_review.md
```

with one of:

```text
DOMAIN_2_CORPUS_ACCEPTED
DOMAIN_2_CORPUS_NEEDS_REVISION
DOMAIN_2_CORPUS_REJECTED
```

Even if the corpus is accepted, oracle population still requires a separate
authorization artifact.
