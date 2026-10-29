from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AuditLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    audit_id: Optional[str] = None
    timestamp: datetime
    user_id: Optional[int] = None
    username: str
    role: str
    industry_id: str
    query_text: str
    status: str
    execution_time_ms: float
    agents_invoked: Optional[str] = None
    sources_accessed: Optional[List[str]] = None
    citations_count: int = 0
    grounding_score: Optional[float] = None
    conflicts_count: int = 0
    is_abstained: bool = False
    ip_address: Optional[str] = None
    trace_stages: Optional[Dict[str, Any]] = None

class AuditLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    logs: List[AuditLogItem]

class AuditSummaryMetrics(BaseModel):
    total_queries: int
    successful_queries: int
    abstained_queries: int
    security_blocked_queries: int
    avg_latency_ms: float
    avg_grounding_score: float
    total_conflicts_detected: int
    industries_breakdown: Dict[str, int]
    roles_breakdown: Dict[str, int]
