from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class SQLQueryRequest(BaseModel):
    query: str
    scenario_id: Optional[str] = None
    industry_id: Optional[str] = "manufacturing"

class SQLQueryResult(BaseModel):
    natural_query: str
    generated_sql: str
    execution_duration_ms: float
    rows_returned: int
    columns: List[str]
    rows: List[Dict[str, Any]]
    summary: str
    is_safe: bool = True
    error: Optional[str] = None

class TableColumnInfo(BaseModel):
    name: str
    type: str
    primary_key: bool = False
    nullable: bool = True

class TableSchemaInfo(BaseModel):
    table_name: str
    description: str
    columns: List[TableColumnInfo]

class DatabaseSchemaResponse(BaseModel):
    industry_id: str
    database_type: str
    allowlisted_tables: List[str]
    tables: List[TableSchemaInfo]
