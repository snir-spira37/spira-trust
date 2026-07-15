# Machine Contract Passthrough Fixture Manifest Hash Repair Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_FIXTURE_MANIFEST_HASH_REPAIR_AUTHORIZED

FIXTURE_MANIFEST_HASH_FIELDS_ONLY

EXISTING_FIXTURE_FILES_ONLY

NO_FIXTURE_SEMANTIC_CHANGES

NO_SCHEMA_CHANGE

NO_VALIDATOR_CHANGE

NO_MVP_CHANGE

NO_RUNNER_CHANGE

VALIDATOR_FIXTURE_REGRESSION_REQUIRED

RESULTS_REPORT_REVIEW_REQUIRED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

The Formal Core V1 integration boundary preflight found that the accepted
machine-contract passthrough fixture regression currently fails because all
fixture files report:

```text
ENVELOPE_FILE_HASH_MISMATCH
```

The fixture files themselves are not modified in the working tree. This
authorization permits only repairing `fixture_manifest.json` hash fields to
match the existing committed fixture files.

## 2. Authorized File Changes

Only this file may be modified:

```text
research/machine_contract_passthrough_fixtures/fixture_manifest.json
```

Research outputs:

```text
research/machine_contract_passthrough_fixture_manifest_hash_repair_results.json
research/machine_contract_passthrough_fixture_manifest_hash_repair_report.md
research/machine_contract_passthrough_fixture_manifest_hash_repair_review.md
```

## 3. Required Checks

The repair must:

```text
preserve fixture count: 43

preserve fixture paths

preserve expected outcomes

preserve classifications

preserve contradiction classes

preserve expected fail-closed flags

update only envelope_sha256 fields when mismatched

run validator fixture regression

run passthrough MVP tests

run envelope validator tests
```

## 4. Acceptance Gates

```text
fixture count: 43

fixture content changes: 0

manifest non-hash semantic changes: 0

updated envelope_sha256 fields: 43 or fewer

validator fixture regression: PASS

tests/test_machine_contract_passthrough_envelope_validator.py: PASS

tests/test_machine_contract_passthrough_mvp.py: PASS
```

## 5. Explicitly Not Authorized

This authorization does not permit:

```text
editing fixture JSON files

changing expected validator outcomes

changing contradiction taxonomy

changing schema

changing validator code

changing MVP code

changing Formal Core code

changing benchmark runners

live agent sessions

production claim

release
```

## 6. Review Outcomes

The review must end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_FIXTURE_MANIFEST_HASH_REPAIR_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_FIXTURE_MANIFEST_HASH_REPAIR_NEEDS_REVISION

MACHINE_CONTRACT_PASSTHROUGH_FIXTURE_MANIFEST_HASH_REPAIR_REJECTED
```
