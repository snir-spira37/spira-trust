#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spira_core.nesira_phase2_dry_run_runner import evaluate_dry_run


FORBIDDEN_EXECUTABLE_KEYS = {
    "apply",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "cwd",
    "environment_variables",
    "execute",
    "network_targets",
    "powershell",
    "python -m",
    "remediate",
    "runbook",
    "script",
    "sever",
    "shell",
    "subprocess_args",
    "write_paths",
}


class ToolInputError(ValueError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the internal Nesira Phase 2 dry-run evaluator and emit a non-executing artifact."
    )
    parser.add_argument("request", type=Path, help="Path to a JSON dry-run request.")
    parser.add_argument("--output", type=Path, help="Optional path for the same JSON artifact.")
    args = parser.parse_args(argv)

    try:
        request = _read_request(args.request)
        artifact = evaluate_dry_run(
            request.get("expected_context"),
            request.get("combined_verdict"),
            request.get("nesira_assessment"),
            request.get("action_authority_result"),
        )
        _assert_exposure_boundary(artifact)
        text = _canonical_json(artifact) + "\n"
        sys.stdout.write(text)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8", newline="\n")
        return 0
    except ToolInputError as exc:
        sys.stderr.write(
            _canonical_json(
                {
                    "schema": "NESIRA_PHASE2_DRY_RUN_REVIEW_TOOL_ERROR_V1",
                    "error": str(exc),
                }
            )
            + "\n"
        )
        return 2
    except Exception:
        sys.stderr.write(
            _canonical_json(
                {
                    "schema": "NESIRA_PHASE2_DRY_RUN_REVIEW_TOOL_ERROR_V1",
                    "error": "dry-run review tool failed without exposing internal paths",
                }
            )
            + "\n"
        )
        return 1


def _read_request(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ToolInputError("request file could not be read") from exc
    except json.JSONDecodeError as exc:
        raise ToolInputError("request file is not valid JSON") from exc
    if not isinstance(data, dict):
        raise ToolInputError("request JSON must be an object")
    return data


def _assert_exposure_boundary(value: Any) -> None:
    if _contains_forbidden_key(value):
        raise ToolInputError("dry-run artifact contains a forbidden executable field")
    markers = value.get("markers") if isinstance(value, dict) else None
    if not isinstance(markers, list) or "ACTION_NOT_PERFORMED" not in markers:
        raise ToolInputError("dry-run artifact did not carry ACTION_NOT_PERFORMED")


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).lower() in FORBIDDEN_EXECUTABLE_KEYS:
                return True
            if _contains_forbidden_key(item):
                return True
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


if __name__ == "__main__":
    raise SystemExit(main())
