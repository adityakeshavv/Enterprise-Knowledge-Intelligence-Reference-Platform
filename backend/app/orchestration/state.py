import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.schemas.query import (
    TraceStep, CitationItem, ConflictItem, MetricItem,
    ValidationReport, FindingItem, FactClassification
)
from app.schemas.sql import SQLQueryResult

class QueryIntent(str, Enum):
    STRUCTURED_ONLY = "STRUCTURED_ONLY"
    DOCUMENT_ONLY = "DOCUMENT_ONLY"
    CROSS_SOURCE_HYBRID = "CROSS_SOURCE_HYBRID"

class SubTask(BaseModel):
    task_id: str
    agent_name: str           # "structured_data_agent", "document_intelligence_agent"
    agent_label: str
    sub_query: str
    target_source: str        # "SQL_DATABASE", "DOCUMENT_STORE"
    dependencies: List[str] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    intent: QueryIntent
    subtasks: List[SubTask]
    is_parallel: bool = True
    reasoning: str

class WorkflowState(BaseModel):
    query_id: str
    raw_query: str
    industry_id: str = "manufacturing"
    user_role: str = "CXO"
    department: Optional[str] = None
    plan: Optional[ExecutionPlan] = None
    
    # Sub-agent execution outputs
    sql_result: Optional[SQLQueryResult] = None
    doc_result: Optional[Dict[str, Any]] = None
    
    # Validation outputs
    validation_report: Optional[ValidationReport] = None
    is_abstained: bool = False
    
    # Aggregated outputs
    citations: List[CitationItem] = Field(default_factory=list)
    conflicts: List[ConflictItem] = Field(default_factory=list)
    metrics: List[MetricItem] = Field(default_factory=list)
    findings: List[FindingItem] = Field(default_factory=list)
    trace_steps: List[TraceStep] = Field(default_factory=list)
    
    # Modular Pipeline Additions
    understanding: Optional[Any] = None
    classification: Optional[Any] = None
    investigation_plan: Optional[Any] = None
    evidence_items: Optional[List[Any]] = None
    trace_record: Optional[Any] = None

    # Telemetry
    start_time: float = Field(default_factory=time.time)
    total_latency_ms: float = 0.0
    confidence_score: float = 0.92

    def add_trace_step(
        self,
        agent_name: str,
        agent_label: str,
        status: str,
        business_message: str,
        technical_detail: Optional[str] = None,
        duration_ms: float = 0.0
    ) -> TraceStep:
        step = TraceStep(
            step_id=len(self.trace_steps) + 1,
            agent_name=agent_name,
            agent_label=agent_label,
            status=status,
            business_message=business_message,
            technical_detail=technical_detail,
            duration_ms=round(duration_ms, 2)
        )
        self.trace_steps.append(step)
        return step
