from __future__ import annotations
import math
from typing import Any, Dict, Optional

TYPE_MAP: Dict[str, type] = {
    "any": object,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def normalize_type_name(type_name: Optional[str]) -> str:
    if not type_name:
        return "any"
    t = type_name.strip().lower()
    return t if t in TYPE_MAP else "any"


def coerce_value(value: Any, type_name: str) -> Any:
    t = normalize_type_name(type_name)
    if t == "any":
        return value
    if t == "float":
        return float(value)
    if t == "int":
        if isinstance(value, bool):
            raise TypeError("cannot coerce bool to int implicitly")
        return int(value)
    if t == "str":
        return str(value)
    if t == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v in {"true", "1", "yes", "on"}:
                return True
            if v in {"false", "0", "no", "off"}:
                return False
        return bool(value)
    if t == "list":
        if isinstance(value, list):
            return value
        raise TypeError(f"cannot coerce {type(value).__name__} to list")
    if t == "dict":
        if isinstance(value, dict):
            return value
        raise TypeError(f"cannot coerce {type(value).__name__} to dict")
    return value


def assert_type(value: Any, type_name: str, label: str) -> Any:
    t = normalize_type_name(type_name)
    coerced = coerce_value(value, t)
    expected = TYPE_MAP[t]
    if t != "any" and not isinstance(coerced, expected):
        raise TypeError(f"{label} expected {t}, got {type(coerced).__name__}")
    return coerced


def finite_number(value: Any, label: str, *, minimum: Optional[float] = None, clamp_min: Optional[float] = None) -> float:
    x = float(value)
    if math.isnan(x) or math.isinf(x):
        raise ValueError(f"{label} must be finite")
    if minimum is not None and x < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    if clamp_min is not None and x < clamp_min:
        x = clamp_min
    return x


def ensure_json_safe(value: Any, path: str = "root") -> Any:
    """Validate recursively that a value can be JSON-serialized without silent coercion."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [ensure_json_safe(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, tuple):
        return [ensure_json_safe(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise TypeError(f"{path}: JSON object keys must be strings, got {type(k).__name__}")
            out[k] = ensure_json_safe(v, f"{path}.{k}")
        return out
    raise TypeError(f"{path}: value of type {type(value).__name__} is not JSON serializable")



