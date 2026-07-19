#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_assessment_wiring import assess_phase2_wiring


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Nesira Phase 2 assessment engine in read-only mode and "
            "emit the raw assessment artifact."
        )
    )
    parser.add_argument("request", type=Path, help="Path to a JSON assessment request.")
    parser.add_argument("--output", type=Path, help="Optional path for the same canonical JSON artifact.")
    args = parser.parse_args(argv)

    try:
        request = _read_request(args.request)
        artifact = assess_phase2_wiring(request)
        _assert_read_only_artifact(artifact)
        text = canonical_json(artifact) + "\n"
        sys.stdout.write(text)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8", newline="\n")
        return 0
    except ToolInputError as exc:
        sys.stderr.write(canonical_json({"error": str(exc), "schema": "NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1"}) + "\n")
        return 2
    except Exception:
        sys.stderr.write(
            canonical_json(
                {
                    "error": "read-only assessment tool failed without exposing internal paths",
                    "schema": "NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1",
                }
            )
            + "\n"
        )
        return 1


class ToolInputError(ValueError):
    pass


def _read_request(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ToolInputError("request file could not be read") from exc
    except json.JSONDecodeError as exc:
        raise ToolInputError("request file is not valid JSON") from exc
    if not isinstance(data, dict):
        raise ToolInputError("request JSON must be an object")
    return _decode_json_request(data)


def _decode_json_request(value: Any) -> Any:
    if isinstance(value, dict):
        if set(value) == {"__spira_bytes_b64"}:
            encoded = value["__spira_bytes_b64"]
            if not isinstance(encoded, str):
                raise ToolInputError("base64 bytes wrapper must contain a string")
            try:
                return base64.b64decode(encoded.encode("ascii"), validate=True)
            except (binascii.Error, UnicodeEncodeError) as exc:
                raise ToolInputError("base64 bytes wrapper is malformed") from exc
        decoded = {str(key): _decode_json_request(item) for key, item in value.items()}
        if "now_utc" in decoded:
            decoded["now_utc"] = _parse_now(decoded["now_utc"])
        return decoded
    if isinstance(value, list):
        return [_decode_json_request(item) for item in value]
    return value


def _parse_now(value: Any) -> datetime | Any:
    if not isinstance(value, str):
        return value
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return value


def _assert_read_only_artifact(value: Any) -> None:
    if _contains_forbidden_key(value):
        raise ToolInputError("assessment artifact contains a forbidden action-like field")


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key) in FORBIDDEN_OUTPUT_KEYS:
                return True
            if _contains_forbidden_key(item):
                return True
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
