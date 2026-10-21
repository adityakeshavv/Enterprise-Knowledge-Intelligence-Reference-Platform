import time
import re
import tempfile
import shutil
from pathlib import Path
from typing import List, Tuple
from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport

try:
    import opendataloader_pdf
    OPENDATALOADER_AVAILABLE = True
except ImportError:
    OPENDATALOADER_AVAILABLE = False

class OpenDataLoaderIngestor:
    """Structure-preserving PDF parser using OpenDataLoader PDF (XY-Cut++).
    Maintains spatial reading order across multi-column documents and complex tables.
    """

    def __init__(self, max_chunk_tokens: int = 350, overlap_tokens: int = 50):
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens

    def parse(self, file_path: Path, metadata: DocumentMetadata) -> Tuple[List[DocumentChunk], IngestionReport]:
        start_time = time.time()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.stat().st_size == 0:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="opendataloader_pdf",
                processing_time_ms=0.0,
                status="FAILED",
                error="File is empty (0 bytes)."
            )
            return [], report

        if not OPENDATALOADER_AVAILABLE:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="opendataloader_pdf",
                processing_time_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error="opendataloader-pdf package is not installed."
            )
            return [], report

        temp_dir = tempfile.mkdtemp(prefix="opendataloader_")
        chunks: List[DocumentChunk] = []

        try:
            # Convert PDF using opendataloader-pdf in quiet mode
            opendataloader_pdf.convert(
                input_path=str(path),
                output_dir=temp_dir,
                format="markdown",
                quiet=True
            )

            # Find generated markdown file
            md_files = list(Path(temp_dir).glob("*.md"))
            if not md_files:
                raise ValueError("OpenDataLoader PDF did not generate any markdown files.")

            extracted_text = md_files[0].read_text(encoding="utf-8", errors="replace")

            # Parse markdown into semantic chunks
            heading_pattern = re.compile(r"^(#{1,6}\s+.+|[A-Z0-9\.\s]{4,}:)", re.MULTILINE)
            current_header = "Structured Section"

            sections = re.split(r"\n(?=#{1,3}\s+)", extracted_text)
            page_estimate = max(1, len(extracted_text) // 2500)
            metadata.page_count = page_estimate

            for s_idx, section in enumerate(sections, start=1):
                clean_sec = section.strip()
                if not clean_sec:
                    continue

                lines = clean_sec.split("\n")
                first_line = lines[0].strip()
                if heading_pattern.match(first_line):
                    current_header = first_line.strip("# ").strip()

                words = clean_sec.split()
                if len(words) > self.max_chunk_tokens:
                    # Subdivide long section by paragraphs
                    paragraphs = clean_sec.split("\n\n")
                    buf = []
                    buf_tok = 0
                    for p in paragraphs:
                        p_words = p.split()
                        p_len = len(p_words)
                        if buf_tok + p_len > self.max_chunk_tokens and buf:
                            chunk_id = f"{metadata.doc_id}_odl_c{len(chunks) + 1}"
                            chunks.append(DocumentChunk(
                                chunk_id=chunk_id,
                                doc_id=metadata.doc_id,
                                text="\n\n".join(buf),
                                page_number=min(page_estimate, (len(chunks) // 3) + 1),
                                section_header=current_header,
                                source_type="opendataloader_markdown",
                                token_count=buf_tok,
                                metadata={
                                    "parser": "opendataloader_pdf",
                                    "section": current_header,
                                    "classification": metadata.classification,
                                    "department": metadata.department
                                }
                            ))
                            buf = [p]
                            buf_tok = p_len
                        else:
                            buf.append(p)
                            buf_tok += p_len
                    if buf:
                        chunk_id = f"{metadata.doc_id}_odl_c{len(chunks) + 1}"
                        chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            doc_id=metadata.doc_id,
                            text="\n\n".join(buf),
                            page_number=min(page_estimate, (len(chunks) // 3) + 1),
                            section_header=current_header,
                            source_type="opendataloader_markdown",
                            token_count=buf_tok,
                            metadata={
                                "parser": "opendataloader_pdf",
                                "section": current_header,
                                "classification": metadata.classification,
                                "department": metadata.department
                            }
                        ))
                else:
                    chunk_id = f"{metadata.doc_id}_odl_c{len(chunks) + 1}"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=metadata.doc_id,
                        text=clean_sec,
                        page_number=min(page_estimate, (len(chunks) // 3) + 1),
                        section_header=current_header,
                        source_type="opendataloader_markdown",
                        token_count=len(words),
                        metadata={
                            "parser": "opendataloader_pdf",
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
                pages_or_sheets=page_estimate,
                parser_used="opendataloader_pdf",
                processing_time_ms=elapsed_ms,
                status="SUCCESS" if chunks else "EMPTY_CONTENT"
            )
            return chunks, report

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="pdf",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="opendataloader_pdf",
                processing_time_ms=elapsed_ms,
                status="FAILED",
                error=f"OpenDataLoader processing error: {e}"
            )
            return [], report

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
