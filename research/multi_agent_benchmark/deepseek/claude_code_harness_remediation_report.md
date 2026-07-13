# Claude Code Harness Remediation Report

## Status

```text
CLAUDE_CODE_HARNESS_READY_FOR_DS_R0
CLAUDE_EXECUTABLE_DISCOVERED
CLAUDE_CODE_VERSION_CONFIRMED
REQUIRED_FLAGS_AVAILABLE
HARNESS_LAUNCH_SMOKE_PASS
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
DS_R0_RERUN_NOT_YET_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization

```text
authorization:
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_authorization.md

authorization commit:
e053f2178dda0167b2165aaf5ac64077d4007b1e
```

## Discovery Input

Phase A discovery established:

```text
claude executable in current PATH:
NOT_FOUND

npm / npx:
NOT_FOUND

Codex bundled node:
available, but no Claude Code launcher

winget:
available
```

That satisfied the condition for narrow Phase B installation/remediation.

## Remediation Performed

```text
installer:
winget

package:
Anthropic.ClaudeCode

installed version:
2.1.206

installer hash verification:
performed by winget

unrelated package updates:
not performed
```

The installed executable was found under the WinGet package location. The raw
local path is not recorded in this repository.

Safe executable metadata:

```text
version:
2.1.206

sha256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2
```

The new command alias was not visible to the already-running shell session
immediately after installation. Temporarily prepending the WinGet package
directory to the process PATH exposed the launcher successfully.

This means the next DS-R0 rerun should either:

```text
start in a fresh shell where the alias is visible
```

or:

```text
temporarily prepend the resolved WinGet package directory to the process PATH
```

without changing the persistent benchmark assets.

## Required Flag Verification

`claude --help` confirmed the required DS-R0 flag surfaces:

```text
--print
--model
--output-format
--max-turns
--permission-mode
--tools
--disallowedTools
--strict-mcp-config
--no-session-persistence
--session-id
```

## Harness Launch Smoke

A non-scored harness smoke was executed with:

```text
model:
deepseek-v4-pro

benchmark case:
none

output mode:
json

tools:
disabled

readiness sessions:
0
```

Result:

```text
HARNESS_LAUNCH_SMOKE_PASS
exit_code: 0
usage accounting: available
web_search_requests: 0
web_fetch_requests: 0
permission_denials: 0
```

The smoke response reported:

```text
modelUsage.deepseek-v4-pro.contextWindow:
200000
```

This does not change the previously accepted model identity amendment. The
benchmark remains pinned to `deepseek-v4-pro`, and no independent `[1m]`
capability claim is authorized.

## Boundary

```text
benchmark cases sent to model:
0

readiness sessions started:
0

primary benchmark started:
false

MVP code changed:
false

cases / prompts / frozen inputs changed:
false

release/version/tag/PyPI:
false
```

## Conclusion

The Claude Code harness blocker has been remediated for DS-R0 purposes:

```text
CLAUDE_CODE_HARNESS_READY_FOR_DS_R0
```

This is not permission to run DS-R0 yet. A remediation review must accept this
result first.

## Next Gate

```text
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_review.md
```

Possible verdicts:

```text
CLAUDE_CODE_HARNESS_REMEDIATION_ACCEPTED
CLAUDE_CODE_HARNESS_REMEDIATION_NEEDS_REVISION
CLAUDE_CODE_HARNESS_REMEDIATION_REJECTED
```

Only if accepted may a fresh DS-R0 rerun be authorized from P1.
