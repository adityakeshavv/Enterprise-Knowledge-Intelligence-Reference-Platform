from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport
from app.ingestion.excel_ingestor import ExcelIngestor
from app.ingestion.docling_ingestor import DoclingIngestor
from app.ingestion.vision_ocr import VisionOCRIngestor
from app.ingestion.pymupdf_ingestor import PyMuPDFIngestor
from app.ingestion.opendataloader_ingestor import OpenDataLoaderIngestor
from app.ingestion.local_vision_engine import LocalVisionEngine

class DocumentIngestionPipeline:
    """Unified routing pipeline for parsing enterprise documents with Tiered Hybrid Cascade.
    - Tier 1: PyMuPDF4LLM for high-speed digital text extraction (<50ms).
    - Tier 2: OpenDataLoader PDF (XY-Cut++) for multi-column and structural layouts.
    - Tier 3: Docling for complex technical sectioning and structured layouts.
    - Air-Gapped Visual Tier: LocalVisionEngine for on-premise schematics, charts, and scans.
    """

    def __init__(self):
        self.excel_ingestor = ExcelIngestor()
        self.docling_ingestor = DoclingIngestor()
        self.vision_ingestor = VisionOCRIngestor()
        self.pymupdf_ingestor = PyMuPDFIngestor()
        self.opendataloader_ingestor = OpenDataLoaderIngestor()
        self.local_vision_engine = LocalVisionEngine()

    def ingest_file(
        self,
        file_path: Path,
        metadata: Optional[DocumentMetadata] = None,
        parser_strategy: str = "auto"
    ) -> Tuple[List[DocumentChunk], IngestionReport]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {path}")

        suffix = path.suffix.lower()
        if metadata is None:
            metadata = DocumentMetadata(
                doc_id=path.stem.upper().replace("-", "_").replace(" ", "_"),
                filename=path.name,
                file_type="excel" if suffix in [".xlsx", ".xlsm", ".xls"] else ("pdf" if suffix == ".pdf" else "image_scan")
            )

        # 1. Excel files
        if suffix in [".xlsx", ".xlsm", ".xls"] or parser_strategy == "excel":
            return self.excel_ingestor.parse(path, metadata)

        # 2. PDF files - Tiered Routing
        elif suffix == ".pdf":
            if parser_strategy in ["pymupdf", "fast"]:
                return self.pymupdf_ingestor.parse(path, metadata)
            elif parser_strategy == "opendataloader":
                return self.opendataloader_ingestor.parse(path, metadata)
            elif parser_strategy in ["docling", "docling_core"]:
                return self.docling_ingestor.parse(path, metadata)
            else:
                # Default "auto" pipeline preserves Docling for verified layout extraction
                return self.docling_ingestor.parse(path, metadata)

        # 3. Image scans and diagrams
        elif suffix in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
            if parser_strategy in ["local_vision", "air_gapped"]:
                return self.local_vision_engine.parse(path, metadata)
            else:
                return self.vision_ingestor.parse(path, metadata)

        # 4. Fallback for plain text
        else:
            try:
                content = path.read_text(encoding="utf-8")
                chunk = DocumentChunk(
                    chunk_id=f"{metadata.doc_id}_txt_1",
                    doc_id=metadata.doc_id,
                    text=content,
                    page_number=1,
                    source_type="plain_text",
                    metadata={"filename": metadata.filename}
                )
                report = IngestionReport(
                    doc_id=metadata.doc_id,
                    filename=metadata.filename,
                    file_type="text",
                    chunks_created=1,
                    pages_or_sheets=1,
                    parser_used="text_reader",
                    processing_time_ms=5.0
                )
                return [chunk], report
            except Exception as e:
                raise ValueError(f"Unsupported file format: {suffix} ({e})")

    def ingest_directory(
        self,
        dir_path: Path,
        metadata_overrides: Optional[Dict[str, Dict[str, Any]]] = None,
        parser_strategy: str = "auto"
    ) -> Tuple[List[DocumentChunk], List[IngestionReport]]:
        all_chunks: List[DocumentChunk] = []
        reports: List[IngestionReport] = []
        directory = Path(dir_path)

        if not directory.exists() or not directory.is_dir():
            return all_chunks, reports

        supported_extensions = {".pdf", ".xlsx", ".xlsm", ".png", ".jpg", ".jpeg", ".txt"}
        for file in sorted(directory.iterdir()):
            if file.is_file() and file.suffix.lower() in supported_extensions:
                meta_dict = (metadata_overrides or {}).get(file.name, {})
                meta = DocumentMetadata(
                    doc_id=meta_dict.get("id", file.stem.upper().replace("-", "_")),
                    filename=file.name,
                    file_type="excel" if file.suffix.lower() in [".xlsx", ".xlsm"] else ("pdf" if file.suffix.lower() == ".pdf" else "image_scan"),
                    department=meta_dict.get("department", "General"),
                    classification=meta_dict.get("classification", "Internal")
                )
                try:
                    chunks, report = self.ingest_file(file, meta, parser_strategy=parser_strategy)
                    all_chunks.extend(chunks)
                    reports.append(report)
                except Exception as err:
                    print(f"Failed to ingest {file.name}: {err}")
                    reports.append(IngestionReport(
                        doc_id=meta.doc_id,
                        filename=file.name,
                        file_type="unknown",
                        chunks_created=0,
                        pages_or_sheets=0,
                        parser_used="none",
                        processing_time_ms=0.0,
                        status="FAILED",
                        error=str(err)
                    ))

        return all_chunks, reports

pipeline = DocumentIngestionPipeline()
