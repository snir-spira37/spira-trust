from __future__ import annotations
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def _validate_non_empty_string(value: str, *, field_name: str) -> str:
    trimmed = value.strip()
    if not trimmed:
        raise ValueError(f"{field_name} must not be empty")
    return trimmed

class SessionCreateRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="Optional explicit session identifier")
    context: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return _validate_non_empty_string(value, field_name="session_id")

class SessionResponse(BaseModel):
    session_id: str
    created_at: float
    last_activity: float
    context: Dict[str, Any]

class DecideRequest(BaseModel):
    context: Dict[str, Any] = Field(default_factory=dict)
    actions: List[str] = Field(default_factory=list)
    metrics: Dict[str, float] = Field(default_factory=dict)
    options: Optional[List[str]] = None

    @field_validator("actions")
    @classmethod
    def validate_actions(cls, value: List[str]) -> List[str]:
        if not value:
            return []
        return [_validate_non_empty_string(item, field_name="actions item") for item in value]

    @field_validator("metrics")
    @classmethod
    def validate_decide_metrics(cls, value: Dict[str, float]) -> Dict[str, float]:
        if not value:
            return {}
        cleaned: Dict[str, float] = {}
        for key, metric in value.items():
            metric_key = _validate_non_empty_string(str(key), field_name="metrics key")
            if not math.isfinite(metric):
                raise ValueError(f"metric {metric_key!r} must be finite")
            cleaned[metric_key] = float(metric)
        return cleaned

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        if not value:
            raise ValueError("options must not be empty")
        return [_validate_non_empty_string(item, field_name="options item") for item in value]

class DecideResponse(BaseModel):
    decision: Any
    coherence: float

class IntentRequest(BaseModel):
    intent: str
    context: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("intent")
    @classmethod
    def validate_intent(cls, value: str) -> str:
        return _validate_non_empty_string(value, field_name="intent")

class IntentResponse(BaseModel):
    coherence: float

class AnomalyRequest(BaseModel):
    metrics: Dict[str, float]

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, value: Dict[str, float]) -> Dict[str, float]:
        if not value:
            return value
        cleaned: Dict[str, float] = {}
        for key, metric in value.items():
            metric_key = _validate_non_empty_string(str(key), field_name="metrics key")
            if not math.isfinite(metric):
                raise ValueError(f"metric {metric_key!r} must be finite")
            cleaned[metric_key] = float(metric)
        return cleaned

class AnomalyResponse(BaseModel):
    is_anomaly: bool
    coherence: float
    confidence: float
    suggested_action: str

class OrchestrateRequest(BaseModel):
    current_state: Dict[str, Any] = Field(default_factory=dict)
    available_actions: List[str] = Field(default_factory=list)

    @field_validator("available_actions")
    @classmethod
    def validate_available_actions(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("available_actions must not be empty")
        return [_validate_non_empty_string(item, field_name="available_actions item") for item in value]

class OrchestrateResponse(BaseModel):
    action: str
    coherence: float

class StateResponse(BaseModel):
    or_level: float
    capacity: float
    screen_strength: float
    coherence: float
    noise: float
    shevira: bool

class HealthResponse(BaseModel):
    status: str
    coherence: float
    active_sessions: int

class ErrorResponse(BaseModel):
    detail: str
