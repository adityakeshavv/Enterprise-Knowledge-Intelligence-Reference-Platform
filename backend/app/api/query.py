import asyncio
import json
import time
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, AuditLog
from app.core.rbac import get_current_user
from app.core.config_loader import config_loader
from app.core.guardrails import security_guardrails
from app.schemas.query import QueryRequest, QueryResponse
from app.orchestration.orchestrator import multi_agent_orchestrator

router = APIRouter(prefix="/query", tags=["Query & Intelligence"])

@router.post("", response_model=QueryResponse)
def execute_query(
    payload: QueryRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes a multi-agent knowledge query and writes an immutable audit log."""
    start_time = time.time()
    active_industry = payload.industry_id or config_loader.active_industry_id
    user_role = current_user.role if current_user else "CXO"
    department = getattr(current_user, "department", None)
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Enterprise Guardrail Inspection (PRD Section 23.1)
    guardrail_res = security_guardrails.evaluate_query(payload.query, user_role=user_role)
    if not guardrail_res.is_safe:
        total_latency_ms = (time.time() - start_time) * 1000.0
        audit = AuditLog(
            audit_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            user_id=current_user.id if current_user else None,
            username=current_user.username if current_user else "anonymous",
            role=user_role,
            industry_id=active_industry,
            query_text=payload.query,
            status="BLOCKED_SECURITY",
            execution_time_ms=round(total_latency_ms, 1),
            agents_invoked="SecurityGuardrail",
            sources_accessed=json.dumps([]),
            citations_count=0,
            grounding_score=0.0,
            conflicts_count=0,
            is_abstained=False,
            ip_address=client_ip,
            trace_stages=json.dumps({"guardrail_ms": round(total_latency_ms, 1)})
        )
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=400,
            detail=f"Enterprise Security Alert: {guardrail_res.violation_details}"
        )

    # 2. Execute end-to-end multi-agent orchestration
    response = multi_agent_orchestrator.orchestrate(
        query_text=guardrail_res.sanitized_query,
        user_role=user_role,
        industry_id=active_industry,
        department=department
    )

    total_latency_ms = (time.time() - start_time) * 1000.0
    response.total_latency_ms = round(total_latency_ms, 1)

    # 3. Write immutable audit event (PRD Section 24.1)
    invoked_agents = ", ".join([step.agent_label for step in response.trace_steps])
    sources_cited = list({c.reference for c in response.citations if getattr(c, "reference", None)})
    is_abstained = bool(response.validation_report and response.validation_report.is_abstained)
    status_str = "ABSTAINED" if is_abstained else "SUCCESS"
    grounding_val = (
        response.validation_report.grounding_score
        if response.validation_report and response.validation_report.grounding_score is not None
        else (response.confidence_score if response.confidence_score else 0.85)
    )

    trace_timing = {
        step.agent_label: getattr(step, "duration_ms", getattr(step, "latency_ms", 0.0))
        for step in response.trace_steps
    }

    audit = AuditLog(
        audit_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
        user_id=current_user.id if current_user else None,
        username=current_user.username if current_user else "anonymous",
        role=user_role,
        industry_id=active_industry,
        query_text=payload.query,
        status=status_str,
        execution_time_ms=total_latency_ms,
        agents_invoked=invoked_agents,
        sources_accessed=json.dumps(sources_cited),
        citations_count=len(response.citations),
        grounding_score=round(grounding_val, 2),
        conflicts_count=len(response.conflicts),
        is_abstained=is_abstained,
        ip_address=client_ip,
        trace_stages=json.dumps(trace_timing)
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
