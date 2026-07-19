# Nesira Phase 2 Public Wheel Read-Only Assessment Exposure Report

## Status

```text
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED_PENDING_COLD_REPRODUCTION
```

## Implemented Surface

This gate exposes the accepted Nesira Phase 2 read-only assessment surface in
the public wheel as a module-only runtime surface:

```text
python -m spira_core.nesira_phase2_read_only_assessment_cli <request.json>
```

No new console entry point is added.

## Public Wheel Runtime Entries

The built public wheel contains exactly the authorized Nesira Phase 2 runtime
entries:

```text
spira_core/nesira_phase2_assessment_wiring.py
spira_core/nesira_phase2_authority_adapter.py
spira_core/nesira_phase2_identity_adapter.py
spira_core/nesira_phase2_isolation_attestation_adapter.py
spira_core/nesira_phase2_read_only_assessment_cli.py
spira_core/nesira_phase2_signature_adapter.py
```

It does not contain harnesses, fixtures, tests, research reports, Lean files,
runner code, or combined-verdict integration for Nesira Phase 2.

## Crypto Posture

The base project dependency list remains empty:

```text
dependencies = []
```

The crypto dependency is exposed only as an explicit optional extra:

```text
Provides-Extra: nesira-assessment
Requires-Dist: cryptography==49.0.0; extra == 'nesira-assessment'
```

The hash-locked requirements file remains unchanged and remains the
reproduction source for the crypto dependency bytes.

## Read-Only Runtime Checks

The built wheel was run directly with:

```text
python -m spira_core.nesira_phase2_read_only_assessment_cli
```

Observed:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS -> exit 0
TRUST_NOT_EVALUATED                   -> exit 0
TRUST_INSUFFICIENT                    -> exit 0
malformed input                       -> clean JSON tool error, exit 2
```

Exit code 0 means only tool success. It is not permission to act.

## V1 Manifest Maintenance

The Formal Core V1 external reproduction package was refreshed narrowly.

Only `pyproject.toml` is pinned among the files changed by this gate. The V1
manifest update changes only that entry, and `SHA256SUMS` changes only:

```text
pyproject.toml
research/formal_core/external_reproduction_package/artifact_manifest.json
```

The V1 inventory, claims, expected results, and Formal Claims documents were
not changed and contain no Nesira Phase 2 runtime entries.

## Local Verification

Completed locally:

```text
focused public-wheel exposure pytest: 63 passed
V1 external reproduction package test: 5 passed
V1 SHA256SUMS self-check: 622/622
full pytest: 349 passed
compileall: PASS
git diff --check: PASS
```

## Boundary

Still not authorized:

```text
RUNNER
COMBINED_VERDICT
PUBLIC_CLAIM
RELEASE
SEVERANCE_ACTION
```

Cold reproduction from a fresh clone remains required before the final accepted
verdict may be recorded.
