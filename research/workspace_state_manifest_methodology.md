# SPIRA Workspace State Manifest Methodology

## Status

```text
METHODOLOGY_LOCKED_BEFORE_PRODUCER_IMPLEMENTATION
```

## Boundary

This document authorizes one measurement experiment for one producer family:

```text
Workspace/State-Manifest
```

It does not authorize:

```text
broad orchestrator
multiple producers in parallel
SPIRA Trust product scope expansion
new savings claim
product claim
```

The prior counterfactual replay remains unchanged:

```text
NO_JUSTIFICATION_FOR_BROAD_ORCHESTRATOR_PILOT
```

The event-volume ranking only authorizes locking this one-producer methodology
and then measuring a runnable producer against the preselected replay data.

## Ranking Basis

The first producer candidate was selected from the public event-volume ranking:

```text
selected_category: STATE_DISCOVERY
events: 3,790
raw_visible_bytes_total: 15,876,852
allocated_fresh_tokens_total: 7,398,093.902
median_event_bytes: 776
p90_event_bytes: 9,974
median_reuse_count: 38
p90_reuse_count: 97
```

The selection is policy-weighted, not pure volume-ranked.

`FILE_READ_OUTPUT` had larger measured volume, but is a riskier first producer
because full source reads may be necessary for the agent's next action.

`STATE_DISCOVERY` was selected because it combines meaningful measured volume,
long context lifetime, mechanical semantics, and a plausible bounded-query
contract.

The rule is:

```text
the data ranks opportunity;
the risk policy selects the first producer candidate.
```

## Research Question

Can a local deterministic producer replace part of the historical
`STATE_DISCOVERY` outputs with smaller measured answers while preserving the
information needed for the agent's next action?

The measured chain is:

```text
raw state-discovery output
-> measured compact answer
-> sufficiency preserved?
-> immediate saving
-> propagated saving until compaction
```

The experiment does not ask whether Workspace/State-Manifest is a good idea in
general. It asks whether one measured producer can replace one locked event
class in this session under the existing replay gates.

## Event Scope

Only replay events with all of the following are in scope:

```text
category: STATE_DISCOVERY
safe_command_class: state_discovery
```

The following classes are out of scope even when they look related:

```text
FILE_READ_OUTPUT
SEARCH_OUTPUT
GIT_OUTPUT
TEST_OUTPUT
BUILD_OUTPUT
PYTHON_OUTPUT
NETWORK_FETCH_OUTPUT
OTHER
```

This prevents one producer experiment from quietly becoming a hidden
orchestrator.

## Historical State Reconstruction Gate

State discovery depends on the workspace state at the historical moment of the
original event.

A producer run against the current workspace must not be attributed to a
historical event unless the relevant historical state can be reconstructed.

Every candidate event receives exactly one reconstruction status:

```text
EXACT
PARTIAL
NOT_AVAILABLE
```

### EXACT

`EXACT` requires enough evidence to reproduce the discovery-relevant workspace
state for the event.

Depending on the query, required inputs may include:

```text
git commit
dirty diff hash
untracked-file inventory hash
workspace root fingerprint
relevant generated-output fingerprints
filesystem metadata required by the query
case-sensitivity policy
symlink policy
excluded-directory policy
```

Only `EXACT` events may enter lower or realistic replay bounds.

### PARTIAL

`PARTIAL` means some relevant state is known, but the historical output cannot
be reproduced with enough confidence for lower or realistic bounds.

`PARTIAL` events may enter only an upper research bound, and only with explicit
disclosure.

### NOT_AVAILABLE

`NOT_AVAILABLE` means the event cannot be reconstructed enough to produce a
measured replacement.

`NOT_AVAILABLE` events are not counted.

No compact replacement may be invented for these events.

## Architecture Constraint

The producer architecture is:

```text
workspace scan
-> local state index
-> bounded query
-> compact answer
```

It is not:

```text
workspace scan
-> giant JSON manifest injected into every prompt
```

The local index may be large. Only the query answer enters the model context.

## Allowed Query Types

V1 may implement only this closed set:

```text
WORKSPACE_OVERVIEW
PATH_EXISTS
PATH_METADATA
TOP_LEVEL_ENTRIES
MATCHING_PATHS
ARTIFACT_LOCATIONS
CHANGED_SINCE_SNAPSHOT
STALE_OUTPUTS
DRILLDOWN_REQUIRED
```

`CHANGED_SINCE_SNAPSHOT` and `STALE_OUTPUTS` are allowed only when the producer
has the inputs needed to compute them directly. They must not smuggle in Git
manifest or build-system behavior.

If a historical event cannot be mapped to one of these query types, it is not
counted for lower or realistic bounds.

## Output Contract

Every compact answer must use this envelope:

```json
{
  "schema": "SPIRA_WORKSPACE_STATE_ANSWER_V1",
  "query_type": "WORKSPACE_OVERVIEW",
  "workspace_fingerprint": "...",
  "producer": {
    "name": "spira-workspace-state-producer",
    "version": "0.1"
  },
  "state_reconstruction_status": "EXACT",
  "stale": false,
  "answer": {
    "root_count": 1,
    "top_level_entry_count": 12,
    "file_count": 487,
    "directory_count": 39
  },
  "sufficient_for": [
    "SELECT_NEXT_DISCOVERY_QUERY"
  ],
  "not_sufficient_for": [
    "EDIT_SOURCE",
    "CONFIRM_CODE_BEHAVIOR"
  ],
  "drilldown": [
    {
      "query_type": "MATCHING_PATHS",
      "available": true
    }
  ],
  "not_evaluated": [],
  "evidence_refs": [],
  "conflicts": []
}
```

Critical fields:

```text
workspace_fingerprint
state_reconstruction_status
stale
sufficient_for
not_sufficient_for
drilldown
not_evaluated
conflicts
```

## Replacement Measurement

For every candidate event, the measurement record must include:

```text
event_id
raw_output_bytes
raw_output_allocated_fresh_tokens
raw_output_sha256
compact_output_bytes
compact_output_estimated_tokens
compact_output_sha256
producer_name
producer_version
query_type
query_fingerprint
workspace_fingerprint
state_reconstruction_status
replacement_status
```

No `compact_target_tokens` may be used in lower or realistic bounds.

If no runnable producer creates a real compact answer:

```text
replacement_status: NOT_MEASURED
```

The event is then excluded from lower and realistic bounds.

## Sufficiency Audit

Each measured replacement must be audited against the agent's next action.

The audit asks:

```text
Did the agent only need to know which paths existed?
Did the agent choose a file or directory from the discovered set?
Did it need ordering, size, timestamps, hidden files, or metadata?
Did it use an outlier entry that the compact answer omitted?
Did the next action require immediate drill-down?
Was drill-down measured and included in the cost?
```

Every replacement receives exactly one sufficiency status:

```text
SUFFICIENT
SUFFICIENT_WITH_MEASURED_DRILLDOWN
INSUFFICIENT
INDETERMINATE
```

Only these statuses may be counted:

```text
SUFFICIENT
SUFFICIENT_WITH_MEASURED_DRILLDOWN
```

`SUFFICIENT_WITH_MEASURED_DRILLDOWN` may be counted only when the drill-down
cost is measured and included.

## Fail-Closed Rules

The producer must return `RERUN_REQUIRED` or `RESCAN_REQUIRED` when any of the
following occurs:

```text
workspace fingerprint changed
snapshot missing
state reconstruction is PARTIAL for lower/realistic use
state reconstruction is NOT_AVAILABLE
permission error
symlink policy unknown
path casing ambiguous
scan interrupted
excluded directories undocumented
query type unsupported
compact answer lacks a required field
conflicting index records
```

The producer must never return stale workspace state as current.

## Replay After Producer

After one runnable producer exists, rerun the same preselected replay and report:

```text
candidate STATE_DISCOVERY events
events with EXACT reconstructed state
measured replacements
sufficiency pass count
sufficiency failure count
drill-down count
immediate fresh savings
propagated savings until compaction
session-wide lower bound
session-wide realistic bound
upper research bound
```

The previous replay result is not replaced. It remains the baseline.

The new result is a before/after measurement for this one producer family.

## Decision Thresholds

The thresholds remain the locked replay thresholds:

```text
REPLAY_INVALID
-> no conclusion and no build authorization

lower < 10%
-> stop; no justification to continue

realistic < 20%
-> no orchestrator justification

realistic 20%-40%
-> at most a limited pilot of up to three tool families

realistic 40%-50%
-> strong support; still requires live A/B

realistic >= 50%
-> counterfactual support only; still requires live A/B

only upper bound passes
-> no build authorization
```

## Not Claimed

This methodology does not claim:

```text
Workspace/State-Manifest will save context.
Workspace/State-Manifest is sufficient for general coding work.
STATE_DISCOVERY represents all local tool output.
The producer may replace file reads, search output, Git output, tests, or builds.
Any CPU, energy, or CO2 saving.
Any product capability in SPIRA Trust.
Any authorization to build a broad orchestrator.
```

## Final Gate

```text
Event-volume ranking: VALID
First producer candidate: REASONABLE
Selection type: POLICY_WEIGHTED_NOT_PURE_VOLUME
Authorized next action: ONE_PRODUCER_IMPLEMENTATION_FOR_MEASUREMENT_ONLY
Broad orchestrator: NOT_AUTHORIZED
Product claim: NOT_AUTHORIZED
```

