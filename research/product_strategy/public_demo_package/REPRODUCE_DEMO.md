# Reproduce The Public Demo

## Supported Environment

- Windows PowerShell or POSIX shell
- Python 3.12+
- `pytest` available for test commands
- Repository checkout pinned to `0aa44f33455d477fe53236d3ce8daddb6d830dad` or the final package build commit that contains this package

Lean/Lake is optional for this demo package review. If Lean/Lake is unavailable, record:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## Working Directory

Run commands from the repository root.

## Dependency Installation

Use the repository's normal Python environment. If dependencies are not installed:

```powershell
python -m pip install -e .
python -m pip install pytest
```

## Exact Demo Command

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

Expected exit code:

```text
0
```

Expected status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
```

## Exact Fixture Paths

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
```

The package also includes byte-for-byte copies under `fixtures/` for review and hash comparison. The existing harness reads the repository fixtures, not the copied package fixtures.

## Expected Generated Artifacts

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json
```

## Expected Actions And Reason Codes

See `demo_expected_results.json`.

Short form:

```text
create_update_delete_01 -> STOP_BLOCKED -> TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE
incomplete_plan_01 -> REPORT_NOT_EVALUATED -> TERRAFORM_PLAN_INCOMPLETE
invalid_json_01 -> RERUN_REQUIRED -> TERRAFORM_PLAN_JSON_INVALID
```

Expected blocking/not-evaluated values:

```text
STOP_BLOCKED blocking_items: resource change requires review
REPORT_NOT_EVALUATED not_evaluated: terraform plan incomplete
RERUN_REQUIRED not_evaluated: Terraform plan JSON parse failed
```

## Focused Test Command

```powershell
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
```

Expected exit code:

```text
0
```

## Full Test Command

```powershell
python -m pytest
```

Expected result in the accepted package-build environment:

```text
270 passed
```

## Package Integrity Command

From inside `research/product_strategy/public_demo_package`, validate `SHA256SUMS` with a SHA256 tool or with Python:

```powershell
python - <<'PY'
import hashlib, pathlib
root = pathlib.Path('.')
for line in (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
    expected, path = line.split('  ', 1)
    actual = hashlib.sha256((root / path).read_bytes()).hexdigest()
    assert actual == expected, path
print('SHA256SUMS PASS')
PY
```

PowerShell does not support the POSIX heredoc syntax above. On Windows, run the same Python code from a `.py` file or paste it into `python -c`.

## Troubleshooting

- If `pytest` is missing, install it in the active Python environment.
- If Lean/Lake is missing, do not mark Lean reproduction as PASS.
- If `invalid_json_01` produces `PROCEED`, treat that as a hard failure.
- If a command is run outside the repository root, relative paths may not resolve.

## Cleanup Guidance

The demo command rewrites generated research result artifacts. Use `git status --short` to inspect local changes after reproduction.

## Interpretation Of NOT_EVALUATED

`NOT_EVALUATED` is not a pass. It means required evidence was not available or could not be evaluated, and SPIRA must not silently upgrade that unknown state into proceed.
