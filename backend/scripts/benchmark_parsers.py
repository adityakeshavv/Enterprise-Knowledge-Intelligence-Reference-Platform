import time
import os
import sys
import psutil
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from typing import Dict, Any, List

from app.ingestion.models import DocumentMetadata
from app.ingestion.pymupdf_ingestor import PyMuPDFIngestor
from app.ingestion.opendataloader_ingestor import OpenDataLoaderIngestor
from app.ingestion.docling_ingestor import DoclingIngestor
from app.ingestion.local_vision_engine import LocalVisionEngine

def get_memory_mb() -> float:
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def benchmark_document(pdf_path: Path) -> List[Dict[str, Any]]:
    results = []
    meta = DocumentMetadata(
        doc_id=pdf_path.stem.upper().replace("-", "_"),
        filename=pdf_path.name,
        file_type="pdf"
    )

    parsers = [
        ("PyMuPDF4LLM (Tier 1 Fast)", PyMuPDFIngestor()),
        ("OpenDataLoader PDF (Tier 2 XY-Cut++)", OpenDataLoaderIngestor()),
        ("Docling (Tier 3 Layout)", DoclingIngestor())
    ]

    for name, parser in parsers:
        mem_before = get_memory_mb()
        t0 = time.perf_counter()
        try:
            chunks, report = parser.parse(pdf_path, meta)
            elapsed_ms = (time.perf_counter() - t0) * 1000
            mem_after = get_memory_mb()
            total_chars = sum(len(c.text) for c in chunks)
            total_words = sum(len(c.text.split()) for c in chunks)

            results.append({
                "Document": pdf_path.name,
                "Parser": name,
                "Status": report.status,
                "Latency (ms)": round(elapsed_ms, 1),
                "Chunks": len(chunks),
                "Words": total_words,
                "Chars": total_chars,
                "Mem Delta (MB)": round(max(0, mem_after - mem_before), 1)
            })
        except Exception as e:
            results.append({
                "Document": pdf_path.name,
                "Parser": name,
                "Status": f"ERROR: {e}",
                "Latency (ms)": 0,
                "Chunks": 0,
                "Words": 0,
                "Chars": 0,
                "Mem Delta (MB)": 0
            })

    return results

def benchmark_vision_images(img_paths: List[Path]) -> List[Dict[str, Any]]:
    engine = LocalVisionEngine()
    results = []
    for img_path in img_paths:
        meta = DocumentMetadata(
            doc_id=img_path.stem.upper(),
            filename=img_path.name,
            file_type="image_scan"
        )
        mem_before = get_memory_mb()
        t0 = time.perf_counter()
        chunks, report = engine.parse(img_path, meta)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        mem_after = get_memory_mb()
        chunk = chunks[0] if chunks else None

        results.append({
            "Image": img_path.name,
            "Engine": "LocalVisionEngine (Air-Gapped ONNX)",
            "Category": chunk.metadata.get("category", "Unknown") if chunk else "N/A",
            "Latency (ms)": round(elapsed_ms, 1),
            "Labels Detected": chunk.metadata.get("labels_count", 0) if chunk else 0,
            "Mem Delta (MB)": round(max(0, mem_after - mem_before), 1)
        })
    return results

def main():
    base_dir = Path("c:/Users/KIIT0001/Desktop/Enterprise Knowlegde Interface")
    unstructured_dir = base_dir / "config/industries/manufacturing/data/unstructured"
    docs_dir = base_dir / "Documents"

    test_pdfs = [
        unstructured_dir / "SOP-Maint-Line3-Hydraulics-v2.pdf",
        unstructured_dir / "Supplier_Quality_Bulletin_Apex_2024.pdf",
    ]
    # Include PRD if present
    prd = docs_dir / "Nebula9_Enterprise_Knowledge_Intelligence_Reference_Platform_PRD.pdf"
    if prd.exists():
        test_pdfs.append(prd)

    test_images = [
        unstructured_dir / "Inspection_Scan_Pump_Seal.png",
        docs_dir / "Architecture_Diagram.png"
    ]

    print("\n=========================================================================================")
    print("      NEBULA9 MULTI-PARSER BENCHMARK (PyMuPDF4LLM vs OpenDataLoader vs Docling)           ")
    print("=========================================================================================\n")

    all_pdf_results = []
    for pdf in test_pdfs:
        if pdf.exists():
            print(f"--> Benchmarking: {pdf.name} ...")
            res = benchmark_document(pdf)
            all_pdf_results.extend(res)

    print("\n### PDF Parser Benchmark Results:\n")
    print(f"| {'Document':<35} | {'Parser':<35} | {'Latency (ms)':<14} | {'Chunks':<7} | {'Words':<8} | {'Mem (MB)':<9} |")
    print(f"|{'-'*37}|{'-'*37}|{'-'*16}|{'-'*9}|{'-'*10}|{'-'*11}|")
    for r in all_pdf_results:
        print(f"| {r['Document']:<35} | {r['Parser']:<35} | {r['Latency (ms)']:<14} | {r['Chunks']:<7} | {r['Words']:<8} | {r['Mem Delta (MB)']:<9} |")

    print("\n--> Benchmarking Air-Gapped Local Vision Engine ...")
    valid_images = [img for img in test_images if img.exists()]
    img_results = benchmark_vision_images(valid_images)

    print("\n### Local Vision Engine Benchmark Results:\n")
    print(f"| {'Image':<32} | {'Category':<40} | {'Latency (ms)':<14} | {'Labels':<8} |")
    print(f"|{'-'*34}|{'-'*42}|{'-'*16}|{'-'*10}|")
    for r in img_results:
        print(f"| {r['Image']:<32} | {r['Category']:<40} | {r['Latency (ms)']:<14} | {r['Labels Detected']:<8} |")

    print("\nBenchmark successfully completed.\n")

if __name__ == "__main__":
    main()
