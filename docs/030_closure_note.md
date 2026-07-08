# SPIRA Trust 030 Closure Note

Status: closed
Date: 2026-07-08

## Production Release

SPIRA Trust is published on production PyPI:

```text
https://pypi.org/project/spira-trust/0.5.5/
```

Install:

```bash
python -m pip install spira-trust==0.5.5
```

Published wheel:

```text
spira_trust-0.5.5-py3-none-any.whl
```

Wheel SHA256:

```text
346443688a565a8b554d06fec5c2d36fa4e0b3f386182bffb84420af0cb800a4
```

## Verified Release Facts

- Production PyPI publication completed.
- Publication used GitHub Actions Trusted Publishing/OIDC.
- The downloaded PyPI wheel SHA256 matched the release candidate.
- Clean installation from PyPI worked.
- `spira-trust version` returned `spira-trust 0.5.5`.
- `spira-trust trust` on the downloaded wheel returned `TRUST_OK`.
- `spira-trust graph --verify-embedded-sboms` returned `GRAPH_OK`.
- Embedded SBOM consistency returned `VERIFIED_OK`.
- Release self-evidence hash contract passed.
- Release self-evidence schema validation passed.
- `INDEX_176` resolved `199/199` references.

## What Is Claimed

SPIRA Trust 0.5.5 is a production PyPI package that performs local, offline
evidence checks over Python wheel artifacts. It verifies wheel structure,
`RECORD` integrity, embedded SBOM consistency, local graph/BOM evidence, and
explicit local policies without contacting package indexes during analysis and
without executing package code.

## What Is Not Claimed

- No runtime behavior safety guarantee.
- No malware detection.
- No CVE intelligence.
- No dependency resolution or package download during analysis.
- No legal compliance certification.
- No full independent PEP 740 index-hosted provenance verification by SPIRA.
- No claim that a package is good, safe, or production-ready merely because it
  passed the checks that were run.

## Closure

030 is closed. SPIRA Trust moved from internal bundle to a production PyPI
package with release evidence verified by SPIRA itself.
