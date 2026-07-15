SPIRA Formal Core V1 External Reproduction Task

Purpose
=======

Reproduce the offline deterministic Formal Core V1 evidence without live agents.

Start from the repository root and run one of:

  PowerShell:
    research\formal_core\external_reproduction_package\verify_all.ps1

  POSIX shell:
    bash research/formal_core/external_reproduction_package/verify_all.sh

Expected result:

  SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS

This package intentionally does not run Claude, Codex, DeepSeek, holdout, carryover, or any live benchmark.

