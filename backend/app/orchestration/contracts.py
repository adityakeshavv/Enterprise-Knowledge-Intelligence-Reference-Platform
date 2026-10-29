from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# =====================================================================
# Status & Error Enums
# =====================================================================

class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"

class ExecutionMode(str, Enum):
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"
    SINGLE_AGENT = "single_agent"

class AgentError(BaseModel):
    error_code: str
    message: str
    retryable: bool = False
    context: Dict[str, Any] = Field(default_factory=dict)

# =====================================================================
# Stage 1: Query Understanding Contracts
# =====================================================================

class QueryUnderstandingResult(BaseModel):
    original_query: str
    normalized_query: str
    primary_intent: str
    secondary_intents: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: Optional[Dict[str, Any]] = None
    constraints: List[str] = Field(default_factory=list)
    ambiguities: List[str] = Field(default_factory=list)
    clarification_required: bool = False
    clarification_prompt: Optional[str] = None
    business_objective: str = ""

# =====================================================================
# Stage 2: Intent Classification Contracts
# =====================================================================

class IntentCategory(str, Enum):
    STRUCTURED_TELEMETRY = "STRUCTURED_TELEMETRY"
    PROCEDURAL_GUIDANCE = "PROCEDURAL_GUIDANCE"
    CROSS_SOURCE_INVESTIGATION = "CROSS_SOURCE_INVESTIGATION"
    QUALITY_SUPPLIER_ANALYSIS = "QUALITY_SUPPLIER_ANALYSIS"
    ANOMALY_DIAGNOSTIC = "ANOMALY_DIAGNOSTIC"
    UNKNOWN_UNSUPPORTED = "UNKNOWN_UNSUPPORTED"

class IntentClassificationResult(BaseModel):
    predicted_intent: IntentCategory
    secondary_intents: List[IntentCategory] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.0)
    required_capabilities: List[str] = Field(default_factory=list)
    target_source_types: List[str] = Field(default_factory=list) # "SQL_DATABASE", "DOCUMENT_STORE", etc.
    processing_strategy: ExecutionMode = ExecutionMode.PARALLEL
    fallback_triggered: bool = False
    fallback_reason: Optional[str] = None

# =====================================================================
# Stage 3: Query Routing Contracts
# =====================================================================

class RoutingDecision(BaseModel):
    workflow_id: str
    selected_agents: List[str] = Field(default_factory=list)
    skipped_agents: List[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL
    authorized_sources: List[str] = Field(default_factory=list)
    rationale: str = ""
    is_authorized: bool = True
    authorization_error: Optional[str] = None

# =====================================================================
# Stage 4: Investigation Planning Contracts
# =====================================================================

class InvestigationTask(BaseModel):
    task_id: str
    objective: str
    assigned_agent: str
    source_type: str
    dependencies: List[str] = Field(default_factory=list)
    required_inputs: Dict[str, Any] = Field(default_factory=dict)
    expected_outputs: List[str] = Field(default_factory=list)
    completion_criteria: str
    status: AgentStatus = AgentStatus.PENDING
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[AgentError] = None
    duration_ms: float = 0.0

class InvestigationPlan(BaseModel):
    plan_id: str
    primary_question: str
    sub_questions: List[str] = Field(default_factory=list)
    tasks: List[InvestigationTask] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.PARALLEL
    fallback_strategy: str = "Return partial evidence with explicit limitations."

# =====================================================================
# Stage 5 & 6: Source Retrieval Result Contracts
# =====================================================================

class StructuredRetrievalResult(BaseModel):
    agent_id: str = "structured_document_agent"
    status: AgentStatus = AgentStatus.COMPLETED
    query_executed: str
    rows_returned: int = 0
    columns: List[str] = Field(default_factory=list)
    data_records: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    source_reference: str = ""
    latency_ms: float = 0.0
    is_safe: bool = True
    error: Optional[AgentError] = None

class UnstructuredRetrievalResult(BaseModel):
    agent_id: str = "unstructured_document_agent"
    status: AgentStatus = AgentStatus.COMPLETED
    query_executed: str
    chunks_retrieved: int = 0
    citations: List[Any] = Field(default_factory=list)
    evidence_passages: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    latency_ms: float = 0.0
    error: Optional[AgentError] = None

# =====================================================================
# Stage 7: Evidence & Detail Extraction Contracts
# =====================================================================

class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    CONFLICTED = "conflicted"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"

class ExtractedEvidenceItem(BaseModel):
    evidence_id: str
    task_id: str
    source_id: str
    source_type: str
    source_title: str
    source_location: str
    extracted_fact: str
    value: Optional[Any] = None
    unit: Optional[str] = None
    timestamp_or_period: Optional[str] = None
    supporting_excerpt: str
    evidence_status: EvidenceStatus = EvidenceStatus.VERIFIED
    related_evidence_ids: List[str] = Field(default_factory=list)
    is_inference: bool = False

class EvidenceExtractionResult(BaseModel):
    evidence_items: List[ExtractedEvidenceItem] = Field(default_factory=list)
    verified_facts_count: int = 0
    inferences_count: int = 0
    conflicts_detected: List[Any] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)

# =====================================================================
# Stage 8: Summarization Contracts
# =====================================================================

class SummarizationResult(BaseModel):
    executive_summary: str
    key_findings: List[str] = Field(default_factory=list)
    findings: List[Any] = Field(default_factory=list)
    metrics: List[Any] = Field(default_factory=list)
    citations: List[Any] = Field(default_factory=list)
    conflicts: List[Any] = Field(default_factory=list)
    confidence_score: float = 0.92
    format_type: str = "EXECUTIVE_INVESTIGATION_BRIEF"

# =====================================================================
# Stage 9: Traceability & Audit Contracts
# =====================================================================

class TraceValidationReport(BaseModel):
    is_valid: bool = True
    completeness_score: float = 1.0 # 0.0 to 1.0
    citations_verified: bool = True
    unsupported_citations: List[str] = Field(default_factory=list)
    broken_references: List[str] = Field(default_factory=list)
    unauthorized_access_detected: bool = False
    validation_notes: List[str] = Field(default_factory=list)

class ExecutionTraceRecord(BaseModel):
    execution_id: str
    original_query: str
    understanding: Optional[QueryUnderstandingResult] = None
    classification: Optional[IntentClassificationResult] = None
    routing: Optional[RoutingDecision] = None
    plan: Optional[InvestigationPlan] = None
    stage_durations_ms: Dict[str, float] = Field(default_factory=dict)
    agent_executions: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_lineage: Dict[str, List[str]] = Field(default_factory=dict)
    validation_report: Optional[TraceValidationReport] = None
    total_duration_ms: float = 0.0
