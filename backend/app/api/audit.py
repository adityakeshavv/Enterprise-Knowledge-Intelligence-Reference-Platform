from fastapi import APIRouter, Security
from app.core.security import get_current_user, require_role
from app.core.logging import audit_logger

router = APIRouter(prefix="/audit", tags=["Audit & Governance"])

@router.get("/events")
def get_audit_events(limit: int = 50, user: dict = Security(require_role("Auditor"))):
    """Retrieve the recent audit events for compliance and security review."""
    return {
        "count": limit,
        "events": audit_logger.get_recent_events(limit=limit)
    }
