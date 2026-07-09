# Real Wheelhouse Example

This example shows how to read SPIRA output on a small real wheelhouse, not a
hand-built fixture.

The local folder contained six Python wheels:

```text
colorama-0.4.6-py2.py3-none-any.whl
iniconfig-2.3.0-py3-none-any.whl
packaging-26.2-py3-none-any.whl
pluggy-1.6.0-py3-none-any.whl
pygments-2.20.0-py3-none-any.whl
pytest-9.1.1-py3-none-any.whl
```

Command:

```bash
spira-trust graph wheels \
  --output-dir out/pytest-wheelhouse \
  --sbom cyclonedx-json \
  --evidence-pack out/pytest-wheelhouse/evidence.zip
```

Observed result:

```text
GRAPH_WARN
exit 2
```

Summary:

```text
Artifacts provided: 6
Declared relationships: 20
Declared artifacts not provided: 13
Declared artifacts ambiguous: 0
Malformed declared relationships: 0
Blocked nodes: 0
Warning nodes: 6
Human-note nodes: 0
```

SPIRA also reported an optional/test circular relationship:

```text
pluggy -> pytest -> pluggy
```

## How To Read This

`GRAPH_WARN` does not mean the wheelhouse is malware, broken, or unsafe.

It means SPIRA found non-terminal evidence that should be reviewed before
treating the local folder as a clean closed set.

In this run:

- no node was `GRAPH_BLOCK`
- no declared relationship was ambiguous
- no malformed declared relationship was found
- some declared relationships pointed to wheels that were not provided locally
- an optional/test-extra relationship formed a cycle

That is useful evidence for a human or agent:

```text
The provided wheels were inspectable.
The folder was not a complete local closure.
Some optional/test dependency context was outside the provided wheelhouse.
```

## Why This Helps Agents

Without SPIRA, an agent has to inspect wheel metadata, infer relationships,
notice missing local wheels, reason about extras, and summarize the result.

With SPIRA, the agent reads:

```text
graph_summary.txt
spira-decision.json
```

For this run, the funnel was:

```text
1.77 MB wheel artifacts
62 KB graph_report.json
85 KB bill_of_materials.json
6.3 KB spira-decision.json
1.5 KB graph_summary.txt
```

The full evidence remains available, but the agent does not need to spend its
context window reconstructing the verdict from raw artifacts.

## Boundary

This example is not a claim that the wheelhouse is production-ready.

SPIRA does not resolve missing dependencies, fetch from PyPI, install packages,
execute package code, or judge whether `pytest` is safe to use.

It reports what local artifact evidence proves, what it does not prove, and
which layers were not evaluated.
