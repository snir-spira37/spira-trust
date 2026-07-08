# 10 Minute Demo

This demo shows SPIRA Trust as a local evidence gate before installing a wheel.

## 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install spira-trust==0.5.8
spira-trust version
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install spira-trust==0.5.8
spira-trust version
```

## 2. Download A Wheel Without Installing It

```bash
mkdir wheels
python -m pip download --no-deps --only-binary=:all: --dest wheels requests
```

## 3. Check One Wheel

```bash
spira-trust trust wheels/*.whl --output-dir spira_trust_out
```

Read the terminal verdict first. Then inspect:

```text
spira_trust_out/artifact_trust_summary.txt
spira_trust_out/artifact_trust_report.json
```

## 4. Check The Local Wheelhouse

```bash
spira-trust graph wheels \
  --output-dir spira_graph_out \
  --sbom cyclonedx-json \
  --verify-embedded-sboms \
  --evidence-pack spira-evidence.zip
```

Inspect:

```text
spira_graph_out/graph_summary.txt
spira_graph_out/spira-decision.json
spira_graph_out/bill_of_materials.json
spira_graph_out/spira-trust.cdx.json
spira-evidence.zip
```

## 5. Demo Questions

Ask the reviewer:

```text
1. Did the terminal verdict tell you enough?
2. Which output would you save in CI?
3. Did SPIRA surface anything you did not expect?
4. What felt useful, noisy, or unclear?
```
