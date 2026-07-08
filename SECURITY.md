# Security Policy

## Supported Versions

Security reports are accepted for the current public PyPI release of
`spira-trust` and for the `main` branch of the public repository.

## Reporting a Vulnerability

Please do not open a public issue for a suspected vulnerability.

Preferred route: use GitHub private vulnerability reporting for this repository
when it is enabled.

If private vulnerability reporting is not available yet, open a public issue
titled `Security report contact request` without exploit details, logs,
artifacts, or sensitive information. We will arrange a private channel before
technical details are shared.

Please include:

- affected version or commit
- operating system and Python version
- command you ran
- artifact type involved, if any
- minimal reproduction steps
- whether the issue can cause incorrect `OK`, hidden `NOT_EVALUATED`, code
  execution, file write outside the output directory, or evidence tampering

## Response Expectations

We aim to acknowledge valid security reports within 5 business days.

SPIRA Trust is an early public project. Fix timelines depend on severity,
reproducibility, and whether the issue affects public releases or only
development artifacts.

## Scope

In scope:

- incorrect trust or graph verdicts
- `NOT_EVALUATED` reported as `OK`
- archive traversal or unsafe file writes
- unintended code execution from reviewed artifacts
- evidence package tampering not detected by verification
- public package metadata or provenance errors that could mislead users

Out of scope:

- vulnerability reports for third-party packages scanned by SPIRA
- requests to add CVE intelligence, malware detection, or dependency resolving
- issues caused by intentionally modified local policy files unless a pinned
  policy was expected to prevent the modification

SPIRA Trust does not claim to prove package safety. It reports local evidence,
explicit policy outcomes, and what it did not evaluate.
