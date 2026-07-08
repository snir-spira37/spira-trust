# Changelog

## spira-trust 0.2.0 - Bundle 027

- Added a slim public `spira-trust` wheel target with only the public trust CLI surface.
- Added Linux/macOS `install.sh`.
- Added Ubuntu GitHub Actions template.
- Added public import-boundary acceptance check.
- Added deterministic tampered-RECORD fixture and empirical installer behavior doc.
- Fixed the PowerShell pre-commit template so `param()` is the first executable statement.
- Declared 027 artifacts as unsigned pilot artifacts; verify SHA256SUMS manually.

## spira-trust 0.3.0 - Bundle 028

- Added opt-in PEP 770 embedded SBOM consistency checks.
- Added opt-in PEP 740 offline attestation metadata/digest/identity checks with explicit local trust roots.
- Added fixtures for SBOM match/mismatch and attestation digest match/mismatch.
- Preserved offline/no-network/no-resolver behavior.
- Declared that 028b is not full Sigstore cryptographic verification.

## spira-trust 0.3.1 - Bundle 028_002

- Fixed attestation digest evaluation so digest mismatches block even when no trust root is supplied.
- Added `--attestation-trust-root-sha256` pinning.
- Kept identity evaluation dependent on an explicit trust root.
- Removed generated `__pycache__` files from release bundles.
- Aligned attestation status names to explicit `ATTESTATION_*` states.

## spira-trust 0.3.2 - Bundle 028_003

- Require `--attestation-trust-root-sha256` whenever an attestation trust root is supplied.
- Convert missing attestation/trust-root files into clean `ATTESTATION_*` graph blocks instead of tracebacks.
- Keep BOM `integrity.record_verified` scoped to RECORD integrity, not graph-level policy blocks.
- Expose PEP 770 / PEP 740 statuses in the BOM combined verdict and CycloneDX export.
- Added trust-root lifecycle documentation.

## spira-trust 0.4.0 - Bundle 029

- Added `SPIRA_DECISION_V1` decision reports: `spira-decision.json` and `spira-decision.md`.
- Added `schemas/spira_decision_v1.json` and `docs/decision_contract.md`.
- Added `--evidence-pack <path.zip>` for archiving decision and graph evidence files together.
- Kept decision reports as aggregators over existing evidence, not a new trust engine.
- Updated verdict documentation for PEP 770 / PEP 740 states.

## spira-trust 0.4.1 - Bundle 029_002

- Hardened `schemas/spira_decision_v1.json` with required layer, standards, evidence, and status fields.
- Made `spira-decision.json` use relative evidence paths by default.
- Added local absolute paths only when `--include-local-paths` is supplied.
- Included the governance graph evidence package inside `--evidence-pack` archives.
- Added combined decision details to graph summary output.
- Removed public README wording that implied `spira-core` is exposed by the public wheel.

## spira-trust 0.4.2 - Bundle 029_003

- Finalize `graph_report.json` and `graph_summary.txt` before computing `spira-decision.json` evidence hashes.
- Added contract tests that compare decision evidence hashes against output-dir files and evidence-pack contents.
- Keep the evidence-pack manifest and decision evidence hashes aligned over the same final bytes.
- Report top-level PEP 740 digest failures as `ATTESTATION_DIGEST_MISMATCH` when applicable.

## spira-trust 0.5.6 - Public surface polish

- Adds README long description and project URLs to PyPI metadata.
- No trust-engine capability changes from 0.5.5.

## spira-trust 0.5.5 - Production PyPI reproducibility correction

- Makes wheel RECORD ordering independent of OS-specific path ordering.
- No feature changes from 0.5.4.

## spira-trust 0.5.4 - Production PyPI release candidate

- Adds deterministic wheel ZIP metadata and normalized text payloads for reproducible release candidates.
- Adds a Production PyPI Trusted Publishing workflow candidate.
- No feature changes from 0.5.3.

## spira-trust 0.5.3 - TestPyPI Trusted Publishing candidate

- Version bump for the first TestPyPI Trusted Publishing/OIDC live run.
- No feature changes from 0.5.2.

## spira-trust 0.5.2 - Bundle 030_003

- Embedded a narrow CycloneDX SBOM under `.dist-info/sboms/` in the public wheel.
- Added release self-evidence support for `--verify-embedded-sboms`.
- Updated TestPyPI workflow self-evidence to verify embedded SBOM consistency.
- Updated docs/templates to separate `./spira-tooling` from scanned `./wheels`.
- Kept TestPyPI live publication explicitly external unless a configured trusted
  publisher or token is supplied.

## spira-trust 0.5.1 - Bundle 030_002

- Restored `schemas/spira_decision_v1.json` to the public pilot bundle.
- Added release self-evidence validation against `SPIRA_DECISION_V1`.
- Made `release_self_evidence_manifest.json` portable by writing relative output paths.
- Added `docs/uv_pip_workflow.md` and a GitLab CI starter template.
- Documented TestPyPI/local-wheel installation expectations for the GitHub Action wrapper.

## spira-trust 0.5.0 - Bundle 030_001

- Added a TestPyPI Trusted Publishing workflow skeleton for dry-run release integration.
- Added a self-evidence release flow that runs SPIRA Trust on its own public wheel and writes a release evidence manifest.
- Added a composite `action.yml` wrapper for GitHub Action integration.
- Added a reusable bundle builder that writes Unix ZIP metadata so `install.sh` can be executable after `unzip`.
- Added 030 integration docs and kept scope to release/dogfooding, not a new detection engine.
