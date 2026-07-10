# SPIRA Trust CLI

SPIRA Trust is a local evidence gate for Python wheel artifacts.

It verifies wheel structure and `RECORD` integrity before installation, builds
an evidence-backed local dependency graph and BOM, applies pinned local policy,
detects drift from an approved baseline, and exports evidence for enterprise
security workflows.

It complements CVE scanners, package firewalls, SBOM tools, and provenance
systems by proving what is physically present on disk.

`spira-trust` is the public pilot CLI. `spira-trust trust` triages one Python
artifact. `spira-trust graph` extends the same evidence model to a local folder
of wheels that you explicitly provide.

The public wheel exposes only `spira-trust` and `spira`. Internal SPIRA
workspace commands are not part of the public pilot wheel.

It asks a narrow question:

```text
What does this package claim, what does the raw artifact prove, and is there
enough evidence to return TRUST_OK_WITH_NOTES, TRUST_WARN, or TRUST_BLOCK?
```

For market positioning and capability boundaries, see
[`docs/capability_matrix.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/capability_matrix.md).

## Install

From production PyPI:

```bash
python -m pip install spira-trust==0.6.1
spira-trust version
```

Every production release is published to PyPI with Trusted Publishing/OIDC.
PyPI displays release provenance for the wheel artifact.

For release closure notes, see
[`docs/030_closure_note.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/030_closure_note.md).

For the release self-check and previous-version gate contract, see
[`docs/release_self_check.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/release_self_check.md).

For pilot onboarding, start with
[`docs/pilot_readiness_pack.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/pilot_readiness_pack.md).

For CI, see [`docs/ci_quickstart.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/ci_quickstart.md).

For external pilot handoff, see:

- [`docs/pilot_outreach_email.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/pilot_outreach_email.md)
- [`docs/why_spira_trust.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/why_spira_trust.md)
- [`docs/demo_10_minutes.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/demo_10_minutes.md)
- [`docs/ci_pilot_15_minutes.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/ci_pilot_15_minutes.md)
- [`docs/pilot_feedback_questions.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/pilot_feedback_questions.md)

Use case:

- [`docs/ai_assisted_builds.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/ai_assisted_builds.md) - use SPIRA Trust to gate Python wheel artifacts produced by coding agents before install or release.
- [`docs/agent_context_tax.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/agent_context_tax.md) - static benchmark of how much release evidence context an agent must ingest to answer narrow gate questions.

From this repository:

```bash
python -m pip install .
```

## Run

Human-readable output is the default:

```bash
spira-trust trust path/to/package.whl --output-dir spira_trust_out
```

Machine-readable output:

```bash
spira-trust trust path/to/package.whl --output-dir spira_trust_out --format json
```

Agent-facing local memory:

```bash
spira-trust graph dist \
  --output-dir spira_graph_out \
  --evidence-pack spira-evidence.zip

spira-trust status dist --format json
spira-trust status --agent --artifact dist/example.whl --format json
spira-trust cache --artifact dist/example.whl --command-fingerprint <sha256> --format json
```

`graph` writes `agent_summary.json` alongside the decision report and stores a
local summary index under `.spira/agent_summaries/` by default. `status`
re-hashes current wheels before matching that local state.
`cache` reuses a prior agent action only when the artifact bytes and requested
evidence context match.

`agent_summary.json` includes an
[Agent Action Contract](docs/agent_action_contract.md): a small deterministic
surface with `stop`, `recommended_agent_action`, `reason_codes`, and evidence
pointers so agents do not have to infer gate policy from broad reports.

The command writes:

- `artifact_trust_summary.txt`
- `artifact_trust_report.json`
- detailed local evidence files under the selected output directory

By default, the CLI prints the summary and public report path only. Use
`--full-evidence` when you want the detailed local evidence paths printed in
the terminal.

## Local Trust Graph

Use graph mode when you have several local wheels and want one evidence graph
over their declared relationships:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out
```

You can pass individual wheels or folders. Folders are scanned for `*.whl`
files only:

```bash
spira-trust graph dist/pkg_a.whl dist/pkg_b.whl --output-dir spira_graph_out
```

Machine-readable output:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out --format json
```

### Evidence-backed CycloneDX export

SPIRA Trust can export a CycloneDX JSON SBOM from its local evidence BOM:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out --sbom cyclonedx-json
```

The default output path is:

```text
spira_graph_out/spira-trust.cdx.json
```

This SBOM is generated only from provided local wheel artifacts. It includes
artifact SHA-256 hashes, RECORD verification status, local dependency
relationships between provided wheels, SPIRA graph status, policy status, and
evidence properties. Top-level properties include both the source graph verdict
(`spira:graph:verdict`) and the combined policy verdict
(`spira:policy:combined_verdict`).

Declared dependencies that were not provided as local wheels are recorded as
SPIRA properties (`spira:declared_missing_requirement`), not invented as
CycloneDX components.

Embedded SBOM files found under a wheel's `.dist-info/sboms/` directory are
recorded as evidence properties with path, SHA-256, byte count, and format hint.
By default, SPIRA does not trust, parse, merge, validate, or mutate embedded
SBOM files. When `--verify-embedded-sboms` is supplied, SPIRA performs a narrow
local consistency check for supported JSON/CycloneDX metadata fields against the
local wheel metadata. This is not full SBOM schema validation.

Absolute local paths are omitted by default. Include them only when needed for a
local/private workflow:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out --sbom cyclonedx-json --include-local-paths
```

The export does not add vulnerability intelligence, malware detection, legal
license analysis, provenance verification, dependency resolution, network
access, wheel mutation, or code execution.

If you want the graph evidence to record the bundle/build SHA that produced the
run, pass it explicitly:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out --bundle-sha256 <sha256>
```

Strict closure mode treats a declared relationship whose wheel was not provided
as a warning instead of an informational note:

```bash
spira-trust graph path/to/wheel-folder --strict-closure
```

License policy screening is optional and explicit. Provide a local JSON policy
file when you want SPIRA to screen observed license visibility strings:

```bash
spira-trust graph path/to/wheel-folder --license-policy policy.json
```

Example policy:

```json
{
  "schema": "SPIRA_LICENSE_POLICY_V1",
  "schema_version": "1.0",
  "match_mode": "case_insensitive_substring",
  "blocked_terms": ["AGPL", "General Public License"],
  "warn_terms": ["Custom", "Unknown"]
}
```

Declared entry-point command screening is also optional and explicit. Provide a
local JSON policy file when you want SPIRA to screen command names declared by
wheel `entry_points.txt`:

```bash
spira-trust graph path/to/wheel-folder --entry-point-policy entry_policy.json
```

Example entry-point policy:

```json
{
  "schema": "SPIRA_ENTRY_POINT_POLICY_V1",
  "schema_version": "1.0",
  "match_mode": "exact_command_name",
  "case_insensitive": true,
  "blocked_command_names": ["pip", "python", "pytest"],
  "warn_command_names": ["ls", "ssh"]
}
```

Target environment screening is optional and explicit. It reads wheel filename
tags and compares them with a local target JSON file:

```bash
spira-trust graph path/to/wheel-folder --target-environment target_environment.json
```

Example target:

```json
{
  "schema": "SPIRA_TARGET_ENVIRONMENT_V1",
  "schema_version": "1.0",
  "python_tag": "cp312",
  "abi_tag": "cp312",
  "platform_tag": "manylinux_2_17_x86_64",
  "strict_target": false,
  "block_on_mismatch": false
}
```

Graph mode writes:

- `graph_summary.txt`
- `graph_report.json`
- `spira-decision.json` and `spira-decision.md`, the stable decision contract
  for CI/audit integrations
- `bill_of_materials.json` with the provided-wheel BOM, declared local
  relationship depth, license visibility, and subtree integrity digests
- `input_manifest.json` with each provided wheel's SHA, normalized name,
  file count, and uncompressed byte count
- `graph_evidence_manifest.json` with schema version, tool identity,
  environment capture, and evidence file hashes
- governance package-lock evidence for the graph outputs
- `graph_evidence_package_result.json` with the governance package paths and
  post-lock verification result

To archive the decision and evidence files together, pass:

```bash
spira-trust graph path/to/wheel-folder --output-dir spira_graph_out --evidence-pack spira-evidence.zip
```

Graph mode is deliberately local:

- no dependency resolver
- no PyPI/network access
- no install
- no execution of package code
- only declared relationships from local wheel `METADATA`

## Bill Of Materials

Graph mode writes a local BOM at `bill_of_materials.json`. The BOM is visibility
only: it records what was present in the provided local wheel set, not what could
exist on PyPI or in a resolver output.

The BOM includes:

- root, provided-transitive, orphan, and declared-missing artifacts
- `depth` over the provided-wheel subgraph only
- `metadata_license` and `license_classifiers` from wheel `METADATA`
- detected LICENSE/COPYING/NOTICE-like files with path, SHA-256, and byte count
- `subtree_integrity_digest` for provided local nodes
- `digest_covers_fields`, written into the BOM so digest coverage is explicit
- optional `license_policy_screening` when `--license-policy` is supplied
- declared `entry_points.txt` console/gui command names and a separate
  `entry_points_digest`
- optional `entry_point_policy_screening` when `--entry-point-policy` is
  supplied
- wheel filename python/abi/platform tags and a separate `wheel_tags_digest`
- optional `target_environment_screening` when `--target-environment` is
  supplied
- `combined_policy_verdict`, a transparent aggregator over evaluated layers

The `subtree_integrity_digest` is tamper-evidence versus a trusted baseline. It
is not a safety proof and does not cover declared dependencies whose wheels were
not provided. The digest is computed from local content and declared visibility
fields, not from the graph verdict or policy mode.

License data in V3-A is visibility, not legal policy. SPIRA records declared
metadata and license-file evidence separately; it does not compare them or issue
license compliance findings in this BOM.

When a license policy file is supplied, V3-B performs narrow local string
screening over observed license visibility values. This is still not legal
advice, legal compliance certification, SPDX expression parsing, or semantic
license interpretation. A blocked policy match can make the graph verdict
`GRAPH_BLOCK`; a warning match can make it `GRAPH_WARN`.

When an entry-point policy file is supplied, V3-C performs declared command-name
screening. This is `DECLARED_ENTRY_POINT_NAME_SCREENING`, not runtime PATH
hijacking detection. Matching is exact command-token matching under the policy's
case-sensitivity rule. SPIRA does not fold executable variants such as `.exe`,
`pip3`, fuzzy typos, or visual confusables. Entry-point visibility and policy do
not change `subtree_integrity_digest`; entry points have their own
`entry_points_digest`.

When a target environment file is supplied, V3-D performs narrow wheel filename
tag relevance screening. This is not full `packaging.tags` compatibility and not
an installability guarantee. Universal wheels such as `py3-none-any` are not
treated as target mismatches. By default, non-exact target relevance creates
notes only; `strict_target` can raise warnings; `block_on_mismatch` is an
explicit user policy choice and is not a safety defect claim. Target tag
visibility and policy do not change `subtree_integrity_digest`; wheel tags have
their own `wheel_tags_digest`.

The combined verdict is an aggregator only. It keeps `per_layer` detail,
records `decided_by`, and separates `evaluated_layers` from
`not_evaluated_layers`. A layer that did not run is `NOT_EVALUATED`, not `OK`.
`GRAPH_OK` means OK across the evaluated layers only.

Lockfile cross-checking is optional and explicit. Provide a local lockfile when
you want SPIRA to compare pinned package facts against the local wheels you
provided:

```bash
spira-trust graph path/to/wheel-folder --lockfile requirements.txt
```

V4-B/V5 supports a narrow local subset: `name==version` requirements lines,
pip-tools style multiline `--hash=sha256:<hash>` requirements, `Pipfile.lock`
JSON package name/version/hash fields, `poetry.lock` `[[package]]`
name/version/hash facts, and `uv.lock` `[[package]]` name/version/hash facts.
Unsupported syntax is reported as a note, not silently accepted and not
hard-blocked solely because unsupported. SPIRA does not resolve, fetch, suggest,
or install packages from the lockfile. A lockfile hash mismatch against the
provided wheel SHA is a blocking factual contradiction.

Unified policy packs are also supported:

```bash
spira-trust graph path/to/wheel-folder --policy-pack spira-policy.json --policy-sha256 <sha256>
```

The policy pack precedence is deterministic: environment overrides, then
explicit CLI flags, then policy pack contents, then defaults. If
`--policy-sha256` is supplied, the pack must be self-contained. Path references
inside a pinned pack are rejected before graph scan with `POLICY_UNTRUSTED`
because the pin would otherwise protect only the wrapper file and not the
referenced policy content. Each run writes `effective_policy.json` into the
graph evidence package so audits can see which layers ran and where each value
came from. A missing pack section is `NOT_EVALUATED`, not `OK`.

## Baseline Drift Watch

Use drift mode when you already approved a BOM and want to know whether the
current local wheel folder changed:

```bash
spira-trust drift path/to/wheel-folder --baseline baseline_bill_of_materials.json --baseline-sha256 <sha256>
```

Drift is a fact, not a verdict. A changed wheel, added wheel, removed wheel, or
changed `subtree_integrity_digest` means the current folder no longer matches
the baseline you pinned. It does not mean the change is bad. Policy verdicts
remain separate and can still return `BLOCK` or `WARN`.

The `--baseline-sha256` pin is the trust anchor. If it is supplied and the
baseline file does not match, SPIRA refuses before scanning the current folder.
If it is omitted, the run is allowed but the report marks the baseline as
`UNPINNED`; `NO_DRIFT` then only means the wheels match that local baseline file.

Drift mode writes:

- `drift_summary.txt`
- `drift_report.json`
- `current_graph/...` with the current graph/BOM evidence
- optional governance package-lock evidence for the drift report

Re-baselining is intentionally not automatic. A new baseline is a human
decision made after reviewing the drift.

## Rebaseline

Use rebaseline mode only after reviewing drift and deciding that the current
wheel folder should become the new trusted baseline:

```bash
spira-trust rebaseline path/to/wheel-folder --from-baseline old_bill_of_materials.json --baseline-sha256 <old_sha256> --output-dir new_baseline_out --yes
```

Without `--yes`, SPIRA writes a drift preview and exits with
`REBASELINE_REQUIRES_CONFIRMATION`. With `--yes`, SPIRA copies the current BOM
to a new baseline file and prints the new SHA-256 that must be pinned in CI.
The old baseline is never mutated. CI templates must never run rebaseline
automatically.

## Exit Codes

```text
0  no blocking trust failure was found
1  TRUST_BLOCK
2  TRUST_UNKNOWN
```

For `spira-trust graph`:

```text
0  GRAPH_OK or GRAPH_OK_WITH_UNVERIFIED
1  GRAPH_BLOCK
1  GRAPH_INPUT_ERROR; invalid graph input such as an empty wheel folder
2  GRAPH_WARN
```

For `spira-trust drift`:

```text
0  NO_DRIFT
1  BLOCK from current policy evaluation
1  DRIFT_INPUT_ERROR; invalid current input such as an empty wheel folder
2  WARN from current policy evaluation
3  DRIFT_DETECTED against the pinned baseline
4  BASELINE_UNTRUSTED; baseline sha256 pin mismatch, no drift computed
```

For policy-pack authentication:

```text
5  POLICY_UNTRUSTED; policy pack sha mismatch or pinned pack references external paths
6  REBASELINE_REQUIRES_CONFIRMATION; no new baseline written without --yes
```

For `spira-trust rebaseline`, invalid current input such as an empty wheel
folder is reported as `REBASELINE_INPUT_ERROR` with exit 1. Input errors are
written as clean reports in the output directory; they must not surface raw
Python tracebacks.

## What The Verdicts Mean

```text
TRUST_OK_WITH_NOTES
  No hard gap was found in the checks SPIRA ran, but there is surfaced prose
  or other context that still needs a human reading.

TRUST_WARN
  One or more structured claims are present but not raw-verifiable, or the
  uncertainty is high enough that manual review is required before trust.

TRUST_BLOCK
  SPIRA found blocking evidence such as RECORD/package-lock integrity failure
  or a condition-matched contradiction.

GRAPH_OK
  All provided graph nodes passed the checks SPIRA ran and no declared local
  relationship introduced a warning or block.

GRAPH_OK_WITH_UNVERIFIED
  No blocking contradiction was found, but at least one declared relationship
  pointed to an artifact that was not provided locally. This is not a clean
  closure claim; the summary reports the number of unverified nodes.

GRAPH_WARN
  The graph has non-terminal risk, such as strict-closure missing artifacts or
  a warning propagated from a child package.

GRAPH_BLOCK
  A provided artifact was blocked, or a blocking child propagated through a
  declared/runtime relationship.
```

See
[`docs/verdicts.md`](https://github.com/snir-spira37/spira-trust/blob/main/docs/verdicts.md)
for the local explanation of verdicts, contradictions, and common fixes.

## What It Checks Automatically

For Python wheels, zips, and folders, v1 mechanically checks structured surfaces
where the raw format is explicit:

- `METADATA` package name and version
- `Requires-Dist`
- `Requires-Python`
- `Development Status` classifiers as claimed-but-not-raw-proof
- wheel `RECORD` hashes against archive contents
- SPIRA package-lock and `not_claimed` boundaries on the review report

The trust decision is then routed through SPIRA's packaged local decision
adapter, whose bundled Python source is SHA-verified before use.

Graph mode uses PEP 503 package-name normalization only: lowercase plus
collapsing `-`, `_`, and `.` runs into `-`. It does not perform Unicode
confusable folding or fuzzy matching. Homoglyph and byte-level path mismatches
remain the responsibility of the single-artifact review layer.

Multiple local versions of the same package are kept as distinct graph nodes
using package name, version, and artifact hash. If a declared relationship
matches more than one local wheel, graph mode marks that relationship as
ambiguous instead of choosing a version silently. Ambiguity on a declared
runtime relationship is fail-closed as `GRAPH_BLOCK`.

Graph mode also fails closed on structural graph hazards:

- circular declared relationships are `GRAPH_BLOCK`
- pinned version conflicts reachable from the same root are `GRAPH_BLOCK`
- supported range constraints that no provided local version satisfies are
  `GRAPH_BLOCK`
- supported range constraints that are unsatisfiable by construction are
  `GRAPH_BLOCK`
- selected malformed or unsatisfiable environment-marker classes are
  `GRAPH_BLOCK` (empty marker, unbalanced quotes, dangling boolean operator,
  comparison without value, and obvious conflicting `python_version` bounds)
- artifact sets larger than the v1 scale limit are `GRAPH_BLOCK` before
  per-artifact review begins

Range checks are local only. They evaluate the wheel versions you provided on
disk; they never fetch, suggest, infer, or invent another version.

V2 range checks support only numeric tuple versions with these operators:
`==`, `!=`, `<`, `<=`, `>`, `>=`, plus comma intersection such as `>=1,<2`.
The compatible-release operator `~=` and non-numeric PEP 440 forms such as
`rc`, `dev`, local versions, epochs, and wildcards become `UNVERIFIED` notes.
They do not silently pass and they do not hard-block solely because SPIRA does
not parse them.

Graph mode does not claim to be a complete PEP 440 or PEP 508 validator.

## Safety Boundaries

- Archive extraction blocks traversal paths and enforces file/member/byte limits.
- v1 does **not** import or execute code from the artifact under review.
- Runtime probes are disabled in v1 until a real sandbox exists.
- Free text is surfaced as `NEEDS_HUMAN_JUDGMENT`; it is not auto-classified.

## What It Does Not Do

- It is not a malware scanner.
- It is not a security certification.
- It does not perform a complete package audit.
- It does not check CVEs.
- It does not resolve or download dependencies.
- It does not execute package code.
- It does not detect typosquatting when the package is internally consistent.
- It does not auto-interpret README or long free-text prose.
- It does not prove that a package is good, safe, or production-ready.

## Pilot Question

For a pilot user, the useful question is not "is SPIRA impressive?" It is:

```text
Did this verdict and evidence help you decide anything about the package you chose?
```

Honest negative feedback is valid output. If the report is confusing, too noisy,
or not useful, that is exactly what the pilot is meant to discover.
