from __future__ import annotations

import base64
import json
import zipfile
from hashlib import sha256
from pathlib import Path

import pytest

from spira_core.agent_status import build_agent_artifact_status, build_agent_status
from spira_core.combined_verdict import agent_default_decision
from spira_core.trust_graph import run_trust_graph


@pytest.mark.parametrize(
    ("verdict", "not_evaluated", "expected_stop", "expected_action"),
    [
        ("GRAPH_BLOCK", [], True, "STOP_BLOCKED"),
        ("GRAPH_WARN", [], True, "ASK_HUMAN"),
        ("GRAPH_OK_WITH_UNVERIFIED", [], True, "REPORT_NOT_EVALUATED"),
        ("GRAPH_OK", ["license_policy"], True, "REPORT_NOT_EVALUATED"),
        ("GRAPH_OK", [], False, "PROCEED"),
        ("GRAPH_OK_WITH_NOTES", [], False, "REPORT_WITH_NOTES"),
        ("GRAPH_UNKNOWN", [], True, "RERUN_REQUIRED"),
    ],
)
def test_agent_action_matrix_is_closed_and_stop_consistent(verdict, not_evaluated, expected_stop, expected_action):
    decision = agent_default_decision(verdict, not_evaluated_layers=not_evaluated)

    assert decision["stop"] is expected_stop
    assert decision["recommended_agent_action"] == expected_action
    if decision["stop"] is False:
        assert decision["recommended_agent_action"] in {"PROCEED", "REPORT_WITH_NOTES"}


@pytest.mark.parametrize("strict_closure", [False, True], ids=["lenient", "strict"])
def test_attestation_not_supplied_stays_not_evaluated_not_warn_or_block(tmp_path, strict_closure):
    wheel = _build_wheel(tmp_path, "clean_pkg", "1.0.0")
    result = run_trust_graph([wheel], tmp_path / "out", strict_closure=strict_closure)

    assert result["verdict"] == "GRAPH_OK"
    assert result["pep740_offline_attestations"]["status"] == "ATTESTATION_NOT_EVALUATED"
    layer = _layer(result, "pep740_offline_attestations")
    assert layer["status"] == "NOT_EVALUATED"


def test_digest_mismatch_blocks_combined_verdict_without_trust_root(tmp_path):
    wheel = _build_wheel(tmp_path, "attested_pkg", "1.0.0")
    attestations = _write_attestations(tmp_path, wheel, sha_value="0" * 64)

    result = run_trust_graph([wheel], tmp_path / "out", attestation_path=attestations)

    assert result["verdict"] == "GRAPH_BLOCK"
    assert result["pep740_offline_attestations"]["status"] == "ATTESTATION_DIGEST_MISMATCH"
    assert result["combined_policy_verdict"]["combined_verdict"] == "GRAPH_BLOCK"
    assert _layer(result, "pep740_offline_attestations")["status"] == "BLOCK"


@pytest.mark.parametrize("strict_closure", [False, True], ids=["lenient", "strict"])
def test_digest_match_without_trust_root_stays_identity_not_evaluated_not_ok_or_block(tmp_path, strict_closure):
    wheel = _build_wheel(tmp_path, "attested_pkg", "1.0.0")
    attestations = _write_attestations(tmp_path, wheel, sha_value=sha256(wheel.read_bytes()).hexdigest())

    result = run_trust_graph(
        [wheel],
        tmp_path / "out",
        strict_closure=strict_closure,
        attestation_path=attestations,
    )

    assert result["verdict"] == "GRAPH_OK"
    assert result["pep740_offline_attestations"]["status"] == "ATTESTATION_UNVERIFIED"
    finding_statuses = {
        item.get("status")
        for item in result["pep740_offline_attestations"].get("findings", [])
    }
    assert finding_statuses == {"ATTESTATION_IDENTITY_NOT_EVALUATED"}
    layer = _layer(result, "pep740_offline_attestations")
    assert layer["status"] == "NOTE"
    assert result["combined_policy_verdict"]["combined_verdict"] == "GRAPH_OK_WITH_NOTES"


@pytest.mark.parametrize("strict_closure", [False, True], ids=["lenient", "strict"])
@pytest.mark.parametrize("with_trust_root", [False, True], ids=["no_trust_root", "trust_root"])
@pytest.mark.parametrize("kind", ["digest_mismatch", "sbom_contradiction", "record_mismatch"])
def test_contradiction_matrix_blocks_for_trust_root_and_strict_modes(
    tmp_path,
    kind,
    strict_closure,
    with_trust_root,
):
    case_dir = tmp_path / f"{kind}_{strict_closure}_{with_trust_root}"
    case_dir.mkdir()
    wheel = _build_case_wheel(case_dir, kind)
    kwargs = _trust_kwargs(case_dir, wheel, kind=kind, with_trust_root=with_trust_root)
    result = run_trust_graph([wheel], case_dir / "out", strict_closure=strict_closure, **kwargs)

    assert result["verdict"] == "GRAPH_BLOCK", (kind, strict_closure, with_trust_root, result)
    assert result["combined_policy_verdict"]["combined_verdict"] == "GRAPH_BLOCK"
    assert result["combined_policy_verdict"]["winning_status"] == "BLOCK"


def test_graph_writes_agent_summary_and_status_rehashes_artifact(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    wheelhouse = tmp_path / "dist"
    wheelhouse.mkdir()
    wheel = _build_wheel(wheelhouse, "summary_pkg", "1.0.0")
    out = tmp_path / "out"

    result = run_trust_graph([wheelhouse], out)
    from spira_core.decision_report import finalize_graph_outputs_for_decision, write_decision_report
    from spira_core.agent_summary import write_agent_summary

    finalize_graph_outputs_for_decision(result, output_dir=out)
    decision = write_decision_report(result, exit_code=0, output_dir=out)
    summary = write_agent_summary(result, decision, output_dir=out)

    summary_path = out / "agent_summary.json"
    assert summary_path.exists()
    assert summary["schema"] == "SPIRA_AGENT_SUMMARY_V1"
    assert summary["created_at"]
    assert "not_evaluated" in summary
    assert summary["decision_semantics_version"] == "SPIRA_DECISION_SEMANTICS_V2"
    assert summary["agent_action_contract"]["schema"] == "SPIRA_AGENT_ACTION_V1"
    assert summary["agent_action_contract"]["decision_semantics_version"] == "SPIRA_DECISION_SEMANTICS_V2"
    assert summary["agent_action_contract"]["artifact_sha256"] == sha256(wheel.read_bytes()).hexdigest()
    assert summary["agent_action_contract"]["artifact_set_sha256"] == summary["summary_of"]["artifact_set_sha256"]
    assert summary["agent_action_contract"]["policy_sha256"] is None
    assert summary["agent_action_contract"]["recommended_agent_action"] == summary["recommended_agent_action"]
    assert summary["agent_action_contract"]["stop"] == summary["stop"]
    assert summary["reason_codes"] == ["REPORT_NOT_EVALUATED"]
    assert summary["agent_action_contract"]["reason_codes"] == ["REPORT_NOT_EVALUATED"]
    assert summary["approval"]["approval_source"] == "unverified"
    assert summary["summary_of"]["command_fingerprint"] == result["command_fingerprint"]
    assert summary_path.stat().st_size < 3 * 1024

    status = build_agent_status([wheelhouse])
    assert status["counts"]["checked"] == 1
    assert status["counts"]["unchecked"] == 0

    artifact_status = build_agent_artifact_status(wheel)
    assert artifact_status["schema"] == "SPIRA_AGENT_ARTIFACT_STATUS_V1"
    assert artifact_status["checked"] is True
    assert artifact_status["stale"] is False
    assert artifact_status["changed_since_check"] is False
    assert artifact_status["artifact_sha256"] == sha256(wheel.read_bytes()).hexdigest()
    assert artifact_status["decision_semantics_version"] == "SPIRA_DECISION_SEMANTICS_V2"
    assert artifact_status["stop"] is True
    assert artifact_status["recommended_agent_action"] == "REPORT_NOT_EVALUATED"
    assert artifact_status["reason_codes"] == ["REPORT_NOT_EVALUATED"]
    assert artifact_status["summary_path"]
    assert len(json.dumps(artifact_status, separators=(",", ":"))) < 1024

    from spira_core.trust_cli import main

    assert main(["status", "--agent", "--artifact", str(wheel), "--format", "json"]) == 0
    cli_status = json.loads(capsys.readouterr().out)
    assert cli_status["schema"] == "SPIRA_AGENT_ARTIFACT_STATUS_V1"
    assert cli_status["checked"] is True
    assert cli_status["recommended_agent_action"] == "REPORT_NOT_EVALUATED"
    assert len(json.dumps(cli_status, separators=(",", ":"))) < 1024

    _replace_wheel_payload(wheel, "summary_pkg", "1.0.0", b"changed")
    changed_status = build_agent_status([wheelhouse])
    assert changed_status["counts"]["checked"] == 0
    assert changed_status["counts"]["changed_since_check"] == 1

    changed_artifact_status = build_agent_artifact_status(wheel)
    assert changed_artifact_status["checked"] is False
    assert changed_artifact_status["stale"] is True
    assert changed_artifact_status["changed_since_check"] is True
    assert changed_artifact_status["recommended_agent_action"] == "RERUN_REQUIRED"
    assert changed_artifact_status["reason_codes"] == ["ARTIFACT_CHANGED_SINCE_CHECK"]

    assert main(["status", "--agent", "--artifact", str(wheel), "--format", "json"]) == 2
    changed_cli_status = json.loads(capsys.readouterr().out)
    assert changed_cli_status["changed_since_check"] is True
    assert changed_cli_status["recommended_agent_action"] == "RERUN_REQUIRED"


def test_agent_action_uses_combined_verdict_not_raw_graph_verdict(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    decision_path = out / "spira-decision.json"
    report_path = out / "graph_report.json"
    bom_path = out / "bill_of_materials.json"
    decision_path.write_text("{}\n", encoding="utf-8")
    report_path.write_text("{}\n", encoding="utf-8")
    bom_path.write_text("{}\n", encoding="utf-8")

    graph_result = {
        "verdict": "GRAPH_OK",
        "report_path": str(report_path),
        "bill_of_materials_path": str(bom_path),
        "nodes": [],
        "propagation_events": [],
    }
    decision = {
        "decision_json_path": str(decision_path),
        "decision": {
            "verdict": "GRAPH_OK",
            "combined_verdict": "GRAPH_OK_WITH_NOTES",
            "winning_status": "NOTE",
            "exit_code": 0,
        },
        "layers": {
            "not_evaluated_layers": [],
        },
    }

    from spira_core.agent_summary import build_agent_summary

    summary = build_agent_summary(graph_result, decision, output_dir=out)

    assert summary["verdict"] == "GRAPH_OK"
    assert summary["combined_verdict"] == "GRAPH_OK_WITH_NOTES"
    assert summary["action_verdict"] == "GRAPH_OK_WITH_NOTES"
    assert summary["stop"] is False
    assert summary["recommended_agent_action"] == "REPORT_WITH_NOTES"
    assert summary["reason_codes"] == ["NOTES_PRESENT", "REPORT_WITH_NOTES"]
    assert summary["agent_action_contract"]["action_verdict"] == "GRAPH_OK_WITH_NOTES"


def _layer(result: dict, name: str) -> dict:
    for layer in result["combined_policy_verdict"]["per_layer"]:
        if layer["layer"] == name:
            return layer
    raise AssertionError(f"missing layer {name}")


def _build_case_wheel(case_dir: Path, kind: str) -> Path:
    if kind == "sbom_contradiction":
        return _build_wheel(case_dir, "sbom_pkg", "1.0.0", sbom_name="different-name")
    if kind == "record_mismatch":
        wheel = _build_wheel(case_dir, "record_pkg", "1.0.0")
        _replace_wheel_payload(wheel, "record_pkg", "1.0.0", b"tampered")
        return wheel
    return _build_wheel(case_dir, "attested_pkg", "1.0.0")


def _trust_kwargs(case_dir: Path, wheel: Path, *, kind: str, with_trust_root: bool) -> dict:
    kwargs = {}
    if kind == "sbom_contradiction":
        kwargs["verify_embedded_sboms"] = True
    if kind == "digest_mismatch":
        kwargs["attestation_path"] = _write_attestations(case_dir, wheel, sha_value="0" * 64)
    elif with_trust_root:
        kwargs["attestation_path"] = _write_attestations(case_dir, wheel, sha_value=sha256(wheel.read_bytes()).hexdigest())
    if with_trust_root:
        trust_root = case_dir / "trust_root.json"
        trust_root.write_text(json.dumps({"allowed_identities": ["builder@example.com"]}) + "\n", encoding="utf-8")
        kwargs["attestation_trust_root_path"] = trust_root
        kwargs["attestation_trust_root_sha256"] = sha256(trust_root.read_bytes()).hexdigest()
    return kwargs


def _write_attestations(case_dir: Path, wheel: Path, *, sha_value: str) -> Path:
    path = case_dir / "attestations.json"
    path.write_text(
        json.dumps(
            {
                "attestations": [
                    {
                        "filename": wheel.name,
                        "sha256": sha_value,
                        "identity": "builder@example.com",
                        "index_verified": True,
                    }
                ]
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _build_wheel(base: Path, name: str, version: str, *, sbom_name: str | None = None) -> Path:
    package_dir = name
    dist_info = f"{name}-{version}.dist-info"
    files: dict[str, bytes] = {
        f"{package_dir}/__init__.py": b"VALUE = 1\n",
        f"{dist_info}/METADATA": f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n".encode("utf-8"),
        f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    }
    if sbom_name:
        files[f"{dist_info}/sboms/{name}.cdx.json"] = json.dumps(
            {
                "bomFormat": "CycloneDX",
                "metadata": {"component": {"name": sbom_name, "version": version, "purl": f"pkg:pypi/{sbom_name}@{version}"}},
            }
        ).encode("utf-8")
    record_path = f"{dist_info}/RECORD"
    record_lines = []
    for path, data in sorted(files.items()):
        record_lines.append(f"{path},sha256={_b64_sha(data)},{len(data)}")
    record_lines.append(f"{record_path},,")
    files[record_path] = ("\n".join(record_lines) + "\n").encode("utf-8")
    wheel = base / f"{name}-{version}-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(files.items()):
            archive.writestr(path, data)
    return wheel


def _replace_wheel_payload(wheel: Path, name: str, version: str, payload: bytes) -> None:
    dist_info = f"{name}-{version}.dist-info"
    with zipfile.ZipFile(wheel, "r") as archive:
        entries = {info.filename: archive.read(info.filename) for info in archive.infolist() if not info.is_dir()}
    entries[f"{name}/__init__.py"] = payload
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(entries.items()):
            archive.writestr(path, data)
    assert f"{dist_info}/RECORD" in entries


def _b64_sha(data: bytes) -> str:
    return base64.urlsafe_b64encode(sha256(data).digest()).decode("ascii").rstrip("=")
