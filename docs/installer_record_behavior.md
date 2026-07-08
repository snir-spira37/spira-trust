# Installer RECORD Behavior - Empirical Record

This document records measured behavior for a wheel whose internal file bytes
were changed without updating `RECORD`.

This is not a claim that pip, uv, or any other installer never verifies
`RECORD`. Behavior may differ by installer, version, platform, and installation
mode.

SPIRA Trust's claim is narrower:

> SPIRA performs a pre-install local evidence gate and reports a blocking
> contradiction when archive bytes do not match the wheel's declared `RECORD`
> hashes.

## Fixture

Public fixture:

https://github.com/snir-spira37/spira-trust/tree/main/tests/fixtures/wheels/record_tampered

Files:

- `record_tampered-1.0.0-py3-none-any.whl`
- `record_tampered_clean-1.0.0-py3-none-any.whl`
- `build_record_tampered_fixture.py`
- `expected.json`
- `test_record_tampered_fixture.py`

Mutation:

```text
record_tampered/__init__.py
VALUE = 1 -> VALUE = 2
```

The `RECORD` file is intentionally not updated after the mutation.

The wheel remains a structurally valid ZIP archive.

## Observed Behavior

Measured on 2026-07-07:

```text
OS: Ubuntu 24
Python: 3.12.3
pip: 24.0
uv: 0.11.7
```

| Tool | Version | Command | Result | Post-install check |
|---|---:|---|---|---|
| SPIRA Trust | 0.1.0 / Bundle 026 | `spira-trust trust record_tampered-1.0.0-py3-none-any.whl` | exit 1, `TRUST_BLOCK`, `CONTRADICTION_FOUND` | n/a, blocked pre-install |
| SPIRA Trust | 0.1.0 / Bundle 026 | `spira-trust trust record_tampered_clean-1.0.0-py3-none-any.whl` | exit 0, `TRUST_OK` | n/a |
| pip | 24.0 | `pip install --no-index ./record_tampered-1.0.0-py3-none-any.whl` | exit 0, installed successfully | `import record_tampered` observed `VALUE = 2` |
| uv | 0.11.7 | `uv pip install --no-index ./record_tampered-1.0.0-py3-none-any.whl` | exit 0, installed successfully | `import record_tampered` observed `VALUE = 2` |

## Interpretation Boundaries

Permitted claim:

> In the measured environment above, the tampered wheel installed successfully
> with pip 24.0 and uv 0.11.7, while SPIRA Trust blocked it before install.

Forbidden claims:

- "pip never verifies RECORD."
- "uv never verifies RECORD."
- "This fixture proves ecosystem-wide installer behavior."
- "SPIRA proves packages are safe."

## Maintenance Rule

When this fixture is run against another installer version, append a new row to
the table. Do not overwrite old rows.

Versioned behavior is the evidence.
