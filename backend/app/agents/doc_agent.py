import time
from typing import Dict, Any, List
from app.agents.base import BaseAgent, AgentTraceStep

# Curated synthetic enterprise document passages for reference demonstration
SYNTHETIC_PASSAGES = [
    {
        "doc_id": "sop_mnt_402",
        "doc_name": "SOP-MNT-402: Hydraulic Assembly & Valve Maintenance",
        "page": 14,
        "section": "Section 4.2: Preventative Flushing Protocols",
        "text": "Quarterly solvent flushing of high-pressure proportional valves has demonstrated a 68% decrease in seizure incidents caused by particulate contamination and varnish buildup.",
        "keywords": ["hydraulic", "valve", "flushing", "seizure", "68%", "preventative", "reduce"]
    },
    {
        "doc_id": "plant_a_q3_memo",
        "doc_name": "Plant A Engineering Root Cause Investigation Memo: Line 2 Outage",
        "page": 2,
        "section": "Section 3.1: Post-Incident Actuator Teardown Findings",
        "text": "Upon full teardown of the Line 2 robotic arm hydraulic manifold on August 16, the mechanical proportional valve was verified clean and undamaged. The root cause was an intermittent upstream pressure sensor calibration drift (Sensor PS-204) triggering false emergency stops on the PLC bus.",
        "keywords": ["plant a", "downtime", "factors", "line 2", "teardown", "sensor", "calibration", "discrepancy", "plc", "upstream", "memo", "disagree", "outage"]
    },
    {
        "doc_id": "oem_vortex_arm",
        "doc_name": "OEM Maintenance Manual: Vortex Robotic Arm Model V3",
        "page": 48,
        "section": "Section 6.4: Thermal Operating Limits",
        "text": "The Vortex Robotic Arm Model V3 operating ambient temperature must not exceed 45°C. When ambient operating temperatures exceed 38°C, hydraulic fluid degradation accelerates, requiring ISO VG 46 high-thermal-stability fluid.",
        "keywords": ["temperature", "ambient", "oem", "manual", "viscosity", "iso vg 46", "45°c"]
    },
    {
        "doc_id": "supplier_audit_apex",
        "doc_name": "Supplier Quality Audit: Apex Hydraulics Inc",
        "page": 5,
        "section": "Section 2.4: Corrective Action Requests",
        "text": "Corrective Action Request (CAR-2026-09) issued following lot defect rate exceeding 840 PPM due to sub-tier machining tolerance drift in valve spool lands.",
        "keywords": ["supplier", "apex", "car", "defect", "ppm", "corrective", "quality"]
    }
]

class DocumentIntelligenceAgent(BaseAgent):
    """Retrieves and extracts relevant passages from enterprise documents with page/section citations."""

    def __init__(self):
        super().__init__(name="Document Intelligence Agent", role="Unstructured Document Retrieval & Section Extraction")

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        query_text = context.get("query", "").lower()
        
        # Keyword-based passage matching for reference demonstration
        matched = []
        for passage in SYNTHETIC_PASSAGES:
            score = sum(1 for kw in passage["keywords"] if kw in query_text)
            if score > 0:
                matched.append((score, passage))
                
        # If no specific keyword match, return top relevant operational docs
        if not matched:
            matched = [(1, p) for p in SYNTHETIC_PASSAGES[:2]]
        else:
            matched.sort(key=lambda x: x[0], reverse=True)

        selected_passages = [p[1] for p in matched[:3]]
        duration = (time.time() - start) * 1000

        doc_names = list(set(p["doc_name"].split(":")[0] for p in selected_passages))
        trace = AgentTraceStep(
            agent=self.name,
            action=f"Retrieved {len(selected_passages)} sections from: {', '.join(doc_names)}",
            duration_ms=round(duration, 2),
            details={"passages_count": len(selected_passages), "sources": doc_names}
        )

        return {
            "passages": selected_passages,
            "trace": trace.model_dump()
        }
