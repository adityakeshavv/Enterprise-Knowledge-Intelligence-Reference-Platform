from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.agents.sql_agent import sql_agent
from app.retrieval.sql_sandbox import sql_sandbox, SQLSecurityError
from app.core.rbac import get_current_user
from app.db.models import User
from app.schemas.sql import SQLQueryRequest, SQLQueryResult, DatabaseSchemaResponse

router = APIRouter(prefix="/sql", tags=["Structured Data Intelligence"])

class TestSandboxRequest(BaseModel):
    raw_sql: str

@router.get("/schema", response_model=DatabaseSchemaResponse)
def get_database_schema(current_user: User = Depends(get_current_user)):
    """Returns allowlisted schema definitions for structured enterprise tables."""
    tables_info = sql_agent.get_schema_summary()
    return DatabaseSchemaResponse(
        industry_id="manufacturing",
        database_type="relational_sql",
        allowlisted_tables=[t.table_name for t in tables_info],
        tables=tables_info
    )

@router.post("/query", response_model=SQLQueryResult)
def execute_natural_query(
    payload: SQLQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """Executes a natural language business question through the Structured Data Agent."""
    result = sql_agent.process(payload.query)
    if not result.is_safe:
        raise HTTPException(status_code=403, detail=result.error or "Query violated SQL security policy.")
    return result

@router.post("/test-sandbox")
def test_sql_sandbox(
    payload: TestSandboxRequest,
    current_user: User = Depends(get_current_user)
):
    """Directly tests SQL AST sanitization and security enforcement."""
    try:
        sanitized = sql_sandbox.validate_and_sanitize(payload.raw_sql)
        columns, rows, duration_ms, _ = sql_sandbox.execute_safe_query(payload.raw_sql)
        return {
            "status": "allowed",
            "sanitized_sql": sanitized,
            "rows_count": len(rows),
            "execution_duration_ms": duration_ms
        }
    except SQLSecurityError as e:
        return {
            "status": "blocked",
            "violation": str(e),
            "error_type": type(e).__name__
        }
