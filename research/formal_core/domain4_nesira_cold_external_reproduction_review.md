# Domain 4 / Nesira Cold External Reproduction Review

## Verdict

```text
DOMAIN4_NESIRA_COLD_EXTERNAL_REPRODUCTION_ACCEPTED
```

Accepted commit:

```text
cf6693b4a3581575783e3a744cf53ede9b3dfa7d
```

This review accepts the cold external reproduction of the Domain4 / Nesira
decision-core chain and the Option A V1/Domain4 boundary.

## Correction To Prior SHA256SUMS Framing

The earlier framing of the `SHA256SUMS` finding as only a reviewer false
positive was not precise enough.

The original problem was a real reproduction hygiene defect: `SHA256SUMS` had
been produced from local line-ending-normalized bytes and did not match what a
fresh clone could see for the affected package files. The fix in `cf6693b`
normalizes the recorded hashes to the committed checkout scenario and makes the
package self-check pass in a clean clone.

Delta from the prior commit:

```text
previous: 2f222e2e784faa813607106713b456a07eb7f522
accepted: cf6693b4a3581575783e3a744cf53ede9b3dfa7d
delta:    exactly 2 SHA256SUMS lines
substance: unchanged
```

## Reproduced Gates

```text
SHA256SUMS from clean clone: 622 / 622 OK
full pytest from short clean clone path: 286 passed, 0 failed
V1 verify_all: PASS
V1 Lean build: 35 jobs
Domain4 built by V1 verify_all: 0
Domain4 harness: DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
```

Domain4 harness coverage:

```text
Layer 1 Python-Lean agreement: 118098 / 0 disagreements
Layer 2 mutation pairs: 0 missing, 0 false PROCEED, 0 false VALID
Layer 3 Phase 1 reproduction: 0 divergences
reason-code fidelity: PASS
two-run equality: PASS
public wheel exclusion: PASS
```

Formal side:

```text
full Lake build: PASS
Domain4 included in full build: yes
axiom boundary: propext only, no sorryAx
Domain4 proofs changed since 28c8a72: no
```

## Option A Boundary

The Option A boundary is preserved:

```text
Formal Core V1 external reproduction package remains V1-scoped.
V1 inventory and claims do not include Domain4.
V1 verify_all builds SpiraFormalCore only.
Domain4 is verified through its own build/harness path.
```

This prevents later domains from silently changing the accepted V1 external
reproduction package.

## Non-Blocking Robustness Notes

```text
WINDOWS_DEEP_PATH_ROBUSTNESS:
  Two Domain4 tests can fail when the repository is cloned under a very deep
  Windows path because nested Lake artifacts can hit MAX_PATH. The same tests
  pass in a short clean clone path. This is environment robustness, not a
  proof, harness, or decision-core failure.

WINDOWS_PYTHON3_STORE_STUB:
  verify_all.sh can select the Windows Store python3 stub in Git Bash. Use
  verify_all.ps1 on Windows or set PYTHON=python when running the shell script.
```

These notes do not block acceptance.

## Boundary Not Claimed

This review does not authorize or claim:

```text
signer trust
signer authority
actual isolation execution
permission to sever
Phase 2 implementation
public capability claim
release
```

## Status

```text
DOMAIN4_NESIRA_DECISION_CORE_PROVEN_AND_EXTERNALLY_REPRODUCED
DOMAIN4_NESIRA_PYTHON_LEAN_BRIDGE_EXTERNALLY_REPRODUCED
DOMAIN4_NESIRA_PHASE1_REPRODUCTION_BRIDGE_EXTERNALLY_REPRODUCED
OPTION_A_V1_DOMAIN4_BOUNDARY_EXTERNALLY_REPRODUCED

PHASE2_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
