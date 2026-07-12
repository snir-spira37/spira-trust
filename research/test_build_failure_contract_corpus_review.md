# Test/Build Failure Contract Corpus Review

Status:

```text
DOMAIN_2_CORPUS_NEEDS_REVISION
CORPUS_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed materialization commit:

```text
e6bae04 Materialize Domain 2 test failure corpus
```

Authorization:

```text
research/test_build_failure_contract_corpus_materialization_authorization.md
DOMAIN_2_CORPUS_MATERIALIZATION_AUTHORIZED
```

This is a corpus review only. It does not authorize oracle population, producer
implementation, Gate B, Domain 3, or release activity.

## Review Summary

The materialized corpus is a strong first pass, but it is not yet accepted.

The synthetic stratum is broad and the public-safety boundary is preserved.
However, the public real-world stratum currently contains generation
instructions and metadata only. It does not contain materialized public run
evidence, nor hashes of regenerated run outputs. Therefore it does not yet
satisfy the methodology requirement for reproducible real-world runs.

Final verdict:

```text
DOMAIN_2_CORPUS_NEEDS_REVISION
```

## Checks That Passed

Mechanical manifest checks passed:

```text
case_count: 38
unique case IDs: 38
synthetic cases: 30
public reproducible instruction cases: 8
public projects represented: 3
declared mutation pairs: 6
missing source files: 0
source hash mismatches: 0
```

The manifest and results JSON parse successfully.

The public artifacts report:

```text
json_validation: PASS
privacy_scan: PASS
path_scan: PASS
secret_scan: PASS
raw_evidence_exclusion_check: PASS
```

No oracle answer fields were found in corpus records:

```text
expected_result_identity: absent
expected_policy_action: absent
result_identity_sha256: absent
scope_identity_sha256: absent
```

All cases are marked:

```text
oracle_expected_answers: NOT_POPULATED
producer_output_seen: false
```

This correctly preserves the boundary between corpus materialization and oracle
population.

## Synthetic Stratum

The synthetic stratum satisfies the required edge-case coverage:

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

Instruction-injection coverage is present:

```text
synthetic_injection_all_passed
synthetic_injection_proceed
synthetic_injection_spira_json
```

The `recommended_agent_action` string found in the corpus appears only inside
the adversarial synthetic console text. That is valid evidence content, not an
oracle answer.

Verdict:

```text
SYNTHETIC_STRATUM_ACCEPTED
```

## Mutation Pairs

The six declared mutation pairs refer to existing case IDs and are marked:

```text
oracle_expected_answers: NOT_POPULATED
```

They cover:

```text
factual mutation
declared formatting mutation
declared path mutation
instruction-injection mutation
rerun target derivability mutation
```

Verdict:

```text
MUTATION_PAIRS_ACCEPTED
```

## Blocking Finding: Public Runs Are Not Yet Materialized

The methodology and authorization require a public real-world stratum with:

```text
8 real-world runs
across at least 3 public projects
public repository identity
pinned commit SHA
pinned Python version
pinned pytest version
recorded command
recorded dependency environment
deterministic generation instructions
source hashes
```

The materialized corpus includes 8 public case directories across 3 public
projects:

```text
https://github.com/pallets/click.git
https://github.com/pallets/flask.git
https://github.com/psf/requests.git
```

But each public case currently contains only:

```text
generation_instructions.txt
metadata.json
```

The instructions explicitly say:

```text
raw_logs: not committed; regenerate from public source before oracle population
```

This preserves privacy and licensing caution, but it means the public stratum
does not yet contain materialized run evidence or hashes of the regenerated
run outputs.

The current hashes prove the generation-instruction files and metadata, not the
actual pytest console or JUnit output that a future oracle would evaluate.

Therefore the public stratum is better described as:

```text
PUBLIC_REPRODUCIBLE_INSTRUCTION_SET
```

not yet:

```text
PUBLIC_REPRODUCIBLE_RUN_CORPUS
```

Required correction:

```text
For each of the 8 public cases, either:

1. materialize safe public run outputs and record their hashes, or
2. materialize local run outputs, withhold raw bytes from public commit after
   privacy/licensing review, and publish stable hashes plus exact reproduction
   instructions.
```

In either path, the manifest must distinguish:

```text
instruction_hashes
raw_run_output_hashes
raw_run_output_publication_status
```

Verdict:

```text
PUBLIC_RUN_EVIDENCE_NOT_YET_MATERIALIZED
```

## Blocking Finding: Dependency Environment Is Underspecified

The public generation instructions record:

```text
repository
commit
python: cpython 3.12.4
pytest: 8.3.2
command
```

They do not yet record a dependency environment sufficient for independent
replay, such as:

```text
install command
constraints file hash
requirements file hash
lockfile hash
package manager command
environment variable policy
plugin discovery policy
```

The methodology requires a recorded dependency environment. Without it, two
reviewers can run the same command at the same commit and still get different
collection or import behavior.

Required correction:

```text
Add deterministic environment instructions and hashes for each public run.
```

Verdict:

```text
PUBLIC_RUN_ENVIRONMENT_UNDERSPECIFIED
```

## Non-Blocking Notes

The corpus generator is useful and should be preserved. The review does not
require replacing the synthetic stratum or changing the accepted validator.

The public raw logs do not need to be committed if licensing or privacy review
is uncertain. It is acceptable to publish only hashes and reproducible
instructions, provided the run outputs are actually materialized and hashed
before oracle population.

## Required Revision

The next revision should be limited to corpus materialization:

```text
1. Materialize or hash actual public run outputs for all 8 public cases.
2. Record deterministic dependency-environment instructions.
3. Separate instruction hashes from raw run output hashes.
4. Update corpus_manifest_v1.json.
5. Update corpus_materialization_report.md.
6. Update corpus_materialization_results.json.
7. Re-run JSON validation, path scan, secret scan and raw-evidence exclusion
   check.
```

Still not authorized:

```text
oracle population
oracle expected answers
producer implementation
Gate B
Domain 3
release/version/tag/PyPI
```

## Final Verdict

```text
DOMAIN_2_CORPUS_NEEDS_REVISION
CORPUS_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

The corpus is close: synthetic coverage, mutation pairs, manifest integrity and
privacy posture are acceptable. The blocker is the public real-world stratum:
instructions alone are not yet materialized public run evidence.
