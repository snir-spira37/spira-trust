# Multi-Agent Benchmark Inter-Track Pause Operating Rule

## Status

```text
CLAUDE_NATIVE_PRIMARY_REMAINS_ACTIVE_TRACK
CLAUDE_NATIVE_PRIMARY_PAUSED_AT_PROVIDER_USAGE_LIMIT
CLAUDE_COMPLETED_SESSIONS_PRESERVED
CODEX_NATIVE_TRACK_PREPARATION_ONLY
CONCURRENT_LIVE_AGENT_TRACK_EXECUTION_FORBIDDEN
CODEX_LIVE_READINESS_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
HOLDOUT_NOT_AUTHORIZED
CARRYOVER_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Current Claude Checkpoint

```text
authorized sessions:
180

completed scored sessions:
122

next_session_index:
123

pause classification:
PROVIDER_USAGE_LIMIT_PAUSE

correctness failure:
false

completed-session replay:
forbidden
```

The Claude benchmark remains the active primary benchmark even while execution
is temporarily paused.

The pause does not:

```text
close the Claude track
invalidate completed sessions
authorize replacement sessions
authorize another primary benchmark
convert unfinished sessions into failures
```

## Claude Artifact Preservation

While Claude is paused, the following must remain unchanged:

```text
Claude session manifest
Claude completed results
Claude private raw-output manifest
Claude runner
Claude model configuration
Claude prompts
Claude frozen inputs
Claude schema
Claude oracles
Claude comparator
Claude session ordering
Claude next_session_index
```

Completed Claude sessions must not be repeated.

The next Claude execution must resume from:

```text
session_index:
123
```

using the accepted resume mechanism.

## Codex Activity Allowed During Claude Pause

Only static preparation work is permitted.

Authorized preparation categories:

```text
Codex readiness authorization drafting
Codex runner skeleton implementation
separate Codex manifests and results-directory preparation
static model-configuration design
CLI discovery and local version inspection
usage-telemetry parser design
tool-permission configuration design
structured-output parser design
session-isolation design
focused unit tests
frozen-asset compatibility validation
documentation and review artifacts
```

All Codex artifacts must use separate names and directories.

Example boundary:

```text
research/multi_agent_benchmark/codex_native/
```

Codex preparation must not write into:

```text
research/multi_agent_benchmark/claude_native/
```

## Codex Live Activity Not Authorized

Without a separate accepted authorization, the following are forbidden:

```text
Codex authentication calls to the provider
live model-identity probes
live usage-telemetry probes
live structured-output probes
live tool-use probes
Codex readiness sessions
Codex primary sessions
Codex holdout sessions
Codex carryover sessions
```

A small live probe is still a live provider session and requires explicit
authorization.

The next permissible Codex live step is therefore:

```text
research/multi_agent_benchmark/codex_native/codex_native_c0_or_readiness_technical_probe_authorization.md
```

or another equivalently narrow authorization accepted before execution.

## Concurrency Rule

The following is prohibited:

```text
Claude live benchmark session
+
Codex live benchmark or readiness session
running concurrently
```

Only one agent track may execute live benchmark-related provider sessions at a
time.

Static Codex preparation may occur while Claude is paused.

## Repository Separation

Claude and Codex must retain separate:

```text
session IDs
config directories
workspaces
private raw-output roots
public manifests
result files
reports
reviews
runner entry points
checkpoint state
```

The following are forbidden:

```text
shared session manifests
shared result arrays
copying Claude usage into Codex results
copying Codex usage into Claude results
reuse of Claude session IDs
reuse of private raw-output identifiers
cross-track checkpoint mutation
```

## Resume Procedure After Claude Usage Reset

When Claude usage becomes available again:

```text
1. Stop Codex preparation at a clean filesystem and Git checkpoint.

2. Confirm that no Codex live provider process is active.

3. Confirm the working tree and frozen benchmark assets are unchanged.

4. Validate the Claude checkpoint:

   completed_session_count = 122
   next_session_index = 123
   prior completed sessions remain immutable

5. Resume with:

   python tools\run_claude_native_primary_benchmark.py --resume

6. Confirm that execution begins at session 123.

7. Complete the remaining Claude sessions.

8. Produce the Claude primary result and report.

9. Perform a separate Claude primary review.

10. Do not begin Codex primary execution before the Claude review is accepted
    and Codex has independently passed its own readiness and authorization gates.
```

## Failure Handling During Resume

If the Claude usage limit recurs:

```text
persist the current checkpoint atomically
preserve all completed sessions
record the next session index
classify the event as a provider usage-limit pause
do not perform hidden retries
do not restart completed sessions
```

A provider quota interruption is not a correctness result.

## Frozen Cross-Agent Policy

Codex preparation must preserve:

```text
18 frozen cases
54 frozen Arm inputs
shared output schema
expected oracles
comparison policy
global Arm A policy
Arm B strict-fidelity gate
Arm C strict-fidelity gate
MVP code
domain producers
```

No benchmark asset may be changed to adapt it to Claude partial results or
anticipated Codex behavior.

## Final Boundary

```text
CLAUDE_NATIVE_PRIMARY:
ACTIVE BUT TEMPORARILY PAUSED

CLAUDE_COMPLETED_SESSIONS:
IMMUTABLE

CODEX_NATIVE:
PREPARATION ONLY

CODEX LIVE READINESS:
SEPARATE AUTHORIZATION REQUIRED

CODEX PRIMARY:
NOT AUTHORIZED

CONCURRENT LIVE TRACKS:
FORBIDDEN

HOLDOUT:
NOT AUTHORIZED

CARRYOVER:
NOT AUTHORIZED

EFFICIENCY CLAIM:
NOT AUTHORIZED

RELEASE:
NOT AUTHORIZED
```

## Practical Rule

```text
Now:
Claude paused, Codex static preparation only.

After quota reset:
stop Codex preparation at a clean checkpoint,
validate the Claude checkpoint,
resume Claude from session 123.

After Claude completion and review:
open Codex readiness through a separate authorization path.
```
