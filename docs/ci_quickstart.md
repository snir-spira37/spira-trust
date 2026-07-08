# SPIRA Trust CI Quickstart

This example runs SPIRA Trust against a local wheelhouse in GitHub Actions.

```yaml
name: SPIRA Trust Gate

on:
  workflow_dispatch:
  pull_request:

jobs:
  spira-trust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install SPIRA Trust
        run: |
          python -m pip install --upgrade pip
          python -m pip install spira-trust==0.5.8
          spira-trust version

      - name: Run SPIRA Trust graph gate
        run: |
          spira-trust graph ./wheels \
            --output-dir spira_graph_out \
            --sbom cyclonedx-json \
            --verify-embedded-sboms \
            --evidence-pack spira-evidence.zip

      - name: Upload SPIRA evidence
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: spira-evidence
          path: |
            spira_graph_out/**
            spira-evidence.zip
```

Do not run `spira-trust rebaseline --yes` automatically in CI. Rebaseline is a
human approval step, not a routine build step.
