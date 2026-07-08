# SPIRA Trust Capability Matrix

SPIRA Trust is a local evidence gate for Python wheels. It complements other
security tools rather than replacing them.

| Area | SPIRA Trust | Not Claimed |
| --- | --- | --- |
| Wheel integrity | Verifies local wheel structure and `RECORD` hashes. | Does not prove runtime behavior is safe. |
| Local graph | Builds a graph over wheels provided on disk. | Does not resolve, fetch, or install dependencies. |
| SBOM | Exports CycloneDX from local evidence and checks narrow embedded SBOM consistency. | Does not perform full SBOM schema validation or merge SBOM authority. |
| Policy | Applies explicit local policy for license visibility, entry points, target tags, lockfiles, and drift. | Does not provide legal advice, CVE intelligence, or malware classification. |
| Release evidence | Verifies its own downloaded release artifact and evidence pack. | Does not yet independently verify PEP 740 index-hosted provenance. |

The core claim is deliberately narrow: SPIRA Trust proves what the local bytes
and declared metadata support, and it records what it did not evaluate.
