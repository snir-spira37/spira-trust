# DeepSeek Read Tool Diagnostic Report

## Status

```text
DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
requested model: deepseek-v4-pro
probe count: 6
benchmark cases sent: 0
readiness sessions: 0
```

## Probes

- read_only_default_prompt: rc=1 tools=[] stderr=NONEMPTY_OTHER mutated=False
- read_only_manual_permission: rc=1 tools=[] stderr=NONEMPTY_OTHER mutated=False
- glob_only_probe: rc=1 tools=[] stderr=NONEMPTY_OTHER mutated=False
- grep_only_probe: rc=1 tools=[] stderr=NONEMPTY_OTHER mutated=False
- read_with_json_output: rc=1 tools=[] stderr=EMPTY mutated=False
- read_with_tools_syntax_space: rc=1 tools=[] stderr=NONEMPTY_OTHER mutated=False
