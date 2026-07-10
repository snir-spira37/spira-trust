from __future__ import annotations

import base64
import json
import zipfile
from hashlib import sha256
from pathlib import Path

from spira_core.sbom_consistency import evaluate_embedded_sbom_consistency
from spira_core.trust_graph import run_trust_graph


def test_non_pypi_component_scope_is_not_wheel_contradiction(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "omni-mdx",
        "0.1.9",
        sboms={
            "omni-mdx.cyclonedx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {
                    "component": {
                        "name": "omni-mdx",
                        "version": "0.2.0",
                        "purl": "pkg:cargo/omni-mdx@0.2.0",
                    }
                },
            }
        },
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="omni-mdx", version="0.1.9")

    assert result["status"] == "NO_WHEEL_SCOPED_SBOM"
    assert result["wheel_scoped_sbom_count"] == 0
    assert result["non_wheel_scoped_sbom_count"] == 1
    assert result["results"][0]["status"] == "COMPONENT_SCOPE_NOT_WHEEL"

    graph = run_trust_graph([str(wheel)], verify_embedded_sboms=True, output_dir=str(tmp_path / "out"))
    assert graph["pep770_sbom_consistency"]["status"] == "NO_WHEEL_SCOPED_SBOM"
    assert graph["verdict"] != "GRAPH_BLOCK"


def test_mixed_pypi_and_cargo_sboms_use_wheel_scoped_sbom_for_verdict(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "a3s-box",
        "2.0.0",
        sboms={
            "crate.cyclonedx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {
                    "component": {
                        "name": "a3s-box-python",
                        "version": "0.6.0",
                        "purl": "pkg:cargo/a3s-box-python@0.6.0",
                    }
                },
            },
            "wheel.cdx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {
                    "component": {
                        "name": "a3s-box",
                        "version": "2.0.0",
                        "purl": "pkg:pypi/a3s-box@2.0.0",
                    }
                },
            },
        },
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="a3s-box", version="2.0.0")

    assert result["status"] == "VERIFIED_OK"
    assert result["wheel_scoped_sbom_count"] == 1
    statuses = {item["path"].rsplit("/", 1)[-1]: item["status"] for item in result["results"]}
    assert statuses == {
        "crate.cyclonedx.json": "COMPONENT_SCOPE_NOT_WHEEL",
        "wheel.cdx.json": "VERIFIED_OK",
    }


def test_pypi_scoped_mismatch_is_contradiction(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "demo-pkg",
        "1.0.0",
        sboms={
            "demo.cdx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {"component": {"name": "demo-pkg", "version": "2.0.0", "purl": "pkg:pypi/demo-pkg@2.0.0"}},
            }
        },
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="demo-pkg", version="1.0.0")

    assert result["status"] == "CONTRADICTION"
    assert result["results"][0]["component_scope"] == "PYPI_WHEEL_SCOPED"
    assert "version '2.0.0' does not match wheel version '1.0.0'" in result["results"][0]["findings"][0]


def test_missing_purl_falls_back_to_matching_name(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "demo-pkg",
        "1.0.0",
        sboms={
            "demo.cdx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {"component": {"name": "demo_pkg", "version": "1.0"}},
            }
        },
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="demo-pkg", version="1.0.0")

    assert result["status"] == "VERIFIED_OK"
    assert result["results"][0]["component_scope"] == "PYPI_WHEEL_SCOPED_INFERRED"


def test_missing_purl_and_nonmatching_name_is_unverified_not_contradiction(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "demo-pkg",
        "1.0.0",
        sboms={
            "demo.cdx.json": {
                "bomFormat": "CycloneDX",
                "metadata": {"component": {"name": "inner-crate", "version": "9.0.0"}},
            }
        },
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="demo-pkg", version="1.0.0")

    assert result["status"] == "UNVERIFIED"
    assert result["results"][0]["component_scope"] == "UNKNOWN_COMPONENT_SCOPE"
    assert result["results"][0]["status"] == "UNVERIFIED"


def test_unparseable_json_sbom_is_invalid_not_inconsistent(tmp_path: Path) -> None:
    wheel = _build_wheel(
        tmp_path,
        "demo-pkg",
        "1.0.0",
        sboms={"broken.cdx.json": b"{not json"},
    )

    result = evaluate_embedded_sbom_consistency(str(wheel), package_name="demo-pkg", version="1.0.0")

    assert result["status"] == "INVALID"
    assert result["results"][0]["status"] == "INVALID"

    graph = run_trust_graph([str(wheel)], verify_embedded_sboms=True, output_dir=str(tmp_path / "out"))
    assert graph["pep770_sbom_consistency"]["status"] == "INVALID"
    assert graph["verdict"] == "GRAPH_BLOCK"


def _build_wheel(base: Path, name: str, version: str, *, sboms: dict[str, dict]) -> Path:
    package_dir = name.replace("-", "_")
    dist_info = f"{package_dir}-{version}.dist-info"
    files: dict[str, bytes] = {
        f"{package_dir}/__init__.py": b"VALUE = 1\n",
        f"{dist_info}/METADATA": f"Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n".encode("utf-8"),
        f"{dist_info}/WHEEL": b"Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
    }
    for filename, payload in sboms.items():
        if isinstance(payload, bytes):
            files[f"{dist_info}/sboms/{filename}"] = payload
        else:
            files[f"{dist_info}/sboms/{filename}"] = json.dumps(payload).encode("utf-8")
    record_path = f"{dist_info}/RECORD"
    record_lines = []
    for path, data in sorted(files.items()):
        record_lines.append(f"{path},sha256={_b64_sha(data)},{len(data)}")
    record_lines.append(f"{record_path},,")
    files[record_path] = ("\n".join(record_lines) + "\n").encode("utf-8")
    wheel = base / f"{package_dir}-{version}-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, data in sorted(files.items()):
            archive.writestr(path, data)
    return wheel


def _b64_sha(data: bytes) -> str:
    return base64.urlsafe_b64encode(sha256(data).digest()).decode("ascii").rstrip("=")
