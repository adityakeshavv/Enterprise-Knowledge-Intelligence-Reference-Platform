from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class QueryRequest(BaseModel):
    query: str
    scenario_id: Optional[str] = None
    industry_id: Optional[str] = None

class CitationItem(BaseModel):
    citation_id: str
    title: str
    source_type: str  # "SQL_QUERY", "DOCUMENT_SOP", "EXTERNAL_API"
    reference: str    # e.g., "plant_downtime_events (SQL)" or "SOP-Maint-Line3.pdf (p.14)"
    snippet: str
    metadata: Dict[str, Any] = {}

class ConflictItem(BaseModel):
    conflict_id: str
    title: str
    description: str
    source_a: str
    source_b: str
    recommendation: str

class MetricItem(BaseModel):
    label: str
    value: str
    subtext: Optional[str] = None
    change_type: Optional[str] = None # "positive", "negative", "neutral"

class TraceStep(BaseModel):
    step_id: int
    agent_name: str
    agent_label: str
    status: str # "running", "completed", "warning"
    business_message: str
    technical_detail: Optional[str] = None
    duration_ms: float

class QueryResponse(BaseModel):
    query_id: str
    industry_id: str
    query_text: str
    executive_summary: str
    key_findings: List[str]
    metrics: List[MetricItem]
    citations: List[CitationItem]
    conflicts: List[ConflictItem] = []
    confidence_score: float
    trace_steps: List[TraceStep]
    total_latency_ms: float
