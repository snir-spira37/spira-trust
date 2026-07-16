from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_deepseek_ds_r0 as dsr0  # noqa: E402


def test_secret_redaction_path_sanitizes_user_path():
    synthetic_user_path = "C:" + "\\Users\\example\\Desktop\\secret.txt"
    sanitized = dsr0.sanitize_path(synthetic_user_path)

    assert sanitized == "REDACTED_PATH/secret.txt"
    assert "example" not in sanitized


def test_recursive_usage_extraction_and_total_input_calculation():
    payload = {
        "outer": {
            "usage": {
                "input_tokens": 10,
                "cache_creation_input_tokens": 2,
                "cache_read_input_tokens": 3,
                "output_tokens": 4,
            }
        }
    }

    usage = dsr0.extract_usage(payload)

    assert usage["total_input_tokens"] == 15
    assert usage["output_tokens"] == 4
    assert usage["cache_decomposition_status"] == "AVAILABLE"


def test_missing_cache_classification_does_not_invent_components():
    usage = dsr0.extract_usage({"usage": {"input_tokens": 7, "output_tokens": 2}})

    assert usage["total_input_tokens"] == 7
    assert usage["cache_creation_input_tokens"] is None
    assert usage["cache_read_input_tokens"] is None
    assert usage["cache_decomposition_status"] == "NOT_EVALUATED"


def test_session_id_uniqueness_summary():
    result = dsr0.session_isolation_summary(
        {"session_id": "a", "nonce_present": True},
        {"session_id": "b", "nonce_present": True},
    )

    assert result["ready"] is True
    assert result["errors"] == []


def test_forbidden_tool_detection():
    forbidden = dsr0.forbidden_tools_present(["Read", "Bash", "mcp__server__tool", "Grep"])

    assert forbidden == {"Bash", "mcp__server__tool"}


def test_model_resolution_rejects_flash_and_old_bracketed_identity():
    assert dsr0.model_resolution_status("deepseek-v4-flash") == "DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED"
    assert dsr0.model_resolution_status("deepseek-v4-pro[1m]") == "DEEPSEEK_REQUESTED_MODEL_NOT_CONFIRMED"
    assert dsr0.model_resolution_status("deepseek-v4-pro") == "DEEPSEEK_V4_PRO_MODEL_RESOLUTION_CONFIRMED"


def test_workspace_digest_detects_mutation(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    before = dsr0.directory_digest(tmp_path)
    (tmp_path / "a.txt").write_text("b", encoding="utf-8")
    after = dsr0.directory_digest(tmp_path)

    assert before != after


def test_raw_private_manifest_omits_path(tmp_path):
    manifest = []
    raw_id = dsr0.record_private_raw(
        tmp_path,
        manifest,
        name="response.json",
        data=json.dumps({"ok": True}).encode("utf-8"),
        classification="TEST",
    )

    assert raw_id
    assert manifest[0]["stored_outside_repository"] is True
    assert manifest[0]["public_path_recorded"] is False
    assert "path" not in manifest[0]


def test_canonical_json_is_deterministic_and_compact():
    left = {"b": 2, "a": {"z": 3, "c": 1}}
    right = {"a": {"c": 1, "z": 3}, "b": 2}

    assert dsr0.canonical_json(left) == dsr0.canonical_json(right)
    assert dsr0.canonical_json(left) == '{"a":{"c":1,"z":3},"b":2}'
