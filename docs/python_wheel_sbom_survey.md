# Embedded SBOMs in Python Wheels: Scope, Consistency, and Agent Context Cost

## Executive Summary

SPIRA Trust surveyed a frozen corpus of 1,954 real Python wheels containing
embedded SBOM material.

The central finding was not that embedded SBOMs were broadly inconsistent with
wheel metadata. The more common problem was that the embedded SBOM did not
describe the wheel itself.

Under the final SPIRA V5 wheel-scope rules:

```text
wheel-scoped SBOM found:           572
no wheel-scoped SBOM found:      1,380
not evaluated:                       2
narrow field inconsistencies:        0
invalid SBOMs under SPIRA V5:        0
tool errors:                         0
```

The context-cost finding was also substantial:

```text
median SBOM bytes:              75,925
median agent_summary bytes:      2,180
median SBOM-to-summary ratio:     34.7x
p90 SBOM-to-summary ratio:       196.6x
max SBOM-to-summary ratio:       765.4x
```

In short:

```text
Evidence presence is not evidence applicability.
```

An embedded SBOM can exist, be parseable, and still not answer the narrow
question an agent often asks: "does this wheel's own artifact evidence support
the gate decision?"

## Snapshot Note

The corpus was selected from a live PyPI ecosystem snapshot captured on
2026-07-09. The full SPIRA V5 evaluation over the 1,954 selected wheels was
completed on 2026-07-10.

The results describe that frozen corpus and should not be interpreted as a
current count of all PyPI wheels with embedded SBOMs.

The snapshot funnel was:

```text
package versions with SBOMs in the live source data: 4,487
grouped PyPI projects:                              2,085
selected wheels under survey scope:                 1,954
```

The survey selected at most one wheel per PyPI project and only selected
x86_64/amd64 or `py3-none-any` wheels. Projects without a matching wheel and
PyPI JSON lookup failures were reported separately.

## What SPIRA Checked

SPIRA did not perform full SBOM validation. It performed a narrow offline
consistency and applicability check for embedded SBOM material in Python wheels.

SPIRA compared exactly these available identity fields:

- component name
- component version
- package URL (`purl`), when present

The final V5 rules also distinguish wheel-scoped SBOMs from SBOMs that describe
other ecosystems or internal components, such as Cargo crates included in a
Python wheel build pipeline.

This distinction was not theoretical. The pilot initially produced apparent
inconsistencies that manual review showed were legitimate multi-ecosystem SBOM
patterns. V4 and V5 corrected the methodology before the final public result.

## Main Finding: Scope, Not Contradiction

Most embedded SBOM wheels in the selected corpus did not include a wheel-scoped
SBOM under SPIRA's final rules:

```text
NO_WHEEL_SCOPED_SBOM: 1,380 / 1,954 = 70.62%
SBOM_CONSISTENT:       572 / 1,954 = 29.27%
NOT_EVALUATED:           2 / 1,954 = 0.10%
SBOM_INCONSISTENT:       0 / 1,954 = 0.00%
SBOM_INVALID:            0 / 1,954 = 0.00%
TOOL_ERROR:              0 / 1,954 = 0.00%
```

Where a wheel-scoped SBOM was found and SPIRA could evaluate the narrow checked
fields, the checked fields were consistent with the wheel metadata.

The more important ecosystem signal is that many embedded SBOMs appear to
describe build inputs or bundled components rather than the top-level wheel
artifact. That may be useful information, but it is not the same as a
wheel-scoped declaration.

## Generator Families

The survey recorded generator families as multi-label counts. Counts can exceed
the number of processed wheels because a wheel may contain more than one SBOM or
more than one generator signature.

```text
CARGO_CYCLONEDX:  1,412
AUDITWHEEL:         531
MATURIN:             29
OTHER:                8
UNKNOWN:              3
SBOMIFY:              2
CYCLONEDX_PYTHON:     1
```

This supports the interpretation that early PEP 770 adoption is heavily shaped
by build tools and SBOM generators, not only by per-project maintainer choices.

## Context Cost for Agents

The context-tax measurement was static bytes, not live-agent tokens. It measured
how much SBOM material exists in the wheel compared with the compact SPIRA
agent summary generated from the narrow check.

```text
SBOM bytes median / p90 / max:
75,925 / 432,201 / 1,703,082

agent_summary bytes median / p90 / max:
2,180 / 2,226 / 2,405

SBOM-to-summary ratio median / p90 / max:
34.6954x / 196.5863x / 765.4301x
```

This does not prove live token savings, latency savings, physical energy
savings, or CO2 savings. It does show that a deterministic local tool can answer
a narrow artifact-evidence question with a much smaller decision surface than
the raw embedded SBOM material.

## Relationship to Invalid SBOM Findings

The survey also checked the live-invalid overlap reported by prior SBOM
ecosystem work. That overlap is orthogonal to SPIRA's narrow consistency result:
an SBOM may fail a full schema validator while still exposing the few fields
SPIRA reads, or the invalid file may not be wheel-scoped at all.

Four overlap cases were both schema-invalid in the external data and
`SBOM_CONSISTENT` under SPIRA's narrow check. The subfinding was recorded
separately because it clarifies the boundary:

```text
SPIRA consistency here means the checked wheel-scoped identity fields agree.
It does not mean the SBOM is fully schema-valid.
```

## Reproducibility

- Methodology: `research/pep770_survey/methodology.v5.json`
- Frozen corpus manifest:
  `research/pep770_survey/results/snapshot_v3_2026-07-09_manifest.json`
- Public V5 results:
  `research/pep770_survey/results/full_v5_public_results.json`
- Human-readable summary:
  `research/pep770_survey/results/full_v5_summary.txt`
- Live-invalid overlap analysis:
  `research/pep770_survey/results/sbomify_live_invalid_intersection_2026-07-10.json`
- Four-case consistent/invalid subfinding:
  `research/pep770_survey/results/sbomify_live_invalid_consistent_subfinding_2026-07-10.json`

The central public result files have SHA256 sidecars in the same directory.

## Not Claimed

This survey does not claim that:

- Embedded SBOMs are security attestations.
- A consistent SBOM means a package is safe.
- A non-wheel-scoped SBOM is malicious or useless.
- SPIRA performs full SBOM validation.
- SPIRA found malware, vulnerabilities, or provenance guarantees.
- The corpus represents every platform wheel or every version of each project.
- Static byte reduction is the same as live-agent token, latency, cost, energy,
  or CO2 reduction.

## Conclusion

PEP 770 makes embedded SBOM material available inside wheels. Availability is
not the same as applicability.

For agents and release workflows, the practical question is often not "is there
an SBOM?" but:

```text
Does the evidence apply to this artifact, under this policy, right now?
```

SPIRA Trust's contribution is to turn that local evidence question into a
small, deterministic action surface rather than asking an agent to infer scope,
policy, and applicability from broad artifact evidence at runtime.
