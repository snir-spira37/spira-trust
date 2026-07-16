# Cold Demo Review Task

Perform the review from the uploaded package or a fresh clone pinned to the exact source commit. Do not rely on the builder's local workspace.

## Review Steps

1. Verify the SHA256 of the ZIP listed in `UPLOAD_NOTE.txt`.
2. Extract the package.
3. Read `README_DEMO.md`.
4. Verify every entry in `SHA256SUMS`.
5. Verify the fixture hashes in `demo_reproduction_manifest.json`.
6. Run the three Domain 3 demo paths through the existing harness:

   ```powershell
   python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
   ```

7. Verify actions and reason codes against `demo_expected_results.json`.
8. Confirm that `invalid_json_01` does not receive a soft PASS.
9. Run focused tests:

   ```powershell
   python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
   ```

10. Run full tests if dependencies are available:

    ```powershell
    python -m pytest
    ```

11. Check for local paths and secrets in the package.
12. Document whether Lean/Lake are available.
13. Do not mark Lean PASS unless Lean/Lake were actually run.
14. Return separate PASS/FAIL results for:

    - demo reproduction
    - package integrity
    - Python tests
    - Lean reproduction
    - claims and boundaries

## Expected Review Boundaries

The package is Domain 3 only. It does not claim arbitrary tool-call interception, MCP gateway enforcement, database/API action enforcement, backup/restore evidence, approval evidence, or universal agent governance.

Source commit for package build input:

```text
19c0e996a79187c444bcbba76f3f4a907e003ae1
```
