from fastapi import APIRouter, HTTPException
from app.config_loader.loader import config_loader

router = APIRouter(prefix="/industries", tags=["Industries"])

@router.get("")
def list_industries():
    """List available industry packs with summary metadata."""
    return config_loader.list_industries_summary()

@router.get("/{industry_id}")
def get_industry_details(industry_id: str):
    """Retrieve full declarative configuration for a specific industry pack."""
    pack = config_loader.get_industry_pack(industry_id)
    if not pack:
        raise HTTPException(status_code=404, detail=f"Industry pack '{industry_id}' not found.")
    return pack

@router.post("/reload")
def reload_configurations():
    """Hot-reload all YAML configurations from disk without downtime."""
    config_loader.reload_all()
    return {"status": "reloaded", "industries": config_loader.get_industry_ids()}
