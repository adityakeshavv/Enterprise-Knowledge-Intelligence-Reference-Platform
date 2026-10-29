from typing import List, Dict, Any, Optional
from app.orchestration.contracts import (
    TraceValidationReport, ExecutionTraceRecord,
    ExtractedEvidenceItem
)
from app.orchestration.trace import ExecutionTracer
from app.agents.validation_agent import evidence_validation_agent
from app.schemas.query import CitationItem, FindingItem

class TraceabilityAuditAgent:
    """Stage 9: Verifies end-to-end execution integrity, evidence lineage, citation grounding,
    and enforces safe abstention boundaries before releasing responses.
    """

    def __init__(self, validation_agent=evidence_validation_agent):
        self.validation_agent = validation_agent

    def evaluate_domain_abstention(
        self,
        query: str,
        citations: List[CitationItem],
        has_structured_evidence: bool = False
    ) -> (bool, Optional[str]):
        """Evaluates whether the query falls outside verified enterprise boundaries."""
        # Check against unindexed domains
        for topic in self.validation_agent.UNINDEXED_TOPICS:
            if topic in query.lower():
                return (
                    True,
                    f"The query references '{topic}', which falls outside the indexed knowledge boundaries "
                    "of the enterprise platform. In accordance with the zero-hallucination policy, "
                    "the platform explicitly abstains from speculative extrapolation."
                )

        # Check total evidence absence
        if not citations and not has_structured_evidence:
            return (
                True,
                "No verifiable structured telemetry or procedural documentation was matched for this query. "
                "The platform safely abstains from answering to preserve enterprise decision integrity."
            )

        return (False, None)

    def validate_execution(
        self,
        tracer: ExecutionTracer,
        citations: List[CitationItem],
        findings: List[FindingItem],
        is_abstained: bool = False
    ) -> TraceValidationReport:
        """Executes full trace audit checking citation integrity and stage completeness."""
        return tracer.validate_trace_and_citations(
            citations=citations,
            findings=findings,
            is_abstained=is_abstained
        )

traceability_agent = TraceabilityAuditAgent()
