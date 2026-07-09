#!/usr/bin/env python3
"""Run the previous public SPIRA Trust version against a candidate wheel."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any

try:
    from packaging.version import InvalidVersion, Version
except ImportError as error:  # pragma: no cover - exercised in release CI environment.
    raise SystemExit(
        "tools/run_previous_version_gate.py requires packaging. "
        "Install release workflow tooling with: python -m pip install packaging"
    ) from error


PYPI_JSON_URL = "https://pypi.org/pypi/spira-trust/json"
SCHEMA = "SPIRA_PREVIOUS_VERSION_GATE_V1"
EXPECTED_BLOCK_SCHEMA = "SPIRA_EXPECTED_PREVIOUS_BLOCK_V1"
SELECTION_MODE = "highest_non_yanked_pypi_release_lower_than_candidate"
BLOCKING_GRAPH_VERDICTS = {"GRAPH_BLOCK"}
BLOCKING_TRUST_VERDICTS = {"TRUST_BLOCK"}
FINDING_CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")


@dataclass(frozen=True)
class PreviousDistribution:
    version: str
    filename: str
    url: str
    sha256: str
    size: int | None
    upload_time_iso_8601: str | None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-wheel", required=True)
    parser.add_argument("--candidate-version", default=None)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--expected-previous-block", default="release/expected_previous_block.json")
    parser.add_argument("--previous-version", default=None)
    parser.add_argument("--first-public-release", action="store_true")
    parser.add_argument("--verify-embedded-sboms", action="store_true")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    candidate_wheel = Path(args.candidate_wheel)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    gate_path = output_dir / "previous_version_gate.json"

    candidate_version = args.candidate_version or _parse_candidate_version(candidate_wheel)
    candidate = {
        "name": "spira-trust",
        "version": candidate_version,
        "wheel_path": _portable_path(candidate_wheel),
        "wheel_sha256": _sha256_file(candidate_wheel),
        "bytes": candidate_wheel.stat().st_size,
    }

    try:
        pypi_json = _fetch_pypi_json()
        previous = _select_previous_distribution(
            pypi_json,
            candidate_version=candidate_version,
            override_version=args.previous_version,
            first_public_release=args.first_public_release,
        )
    except GateError as error:
        result = _base_result(candidate)
        result["previous"] = {
            "selection_mode": SELECTION_MODE,
            "version": args.previous_version,
            "filename": None,
            "pypi_sha256": None,
            "install_mode": "pinned_hash",
            "command": None,
        }
        result["expected_previous_block"] = _read_expected_block_state(
            Path(args.expected_previous_block), candidate_version, None
        )
        result["gate"] = {
            "status": "PREVIOUS_VERSION_RESOLUTION_ERROR",
            "publish_allowed": False,
            "reason": str(error),
        }
        _write_json(gate_path, result)
        return 1

    previous_dir = output_dir / "previous"
    previous_dir.mkdir(parents=True, exist_ok=True)
    requirements_path = previous_dir / "previous-requirements.txt"
    requirements_path.write_text(
        f"spira-trust=={previous.version} --hash=sha256:{previous.sha256}\n",
        encoding="utf-8",
        newline="\n",
    )
    (previous_dir / "pypi_selection.json").write_text(
        json.dumps(_pypi_selection_evidence(previous), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    venv_dir = previous_dir / ".venv-previous"
    try:
        command_path = _install_previous(args.python, venv_dir, requirements_path)
    except GateError as error:
        result = _base_result(candidate)
        result["previous"] = _previous_block(previous, command=None)
        result["expected_previous_block"] = _read_expected_block_state(
            Path(args.expected_previous_block), candidate_version, previous.version
        )
        result["gate"] = {
            "status": "PREVIOUS_VERSION_INSTALL_ERROR",
            "publish_allowed": False,
            "reason": str(error),
        }
        _write_json(gate_path, result)
        return 1

    trust = _run_previous_trust(command_path, candidate_wheel, output_dir)
    graph = _run_previous_graph(command_path, candidate_wheel, output_dir, args.verify_embedded_sboms)
    expected = _read_expected_block_state(Path(args.expected_previous_block), candidate_version, previous.version)
    result = _base_result(candidate)
    result["previous"] = _previous_block(previous, command=command_path)
    result["trust"] = trust
    result["graph"] = graph
    result["expected_previous_block"] = expected

    gate = _decide_gate(trust, graph, expected)
    result["gate"] = gate
    _write_json(gate_path, result)
    return 0 if gate["publish_allowed"] else 1


class GateError(RuntimeError):
    pass


def _fetch_pypi_json() -> dict[str, Any]:
    try:
        request = urllib.request.Request(PYPI_JSON_URL, headers={"User-Agent": "spira-previous-version-gate"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        raise GateError(f"could not fetch PyPI metadata: {error}") from error


def _select_previous_distribution(
    pypi_json: dict[str, Any],
    *,
    candidate_version: str,
    override_version: str | None,
    first_public_release: bool,
) -> PreviousDistribution:
    releases = pypi_json.get("releases")
    if not isinstance(releases, dict):
        raise GateError("PyPI metadata did not contain a releases object")
    if override_version:
        version = override_version
    else:
        lower_versions = [
            version
            for version, files in releases.items()
            if _version_key(version) < _version_key(candidate_version) and _release_has_non_yanked_wheel(files)
        ]
        if not lower_versions:
            if first_public_release:
                raise GateError("first public release mode is not implemented for production previous gate")
            raise GateError(f"no non-yanked public release lower than {candidate_version} was found")
        version = max(lower_versions, key=_version_key)
    files = releases.get(version)
    if not isinstance(files, list):
        raise GateError(f"PyPI release {version} did not contain a file list")
    wheel = _select_wheel_file(files, version)
    return PreviousDistribution(
        version=version,
        filename=str(wheel.get("filename")),
        url=str(wheel.get("url")),
        sha256=str((wheel.get("digests") or {}).get("sha256") or ""),
        size=wheel.get("size"),
        upload_time_iso_8601=wheel.get("upload_time_iso_8601"),
    )


def _release_has_non_yanked_wheel(files: Any) -> bool:
    return isinstance(files, list) and any(
        isinstance(item, dict) and item.get("packagetype") == "bdist_wheel" and not item.get("yanked")
        for item in files
    )


def _select_wheel_file(files: list[Any], version: str) -> dict[str, Any]:
    wheels = [
        item
        for item in files
        if isinstance(item, dict)
        and item.get("packagetype") == "bdist_wheel"
        and not item.get("yanked")
        and str(item.get("filename", "")).endswith(".whl")
    ]
    if not wheels:
        raise GateError(f"PyPI release {version} had no non-yanked wheel file")
    wheels.sort(key=lambda item: (0 if "py3-none-any" in str(item.get("filename", "")) else 1, str(item.get("filename"))))
    wheel = wheels[0]
    if not (wheel.get("digests") or {}).get("sha256"):
        raise GateError(f"PyPI wheel {wheel.get('filename')} did not include a SHA-256 digest")
    if not wheel.get("url"):
        raise GateError(f"PyPI wheel {wheel.get('filename')} did not include a download URL")
    return wheel


def _install_previous(python: str, venv_dir: Path, requirements_path: Path) -> str:
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    try:
        create = subprocess.run([python, "-m", "venv", str(venv_dir)], text=True, capture_output=True)
    except OSError as error:
        raise GateError(f"could not launch Python for previous-version virtualenv: {error}") from error
    (requirements_path.parent / "venv-create.stdout").write_text(create.stdout, encoding="utf-8", newline="\n")
    (requirements_path.parent / "venv-create.stderr").write_text(create.stderr, encoding="utf-8", newline="\n")
    if create.returncode != 0:
        raise GateError(f"could not create previous-version virtualenv: exit code {create.returncode}")
    pip = _venv_python(venv_dir)
    install_cmd = [
        pip,
        "-m",
        "pip",
        "install",
        "--require-hashes",
        "--only-binary=:all:",
        "--no-deps",
        "-r",
        str(requirements_path),
    ]
    run = subprocess.run(install_cmd, text=True, capture_output=True)
    (requirements_path.parent / "pip-install.stdout").write_text(run.stdout, encoding="utf-8", newline="\n")
    (requirements_path.parent / "pip-install.stderr").write_text(run.stderr, encoding="utf-8", newline="\n")
    if run.returncode != 0:
        raise GateError(f"pip install failed with exit code {run.returncode}")
    command = _venv_script(venv_dir, "spira-trust")
    if not Path(command).exists():
        raise GateError("installed previous version did not expose spira-trust command")
    return command


def _run_previous_trust(command_path: str, candidate_wheel: Path, output_dir: Path) -> dict[str, Any]:
    trust_dir = output_dir / "trust"
    trust_dir.mkdir(parents=True, exist_ok=True)
    cmd = [command_path, "trust", str(candidate_wheel), "--output-dir", str(trust_dir), "--format", "json"]
    return _run_and_parse(cmd, trust_dir, "trust", "artifact_trust_report.json")


def _run_previous_graph(
    command_path: str,
    candidate_wheel: Path,
    output_dir: Path,
    verify_embedded_sboms: bool,
) -> dict[str, Any]:
    graph_dir = output_dir / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        command_path,
        "graph",
        str(candidate_wheel),
        "--output-dir",
        str(graph_dir),
        "--sbom",
        "cyclonedx-json",
        "--evidence-pack",
        str(output_dir / "previous-version-evidence.zip"),
        "--format",
        "json",
    ]
    if verify_embedded_sboms:
        cmd.append("--verify-embedded-sboms")
    return _run_and_parse(cmd, graph_dir, "graph", "spira-decision.json")


def _run_and_parse(cmd: list[str], output_dir: Path, name: str, report_filename: str) -> dict[str, Any]:
    stdout_path = output_dir / f"{name}.stdout"
    stderr_path = output_dir / f"{name}.stderr"
    run = subprocess.run(cmd, text=True, capture_output=True)
    stdout_path.write_text(run.stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(run.stderr, encoding="utf-8", newline="\n")
    parsed_stdout = _try_parse_json(run.stdout)
    report_path = output_dir / report_filename
    parsed_report = _try_load_json(report_path)
    verdict = _extract_verdict(parsed_report) or _extract_verdict(parsed_stdout)
    finding_codes = sorted(_collect_finding_codes(parsed_stdout) | _collect_finding_codes(parsed_report))
    return {
        "exit_code": run.returncode,
        "verdict": verdict,
        "stdout_path": _portable_path(stdout_path),
        "stderr_path": _portable_path(stderr_path),
        "report_path": _portable_path(report_path) if report_path.exists() else None,
        "finding_codes": finding_codes,
        "schema_readable": parsed_stdout is not None or parsed_report is not None,
    }


def _decide_gate(trust: dict[str, Any], graph: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    active_declaration = expected.get("declaration_path") is not None
    declaration_valid = bool(expected.get("declaration_valid"))

    if not trust.get("verdict"):
        return {
            "status": "PREVIOUS_VERSION_SCHEMA_UNREADABLE",
            "publish_allowed": False,
            "reason": "previous trust output did not contain a parseable verdict",
        }
    if not graph.get("verdict"):
        return {
            "status": "PREVIOUS_VERSION_SCHEMA_UNREADABLE",
            "publish_allowed": False,
            "reason": "previous graph output did not contain a parseable verdict",
        }
    trust_verdict = trust.get("verdict")
    graph_verdict = graph.get("verdict")
    trust_blocked = trust_verdict in BLOCKING_TRUST_VERDICTS
    graph_blocked = graph_verdict in BLOCKING_GRAPH_VERDICTS
    previous_blocked = trust_blocked or graph_blocked
    if previous_blocked:
        if active_declaration and not declaration_valid:
            return {
                "status": "EXPECTED_PREVIOUS_BLOCK_INVALID",
                "publish_allowed": False,
                "reason": "release/expected_previous_block.json exists but is invalid for this candidate, previous version, finding codes, or release notes",
            }
        expected_matches = _expected_block_matches_observed(expected, trust, graph)
        expected["matched"] = expected_matches
        if expected_matches:
            return {
                "status": "DOCUMENTED_PREVIOUS_BLOCK",
                "publish_allowed": True,
                "reason": "previous public version blocked the candidate, and the block matched release/expected_previous_block.json and release notes",
            }
        if active_declaration:
            return {
                "status": "EXPECTED_PREVIOUS_BLOCK_INVALID",
                "publish_allowed": False,
                "reason": "release/expected_previous_block.json exists but did not match the observed previous-version block",
            }
        return {
            "status": "PREVIOUS_VERSION_BLOCK",
            "publish_allowed": False,
            "reason": "previous public version blocked the candidate and no valid matching expected previous-block declaration was present",
        }
    if trust.get("exit_code") not in {0, 2}:
        return {
            "status": "PREVIOUS_VERSION_RUN_ERROR",
            "publish_allowed": False,
            "reason": f"previous trust command returned non-verdict exit code {trust.get('exit_code')}",
        }
    if graph.get("exit_code") not in {0, 2}:
        return {
            "status": "PREVIOUS_VERSION_RUN_ERROR",
            "publish_allowed": False,
            "reason": f"previous graph command returned non-verdict exit code {graph.get('exit_code')}",
        }
    if active_declaration and not declaration_valid:
        return {
            "status": "EXPECTED_PREVIOUS_BLOCK_INVALID",
            "publish_allowed": False,
            "reason": "release/expected_previous_block.json exists but is invalid for this candidate, previous version, finding codes, or release notes",
        }
    if active_declaration and declaration_valid:
        return {
            "status": "EXPECTED_PREVIOUS_BLOCK_NOT_OBSERVED",
            "publish_allowed": False,
            "reason": "release/expected_previous_block.json exists, but the previous public version did not block the candidate",
        }
    return {
        "status": "PASS",
        "publish_allowed": True,
        "reason": "previous public version did not block candidate artifact",
    }


def _expected_block_matches_observed(
    expected: dict[str, Any],
    trust: dict[str, Any],
    graph: dict[str, Any],
) -> bool:
    declaration = expected.get("declaration")
    if not isinstance(declaration, dict):
        return False
    if expected.get("validation_errors"):
        return False
    observed_verdicts = {str(trust.get("verdict")), str(graph.get("verdict"))}
    expected_verdict = declaration.get("expected_previous_verdict")
    if expected_verdict and expected_verdict not in observed_verdicts:
        expected.setdefault("validation_errors", []).append("expected_previous_verdict did not match observed previous verdict")
        return False
    observed_codes = set(trust.get("finding_codes") or []) | set(graph.get("finding_codes") or [])
    missing_codes = [code for code in declaration.get("expected_finding_codes", []) or [] if code not in observed_codes]
    if missing_codes:
        expected.setdefault("validation_errors", []).append(
            "expected finding codes were not observed: " + ", ".join(str(code) for code in missing_codes)
        )
        return False
    return True


def _read_expected_block_state(path: Path, candidate_version: str, previous_version: str | None) -> dict[str, Any]:
    state: dict[str, Any] = {
        "declaration_path": _portable_path(path) if path.exists() else None,
        "matched": False,
        "declaration_valid": False,
        "validation_errors": [],
    }
    if not path.exists():
        return state
    try:
        declaration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        state["validation_errors"].append(f"could not read expected previous-block declaration: {error}")
        return state
    state["declaration"] = declaration
    if declaration.get("schema") != EXPECTED_BLOCK_SCHEMA:
        state["validation_errors"].append(f"schema must be {EXPECTED_BLOCK_SCHEMA}")
    if declaration.get("candidate_version") != candidate_version:
        state["validation_errors"].append("candidate_version does not match release candidate")
    if previous_version and declaration.get("previous_version") != previous_version:
        state["validation_errors"].append("previous_version does not match selected previous release")
    notes_path = Path(str(declaration.get("release_notes_path", "")))
    required_terms = declaration.get("release_notes_required_terms") or []
    mechanical_terms = [
        candidate_version,
        "DOCUMENTED_PREVIOUS_BLOCK",
        *(str(code) for code in declaration.get("expected_finding_codes", []) or []),
    ]
    if previous_version:
        mechanical_terms.append(previous_version)
    if not notes_path.is_file():
        state["validation_errors"].append("release notes path is missing")
    else:
        text = notes_path.read_text(encoding="utf-8")
        for term in mechanical_terms:
            if str(term) not in text:
                state["validation_errors"].append(f"release notes missing mechanical term: {term}")
        for term in required_terms:
            if str(term) not in text:
                state["validation_errors"].append(f"release notes missing required term: {term}")
    state["declaration_valid"] = not state["validation_errors"]
    return state


def _extract_verdict(data: Any) -> str | None:
    if not isinstance(data, dict):
        return None
    candidates = [
        data.get("verdict"),
        (data.get("decision") or {}).get("verdict") if isinstance(data.get("decision"), dict) else None,
        (data.get("decision") or {}).get("combined_verdict") if isinstance(data.get("decision"), dict) else None,
        (data.get("decision") or {}).get("trust_status") if isinstance(data.get("decision"), dict) else None,
        data.get("trust_status"),
    ]
    for value in candidates:
        if isinstance(value, str) and value:
            return value
    return None


def _collect_finding_codes(data: Any) -> set[str]:
    codes: set[str] = set()
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"code", "finding_code", "status", "verdict", "reason_code"} and isinstance(value, str):
                if FINDING_CODE_PATTERN.match(value):
                    codes.add(value)
            codes.update(_collect_finding_codes(value))
    elif isinstance(data, list):
        for item in data:
            codes.update(_collect_finding_codes(item))
    return codes


def _try_parse_json(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _try_load_json(path: Path) -> Any:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _base_result(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "candidate": candidate,
        "previous": {},
        "trust": {},
        "graph": {},
        "expected_previous_block": {},
        "gate": {},
        "not_claimed": [
            "previous-version gate does not prove the candidate is safe",
            "previous-version gate does not validate all new release semantics",
            "previous-version gate records whether the previous public SPIRA version blocked the candidate wheel",
            "this process provides transparency, not independent review",
        ],
    }


def _previous_block(previous: PreviousDistribution, command: str | None) -> dict[str, Any]:
    return {
        "selection_mode": SELECTION_MODE,
        "version": previous.version,
        "filename": previous.filename,
        "pypi_sha256": previous.sha256,
        "install_mode": "pinned_hash",
        "command": _portable_path(Path(command)) if command else None,
        "size": previous.size,
        "upload_time_iso_8601": previous.upload_time_iso_8601,
    }


def _pypi_selection_evidence(previous: PreviousDistribution) -> dict[str, Any]:
    return {
        "schema": "SPIRA_PREVIOUS_VERSION_PYPI_SELECTION_V1",
        "selection_mode": SELECTION_MODE,
        "version": previous.version,
        "filename": previous.filename,
        "url": previous.url,
        "sha256": previous.sha256,
        "size": previous.size,
        "upload_time_iso_8601": previous.upload_time_iso_8601,
    }


def _parse_candidate_version(wheel: Path) -> str:
    match = re.match(r"^spira_trust-(?P<version>[^-]+)-", wheel.name)
    if not match:
        raise GateError(f"could not infer candidate version from wheel name: {wheel.name}")
    return match.group("version")


def _version_key(version: str) -> Version:
    try:
        return Version(version)
    except InvalidVersion as error:
        raise GateError(f"invalid PyPI version {version!r}: {error}") from error


def _venv_python(venv_dir: Path) -> str:
    if os.name == "nt":
        return str(venv_dir / "Scripts" / "python.exe")
    return str(venv_dir / "bin" / "python")


def _venv_script(venv_dir: Path, name: str) -> str:
    if os.name == "nt":
        return str(venv_dir / "Scripts" / f"{name}.exe")
    return str(venv_dir / "bin" / name)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _portable_path(path: Path) -> str:
    return path.as_posix()


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
