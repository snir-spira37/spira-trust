from __future__ import annotations

import zipfile

from spira_core import review


def test_review_fails_closed_when_post_extraction_manifest_fails(tmp_path, monkeypatch):
    wheel = _build_minimal_wheel(tmp_path)

    def raise_os_error(_root):
        raise OSError("simulated inaccessible extracted file")

    monkeypatch.setattr(review, "build_manifest", raise_os_error)

    report = review.review_artifact(wheel, tmp_path / "out", package=False)

    assert report["overall_verdict"] == "CONTRADICTION_FOUND"
    assert report["manifest"]["verdict"] == "ARTIFACT_EXTRACTION_BLOCKED"
    assert report["manifest"]["error_type"] == "OSError"
    assert report["claims"][0]["gap_type"] == "artifact_extraction_blocked"
    assert "traceback" not in report["manifest"]["error"].lower()


def _build_minimal_wheel(tmp_path):
    wheel = tmp_path / "sample-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sample/__init__.py", b"VALUE = 1\n")
        archive.writestr(
            "sample-1.0.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: sample\nVersion: 1.0.0\n",
        )
        archive.writestr(
            "sample-1.0.0.dist-info/WHEEL",
            "Wheel-Version: 1.0\nGenerator: test\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        archive.writestr("sample-1.0.0.dist-info/RECORD", "sample/__init__.py,,\n")
    return wheel
