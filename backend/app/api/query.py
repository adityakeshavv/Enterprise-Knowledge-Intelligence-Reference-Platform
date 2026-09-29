import time
import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Security, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.core.logging import audit_logger, logger
from app.config_loader.loader import config_loader
from app.agents.router import QueryRouterAgent
from app.agents.data_agent import StructuredDataAgent
from app.agents.doc_agent import DocumentIntelligenceAgent
from app.agents.ext_agent import ExternalIntelligenceAgent
from app.agents.validation_agent import EvidenceValidationAgent
from app.agents.synthesis_agent import SynthesisAgent

router = APIRouter(prefix="/query", tags=["Query Engine"])

# Initialize agents
router_agent = QueryRouterAgent()
data_agent = StructuredDataAgent()
doc_agent = DocumentIntelligenceAgent()
ext_agent = ExternalIntelligenceAgent()
validation_agent = EvidenceValidationAgent()
synthesis_agent = SynthesisAgent()

class QueryRequest(BaseModel):
    query: str
    industry_id: str = "manufacturing"
    workspace_id: Optional[str] = "plant_a"
    scenario_id: Optional[str] = None

@router.post("")
async def execute_query(req: QueryRequest, user: dict = Security(get_current_user)):
    """Executes multi-agent query across structured and unstructured knowledge sources."""
    start_time = time.time()
    query_id = f"qry_{uuid.uuid4().hex[:8]}"

    # 1. Fetch Industry Configuration Pack
    pack = config_loader.get_industry_pack(req.industry_id)
    if not pack:
        raise HTTPException(status_code=400, detail=f"Invalid industry_id '{req.industry_id}'.")

    # Shared execution context (Blackboard)
    context: Dict[str, Any] = {
        "query_id": query_id,
        "query": req.query,
        "industry_id": req.industry_id,
        "workspace_id": req.workspace_id,
        "industry_pack": pack,
        "user": user
    }

    agent_traces = []

    # 2. Planning Stage (Query Router)
    router_res = await router_agent.process(context)
    context["plan"] = router_res["plan"]
    agent_traces.append(router_res["trace"])

    # 3. Retrieval & Data Gathering
    # 3a. Structured Data Agent
    data_res = await data_agent.process(context)
    context["structured_data"] = data_res["structured_data"]
    context["sql_executed"] = data_res["sql_executed"]
    agent_traces.append(data_res["trace"])

    # 3b. Document Intelligence Agent
    doc_res = await doc_agent.process(context)
    context["passages"] = doc_res["passages"]
    agent_traces.append(doc_res["trace"])

    # 3c. External Intelligence Agent
    ext_res = await ext_agent.process(context)
    context["external_intelligence"] = ext_res["external_intelligence"]
    agent_traces.append(ext_res["trace"])

    # 4. Evidence Validation & Conflict Detection
    val_res = await validation_agent.process(context)
    context["validation"] = val_res
    agent_traces.append(val_res["trace"])

    # 5. Executive Synthesis
    synth_res = await synthesis_agent.process(context)
    agent_traces.append(synth_res["trace"])

    total_latency_ms = round((time.time() - start_time) * 1000, 2)

    # 6. Structured Audit Logging
    sources_accessed = []
    if context.get("sql_executed"):
        sources_accessed.append({"type": "database", "query": context["sql_executed"]})
    for p in context.get("passages", []):
        sources_accessed.append({"type": "document", "name": p["doc_name"], "page": p["page"]})

    audit_logger.record_event(
        event_type="EXECUTIVE_QUERY",
        user=user,
        industry_id=req.industry_id,
        query=req.query,
        agents_invoked=[t["agent"] for t in agent_traces],
        sources_accessed=sources_accessed,
        latency_ms=total_latency_ms,
        grounding_score=val_res.get("grounding_score", 0.0),
        conflict_detected=len(val_res.get("conflicts", [])) > 0,
        status="SUCCESS",
        metadata={"query_id": query_id}
    )

    # 7. Construct Final Executive Response Payload
    return {
        "query_id": query_id,
        "industry_id": req.industry_id,
        "execution_time_ms": total_latency_ms,
        "executive_summary": synth_res["executive_summary"],
        "key_findings": synth_res["key_findings"],
        "metrics_table": synth_res["metrics_table"],
        "grounding_confidence": val_res["grounding_score"],
        "citations": val_res["citations"],
        "conflicts": val_res["conflicts"],
        "agent_trace": agent_traces
    }
