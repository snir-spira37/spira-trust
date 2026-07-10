# Cache Performance Benchmark v1

Created: 2026-07-10T15:56:04.439338Z

Cold path: full graph verification, decision, agent summary, state copy.
Warm path: artifact re-hash and exact-context cache query.

```text
runs: 20
cold median seconds: 0.378364
warm median seconds: 0.013166
median speedup ratio: 28.94x
cold median output bytes: 3131.0
warm median output bytes: 990.0
all cache hits: True
all actions equivalent: True
all miss cases fail closed: True
```

Not claimed: CPU cycles, energy, CO2, live-agent token savings, or OS-level file-open tracing.
