from typing import List, Dict, Any, Tuple, Optional
from app.orchestration.contracts import (
    SummarizationResult, ExtractedEvidenceItem, EvidenceExtractionResult,
    QueryUnderstandingResult, IntentClassificationResult, AgentStatus
)
from app.agents.synthesis_agent import synthesis_agent
from app.orchestration.state import WorkflowState, QueryIntent
from app.schemas.query import MetricItem, CitationItem, ConflictItem, FindingItem

class SummarizerAgent:
    """Stage 8: Transforms validated evidence items and cross-source findings into
    an executive brief with KPI metric cards, auditable inline citations, and explicit uncertainty notices.
    """

    def __init__(self, underlying_synthesis=synthesis_agent):
        self.underlying_synthesis = underlying_synthesis

    def summarize(
        self,
        understanding: QueryUnderstandingResult,
        classification: IntentClassificationResult,
        evidence_result: EvidenceExtractionResult,
        citations: List[CitationItem],
        state_context: Optional[WorkflowState] = None
    ) -> SummarizationResult:
        # Build synthetic state if not provided
        if state_context is None:
            state_context = WorkflowState(
                query_id="SUMMARIZE_TMP",
                raw_query=understanding.normalized_query,
                citations=citations,
                conflicts=evidence_result.conflicts_detected
            )

        # Delegate executive synthesis to our established synthesis agent
        exec_summary, findings_str, metrics, conflicts = self.underlying_synthesis.synthesize(state_context)

        # Format type adaptation based on intent
        format_type = "EXECUTIVE_INVESTIGATION_BRIEF"
        if classification.predicted_intent.value == "STRUCTURED_TELEMETRY":
            format_type = "QUANTITATIVE_TELEMETRY_REPORT"
        elif classification.predicted_intent.value == "PROCEDURAL_GUIDANCE":
            format_type = "STANDARD_OPERATING_PROCEDURE_GUIDE"
        elif classification.predicted_intent.value == "QUALITY_SUPPLIER_ANALYSIS":
            format_type = "SUPPLIER_QUALITY_AUDIT"

        return SummarizationResult(
            executive_summary=exec_summary,
            key_findings=findings_str,
            findings=state_context.findings,
            metrics=metrics,
            citations=citations,
            conflicts=conflicts,
            confidence_score=state_context.confidence_score,
            format_type=format_type
        )

summarizer_agent = SummarizerAgent()
