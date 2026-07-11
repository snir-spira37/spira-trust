# Event Volume Ranking V1

```text
source_session_id: program_completion_stable_codex
source_replay_status: NO_JUSTIFICATION_FOR_BROAD_ORCHESTRATOR_PILOT
source_replay_valid: True
event_count: 95496
actual_fresh_input_tokens: 110755602
```

## Decision

```text
status: ONE_PRODUCER_MEASUREMENT_AUTHORIZED
authorized_scope: Workspace/State-Manifest
```

This does not authorize a broad orchestrator or multiple producers. It only selects one producer candidate for a measured output/sufficiency experiment.

## Top Categories

| rank | category | events | raw bytes | allocated fresh tokens | median bytes | p90 bytes | median reuse | p90 reuse | exposure byte-calls | answerability |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | `FILE_READ_OUTPUT` | 7481 | 47349054 | 19403503.777 | 4025 | 13893 | 31 | 89 | 1746413246 | `{"BOUNDED_SUMMARY": 7481}` |
| 2 | `CODE_WRITE` | 2936 | 27147523 | 9418358.685 | 5805 | 23637 | 44 | 99 | 1378950439 | `{"NOT_TOOL_ANSWERABLE": 2936}` |
| 3 | `REASONING_OR_INSTRUCTIONS` | 31820 | 15105969 | 42640769.531 | 256 | 1239 | 42 | 99 | 700619087 | `{"NOT_TOOL_ANSWERABLE": 31820}` |
| 4 | `SEARCH_OUTPUT` | 2203 | 20269880 | 5820090.348 | 1476 | 40095 | 27 | 88 | 668631181 | `{"BOUNDED_SUMMARY": 2203}` |
| 5 | `STATE_DISCOVERY` | 3790 | 15876852 | 7398093.902 | 776 | 9974 | 38 | 97 | 561616739 | `{"BOUNDED_SUMMARY": 3790}` |
| 6 | `OTHER` | 10108 | 12218546 | 7910420.335 | 154 | 1874 | 45 | 104 | 553710861 | `{"NOT_TOOL_ANSWERABLE": 10108}` |
| 7 | `PYTHON_OUTPUT` | 2633 | 5014929 | 5215140.308 | 756 | 3332 | 39 | 97 | 219543072 | `{"BOUNDED_SUMMARY": 2633}` |
| 8 | `TOOL_INVOCATION` | 29152 | 3590557 | 9506241.311 | 125 | 131 | 38 | 97 | 168430100 | `{"NOT_TOOL_ANSWERABLE": 29152}` |
| 9 | `TEST_OUTPUT` | 1520 | 2020209 | 1343632.946 | 174 | 1249 | 40 | 102 | 70655702 | `{"BOUNDED_SUMMARY": 1520}` |
| 10 | `BUILD_OUTPUT` | 766 | 1176213 | 972964.818 | 633 | 2341 | 42 | 89 | 52792256 | `{"BOUNDED_SUMMARY": 766}` |
| 11 | `NETWORK_FETCH_OUTPUT` | 477 | 1227627 | 842723.221 | 496 | 3794 | 42 | 104 | 43901470 | `{"NOT_TOOL_ANSWERABLE": 477}` |
| 12 | `GIT_OUTPUT` | 171 | 291785 | 163356.192 | 456 | 5156 | 55 | 119 | 17221622 | `{"BOUNDED_SUMMARY": 171}` |

## First Producer Candidate

```text
producer_candidate: Workspace/State-Manifest
selected_category: STATE_DISCOVERY
selection_reason: highest weighted candidate among BOUNDED_SUMMARY classes using measured context exposure and a deterministic-semantics preference; this authorizes one producer measurement only
```

## Not Claimed

- No new savings are claimed.
- Context exposure byte-calls are a ranking signal, not billing.
- The previous replay result remains unchanged.
- A producer must still generate measured output and pass sufficiency audit before any replay savings can be counted.
