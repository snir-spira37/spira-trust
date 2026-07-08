# record_tampered - empirical RECORD fixture

This fixture contains two tiny Python wheels:

- `record_tampered_clean-1.0.0-py3-none-any.whl`
- `record_tampered-1.0.0-py3-none-any.whl`

The tampered wheel is a structurally valid ZIP archive, but one byte inside
`record_tampered/__init__.py` was changed after the wheel `RECORD` file was
written.

That means the archive opens, but the physical bytes no longer match the hash
declared for that file in `RECORD`.

## Files

- `build_record_tampered_fixture.py` - deterministic fixture builder
- `expected.json` - pinned hashes and expected SPIRA verdicts
- `record_tampered-1.0.0-py3-none-any.whl` - tampered artifact
- `record_tampered_clean-1.0.0-py3-none-any.whl` - clean control
- `test_record_tampered_fixture.py` - fixture acceptance tests

## Expected SPIRA Behavior

```bash
spira-trust trust record_tampered_clean-1.0.0-py3-none-any.whl
# expected: TRUST_OK, exit 0

spira-trust trust record_tampered-1.0.0-py3-none-any.whl
# expected: TRUST_BLOCK, exit 1
```

## Measurement Discipline

This fixture is not a claim that any installer always behaves a certain way.
Installer behavior can vary by tool, version, installation mode, and platform.

Use this fixture to reproduce behavior in a specific environment and report the
exact versions you measured.
