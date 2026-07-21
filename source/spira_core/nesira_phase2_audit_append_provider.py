from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping


PROVIDER_CLASS = "DECLARED_AUDIT_APPEND_CAPABILITY_PROVIDER"
ACTION_CLASS = "AUDIT_RECORD_APPEND_ONLY"
EFFECT_SHAPE = "APPEND_ONE_BOUNDED_RECORD"

APPEND_APPLIED = "APPEND_APPLIED"
APPEND_STATUS_UNKNOWN = "APPEND_STATUS_UNKNOWN"
APPEND_NOT_AUTHORIZED = "APPEND_NOT_AUTHORIZED"

CAPABILITY_PROVIDER_ASSUMPTION_FLOOR = (
    "CAP-PROVIDER-01",
    "CAP-PROVIDER-02",
    "CAP-PROVIDER-03",
    "CAP-SINK-01",
    "CAP-SINK-02",
    "CAP-IDEMPOTENCY-01",
    "CAP-IDEMPOTENCY-02",
    "CAP-STATUS-01",
    "CAP-TCB-01",
)

RUNNER_FACING_KEYS = {
    "append_one",
    "append_capability_ref",
    "append_capability_root_digest",
    "audit_sink_root_ref",
    "provider_contract_version",
}

FORBIDDEN_PAYLOAD_KEYS = {
    "absolute_path",
    "bash",
    "command",
    "command_line",
    "copy_paste_steps",
    "network_target",
    "network_targets",
    "path",
    "powershell",
    "python -m",
    "runbook",
    "script",
    "secret",
    "sink_path",
    "subprocess_args",
    "token",
    "write_paths",
}


def canonical_descriptor(sink_binding: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "provider_id": _string(sink_binding.get("provider_id")),
        "provider_contract_version": _string(sink_binding.get("provider_contract_version")),
        "audit_sink_root_id": _string(sink_binding.get("audit_sink_root_id")),
        "audit_sink_root_version": _string(sink_binding.get("audit_sink_root_version")),
        "sink_binding_digest": _string(sink_binding.get("sink_binding_digest")),
        "append_only_policy_id": _string(sink_binding.get("append_only_policy_id")),
        "append_only_policy_digest": _string(sink_binding.get("append_only_policy_digest")),
        "idempotency_namespace": _string(sink_binding.get("idempotency_namespace")),
        "record_schema_id": _string(sink_binding.get("record_schema_id")),
        "record_schema_version": _string(sink_binding.get("record_schema_version")),
        "max_record_size": _int_or_zero(sink_binding.get("max_record_size")),
        "authorized_action_class": ACTION_CLASS,
        "effect_shape": EFFECT_SHAPE,
        "effect_count": 1,
        "total_effect_count": 1,
        "retry_count": 0,
        "supporting_effects": "none",
        "network_allowed": False,
        "arbitrary_path_allowed": False,
    }


def descriptor_digest(descriptor: Mapping[str, Any]) -> str:
    payload = json.dumps(descriptor, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_declared_audit_append_capability(sink_binding: Mapping[str, Any]) -> dict[str, Any]:
    descriptor = canonical_descriptor(sink_binding if isinstance(sink_binding, Mapping) else {})
    capability_digest = descriptor_digest(descriptor)
    sink_target = _string(sink_binding.get("_private_sink_target")) if isinstance(sink_binding, Mapping) else ""
    binding_ok = _sink_binding_ok(sink_binding, descriptor)
    seen_idempotency_keys: set[str] = set()

    def append_one(record_payload: Any, idempotency_key: str) -> dict[str, Any]:
        if not binding_ok or not sink_target:
            return _response(APPEND_NOT_AUTHORIZED)
        if not _payload_allowed(record_payload, descriptor, idempotency_key):
            return _response(APPEND_NOT_AUTHORIZED)
        if idempotency_key in seen_idempotency_keys:
            return _response(APPEND_NOT_AUTHORIZED)
        line = _record_line(record_payload)
        max_size = _int_or_zero(descriptor.get("max_record_size"))
        if max_size <= 0 or len(line.encode("utf-8")) > max_size:
            return _response(APPEND_NOT_AUTHORIZED)
        try:
            with open(sink_target, "a", encoding="utf-8", newline="\n") as sink:
                sink.write(line)
        except Exception:
            return _response(APPEND_STATUS_UNKNOWN)
        seen_idempotency_keys.add(idempotency_key)
        return _response(APPEND_APPLIED)

    return {
        "append_one": append_one,
        "append_capability_ref": _string(sink_binding.get("append_capability_ref")) if isinstance(sink_binding, Mapping) else "",
        "append_capability_root_digest": capability_digest,
        "audit_sink_root_ref": _audit_sink_root_ref(descriptor),
        "provider_contract_version": _string(descriptor.get("provider_contract_version")),
    }


def _sink_binding_ok(sink_binding: Mapping[str, Any] | Any, descriptor: Mapping[str, Any]) -> bool:
    if not isinstance(sink_binding, Mapping):
        return False
    if sink_binding.get("declared_sink_binding") is not True:
        return False
    if _string(sink_binding.get("provider_class")) != PROVIDER_CLASS:
        return False
    if _string(sink_binding.get("authorized_action_class")) != ACTION_CLASS:
        return False
    if _string(sink_binding.get("effect_shape")) != EFFECT_SHAPE:
        return False
    if sink_binding.get("effect_count") != 1 or sink_binding.get("total_effect_count") != 1:
        return False
    if sink_binding.get("retry_count") != 0:
        return False
    if sink_binding.get("supporting_effects") not in (None, [], "none"):
        return False
    required = (
        "provider_id",
        "provider_contract_version",
        "audit_sink_root_id",
        "audit_sink_root_version",
        "sink_binding_digest",
        "append_only_policy_id",
        "append_only_policy_digest",
        "idempotency_namespace",
        "record_schema_id",
        "record_schema_version",
        "append_capability_ref",
        "_private_sink_target",
    )
    if any(not _string(sink_binding.get(key)) for key in required):
        return False
    return _int_or_zero(descriptor.get("max_record_size")) > 0


def _payload_allowed(record_payload: Any, descriptor: Mapping[str, Any], idempotency_key: str) -> bool:
    if not isinstance(record_payload, Mapping):
        return False
    if _contains_key(record_payload, FORBIDDEN_PAYLOAD_KEYS):
        return False
    if _string(record_payload.get("schema_id")) != _string(descriptor.get("record_schema_id")):
        return False
    if _string(record_payload.get("schema_version")) != _string(descriptor.get("record_schema_version")):
        return False
    if _string(record_payload.get("action_class")) != ACTION_CLASS:
        return False
    if not idempotency_key or _string(record_payload.get("idempotency_key")) != idempotency_key:
        return False
    return True


def _record_line(record_payload: Mapping[str, Any]) -> str:
    return json.dumps(record_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def _response(status: str) -> dict[str, Any]:
    return {
        "effect_status": status,
        "assumptions": list(CAPABILITY_PROVIDER_ASSUMPTION_FLOOR) if status == APPEND_APPLIED else [],
        "provider_truth_claim": "NOT_PROVEN",
    }


def _audit_sink_root_ref(descriptor: Mapping[str, Any]) -> str:
    root_id = _string(descriptor.get("audit_sink_root_id"))
    version = _string(descriptor.get("audit_sink_root_version"))
    return f"{root_id}@{version}" if root_id and version else ""


def _contains_key(value: Any, forbidden: set[str]) -> bool:
    stack: list[Any] = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, item in current.items():
                if str(key).lower() in forbidden:
                    return True
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _string(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _int_or_zero(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
