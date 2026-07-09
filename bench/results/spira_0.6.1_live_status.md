# Stage B Live Agent Benchmark

Status: NOT RUN

Reason: no live model API credentials are available in this environment.

Checked environment variables:

```text
OPENAI_API_KEY=false
ANTHROPIC_API_KEY=false
AZURE_OPENAI_API_KEY=false
OPENROUTER_API_KEY=false
```

Available local Python client packages:

```text
openai=false
anthropic=false
tiktoken=false
```

No proxy result was produced.

Correctness-before-savings rule:

```text
Arm A and Arm B must reach the same gate decision and materially equivalent
reasons before any live savings number is reported.
```

Live table:

| stage | arm | repetitions | correctness equivalence | usage measurement | result |
|---|---:|---:|---|---|---|
| B | A: raw evidence prompt | 0 | not evaluated | not measured | not run |
| B | B: agent_summary/status prompt | 0 | not evaluated | not measured | not run |

Not claimed:

- This is not a failed benchmark result.
- This is not evidence that live savings are zero.
- This is not a substitute for the live two-arm agent run.
- No token, latency, cost, energy, or correctness claim is made for Stage B.
