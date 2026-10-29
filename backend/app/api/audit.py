import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.db.session import get_db
from app.db.models import User, AuditLog
from app.core.rbac import get_current_user, require_roles
from app.schemas.audit import AuditLogItem, AuditLogListResponse, AuditSummaryMetrics

router = APIRouter(prefix="/audit", tags=["Governance & Auditability"])

def _parse_json_list(val: Optional[str]) -> Optional[List[str]]:
    if not val:
        return None
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, list) else [str(parsed)]
    except Exception:
        return [s.strip() for s in val.split(",") if s.strip()]

def _parse_json_dict(val: Optional[str]) -> Optional[Dict[str, Any]]:
    if not val:
        return None
    try:
        parsed = json.loads(val)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None

@router.get("/logs", response_model=AuditLogListResponse)
def get_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    industry: Optional[str] = Query(default=None),
    role: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    search: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves paginated audit log events (PRD Section 24.1).
    Auditors, Admins, and CXOs can view all enterprise logs.
    Operators are restricted strictly to their own query activity (SEC-02).
    """
    query = db.query(AuditLog)

    # Enforce role boundaries on log visibility
    user_role = current_user.role if current_user else "CXO"
    if user_role not in ["Admin", "CXO", "Auditor"]:
        # Standard users only see their own logs
        query = query.filter(AuditLog.username == current_user.username)

    if industry:
        query = query.filter(AuditLog.industry_id == industry)
    if role:
        query = query.filter(AuditLog.role == role)
    if status_filter:
        query = query.filter(AuditLog.status == status_filter)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (AuditLog.query_text.ilike(search_pattern)) |
            (AuditLog.audit_id.ilike(search_pattern)) |
            (AuditLog.username.ilike(search_pattern))
        )

    total = query.count()
    offset = (page - 1) * page_size
    records = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(page_size).all()

    items = []
    for r in records:
        items.append(AuditLogItem(
            id=r.id,
            audit_id=r.audit_id or f"AUD-LEGACY-{r.id}",
            timestamp=r.timestamp,
            user_id=r.user_id,
            username=r.username,
            role=r.role,
            industry_id=r.industry_id,
            query_text=r.query_text,
            status=r.status,
            execution_time_ms=r.execution_time_ms,
            agents_invoked=r.agents_invoked,
            sources_accessed=_parse_json_list(r.sources_accessed),
            citations_count=r.citations_count or 0,
            grounding_score=r.grounding_score,
            conflicts_count=r.conflicts_count or 0,
            is_abstained=bool(r.is_abstained),
            ip_address=r.ip_address,
            trace_stages=_parse_json_dict(r.trace_stages)
        ))

    return AuditLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        logs=items
    )

@router.get("/summary", response_model=AuditSummaryMetrics)
def get_audit_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns aggregated governance and compliance metrics (SEC-07, Section 24.1).
    """
    total = db.query(AuditLog).count()
    success_count = db.query(AuditLog).filter(AuditLog.status == "SUCCESS").count()
    abstained_count = db.query(AuditLog).filter(AuditLog.is_abstained == True).count()
    blocked_count = db.query(AuditLog).filter(AuditLog.status == "BLOCKED_SECURITY").count()

    avg_lat = db.query(func.avg(AuditLog.execution_time_ms)).scalar() or 0.0
    valid_scores = [
        r[0] for r in db.query(AuditLog.grounding_score).filter(AuditLog.grounding_score.isnot(None)).all()
    ]
    avg_grounding = (sum(valid_scores) / len(valid_scores)) if valid_scores else 0.92

    total_conflicts = db.query(func.sum(AuditLog.conflicts_count)).scalar() or 0

    # Industry breakdown
    ind_counts = dict(
        db.query(AuditLog.industry_id, func.count(AuditLog.id)).group_by(AuditLog.industry_id).all()
    )

    # Role breakdown
    role_counts = dict(
        db.query(AuditLog.role, func.count(AuditLog.id)).group_by(AuditLog.role).all()
    )

    return AuditSummaryMetrics(
        total_queries=total,
        successful_queries=success_count,
        abstained_queries=abstained_count,
        security_blocked_queries=blocked_count,
        avg_latency_ms=round(float(avg_lat), 1),
        avg_grounding_score=round(float(avg_grounding), 2),
        total_conflicts_detected=int(total_conflicts),
        industries_breakdown=ind_counts,
        roles_breakdown=role_counts
    )

@router.get("/logs/{audit_id}", response_model=AuditLogItem)
def get_audit_log_by_id(
    audit_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches details for a single audit record by audit_id."""
    r = db.query(AuditLog).filter(
        (AuditLog.audit_id == audit_id) | (AuditLog.id == int(audit_id) if audit_id.isdigit() else False)
    ).first()

    if not r:
        raise HTTPException(status_code=404, detail=f"Audit record '{audit_id}' not found")

    user_role = current_user.role if current_user else "CXO"
    if user_role not in ["Admin", "CXO", "Auditor"] and r.username != current_user.username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot view audit logs belonging to another user"
        )

    return AuditLogItem(
        id=r.id,
        audit_id=r.audit_id or f"AUD-LEGACY-{r.id}",
        timestamp=r.timestamp,
        user_id=r.user_id,
        username=r.username,
        role=r.role,
        industry_id=r.industry_id,
        query_text=r.query_text,
        status=r.status,
        execution_time_ms=r.execution_time_ms,
        agents_invoked=r.agents_invoked,
        sources_accessed=_parse_json_list(r.sources_accessed),
        citations_count=r.citations_count or 0,
        grounding_score=r.grounding_score,
        conflicts_count=r.conflicts_count or 0,
        is_abstained=bool(r.is_abstained),
        ip_address=r.ip_address,
        trace_stages=_parse_json_dict(r.trace_stages)
    )
