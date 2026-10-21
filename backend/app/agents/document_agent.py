import re
from typing import Dict, Any, List, Optional
from app.retrieval.retriever import document_retriever
from app.schemas.query import CitationItem

class DocumentIntelligenceAgent:
    """Specialized AI agent retrieving, reasoning over, and validating unstructured enterprise documents."""

    def __init__(self, retriever=document_retriever):
        self.retriever = retriever

    def process(
        self,
        query: str,
        department: Optional[str] = None,
        user_role: str = "CXO"
    ) -> Dict[str, Any]:
        # 1. Defense against direct prompt injection in queries
        sanitized_query = self._sanitize_input(query)

        # 2. Retrieve relevant document passages
        retrieval_results = self.retriever.retrieve(
            query=sanitized_query,
            top_k=4,
            department=department,
            user_role=user_role
        )

        if not retrieval_results:
            return {
                "agent_name": "document_intelligence_agent",
                "status": "insufficient_evidence",
                "summary": "No relevant documentation or operating procedures were found matching the query within your clearance level.",
                "citations": [],
                "evidence_passages": [],
                "claims": []
            }

        citations: List[CitationItem] = []
        evidence_fences: List[str] = []
        claims: List[str] = []

        for item in retrieval_results:
            chunk = item["chunk"]
            citation = item["citation"]
            citations.append(citation)

            # Defensive XML bounding fence (PRD Section 7.3)
            fence = (
                f'<retrieved_evidence id="{citation.citation_id}" source="{citation.reference}">\n'
                f'{chunk.text}\n'
                f'</retrieved_evidence>'
            )
            evidence_fences.append(fence)

            # Extract factoid claims
            first_line = chunk.text.split("\n")[0] if "\n" in chunk.text else chunk.text[:120]
            claims.append(f"Document evidence from {citation.reference}: {first_line}")

        summary = self._synthesize_document_findings(query, citations, retrieval_results)

        return {
            "agent_name": "document_intelligence_agent",
            "status": "completed",
            "summary": summary,
            "citations": citations,
            "evidence_fences": evidence_fences,
            "claims": claims
        }

    def _sanitize_input(self, text: str) -> str:
        # Detect adversarial prompt injection patterns
        injection_patterns = [
            r"ignore (?:all )?previous instructions",
            r"system override",
            r"reveal (?:admin )?password",
            r"disregard (?:safety|guardrails)",
            r"output (?:all )?secrets"
        ]
        sanitized = text
        for pat in injection_patterns:
            sanitized = re.sub(pat, "[FILTERED_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def _synthesize_document_findings(
        self,
        query: str,
        citations: List[CitationItem],
        retrieval_results: List[Dict[str, Any]]
    ) -> str:
        # Synthesize verified claims with citation anchors
        findings = []
        for item in retrieval_results:
            c = item["citation"]
            findings.append(f"Found protocol in {c.reference} [{c.citation_id}]")
        return "; ".join(findings)

document_agent = DocumentIntelligenceAgent()
