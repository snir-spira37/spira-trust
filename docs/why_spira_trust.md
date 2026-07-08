# Why SPIRA Trust Exists

Python supply-chain tooling often answers questions after package identity has
already been accepted:

```text
Is this package known to have a CVE?
Is this version allowed by policy?
Does an SBOM exist?
Was this release published through a trusted mechanism?
```

Those are useful questions, but they skip a local evidence question that should
come first:

```text
Do the artifact bytes in front of me match the claims inside the artifact?
```

SPIRA Trust is a local evidence gate for Python wheels. It checks the package
file you explicitly provide, without resolving dependencies, contacting PyPI,
installing the package, or executing package code.

## What It Checks

- Wheel structure and `RECORD` integrity.
- Package metadata such as name, version, and declared requirements.
- Embedded SBOM consistency for narrow supported CycloneDX/JSON metadata.
- Local dependency relationships between provided wheels.
- Local BOM visibility and subtree integrity digests.
- Optional local policy for license visibility, entry-point command names,
  target environment tags, lockfile facts, and baseline drift.
- Evidence package consistency for audit workflows.

## What It Does Not Claim

- It is not a malware scanner.
- It is not a CVE database.
- It is not a dependency resolver.
- It does not install packages.
- It does not execute package code.
- It does not provide legal compliance certification.
- It does not prove runtime safety.
- It does not independently verify PyPI-hosted PEP 740 provenance yet.

## The Practical Use

SPIRA Trust helps answer:

```text
Should I allow this wheel or wheelhouse into the next step of my workflow?
```

It is most useful before installation, in vendor intake, in air-gapped
wheelhouse review, and in CI pipelines that need a local evidence checkpoint.
