from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class FactClassification(str, Enum):
    VERIFIED_FACT = "VERIFIED_FACT"
    ANALYTICAL_INFERENCE = "ANALYTICAL_INFERENCE"

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

class FindingItem(BaseModel):
    statement: str
    classification: FactClassification
    citation_ids: List[str] = []
    confidence: float = 1.0

class EvidenceGraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # "query", "finding", "sql_source", "doc_source", "conflict"
    category: Optional[str] = None # "fact", "inference", "telemetry", "sop", "discrepancy"
    metadata: Dict[str, Any] = {}

class EvidenceGraphEdge(BaseModel):
    source: str
    target: str
    relation: str  # "GROUNDS", "CONTRADICTS", "DERIVED_FROM", "QUERIED_FROM", "RECOMMENDS"
    is_conflict: bool = False

class EvidenceGraph(BaseModel):
    nodes: List[EvidenceGraphNode] = []
    edges: List[EvidenceGraphEdge] = []

class ValidationReport(BaseModel):
    grounding_score: float  # 0.0 to 1.0
    supported_claims: List[str] = []
    unsupported_claims: List[str] = []
    conflicts: List[ConflictItem] = []
    is_abstained: bool = False
    abstention_reason: Optional[str] = None

class QueryResponse(BaseModel):
    query_id: str
    industry_id: str
    query_text: str
    executive_summary: str
    key_findings: List[str]
    findings: Optional[List[FindingItem]] = None
    metrics: List[MetricItem]
    citations: List[CitationItem]
    conflicts: List[ConflictItem] = []
    confidence_score: float
    validation_report: Optional[ValidationReport] = None
    evidence_graph: Optional[EvidenceGraph] = None
    is_abstained: bool = False
    trace_steps: List[TraceStep]
    total_latency_ms: float
