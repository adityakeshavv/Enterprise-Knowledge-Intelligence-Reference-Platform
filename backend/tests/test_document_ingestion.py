import pytest
from pathlib import Path
from app.ingestion.excel_ingestor import ExcelIngestor
from app.ingestion.docling_ingestor import DoclingIngestor
from app.ingestion.vision_ocr import VisionOCRIngestor
from app.ingestion.pipeline import DocumentIngestionPipeline
from app.ingestion.models import DocumentMetadata

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "industries" / "manufacturing" / "data" / "unstructured"

def test_excel_ingestor_with_openpyxl():
    excel_file = DATA_DIR / "Plant_A_Shift_Incident_Logs_Q1.xlsx"
    assert excel_file.exists(), f"Excel file missing at {excel_file}"

    ingestor = ExcelIngestor()
    meta = DocumentMetadata(doc_id="TEST_XLS", filename=excel_file.name, file_type="excel")
    chunks, report = ingestor.parse(excel_file, meta)

    assert report.parser_used == "openpyxl"
    assert report.chunks_created >= 2
    assert report.status == "SUCCESS"

    # Verify sheet names and cell range metadata
    sheet_names = {c.sheet_name for c in chunks}
    assert "Shift_Incidents" in sheet_names
    assert "Component_Replacements" in sheet_names

    # Verify exact contents extracted
    full_text = " ".join(c.text for c in chunks)
    assert "INC-101" in full_text
    assert "AFD-SEAL-882" in full_text

def test_docling_pdf_ingestor():
    sop_file = DATA_DIR / "SOP-Maint-Line3-Hydraulics-v2.pdf"
    assert sop_file.exists(), f"PDF missing at {sop_file}"

    ingestor = DoclingIngestor()
    meta = DocumentMetadata(doc_id="TEST_SOP", filename=sop_file.name, file_type="pdf", department="Reliability")
    chunks, report = ingestor.parse(sop_file, meta)

    assert report.parser_used == "docling_core"
    assert len(chunks) >= 2
    assert report.pages_or_sheets >= 2

    # Verify section extraction
    sections = [c.section_header for c in chunks if c.section_header]
    full_text = " ".join(c.text for c in chunks)
    assert any("Section" in s for s in sections)
    assert "250 operational hours" in full_text
    assert "41%" in full_text

def test_vision_ocr_ingestor_rapidocr():
    img_file = DATA_DIR / "Inspection_Scan_Pump_Seal.png"
    assert img_file.exists(), f"Scan image missing at {img_file}"

    ingestor = VisionOCRIngestor()
    meta = DocumentMetadata(doc_id="TEST_SCAN", filename=img_file.name, file_type="image_scan")
    chunks, report = ingestor.parse(img_file, meta)

    assert report.chunks_created >= 1
    assert report.status == "SUCCESS"

    ocr_text = chunks[0].text
    # RapidOCR should detect key inspection markers
    assert "AFD-SEAL-882" in ocr_text or "SEAL" in ocr_text
    assert "409" in ocr_text or "PASSED" in ocr_text or "INSPECTION" in ocr_text

def test_unified_pipeline_directory_ingest():
    pipeline = DocumentIngestionPipeline()
    chunks, reports = pipeline.ingest_directory(DATA_DIR)

    assert len(chunks) >= 5
    assert len(reports) == 4

    parsers = {r.parser_used for r in reports}
    assert "openpyxl" in parsers
    assert "docling_core" in parsers
