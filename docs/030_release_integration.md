# SPIRA Trust 030 Release Integration

030 is an integration and dogfooding release. It does not add a new detection
engine. Its claim is narrower:

```text
SPIRA Trust verifies its own release evidence before asking anyone else to trust it.
```

## Scope

- Build public wheel `spira-trust 0.5.2`.
- Generate self-evidence for the release wheel.
- Keep `spira-decision.json` and `evidence.zip` hash contracts aligned.
- Ship the public `schemas/spira_decision_v1.json` decision contract in both
  the bundle and the wheel.
- Embed a narrow CycloneDX SBOM under `.dist-info/sboms/` inside the public
  wheel and verify it locally with `--verify-embedded-sboms`.
- Provide a TestPyPI Trusted Publishing workflow skeleton.
- Provide a composite GitHub Action wrapper over the existing CLI.
- Fix bundle ZIP metadata so `install.sh` can be executable after Unix unzip.

## Not Claimed

- Not PyPI production GA in 030_003 unless a live TestPyPI publish is executed
  and evidenced separately.
- Not a new trust engine.
- No secrets scanning, AST scanning, entropy scanning, resolver behavior,
  online advisory integration, malware execution, or deep legal/SPDX analysis.
- The TestPyPI workflow is a dry-run integration surface until configured in a
  public repository with a TestPyPI trusted publisher.

## Local Golden Path

```bash
unzip SPIRA_TRUST_PILOT_BUNDLE_030_INTEGRATION_GATE_TESTPYPI_DOGFOODING_003.zip -d spira-trust-030
cd spira-trust-030
./install.sh
./bin/spira-trust version
```

If a ZIP extractor ignores Unix mode bits, use `bash install.sh`; that is a
tooling fallback, not the 030 golden path.

## TestPyPI Dry Run

The workflow at `.github/workflows/testpypi-trusted-publishing.yml` is designed
for a repository configured with a TestPyPI trusted publisher. It:

1. Builds the public wheel.
2. Installs that exact wheel.
3. Runs SPIRA self-evidence on the wheel.
4. Uploads the evidence pack as a workflow artifact.
5. Publishes only Python distribution files to TestPyPI.

The evidence pack is not uploaded to PyPI as a package distribution.

## Decision Contract Validation

030_002 and later include `schemas/spira_decision_v1.json` as a public local contract.
Release self-evidence validates generated `spira-decision.json` files against
the frozen `SPIRA_DECISION_V1` surface before the bundle is accepted.

## GitHub Action Wrapper

`action.yml` is a composite action wrapper around `spira-trust graph`. It
exposes:

- `verdict`
- `combined-verdict`
- `decision-json`
- `evidence-pack`

The action is intentionally thin. It does not create a second policy language
or a second decision engine.

Before production PyPI publication, set `install-command` explicitly for the
environment being tested. Examples:

```yaml
with:
  install-command: "python -m pip install --no-index --find-links ./spira-tooling spira-trust"
```

For TestPyPI dry runs:

```yaml
with:
  install-command: "python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ spira-trust"
```

The default `python -m pip install spira-trust` is intended for the future
production PyPI package, not for unsigned local pilot bundles.

Keep the tool wheelhouse separate from the scanned artifact wheelhouse:

```text
./spira-tooling  SPIRA Trust wheel used to install the tool
./wheels         artifacts evaluated by `spira-trust graph`
```
