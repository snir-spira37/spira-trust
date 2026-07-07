# SPIRA Trust with uv and pip

This guide describes the local pilot workflow for teams that build wheels with
`pip`, `uv`, or another Python packaging frontend.

## Local Wheel Gate

Build or collect wheels into one directory, then run SPIRA Trust against the
local artifacts. Keep the SPIRA Trust tool wheel separate from the artifacts
being scanned:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --no-index --find-links ./spira-tooling spira-trust
spira-trust graph ./wheels --output-dir spira-out --sbom cyclonedx-json --evidence-pack spira-out/spira-evidence.zip
```

SPIRA Trust evaluates only the wheel files you provide locally. It does not
resolve dependencies, download from PyPI, execute package code, or consult
online advisory databases.

Directory convention:

```text
./spira-tooling  SPIRA Trust wheel used to install the tool
./wheels         project artifacts to evaluate
```

## uv Example

If `uv` is used to prepare a wheelhouse, keep the resolver step separate from
SPIRA Trust:

```bash
uv pip compile pyproject.toml -o requirements.lock
uv pip download -r requirements.lock --dest wheels
spira-trust graph ./wheels --lockfile requirements.lock --output-dir spira-out
```

SPIRA Trust treats the lockfile as a declared local input. If hashes are present,
it cross-checks those hashes against the wheel bytes on disk. It does not
suggest alternate versions or perform resolver work.

## CI Install Command

For unsigned pilot bundles or TestPyPI dry runs, configure the GitHub Action
`install-command` explicitly:

```yaml
with:
  install-command: "python -m pip install --no-index --find-links ./spira-tooling spira-trust"
```

For a TestPyPI integration run:

```yaml
with:
  install-command: "python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ spira-trust"
```

The plain `python -m pip install spira-trust` default is reserved for the future
production PyPI package.
