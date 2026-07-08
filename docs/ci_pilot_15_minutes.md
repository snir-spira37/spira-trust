# 15 Minute CI Pilot

This pilot adds SPIRA Trust as a local wheelhouse gate in GitHub Actions.

## Workflow

Create `.github/workflows/spira-trust-gate.yml`:

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

      - name: Build local wheelhouse
        run: |
          mkdir -p wheels
          python -m pip wheel --wheel-dir wheels -r requirements.txt

      - name: Run SPIRA Trust
        run: |
          spira-trust graph wheels \
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

## Exit Code Handling

For a first pilot, let the command fail the job naturally. After the team sees
real output, decide whether warnings should fail or only upload evidence.

Useful meanings:

```text
0  pass for evaluated checks
1  block or input error
2  warning
3  drift detected
4  baseline hash pin mismatch
5  policy hash pin mismatch
6  rebaseline requires explicit confirmation
```

## What To Review

Open the uploaded artifact and inspect:

```text
spira_graph_out/graph_summary.txt
spira_graph_out/spira-decision.json
spira_graph_out/bill_of_materials.json
spira-evidence.zip
```

## CI Rule

Do not run:

```bash
spira-trust rebaseline --yes
```

automatically in CI. Rebaseline is a human approval step.
