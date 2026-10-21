import time
import re
from pathlib import Path
from typing import List, Tuple, Optional
import pymupdf
import pymupdf4llm
from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport

class PyMuPDFIngestor:
    """High-speed native PDF-to-Markdown parser using PyMuPDF4LLM.
    Ideal for digital text PDFs, manuals, and standard operational documents.
    Operates in sub-50ms latency with zero GPU requirements.
    """

    def __init__(self, max_chunk_tokens: int = 350, overlap_tokens: int = 50):
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens

    def parse(self, file_path: Path, metadata: DocumentMetadata) -> Tuple[List[DocumentChunk], IngestionReport]:
        start_time = time.time()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Edge case: empty file
        if path.stat().st_size == 0:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="pymupdf4llm",
                processing_time_ms=0.0,
                status="FAILED",
                error="File is empty (0 bytes)."
            )
            return [], report

        try:
            # Open document with PyMuPDF
            doc = pymupdf.open(str(path))
        except Exception as e:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="pymupdf4llm",
                processing_time_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error=f"Corrupted or invalid PDF format: {e}"
            )
            return [], report

        # Edge case: encrypted / password-protected PDF
        if doc.is_encrypted:
            doc.close()
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="pymupdf4llm",
                processing_time_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error="PDF is encrypted / password-protected."
            )
            return [], report

        page_count = len(doc)
        metadata.page_count = page_count

        chunks: List[DocumentChunk] = []

        try:
            # Convert PDF pages to structured Markdown using pymupdf4llm
            # to_markdown supports page_chunks=True to preserve per-page grounding
            page_data = pymupdf4llm.to_markdown(doc, page_chunks=True)
        except Exception as e:
            doc.close()
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=page_count,
                parser_used="pymupdf4llm",
                processing_time_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error=f"Markdown extraction failed: {e}"
            )
            return [], report

        doc.close()

        heading_pattern = re.compile(r"^(#{1,6}\s+.+|[A-Z0-9\.\s]{4,}:)", re.MULTILINE)
        current_header = "Document Section"

        for p_idx, item in enumerate(page_data, start=1):
            page_text = item.get("text", "") if isinstance(item, dict) else str(item)
            p_num = item.get("metadata", {}).get("page", p_idx) if isinstance(item, dict) else p_idx

            if not page_text.strip():
                continue

            # Split into semantic paragraphs / sections
            paragraphs = page_text.split("\n\n")
            current_buffer = []
            current_tokens = 0

            for para in paragraphs:
                cleaned_para = para.strip()
                if not cleaned_para:
                    continue

                # Check if paragraph begins with a heading
                match = heading_pattern.match(cleaned_para)
                if match:
                    current_header = match.group(0).strip("# ").strip()

                words = cleaned_para.split()
                est_tokens = len(words)

                if current_tokens + est_tokens > self.max_chunk_tokens and current_buffer:
                    chunk_text = "\n\n".join(current_buffer)
                    chunk_id = f"{metadata.doc_id}_p{p_num}_c{len(chunks) + 1}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=metadata.doc_id,
                        text=chunk_text,
                        page_number=p_num,
                        section_header=current_header,
                        source_type="pdf_markdown",
                        token_count=current_tokens,
                        metadata={
                            "parser": "pymupdf4llm",
                            "page": p_num,
                            "section": current_header,
                            "classification": metadata.classification,
                            "department": metadata.department
                        }
                    ))
                    # Overlap with last paragraph if suitable
                    current_buffer = [cleaned_para]
                    current_tokens = est_tokens
                else:
                    current_buffer.append(cleaned_para)
                    current_tokens += est_tokens

            if current_buffer:
                chunk_text = "\n\n".join(current_buffer)
                chunk_id = f"{metadata.doc_id}_p{p_num}_c{len(chunks) + 1}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=metadata.doc_id,
                    text=chunk_text,
                    page_number=p_num,
                    section_header=current_header,
                    source_type="pdf_markdown",
                    token_count=current_tokens,
                    metadata={
                        "parser": "pymupdf4llm",
                        "page": p_num,
                        "section": current_header,
                        "classification": metadata.classification,
                        "department": metadata.department
                    }
                ))

        elapsed_ms = (time.time() - start_time) * 1000
        report = IngestionReport(
            doc_id=metadata.doc_id,
            filename=metadata.filename,
            file_type="pdf",
            chunks_created=len(chunks),
            pages_or_sheets=page_count,
            parser_used="pymupdf4llm",
            processing_time_ms=elapsed_ms,
            status="SUCCESS" if chunks else "EMPTY_CONTENT"
        )
        return chunks, report
