import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.rbac import get_current_user, require_roles
from app.db.models import User
from app.evaluation.engine import evaluation_engine
from app.evaluation.runner import run_evaluation_suite, REPORTS_DIR

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Benchmarking"])

class RunEvaluationRequest(BaseModel):
    industry_id: str = "all"  # "manufacturing", "pharma", or "all"

@router.get("/benchmarks")
def get_benchmarks(
    industry: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """Retrieves available gold-standard evaluation fixtures (PRD Section 26)."""
    industries = [industry] if industry in ["manufacturing", "pharma"] else ["manufacturing", "pharma"]
    items = []
    for ind in industries:
        items.extend(evaluation_engine.load_dataset(ind))
    return {
        "total": len(items),
        "items": items
    }

@router.get("/latest")
def get_latest_evaluation_report(current_user: User = Depends(get_current_user)):
    """Retrieves the latest benchmark evaluation results and quantitative metrics."""
    json_path = REPORTS_DIR / "evaluation_report.json"
    if not json_path.exists():
        # Run automatically if no report exists yet
        reports = run_evaluation_suite("all")
        return {k: v.model_dump() for k, v in reports.items()}

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@router.post("/run")
def trigger_evaluation_run(
    payload: RunEvaluationRequest,
    current_user: User = Depends(require_roles(["Admin", "CXO", "Auditor"]))
):
    """Executes the benchmark evaluation suite on demand (Admin/CXO/Auditor only)."""
    reports = run_evaluation_suite(payload.industry_id)
    return {
        "status": "completed",
        "industry": payload.industry_id,
        "reports": {k: v.model_dump() for k, v in reports.items()}
    }
