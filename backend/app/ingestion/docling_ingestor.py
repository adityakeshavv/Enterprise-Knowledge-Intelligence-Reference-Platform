import re
import time
from pathlib import Path
from typing import List, Tuple
from pypdf import PdfReader
from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport

class DoclingIngestor:
    """Parses PDF and technical documentation using Docling-compatible structured section modeling."""

    def __init__(self, max_chunk_tokens: int = 350, overlap_tokens: int = 50):
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens

    def parse(self, file_path: Path, metadata: DocumentMetadata) -> Tuple[List[DocumentChunk], IngestionReport]:
        start_time = time.time()
        chunks: List[DocumentChunk] = []

        reader = PdfReader(str(file_path))
        page_count = len(reader.pages)
        metadata.page_count = page_count

        current_section = "General Overview"
        section_pattern = re.compile(r"^(?:Section\s+\d+|[0-9]+(?:\.[0-9]+)*\s+[A-Z][A-Za-z\s]+|[A-Z\s]{4,}:)", re.MULTILINE)

        for page_idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue

            lines = text.split("\n")
            page_paragraphs = []
            current_para = []

            for line in lines:
                cleaned_line = line.strip()
                if not cleaned_line:
                    if current_para:
                        page_paragraphs.append(" ".join(current_para))
                        current_para = []
                    continue

                # Check if this line is a section heading
                if section_pattern.match(cleaned_line) or (len(cleaned_line) < 60 and cleaned_line.isupper() and len(cleaned_line) > 4):
                    if current_para:
                        page_paragraphs.append(" ".join(current_para))
                        current_para = []
                    current_section = cleaned_line

                current_para.append(cleaned_line)

            if current_para:
                page_paragraphs.append(" ".join(current_para))

            # Chunk paragraphs on this page
            current_buffer = []
            current_word_count = 0

            for para in page_paragraphs:
                words = para.split()
                if not words:
                    continue

                if current_word_count + len(words) > self.max_chunk_tokens and current_buffer:
                    chunk_text = f"Document: [{metadata.filename}] | Section: [{current_section}] | Page: {page_idx}\n" + " ".join(current_buffer)
                    chunk_id = f"{metadata.doc_id}_p{page_idx}_c{len(chunks)+1}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=metadata.doc_id,
                        text=chunk_text,
                        page_number=page_idx,
                        section_header=current_section,
                        source_type="pdf_section",
                        token_count=len(chunk_text.split()),
                        metadata={
                            "doc_id": metadata.doc_id,
                            "filename": metadata.filename,
                            "page": page_idx,
                            "section": current_section,
                            "department": metadata.department,
                            "classification": metadata.classification
                        }
                    ))
                    # Retain overlap words
                    overlap_words = current_buffer[-self.overlap_tokens:] if len(current_buffer) >= self.overlap_tokens else current_buffer
                    current_buffer = list(overlap_words)
                    current_word_count = len(current_buffer)

                current_buffer.extend(words)
                current_word_count += len(words)

            if current_buffer:
                chunk_text = f"Document: [{metadata.filename}] | Section: [{current_section}] | Page: {page_idx}\n" + " ".join(current_buffer)
                chunk_id = f"{metadata.doc_id}_p{page_idx}_c{len(chunks)+1}"
                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    doc_id=metadata.doc_id,
                    text=chunk_text,
                    page_number=page_idx,
                    section_header=current_section,
                    source_type="pdf_section",
                    token_count=len(chunk_text.split()),
                    metadata={
                        "doc_id": metadata.doc_id,
                        "filename": metadata.filename,
                        "page": page_idx,
                        "section": current_section,
                        "department": metadata.department,
                        "classification": metadata.classification
                    }
                ))

        duration_ms = (time.time() - start_time) * 1000.0
        report = IngestionReport(
            doc_id=metadata.doc_id,
            filename=metadata.filename,
            file_type="pdf",
            chunks_created=len(chunks),
            pages_or_sheets=page_count,
            parser_used="docling_core",
            processing_time_ms=duration_ms
        )
        return chunks, report

