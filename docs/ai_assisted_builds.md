# AI-Assisted Builds

AI coding agents can generate code, packaging changes, and release artifacts very quickly.

That creates a simple question:

> What actually got built?

SPIRA Trust helps answer that question for Python wheel artifacts.

It does not review code quality.
It does not decide whether an AI-generated patch is good.
It does not prove that code is safe.

It verifies the local wheel artifact before install or release.

```text
AI agents generate artifacts.
SPIRA verifies artifacts.
Humans approve.
```

## Artifact Trust, Not Code Review

SPIRA Trust does not answer:

- Is this code well designed?
- Are the tests sufficient?
- Is the AI-generated patch correct?
- Is the package malware-free?
- Is the package safe to run?

SPIRA answers a narrower question:

> Does this local wheel artifact match the evidence and policy we can verify before install?

## Why This Matters For Agentic Development

AI-assisted development can produce many small release candidates:

```text
0.5.4
0.5.5
0.5.6
0.5.7
0.5.8
```

The operational risk is not only that the code may be wrong.

The operational risk is that nobody can clearly answer:

- Which artifact was actually built?
- Did the wheel structure change?
- Did the embedded SBOM still match?
- Did the lockfile intent still match?
- Did the baseline drift?
- Which artifact was approved?
- Which evidence belongs to which version?

SPIRA gives each wheel a local evidence record before it moves forward.

## Quick Demo With SPIRA's Own Wheel

Install SPIRA Trust:

```bash
python -m pip install spira-trust
```

Download the public SPIRA Trust wheel into a local wheelhouse:

```bash
mkdir -p wheels
python -m pip download spira-trust \
  --only-binary=:all: \
  --no-deps \
  -d wheels
```

Run the artifact gate:

```bash
spira-trust graph wheels \
  --output-dir out/graph \
  --sbom cyclonedx-json \
  --verify-embedded-sboms \
  --evidence-pack out/spira-evidence.zip
```

Review the human-readable outputs:

```bash
cat out/graph/graph_summary.txt
cat out/graph/spira-decision.md
```

Expected result for the current public SPIRA Trust wheel: the command exits 0
and the graph summary reports a passing verdict. If a future wheel adds
declared dependencies that you did not download into the wheelhouse, SPIRA may
surface `GRAPH_OK_WITH_UNVERIFIED`; that means the artifact passed the checks
SPIRA ran, but the local dependency closure was not complete.

Machine-readable and evidence outputs include:

```text
out/graph/spira-decision.json
out/graph/spira-decision.md
out/graph/graph_report.json
out/graph/bill_of_materials.json
out/graph/spira-trust.cdx.json
out/spira-evidence.zip
```

If you want Claude, Codex, or another coding agent to run SPIRA as part of its
local workflow, see
[`agent_integration.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/agent_integration.md).

This demo uses `spira-trust` itself because the public wheel includes an
embedded SBOM under `.dist-info/sboms/`, so `--verify-embedded-sboms` can check
local embedded SBOM consistency.

For a general wheelhouse whose wheels may not contain embedded SBOMs, use:

```bash
spira-trust graph wheels \
  --output-dir out/graph \
  --sbom cyclonedx-json \
  --evidence-pack out/spira-evidence.zip
```

Use `--verify-embedded-sboms` when you want SPIRA to check embedded SBOM
consistency for wheels that contain `.dist-info/sboms/`.

## Example Team Rule

A team using coding agents can adopt a simple rule:

> No AI-generated wheel is installed, promoted, or released until SPIRA Trust
> produces a passing decision and evidence pack.

This does not mean the code is correct.

It means the artifact passed the local evidence gate.

## CI Pattern

```yaml
name: SPIRA Trust artifact gate

on:
  pull_request:
  push:
    branches:
      - main

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
          python -m pip install spira-trust

      - name: Build or collect wheels
        run: |
          mkdir -p wheels
          python -m pip wheel . -w wheels

      - name: Run SPIRA Trust gate
        run: |
          spira-trust graph wheels \
            --output-dir spira-out \
            --sbom cyclonedx-json \
            --evidence-pack spira-out/spira-evidence.zip

      - name: Upload SPIRA evidence
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: spira-trust-evidence
          path: spira-out/**
```

For production CI, pin the `spira-trust` version if your team requires a
reproducible toolchain.

## Human Review

After SPIRA runs, a human should review:

- `spira-decision.md`
- `graph_summary.txt`
- `spira-decision.json`

Ask:

- What was checked?
- What was not checked?
- Did the artifact pass?
- Did anything require human review?
- Did the artifact drift from baseline?
- Is the evidence pack complete?

## Positioning

SPIRA Trust is useful in AI-assisted build workflows because agents generate
artifacts quickly.

But SPIRA is not an AI governance platform.

It is a local evidence gate for Python wheel artifacts.

The same artifact evidence workflow is useful for:

- AI-assisted builds
- vendor wheel intake
- air-gapped environments
- regulated CI gates
- baseline drift review
- release evidence packs
