# Reproduce Nesira Phase 1

## Source

```powershell
git clone https://github.com/snir-spira37/spira-trust.git spira-trust-phase1
cd spira-trust-phase1
git checkout c21abef47dd174284a5d1938182a633b93bd8785
git status --short
```

The initial status must be clean.

## Environment

Observed builder environment:

```text
OS: Windows-10-10.0.19045-SP0
Python: 3.12.10
```

Install the normal repository test dependencies. Do not rely on recorded
reports; run the commands yourself.

## Required Commands

```powershell
python -m compileall source tests
python -m pytest tests/test_nesira_policy_profile_validator.py -q
python -m pytest -q
python tools/build_spira_trust_public.py <output-dir>
git diff --check
```

Expected outcomes:

```text
compileall: exit 0
focused Phase 1 tests: 11 passed
full pytest: 281 passed
public wheel build: exit 0
git diff --check: exit 0
```

Run the focused Phase 1 semantic layer twice and verify identical fixture
outcomes, mutation outcomes, path-security outcomes, and hash-binding outcomes.
Separate timestamps or environment metadata from semantic decision content.

If the V1.1 authorization ZIP is unavailable, report that verification layer as
`NOT_EVALUATED`, not `PASS`.
