import time
import math
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from PIL import Image
import numpy as np

try:
    from rapidocr_onnxruntime import RapidOCR
    RAPID_OCR_AVAILABLE = True
except ImportError:
    RAPID_OCR_AVAILABLE = False

from app.ingestion.models import DocumentMetadata, DocumentChunk, IngestionReport

class LocalVisionEngine:
    """100% Air-Gapped Local Vision Engine for Technical Schematics, Charts, and Scans.
    Requires ZERO external API calls, ensuring complete enterprise data privacy.
    Combines local ONNX OCR with morphological analysis to classify visual artifacts
    (schematics, charts, inspection tags, architecture flows) and extract structured evidence.
    """

    def __init__(self):
        if RAPID_OCR_AVAILABLE:
            try:
                self.ocr = RapidOCR()
            except Exception:
                self.ocr = None
        else:
            self.ocr = None

    def analyze_image_characteristics(self, image: Image.Image) -> Dict[str, Any]:
        """Performs local computer vision morphological analysis to classify image type."""
        w, h = image.size
        img_gray = image.convert("L")
        arr = np.array(img_gray)

        dx = np.diff(arr, axis=1)
        dy = np.diff(arr, axis=0)
        grad_mag = np.sqrt(dx[:-1, :]**2 + dy[:, :-1]**2)
        edge_ratio = float(np.mean(grad_mag > 25))

        # 2. Color variance / monochrome ratio
        if image.mode in ("RGB", "RGBA"):
            rgb_arr = np.array(image.convert("RGB"))
            r, g, b = rgb_arr[:, :, 0], rgb_arr[:, :, 1], rgb_arr[:, :, 2]
            color_variance = float(np.std(r.astype(float) - g.astype(float)) + np.std(g.astype(float) - b.astype(float)))
        else:
            color_variance = 0.0

        # 3. Classify visual archetype
        if edge_ratio > 0.08 and color_variance < 15.0:
            category = "Technical Engineering Schematic / CAD Wireframe"
        elif edge_ratio > 0.05 and color_variance >= 15.0:
            category = "System Architecture / Process Flowchart"
        elif edge_ratio < 0.03:
            category = "Tabular / Form Document Scan"
        else:
            category = "Component / Physical Asset Inspection Photograph"

        return {
            "width": w,
            "height": h,
            "aspect_ratio": round(w / max(1, h), 2),
            "edge_density": round(edge_ratio, 4),
            "color_variance": round(color_variance, 2),
            "category": category
        }

    def parse(self, file_path: Path, metadata: DocumentMetadata) -> Tuple[List[DocumentChunk], IngestionReport]:
        start_time = time.time()
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if path.stat().st_size == 0:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="image_scan",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="local_vision_engine",
                processing_time_ms=0.0,
                status="FAILED",
                error="Image file is empty (0 bytes)."
            )
            return [], report

        # Check if file is an SVG vector diagram (frequently stored with .png extension)
        try:
            with open(str(path), "rb") as f_check:
                header_bytes = f_check.read(128).strip()
            if header_bytes.startswith(b"<svg") or header_bytes.startswith(b"<?xml") or b"<svg" in header_bytes:
                svg_text = path.read_text(encoding="utf-8", errors="replace")
                text_elements = re.findall(r"<text[^>]*>(.*?)</text>", svg_text, re.DOTALL)
                clean_texts = [re.sub(r"<[^>]+>", "", t).strip() for t in text_elements if t.strip()]

                visual_synthesis = (
                    f"### Visual Intelligence Analysis: {metadata.filename}\n"
                    f"- **Visual Category**: System Architecture / Process Flowchart (Vector SVG Diagram)\n"
                    f"- **Vector Format**: Scalable Vector Graphics (SVG)\n"
                    f"- **Detected Component Nodes & Labels** ({len(clean_texts)} elements):\n"
                    f"  {' | '.join(clean_texts) if clean_texts else 'Vector shapes detected.'}\n\n"
                    f"> **Air-Gapped Audit**: Processed locally without external network transfer."
                )
                chunk = DocumentChunk(
                    chunk_id=f"{metadata.doc_id}_vis_1",
                    doc_id=metadata.doc_id,
                    text=visual_synthesis,
                    page_number=1,
                    section_header="Visual Analysis - System Architecture Flowchart",
                    source_type="local_vision_analysis",
                    token_count=len(visual_synthesis.split()),
                    metadata={
                        "parser": "local_vision_engine",
                        "category": "System Architecture / Process Flowchart",
                        "format": "SVG_VECTOR",
                        "labels_count": len(clean_texts),
                        "classification": metadata.classification,
                        "department": metadata.department,
                        "air_gapped": True
                    }
                )
                elapsed_ms = (time.time() - start_time) * 1000
                report = IngestionReport(
                    doc_id=metadata.doc_id,
                    filename=metadata.filename,
                    file_type="image_scan",
                    chunks_created=1,
                    pages_or_sheets=1,
                    parser_used="local_vision_engine",
                    processing_time_ms=elapsed_ms,
                    status="SUCCESS"
                )
                return [chunk], report

            with Image.open(str(path)) as img:
                img_copy = img.copy()
        except Exception as e:
            report = IngestionReport(
                doc_id=metadata.doc_id,
                filename=metadata.filename,
                file_type="image_scan",
                chunks_created=0,
                pages_or_sheets=0,
                parser_used="local_vision_engine",
                processing_time_ms=(time.time() - start_time) * 1000,
                status="FAILED",
                error=f"Unreadable or corrupted image file: {e}"
            )
            return [], report

        # Extract morphology
        morphology = self.analyze_image_characteristics(img_copy)

        # Extract text elements and labels using local ONNX RapidOCR
        detected_labels = []
        full_transcription = []

        if self.ocr is not None:
            try:
                ocr_result, _ = self.ocr(str(path))
                if ocr_result:
                    for item in ocr_result:
                        # item format: [box, text, score]
                        if len(item) >= 2:
                            box = item[0]
                            text = str(item[1]).strip()
                            score = float(item[2]) if len(item) > 2 else 1.0
                            if text:
                                full_transcription.append(text)
                                detected_labels.append({
                                    "text": text,
                                    "confidence": round(score, 3),
                                    "bounding_box": box
                                })
            except Exception as ocr_err:
                full_transcription.append(f"[Local OCR Warning: {ocr_err}]")

        # Synthesize local structured visual representation
        transcribed_text = " | ".join(full_transcription) if full_transcription else "No embedded text annotations detected."
        
        visual_synthesis = (
            f"### Visual Intelligence Analysis: {metadata.filename}\n"
            f"- **Visual Category**: {morphology['category']}\n"
            f"- **Dimensions**: {morphology['width']}x{morphology['height']} px (Aspect Ratio: {morphology['aspect_ratio']})\n"
            f"- **Edge Complexity**: {morphology['edge_density']} (Structural Line Density)\n"
            f"- **Detected Annotations / Component Labels** ({len(detected_labels)} items):\n"
            f"  {transcribed_text}\n\n"
            f"> **Air-Gapped Audit**: Processed locally without external network transfer."
        )

        chunk = DocumentChunk(
            chunk_id=f"{metadata.doc_id}_vis_1",
            doc_id=metadata.doc_id,
            text=visual_synthesis,
            page_number=1,
            section_header=f"Visual Analysis - {morphology['category']}",
            source_type="local_vision_analysis",
            token_count=len(visual_synthesis.split()),
            metadata={
                "parser": "local_vision_engine",
                "category": morphology["category"],
                "width": morphology["width"],
                "height": morphology["height"],
                "labels_count": len(detected_labels),
                "classification": metadata.classification,
                "department": metadata.department,
                "air_gapped": True
            }
        )

        elapsed_ms = (time.time() - start_time) * 1000
        report = IngestionReport(
            doc_id=metadata.doc_id,
            filename=metadata.filename,
            file_type="image_scan",
            chunks_created=1,
            pages_or_sheets=1,
            parser_used="local_vision_engine",
            processing_time_ms=elapsed_ms,
            status="SUCCESS"
        )
        return [chunk], report
