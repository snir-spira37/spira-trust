# SPIRA Trust Release Self-Check

SPIRA Trust releases are checked before publication.

This process is a release-evidence ritual, not an independent security audit.
It records what SPIRA checked about its own release artifact, what the previous
public version would have done with the candidate artifact, and what is not
claimed.

The goal is transparency and reproducibility around release evidence. The goal
is not to prove that the release is safe, bug-free, malware-free, or
independently approved.

## Release Invariant

Every production release candidate must be evaluated before publication.

The candidate wheel is checked by two SPIRA versions:

1. the candidate version
2. the previous public version

These are different checks.

The candidate self-check asks:

```text
Can the candidate version produce and validate its own release evidence contract
for the exact wheel that is about to be published?
```

The previous-version gate asks:

```text
Would the already-published previous public version have blocked this candidate
wheel?
```

A release must not silently ignore a blocking result from either check.

## Candidate Self-Check

The candidate self-check runs the candidate `spira-trust` CLI against the
candidate wheel built by the release workflow.

It produces release evidence such as:

- single-artifact trust output
- graph output
- decision JSON
- decision Markdown
- agent summary JSON, when supported by the candidate version
- evidence pack
- release evidence manifest

If the candidate version blocks itself, the release does not publish.

A candidate self-block means the new version could not satisfy its own release
evidence contract for the artifact being released.

There is no documented-exception path for candidate self-check.

The documented previous-block path applies only to the previous-version gate.
It exists because a previously published SPIRA version may block a candidate due
to an intentional release-semantics change.

A candidate version blocking its own release artifact is different. It means the
candidate could not satisfy its own current release evidence contract.

If candidate self-check blocks, the release does not publish. That result cannot
be converted into `DOCUMENTED_PREVIOUS_BLOCK`, and there is no
`DOCUMENTED_CANDIDATE_BLOCK` status.

## Previous Public Version Gate

The previous-version gate runs the previous public `spira-trust` release from
PyPI against the candidate wheel.

The previous public version is resolved from PyPI at release time. It must not
be hardcoded in the production workflow.

The selected previous version must be recorded in evidence, including:

- selected package version
- selected distribution filename
- selected distribution SHA-256
- PyPI source metadata used for selection
- installed command path
- candidate wheel path
- candidate wheel SHA-256

The previous version must be installed with a pinned distribution hash. SPIRA
does not install its own previous release in release CI without recording and
checking the package digest used for that install.

The previous-version gate must be tolerant of older output schemas. It checks
what the previous version concluded about the candidate artifact; it must not
require the previous version to emit the current candidate schema.

## Previous-Version Selection

For a normal production release, the previous public version is:

```text
the highest non-yanked PyPI release version that is strictly lower than the
candidate version
```

The release evidence must record the selected version and the reason it was
selected.

If no previous public version can be resolved, the previous-version gate fails
as release infrastructure failure unless the release is explicitly marked as the
first public release.

A manual previous-version override may exist for local debugging or non-publish
test workflows. It must not be the normal production release path.

## Gate Statuses

The previous-version gate writes a machine-readable gate result.

Allowed statuses:

```text
PASS
DOCUMENTED_PREVIOUS_BLOCK
PREVIOUS_VERSION_BLOCK
PREVIOUS_VERSION_RUN_ERROR
PREVIOUS_VERSION_RESOLUTION_ERROR
PREVIOUS_VERSION_INSTALL_ERROR
PREVIOUS_VERSION_SCHEMA_UNREADABLE
EXPECTED_PREVIOUS_BLOCK_INVALID
EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED
```

`PASS` means the previous public version did not block the candidate artifact.

`DOCUMENTED_PREVIOUS_BLOCK` means the previous public version did block the
candidate artifact, but the block was expected, declared in the repository, and
documented in the release notes.

`PREVIOUS_VERSION_BLOCK` means the previous public version blocked the candidate
artifact and no valid documented previous-block declaration was present.

`PREVIOUS_VERSION_RUN_ERROR` means the previous version could not run cleanly,
crashed, or returned a non-verdict infrastructure failure.

`PREVIOUS_VERSION_RESOLUTION_ERROR` means the workflow could not resolve the
previous public version from PyPI.

`PREVIOUS_VERSION_INSTALL_ERROR` means the previous public version could not be
installed with the pinned hash selected from PyPI metadata.

`PREVIOUS_VERSION_SCHEMA_UNREADABLE` means the helper could not extract a
verdict or useful decision state from the previous version outputs.

`EXPECTED_PREVIOUS_BLOCK_INVALID` means an active expected previous-block
declaration exists, but it is stale or invalid for the current candidate,
previous version, finding codes, or release notes.

`EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED` means an active expected previous-block
declaration exists, but the previous public version did not block the candidate
artifact.

A SPIRA verdict block and a CLI/runtime failure are different failure modes.
They must not be collapsed into the same status.

An expected previous-block declaration only covers an observed SPIRA verdict
block from the previous public version.

It does not cover release infrastructure failures.

If the previous version crashes, exits without a parseable verdict, fails to
produce readable evidence, or cannot be run cleanly, the release fails with the
corresponding infrastructure status even when an expected previous-block
declaration is present.

A declaration expecting `GRAPH_BLOCK` must never convert a CLI crash or
unreadable schema into `DOCUMENTED_PREVIOUS_BLOCK`.

## If the Previous Version Blocks

A previous-version block is not automatically a bad release.

It may mean:

- the candidate artifact contains a real contradiction
- the new version intentionally changes release evidence semantics
- the previous version classified something as blocking that the new release
  represents differently

However, a previous-version block must never be ignored silently.

If the previous public version blocks the candidate, the default result is:

```text
release stops
publish is denied
evidence is preserved
```

A release may proceed only through the documented previous-block path.

## Documented Previous-Block Path

The documented previous-block path exists for intentional, explained release
semantics changes.

The declaration must live in the repository at:

```text
release/expected_previous_block.json
```

It must be committed before the release tag is created. The tag must point to a
commit that already contains the declaration.

The declaration must not be supplied as an ad hoc CI input during the production
publish workflow. A runtime input is not a durable release record.

If the declaration file is present, it must match the candidate version. A stale
or mismatched declaration is a release hygiene failure.

An active expected previous-block declaration is itself part of the release
contract.

If `release/expected_previous_block.json` exists and the previous version does
not block, the release fails with:

```text
EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED
```

A stale exception file must not remain in the repository after the release it
was written for.

If `release/expected_previous_block.json` exists but does not match the current
candidate version, previous version, required finding codes, or release notes,
the release fails with:

```text
EXPECTED_PREVIOUS_BLOCK_INVALID
```

A declaration file is allowed to explain an observed previous-version `BLOCK`.
It is not allowed to explain the absence of a block.

The declaration must identify structured finding codes rather than free-text
message fragments wherever possible. Human-readable messages may change between
versions; finding codes are the durable matching surface.

Minimum declaration fields:

```json
{
  "schema": "SPIRA_EXPECTED_PREVIOUS_BLOCK_V1",
  "candidate_version": "0.6.1",
  "previous_version": "0.6.0",
  "expected_previous_verdict": "GRAPH_BLOCK",
  "expected_finding_codes": [
    "ATTESTATION_DIGEST_MISMATCH"
  ],
  "release_notes_path": "CHANGELOG.md",
  "release_notes_required_terms": [
    "previous version blocked",
    "0.6.0",
    "0.6.1",
    "ATTESTATION_DIGEST_MISMATCH"
  ],
  "why_expected": "Explain why this previous-version block is expected for this release."
}
```

A documented previous block is not a pass.

The gate status must be:

```text
DOCUMENTED_PREVIOUS_BLOCK
```

not:

```text
PASS
```

This distinction is part of the release evidence.

## Release Notes Requirement

If a release proceeds after a previous-version block, the release notes must say
so explicitly.

The release notes must include:

- previous SPIRA version
- candidate SPIRA version
- previous verdict
- blocking finding code or reason
- why the block is expected or intentionally changed
- where the evidence artifact is attached

Release notes referenced by `release/expected_previous_block.json` must mention
the current candidate version.

If the notes file exists but does not contain the candidate version, the helper
treats it as stale release-note residue and fails the release.

The expected-block declaration must not point to release notes from a previous
release.

The mechanical requirement is:

```text
notes file must contain candidate_version
notes file must contain previous_version
notes file must contain DOCUMENTED_PREVIOUS_BLOCK
notes file must contain every expected_finding_code
```

Suggested wording:

```text
Previous-version gate:

The previous public SPIRA Trust version, <previous>, blocked the <candidate>
release candidate with <finding_code>. This release proceeds through the
documented previous-block path because <reason>. The gate result is recorded as
DOCUMENTED_PREVIOUS_BLOCK, not PASS, and the evidence is attached to this GitHub
Release.
```

## Evidence Storage

Release evidence has two storage paths.

For all workflow runs, including failed runs, the workflow uploads release
evidence as a GitHub Actions workflow artifact when possible.

For successful production releases, the evidence must also be attached to the
GitHub Release as release assets.

Workflow artifacts are temporary. GitHub Release assets are the durable public
release evidence.

A successful production release must attach at least:

```text
spira-release-evidence.zip
release_self_evidence_manifest.json
previous_version_gate.json
previous-version-gate.zip
agent_summary.json, when emitted
```

The release is not considered complete until the release evidence assets are
attached to the GitHub Release.

## Release Asset Ordering

The workflow should avoid publishing to PyPI when release evidence cannot be
attached to the GitHub Release.

The preferred production sequence is:

```text
1. build candidate wheel
2. run candidate self-check
3. resolve and install previous public version with pinned hash
4. run previous-version gate
5. upload workflow evidence artifact, even on failure
6. attach release evidence to a draft GitHub Release
7. publish to PyPI
8. publish or finalize the GitHub Release
```

If release asset upload fails before PyPI publication, the release does not
publish to PyPI.

If PyPI publication succeeds but GitHub Release finalization fails, the workflow
must fail visibly and the maintainer must repair the GitHub Release assets
before public announcement.

## Solo-Maintainer Limitation

This process provides transparency, not independent review.

SPIRA Trust may be released by a solo maintainer. The same maintainer may write
the expected previous-block declaration, write the release notes, tag the
release, and trigger the release workflow.

That does not invalidate the ritual, but it limits the claim.

The value of the process is that exceptions are:

- committed to the repository
- tied to the release tag
- checked by CI
- recorded in machine-readable evidence
- attached to the public GitHub Release

The value is not that the exception was independently approved by a separate
party.

## What Is Not Claimed

This process does not prove that the release is safe.

It does not prove:

- the code is correct
- the code is malware-free
- the release is vulnerability-free
- the release is production-ready
- the maintainer made the right judgment
- the expected previous-block declaration was independently reviewed
- the build environment was uncompromised
- the GitHub account or PyPI project was uncompromised
- the previous public SPIRA version was a complete verifier

The process proves only that SPIRA recorded and published its local release
evidence ritual, including what happened when the gate failed or was explicitly
documented.

## Public Summary

Short public wording:

```text
SPIRA releases are checked by SPIRA before publication, including by the
previous public version. If the previous version blocks the candidate, the
release stops unless the block is explicitly declared in the repository,
documented in the release notes, and preserved in the public release evidence.
A documented previous block is recorded as DOCUMENTED_PREVIOUS_BLOCK, not PASS.
```

Decision matrix:

```text
no declaration + previous PASS
  => PASS
  => publish_allowed: true

no declaration + previous GRAPH_BLOCK
  => PREVIOUS_VERSION_BLOCK
  => publish_allowed: false

valid declaration + previous GRAPH_BLOCK + finding code matches + notes match
  => DOCUMENTED_PREVIOUS_BLOCK
  => publish_allowed: true

valid declaration + previous PASS
  => EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED
  => publish_allowed: false

declaration exists but candidate_version / previous_version / notes / codes invalid
  => EXPECTED_PREVIOUS_BLOCK_INVALID
  => publish_allowed: false

valid declaration + previous CLI crash / nonzero without verdict / unreadable schema
  => PREVIOUS_VERSION_RUN_ERROR or PREVIOUS_VERSION_SCHEMA_UNREADABLE
  => publish_allowed: false
```

A documented previous block documents a previous SPIRA verdict. It does not
document a crash, a missing conclusion, stale notes, or a stale exception file.
