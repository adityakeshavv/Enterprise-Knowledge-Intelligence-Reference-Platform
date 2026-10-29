from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.core.config_loader import config_loader
from app.core.rbac import get_current_user, require_roles
from app.db.models import User
from app.schemas.config import IndustrySummary, IndustryDetail, ChangeActiveIndustryRequest

router = APIRouter(prefix="/config", tags=["Configuration"])

@router.get("/industries", response_model=List[IndustrySummary])
def get_industries():
    """List all available industries loaded from /config/industries/."""
    return config_loader.list_available_industries()

@router.get("/active", response_model=IndustryDetail)
def get_active_industry():
    """Get currently active industry configuration, terminology, sources, and scenarios."""
    return config_loader.get_active_industry()

@router.post("/active")
def switch_active_industry(
    payload: ChangeActiveIndustryRequest,
    current_user: User = Depends(require_roles(["Admin", "CXO", "Auditor", "Quality Analyst"]))
):
    """Switch the platform active industry in runtime memory."""
    success = config_loader.set_active_industry(payload.industry_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Industry configuration '{payload.industry_id}' not found in registry"
        )
    return {
        "status": "success",
        "message": f"Active industry switched to '{payload.industry_id}'",
        "active_industry": config_loader.get_active_industry()["metadata"]
    }

@router.post("/reload")
def reload_configurations(current_user: User = Depends(require_roles(["Admin"]))):
    """Reload all YAML files from disk into memory cache (Admin only)."""
    config_loader.reload_all()
    return {"status": "success", "message": "All industry configurations reloaded from disk"}
