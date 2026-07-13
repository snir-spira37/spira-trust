from __future__ import annotations

import copy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_multi_agent_benchmark_assets as validator  # noqa: E402


def test_multi_agent_benchmark_assets_validate():
    result = validator.validate_assets()

    assert result["status"] == "MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_PASS", result["errors"]
    assert result["errors"] == []


def test_output_schema_rejects_additional_properties():
    errors: list[str] = []
    schema = validator._read_json(validator.BENCHMARK_ROOT / "agent_output.schema.json", errors)
    schema = copy.deepcopy(schema)
    schema["additionalProperties"] = True

    validator._validate_output_schema(schema, errors)

    assert "OUTPUT_SCHEMA_ALLOWS_ADDITIONAL_PROPERTIES" in errors
