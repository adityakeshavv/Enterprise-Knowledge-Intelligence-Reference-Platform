import asyncio
import json
import time
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, Query as QueryParam
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, AuditLog
from app.core.rbac import get_current_user
from app.core.config_loader import config_loader
from app.schemas.query import QueryRequest, QueryResponse
from app.orchestration.orchestrator import multi_agent_orchestrator

router = APIRouter(prefix="/query", tags=["Query & Intelligence"])

@router.post("", response_model=QueryResponse)
def execute_query(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes a multi-agent knowledge query and writes an immutable audit log."""
    start_time = time.time()
    active_industry = payload.industry_id or config_loader.active_industry_id
    user_role = current_user.role if current_user else "CXO"
    department = getattr(current_user, "department", None)

    # Execute end-to-end multi-agent orchestration
    response = multi_agent_orchestrator.orchestrate(
        query_text=payload.query,
        user_role=user_role,
        industry_id=active_industry,
        department=department
    )

    total_latency_ms = (time.time() - start_time) * 1000.0
    response.total_latency_ms = round(total_latency_ms, 1)

    # Write write-ahead audit log (PRD Section 7.4)
    invoked_agents = ", ".join([step.agent_label for step in response.trace_steps])
    audit = AuditLog(
        user_id=current_user.id if current_user else None,
        username=current_user.username if current_user else "anonymous",
        role=user_role,
        industry_id=active_industry,
        query_text=payload.query,
        status="SUCCESS",
        execution_time_ms=total_latency_ms,
        agents_invoked=invoked_agents
    )
    db.add(audit)
    db.commit()

    return response

@router.get("/stream")
async def stream_query_trace(
    query: str = QueryParam(...),
    industry: str = QueryParam(default="manufacturing")
):
    """Server-Sent Events (SSE) endpoint streaming live agent execution steps and response."""
    async def event_generator() -> AsyncGenerator[str, None]:
        async for item in multi_agent_orchestrator.stream_orchestration(
            query_text=query,
            industry_id=industry
        ):
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
