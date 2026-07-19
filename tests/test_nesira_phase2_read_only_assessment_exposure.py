from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tomllib
import zipfile
from datetime import datetime
from pathlib import Path

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_assessment_wiring import EXECUTION_MARKER
from spira_core.nesira_phase2_assessment_wiring_harness import _valid_request


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "run_nesira_phase2_read_only_assessment.py"
PUBLIC_MODULE = "spira_core.nesira_phase2_read_only_assessment_cli"
FORBIDDEN_FLAGS = (
    "--enforce",
    "--apply",
    "--execute",
    "--sever",
    "--proceed",
    "--auto",
    "--fix",
    "--remediate",
    "--run-isolation",
    "--combined-verdict",
)
FORBIDDEN_OUTPUT_KEYS = {
    "agent_" + "action",
    "combined_" + "verdict",
    "execute",
    "permission_to_" + "sev" + "er",
    "pro" + "ceed",
    "recommended_agent_" + "action",
    "release",
    "safe_to_" + "sev" + "er",
    "se" + "ver",
}
FORBIDDEN_RELABELS = (
    "approved",
    "safe",
    "proceed",
    "authorized",
    "sever",
)


def test_read_only_tool_emits_raw_assessment_tokens_and_success_exit_for_sufficient(tmp_path):
    request = _write_request(tmp_path, _valid_request())
    result = _run_tool(request)
    artifact = json.loads(result.stdout)

    assert result.returncode == 0
    assert artifact["verdict"] == "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
    assert artifact["execution_marker"] == EXECUTION_MARKER
    assert "PT-ISOLATION-01" in artifact["assumptions"]
    assert not _contains_forbidden_key(artifact)
    assert "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS" in result.stdout


def test_exit_code_reflects_tool_success_not_assessment_permission(tmp_path):
    request_data = _valid_request()
    request_data["signature_root"] = None
    request = _write_request(tmp_path, request_data)
    result = _run_tool(request)
    artifact = json.loads(result.stdout)

    assert result.returncode == 0
    assert artifact["verdict"] == "TRUST_NOT_EVALUATED"
    assert artifact["execution_marker"] == EXECUTION_MARKER


def test_output_file_matches_stdout_byte_for_byte(tmp_path):
    request = _write_request(tmp_path, _valid_request())
    output = tmp_path / "assessment.json"
    result = _run_tool(request, "--output", str(output))

    assert result.returncode == 0
    assert output.read_text(encoding="utf-8") == result.stdout


def test_two_run_output_is_byte_identical(tmp_path):
    request = _write_request(tmp_path, _valid_request())
    first = _run_tool(request)
    second = _run_tool(request)

    assert first.returncode == 0
    assert first.stdout == second.stdout


def test_malformed_input_returns_clean_tool_error_without_traceback_or_local_path(tmp_path):
    request = tmp_path / "bad.json"
    request.write_text("{not json", encoding="utf-8")
    result = _run_tool(request)

    assert result.returncode != 0
    assert result.stdout == ""
    error = json.loads(result.stderr)
    assert error["schema"] == "NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1"
    assert "Traceback" not in result.stderr
    assert "C:\\Users\\" not in result.stderr
    assert "C:/Users/" not in result.stderr


def test_tool_surface_has_no_forbidden_flags_or_action_fields():
    source = TOOL.read_text(encoding="utf-8")
    parser_region = source.split("FORBIDDEN_OUTPUT_KEYS", 1)[0]

    for flag in FORBIDDEN_FLAGS:
        assert flag not in parser_region
    for key in FORBIDDEN_OUTPUT_KEYS:
        assert key not in parser_region
    for relabel in FORBIDDEN_RELABELS:
        assert relabel not in parser_region.lower()


def test_no_console_entry_point_and_crypto_remains_gated():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    scripts = pyproject["project"].get("scripts", {})
    optional = pyproject["project"].get("optional-dependencies", {})

    assert pyproject["project"]["dependencies"] == []
    assert optional == {"nesira-assessment": ["cryptography==49.0.0"]}
    assert all("nesira_phase2" not in name for name in scripts)
    assert all("nesira_phase2" not in target for target in scripts.values())


def test_read_only_runtime_is_exposed_in_public_wheel_without_action_surface(tmp_path):
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert all("run_nesira_phase2_read_only_assessment" not in name for name in names)
    assert "spira_core/nesira_phase2_read_only_assessment_cli.py" in names
    assert "spira_core/nesira_phase2_assessment_wiring.py" in names
    assert "spira_core/nesira_phase2_signature_adapter.py" in names
    assert "spira_core/nesira_phase2_identity_adapter.py" in names
    assert "spira_core/nesira_phase2_authority_adapter.py" in names
    assert "spira_core/nesira_phase2_isolation_attestation_adapter.py" in names
    assert "spira_core/unification_proof.py" in names
    assert all("_harness.py" not in name for name in names)
    assert "Provides-Extra: nesira-assessment" in metadata
    assert "Requires-Dist: cryptography==49.0.0; extra == 'nesira-assessment'" in metadata


def test_public_wheel_graph_command_has_runtime_dependencies(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    graph_out = tmp_path / "graph"
    install_target = tmp_path / "installed"
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-index", "--target", str(install_target), str(wheel_path)],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(install_target)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "spira_core.trust_cli",
            "graph",
            str(wheel_path),
            "--output-dir",
            str(graph_out),
            "--format",
            "json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    assert "ModuleNotFoundError" not in result.stderr
    assert (graph_out / "unification_proof.json").is_file()


def test_public_wheel_module_runs_read_only_assessment_with_tool_success_exit(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    request = _write_request(tmp_path, _valid_request())
    result = _run_wheel_module(wheel_path, request)
    artifact = json.loads(result.stdout)

    assert result.returncode == 0
    assert artifact["verdict"] == "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
    assert artifact["execution_marker"] == EXECUTION_MARKER
    assert not _contains_forbidden_key(artifact)


def test_public_wheel_module_returns_clean_json_error_for_malformed_input(tmp_path):
    wheel_path = _build_public_wheel(tmp_path)
    request = tmp_path / "bad.json"
    request.write_text("{not json", encoding="utf-8")
    result = _run_wheel_module(wheel_path, request)

    assert result.returncode != 0
    assert result.stdout == ""
    error = json.loads(result.stderr)
    assert error["schema"] == "NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1"
    assert "Traceback" not in result.stderr
    assert "C:\\Users\\" not in result.stderr
    assert "C:/Users/" not in result.stderr


def _write_request(tmp_path: Path, request: dict[str, object]) -> Path:
    path = tmp_path / "request.json"
    path.write_text(canonical_json(_json_ready(request)) + "\n", encoding="utf-8", newline="\n")
    return path


def _run_tool(request: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), str(request), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def _build_public_wheel(tmp_path: Path) -> Path:
    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.splitlines()[0])


def _run_wheel_module(wheel_path: Path, request: Path) -> subprocess.CompletedProcess[str]:
    env = dict(**__import__("os").environ)
    env["PYTHONPATH"] = str(wheel_path)
    return subprocess.run(
        [sys.executable, "-m", PUBLIC_MODULE, str(request)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


def _contains_forbidden_key(value: object) -> bool:
    if isinstance(value, dict):
        return any(str(key) in FORBIDDEN_OUTPUT_KEYS or _contains_forbidden_key(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _json_ready(value: object) -> object:
    if isinstance(value, bytes):
        return {"__spira_bytes_b64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, datetime):
        return value.isoformat().replace("+00:00", "Z")
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value
