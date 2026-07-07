from __future__ import annotations

import math
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .bridge import SpiraBridge, SpiraBridgeConfig, VesselIntent


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
        return str(value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return str(value)

from .schemas import (
    AnomalyRequest,
    AnomalyResponse,
    DecideRequest,
    DecideResponse,
    HealthResponse,
    IntentRequest,
    IntentResponse,
    OrchestrateRequest,
    OrchestrateResponse,
    SessionCreateRequest,
    SessionResponse,
    StateResponse,
)


def create_app(config: Optional[SpiraBridgeConfig] = None) -> FastAPI:
    bridge = SpiraBridge(config=config)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.spira_bridge = bridge
        try:
            yield
        finally:
            bridge.close()

    app = FastAPI(title="Spira Production API", version="production-final", lifespan=lifespan)
    app.state.spira_bridge = bridge

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": _json_safe(exc.errors())})

    @app.get("/api/v1/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            coherence=bridge.peek_coherence(),
            active_sessions=bridge.get_active_session_count(),
        )

    @app.post("/api/v1/sessions", response_model=SessionResponse)
    def create_session(req: SessionCreateRequest) -> SessionResponse:
        session_id = req.session_id or str(uuid.uuid4())
        try:
            s = bridge.create_session(session_id, req.context)
        except ValueError as e:
            raise HTTPException(status_code=409, detail=str(e))
        return SessionResponse(
            session_id=s.session_id,
            created_at=s.created_at,
            last_activity=s.last_activity,
            context=s.context,
        )

    @app.get("/api/v1/sessions")
    def list_sessions() -> dict:
        return {"sessions": bridge.list_sessions()}

    @app.get("/api/v1/sessions/{session_id}/state", response_model=StateResponse)
    def get_state(session_id: str) -> StateResponse:
        try:
            state = bridge.get_vessel_state(session_id=session_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return StateResponse(**state)

    @app.post("/api/v1/sessions/{session_id}/decide", response_model=DecideResponse)
    def decide(session_id: str, req: DecideRequest) -> DecideResponse:
        try:
            decision = bridge.decide(
                req.context,
                req.options,
                session_id=session_id,
                actions=req.actions,
                metrics=req.metrics,
            )
            coherence = bridge.get_coherence(session_id=session_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return DecideResponse(decision=decision, coherence=coherence)

    @app.post("/api/v1/sessions/{session_id}/intent", response_model=IntentResponse)
    def intent(session_id: str, req: IntentRequest) -> IntentResponse:
        if not bridge.session_exists(session_id):
            raise HTTPException(status_code=404, detail=f"unknown session: {session_id}")
        try:
            intent_enum = VesselIntent(req.intent)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"invalid intent: {req.intent}")
        try:
            coherence = bridge.execute_intent(intent_enum, context=req.context, session_id=session_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return IntentResponse(coherence=coherence)

    @app.post("/api/v1/sessions/{session_id}/orchestrate", response_model=OrchestrateResponse)
    def orchestrate(session_id: str, req: OrchestrateRequest) -> OrchestrateResponse:
        try:
            action = bridge.orchestrate(req.current_state, req.available_actions, session_id=session_id)
            coherence = bridge.get_coherence(session_id=session_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        return OrchestrateResponse(action=action, coherence=coherence)

    @app.post("/api/v1/anomaly", response_model=AnomalyResponse)
    def anomaly(req: AnomalyRequest) -> AnomalyResponse:
        result = bridge.detect_anomaly(req.metrics)
        return AnomalyResponse(**result)

    @app.get("/api/v1/stats")
    def stats() -> dict:
        return bridge.get_stats()

    @app.delete("/api/v1/sessions/{session_id}")
    def close_session(session_id: str) -> dict:
        closed = bridge.close_session(session_id)
        if not closed:
            raise HTTPException(status_code=404, detail=f"unknown session: {session_id}")
        return {"ok": True, "session_id": session_id, "closed_at": time.time()}

    return app
