import re
from typing import List, Dict, Any, Optional
from app.orchestration.contracts import (
    ExtractedEvidenceItem, EvidenceExtractionResult, EvidenceStatus,
    StructuredRetrievalResult, UnstructuredRetrievalResult
)
from app.agents.validation_agent import evidence_validation_agent
from app.schemas.query import CitationItem, ConflictItem

class EvidenceExtractionAgent:
    """Stage 7: Consolidates structured and unstructured retrieval findings into structured
    empirical evidence items, extracting facts, units, timestamps, and detecting contradictions.
    """

    def __init__(self, validation_agent=evidence_validation_agent):
        self.validation_agent = validation_agent

    def extract(
        self,
        query: str,
        structured_res: Optional[StructuredRetrievalResult],
        unstructured_res: Optional[UnstructuredRetrievalResult],
        citations: List[CitationItem]
    ) -> EvidenceExtractionResult:
        evidence_items: List[ExtractedEvidenceItem] = []
        conflicts: List[ConflictItem] = []
        unsupported_claims: List[str] = []
        missing_info: List[str] = []

        # 1. Extract Evidence from Structured Telemetry
        if structured_res and structured_res.rows_returned > 0:
            for idx, row in enumerate(structured_res.data_records):
                row_str = ", ".join(f"{k}: {v}" for k, v in row.items())
                item = ExtractedEvidenceItem(
                    evidence_id=f"EVD-SQL-{idx+1:02d}",
                    task_id="task_structured_retrieval",
                    source_id="SQL_DATABASE",
                    source_type="RELATIONAL_TELEMETRY",
                    source_title="Plant Downtime Events & Work Orders",
                    source_location=f"Row {idx+1}",
                    extracted_fact=f"Telemetry record: {row_str}",
                    value=row.get("downtime_minutes") or row.get("total_downtime"),
                    unit="minutes" if ("downtime" in row_str.lower()) else None,
                    timestamp_or_period=str(row.get("start_timestamp") or row.get("delivery_date") or ""),
                    supporting_excerpt=f"Executed SQL: {structured_res.query_executed} returned {row_str}",
                    evidence_status=EvidenceStatus.VERIFIED,
                    is_inference=False
                )
                evidence_items.append(item)
        elif structured_res and structured_res.status.value == "failed":
            missing_info.append(f"Structured telemetry query failed: {structured_res.summary}")

        # 2. Extract Evidence from Unstructured Documents
        if unstructured_res and unstructured_res.citations:
            for idx, cit in enumerate(unstructured_res.citations):
                snippet = cit.snippet
                # Extract potential metrics or dates
                date_match = re.search(r"\b(March \d{1,2}|2024|2025|2026)\b", snippet)
                val_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:hours|minutes|ppm|bar|psi|%)\b", snippet, flags=re.IGNORECASE)

                item = ExtractedEvidenceItem(
                    evidence_id=f"EVD-DOC-{idx+1:02d}",
                    task_id="task_unstructured_retrieval",
                    source_id=cit.citation_id,
                    source_type=cit.source_type,
                    source_title=cit.title,
                    source_location=cit.reference,
                    extracted_fact=snippet[:180],
                    value=val_match.group(1) if val_match else None,
                    unit=val_match.group(0).split()[-1] if val_match else None,
                    timestamp_or_period=date_match.group(1) if date_match else None,
                    supporting_excerpt=snippet,
                    evidence_status=EvidenceStatus.VERIFIED,
                    is_inference=False
                )
                evidence_items.append(item)
        elif unstructured_res and unstructured_res.status.value == "failed":
            missing_info.append(f"Document retrieval failed: {unstructured_res.summary}")

        # 3. Detect Cross-Source Contradictions (e.g. CONF-01, CONF-02)
        # We reuse the battle-tested domain rules from evidence_validation_agent
        dummy_sql = None
        if structured_res:
            class DummySQL:
                pass
            dummy_sql = DummySQL()
            dummy_sql.rows = structured_res.data_records
            dummy_sql.is_safe = structured_res.is_safe
            dummy_sql.rows_returned = structured_res.rows_returned

        dummy_doc = {"citations": citations}
        detected_conflicts = self.validation_agent.detect_conflicts(
            query=query,
            sql_result=dummy_sql,
            doc_result=dummy_doc,
            citations=citations
        )
        conflicts.extend(detected_conflicts)

        # Mark conflicted evidence items
        if conflicts:
            for item in evidence_items:
                for conf in conflicts:
                    if conf.conflict_id == "CONF-01" and "maintenance" in item.extracted_fact.lower():
                        item.evidence_status = EvidenceStatus.CONFLICTED
                        item.related_evidence_ids.append(conf.conflict_id)

        verified_count = sum(1 for e in evidence_items if not e.is_inference)
        inference_count = sum(1 for e in evidence_items if e.is_inference)

        return EvidenceExtractionResult(
            evidence_items=evidence_items,
            verified_facts_count=verified_count,
            inferences_count=inference_count,
            conflicts_detected=conflicts,
            unsupported_claims=unsupported_claims,
            missing_information=missing_info
        )

evidence_extraction_agent = EvidenceExtractionAgent()
