from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class DocumentMetadata(BaseModel):
    doc_id: str
    filename: str
    file_type: str  # "excel", "pdf", "image_scan", "docx"
    department: str = "General"
    classification: str = "Internal"  # "Public", "Internal", "Confidential", "Restricted"
    version: str = "1.0"
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    page_count: int = 1
    custom_metadata: Dict[str, Any] = {}

class DocumentChunk(BaseModel):
    chunk_id: str
    doc_id: str
    text: str
    page_number: Optional[int] = None
    section_header: Optional[str] = None
    sheet_name: Optional[str] = None
    cell_range: Optional[str] = None
    source_type: str = "document"  # "pdf_section", "excel_sheet", "ocr_scan", "diagram"
    bounding_box: Optional[Dict[str, float]] = None
    token_count: int = 0
    metadata: Dict[str, Any] = {}

class IngestionReport(BaseModel):
    doc_id: str
    filename: str
    file_type: str
    chunks_created: int
    pages_or_sheets: int
    parser_used: str  # "openpyxl", "docling_core", "rapidocr", "vision"
    processing_time_ms: float
    status: str = "SUCCESS"
    error: Optional[str] = None
