# Claims and Boundaries

## EMPIRICALLY_REPRODUCED

A reviewer may reproduce that Phase 1 validates structure, binding, evidence
integrity, and safe evidence paths for `SEVERANCE_AUTHORIZATION` and
`LEGACY_ISOLATION_RESULT` artifacts.

## TEST_SUITE_VALIDATED

```text
focused Phase 1 tests: 11 passed
full pytest: 281 passed
compileall: PASS
```

## STRUCTURE_VALIDATED

Phase 1 checks JSON/schema shape and DSSE envelope/payload decoding for the two
supported artifact types.

## BINDING_VALIDATED

Phase 1 checks subject, candidate, environment, profile/policy, revision, and
temporal binding against the provided expected context.

## EVIDENCE_INTEGRITY_VALIDATED

Phase 1 checks evidence file existence and SHA256 integrity for declared legacy
isolation evidence files.

## SAFE_EVIDENCE_PATHS_VALIDATED

Phase 1 rejects traversal, absolute paths, drive-relative paths, UNC/network
paths, symlink escapes, directories as evidence files, and duplicate canonical
evidence paths.

Synthetic absolute paths such as `/tmp/evidence.txt` and `C:/tmp/evidence.txt`
may appear only as documented negative test vectors.

## NOT_EVALUATED

```text
cryptographic signature trust
signer identity
signer authority
actual isolation execution
independent isolation observation
severance authorization
permission to sever
production readiness
product integration
public capability availability
```

## NOT_CLAIMED

Phase 1 does not claim that a signature is trusted, that a signer is authorized,
that isolation actually executed, that severance is authorized, that it is safe
to proceed, or that this capability is publicly exposed in the product.

Phase 1 does not add a new Lean proof. Existing Formal Core identity may be
checked separately, but the Phase 1 validator, DSSE parser, path validator, and
end-to-end trust path are not formally proved by this package.
