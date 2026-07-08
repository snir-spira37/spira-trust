# Pilot Outreach Email

Subject: Quick pilot request: local evidence gate for Python wheels

Hi <name>,

I am looking for feedback on SPIRA Trust, a small local CLI for checking Python
wheel evidence before installation.

Install:

```bash
python -m pip install spira-trust==0.5.6
```

The tool does not try to be a malware scanner or CVE database. It asks a
narrower question:

```text
Do the wheel bytes, metadata, RECORD hashes, embedded SBOM claims, and local
policy inputs agree before I install this package?
```

Two useful pilot paths:

```bash
spira-trust trust ./some-package.whl --output-dir spira_out
```

or, for a local wheelhouse:

```bash
spira-trust graph ./wheels \
  --output-dir spira_graph_out \
  --sbom cyclonedx-json \
  --verify-embedded-sboms \
  --evidence-pack spira-evidence.zip
```

What I would value from you is not praise. I want to know whether the evidence
changed a decision, reduced uncertainty, or was too noisy/confusing to be useful.

Pilot questions:

```text
1. Did the verdict change what you would do with this package or wheelhouse?
2. Was the terminal output enough, or did you need the JSON?
3. Which finding was useful, noisy, or confusing?
4. Would you put any SPIRA command into CI?
5. What would need to change before you used it regularly?
```

Links:

- PyPI: https://pypi.org/project/spira-trust/0.5.6/
- GitHub: https://github.com/snir-spira37/spira-trust

Thanks,
<your name>
