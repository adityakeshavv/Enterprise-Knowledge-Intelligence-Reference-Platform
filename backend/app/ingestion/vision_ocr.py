import os
import time
from pathlib import Path
from typing import List, Tuple, Optional
from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport

class VisionOCRIngestor:
    """Extracts text, annotations, and tables from images and scanned documents using RapidOCR and optional Gemini Vision."""

    def __init__(self):
        self._rapid_ocr = None
        self._has_gemini = bool(os.environ.get("GEMINI_API_KEY"))

    def _get_ocr(self):
        if self._rapid_ocr is None:
            try:
                from rapidocr_onnxruntime import RapidOCR
                self._rapid_ocr = RapidOCR()
            except Exception as e:
                print(f"Warning: Failed to initialize RapidOCR: {e}")
                self._rapid_ocr = None
        return self._rapid_ocr

    def parse(self, file_path: Path, metadata: DocumentMetadata) -> Tuple[List[DocumentChunk], IngestionReport]:
        start_time = time.time()
        chunks: List[DocumentChunk] = []
        parser_used = "rapidocr"

        # Check if Gemini Vision can be used
        if self._has_gemini:
            try:
                from google import genai
                client = genai.Client()
                with open(file_path, "rb") as img_file:
                    image_bytes = img_file.read()
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        "Perform an exhaustive technical transcription of this scanned engineering inspection document. Extract all timestamps, part numbers, technician notes, stamp text, and inspection ratings.",
                        genai.types.Part.from_bytes(data=image_bytes, mime_type="image/png")
                    ]
                )
                if response and response.text:
                    chunk_text = f"Scanned Inspection Scan (Gemini Vision OCR): [{metadata.filename}]\n{response.text}"
                    chunk_id = f"{metadata.doc_id}_vision_p1"
                    chunks.append(DocumentChunk(
                        chunk_id=chunk_id,
                        doc_id=metadata.doc_id,
                        text=chunk_text,
                        page_number=1,
                        section_header="Vision Document Transcription",
                        source_type="ocr_scan",
                        token_count=len(chunk_text.split()),
                        metadata={"filename": metadata.filename, "engine": "gemini-2.5-flash"}
                    ))
                    parser_used = "gemini_vision"
            except Exception as e:
                print(f"Gemini vision call failed, falling back to RapidOCR: {e}")

        # Fallback to RapidOCR if no chunks yet
        if not chunks:
            ocr_engine = self._get_ocr()
            if ocr_engine is not None:
                try:
                    result, elapse_list = ocr_engine(str(file_path))
                    if result:
                        extracted_lines = []
                        for item in result:
                            # item: [box, text, score]
                            box, text, score = item[0], item[1], item[2]
                            try:
                                score_val = float(score)
                                extracted_lines.append(f"{text} (conf: {score_val:.2f})")
                            except Exception:
                                extracted_lines.append(f"{text}")

                        full_ocr_text = "\n".join(extracted_lines)
                        chunk_text = f"Scanned Equipment Inspection Document [{metadata.filename}] | OCR Extraction:\n{full_ocr_text}"
                        chunk_id = f"{metadata.doc_id}_ocr_p1"
                        chunks.append(DocumentChunk(
                            chunk_id=chunk_id,
                            doc_id=metadata.doc_id,
                            text=chunk_text,
                            page_number=1,
                            section_header="Scanned Inspection Note",
                            source_type="ocr_scan",
                            token_count=len(chunk_text.split()),
                            metadata={"filename": metadata.filename, "engine": "RapidOCR"}
                        ))
                except Exception as err:
                    print(f"RapidOCR parsing error: {err}")

        # Fallback if image has no readable text
        if not chunks:
            chunk_id = f"{metadata.doc_id}_empty"
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                doc_id=metadata.doc_id,
                text=f"Image Scan [{metadata.filename}]: No text or annotations detected by OCR engine.",
                page_number=1,
                source_type="ocr_scan",
                metadata={"filename": metadata.filename}
            ))

        duration_ms = (time.time() - start_time) * 1000.0
        report = IngestionReport(
            doc_id=metadata.doc_id,
            filename=metadata.filename,
            file_type="image_scan",
            chunks_created=len(chunks),
            pages_or_sheets=1,
            parser_used=parser_used,
            processing_time_ms=duration_ms
        )
        return chunks, report
