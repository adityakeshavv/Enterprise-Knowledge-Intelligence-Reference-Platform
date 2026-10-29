from typing import List, Dict, Any, Optional
from app.retrieval.hybrid_index import hybrid_index
from app.ingestion.models import DocumentChunk
from app.schemas.query import CitationItem

class DocumentRetriever:
    """High-level document retriever enforcing RBAC clearance and generating deep provenance citations."""

    def __init__(self, index=hybrid_index):
        self.index = index
        self.is_default_index = (index is hybrid_index)
        self.loaded_industry: Optional[str] = None

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        department: Optional[str] = None,
        user_role: str = "CXO"
    ) -> List[Dict[str, Any]]:
        # Auto-initialize or switch from active industry directory when using the global default index
        if self.is_default_index:
            try:
                from pathlib import Path
                from app.core.config_loader import config_loader
                from app.ingestion.pipeline import pipeline

                active_ind = config_loader.active_industry_id
                if self.loaded_industry != active_ind or len(self.index.chunks) == 0:
                    data_dir = Path(config_loader.config_dir).resolve() / active_ind / "data" / "unstructured"
                    if not data_dir.exists():
                        data_dir = Path(__file__).resolve().parent.parent.parent.parent / "config" / "industries" / active_ind / "data" / "unstructured"
                    if data_dir.exists():
                        self.index.clear()
                        chunks, _ = pipeline.ingest_directory(data_dir)
                        self.index.add_chunks(chunks)
                        self.loaded_industry = active_ind
            except Exception:
                pass

        # Map user role to maximum clearance
        role_clearance_map = {
            "CXO": "Restricted",
            "Admin": "Restricted",
            "Auditor": "Restricted",
            "Quality Analyst": "Restricted",
            "Operator": "Internal"
        }
        max_clearance = role_clearance_map.get(user_role, "Internal")

        filters = {"max_classification": max_clearance}
        if department:
            filters["department"] = department

        ranked = self.index.search(query=query, top_k=top_k, filters=filters)

        from app.core.guardrails import security_guardrails

        output = []
        for rank, (chunk, score) in enumerate(ranked, start=1):
            citation_id = self._build_citation_id(chunk, rank)
            reference = self._build_reference_str(chunk)

            citation = CitationItem(
                citation_id=citation_id,
                title=f"{chunk.metadata.get('filename', 'Document')} — {chunk.section_header or chunk.sheet_name or 'Passage'}",
                source_type="DOCUMENT_SOP" if chunk.source_type == "pdf_section" else ("SQL_QUERY" if chunk.source_type == "excel_sheet" else "DOCUMENT_SOP"),
                reference=reference,
                snippet=security_guardrails.sanitize_untrusted_text(chunk.text),
                metadata={
                    "doc_id": chunk.doc_id,
                    "score": round(score, 3),
                    "page_number": chunk.page_number,
                    "section": chunk.section_header,
                    "sheet_name": chunk.sheet_name,
                    "cell_range": chunk.cell_range,
                    "source_type": chunk.source_type,
                    "classification": chunk.metadata.get("classification", "Internal")
                }
            )
            output.append({
                "chunk": chunk,
                "score": score,
                "citation": citation
            })
        return output

    def _build_citation_id(self, chunk: DocumentChunk, rank: int) -> str:
        if chunk.source_type == "excel_sheet":
            return f"Doc-XLS-r{chunk.cell_range.replace(' ', '').replace('Rows', '').replace('Row', '')}" if chunk.cell_range else f"Doc-XLS-{rank}"
        elif chunk.source_type == "ocr_scan":
            return f"Doc-OCR-p{chunk.page_number or 1}"
        else:
            p = chunk.page_number or rank
            return f"Doc-SOP-p.{p}"

    def _build_reference_str(self, chunk: DocumentChunk) -> str:
        fname = chunk.metadata.get("filename", "Document")
        if chunk.source_type == "excel_sheet":
            return f"{fname} (Sheet: {chunk.sheet_name}, {chunk.cell_range})"
        elif chunk.source_type == "ocr_scan":
            return f"{fname} (OCR Scan, Page {chunk.page_number or 1})"
        else:
            sec = f", Section: {chunk.section_header}" if chunk.section_header else ""
            return f"{fname} (Page {chunk.page_number or 1}{sec})"

document_retriever = DocumentRetriever()
