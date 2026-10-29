import time
from typing import Dict, Any, Optional
from app.orchestration.contracts import (
    UnstructuredRetrievalResult, AgentStatus, AgentError
)
from app.agents.document_agent import document_agent

class UnstructuredDocumentAgent:
    """Stage 6: Specialized agent retrieving and verifying unstructured manuals, SOPs,
    and quality bulletins via hybrid BM25 lexical + dense semantic index.
    """

    def __init__(self, underlying_agent=document_agent):
        self.underlying_agent = underlying_agent

    def execute_task(
        self,
        query: str,
        user_role: str = "CXO",
        department: Optional[str] = None
    ) -> UnstructuredRetrievalResult:
        start_t = time.perf_counter()
        try:
            doc_res = self.underlying_agent.process(
                query=query,
                user_role=user_role,
                department=department
            )
            latency_ms = (time.perf_counter() - start_t) * 1000

            citations = doc_res.get("citations", [])
            evidence_passages = [
                {"passage": p, "id": getattr(c, "citation_id", f"C-{i}")}
                for i, (p, c) in enumerate(zip(doc_res.get("evidence_fences", []), citations))
            ]

            status = AgentStatus.COMPLETED if citations else AgentStatus.PARTIAL

            return UnstructuredRetrievalResult(
                status=status,
                query_executed=query,
                chunks_retrieved=len(citations),
                citations=citations,
                evidence_passages=evidence_passages,
                summary=doc_res.get("summary", ""),
                latency_ms=latency_ms
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_t) * 1000
            return UnstructuredRetrievalResult(
                status=AgentStatus.FAILED,
                query_executed=query,
                chunks_retrieved=0,
                citations=[],
                evidence_passages=[],
                summary=f"Unstructured retrieval error: {str(e)}",
                latency_ms=latency_ms,
                error=AgentError(
                    error_code="UNSTRUCTURED_RETRIEVAL_ERROR",
                    message=str(e),
                    retryable=True
                )
            )

unstructured_document_agent = UnstructuredDocumentAgent()
