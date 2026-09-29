import time
from typing import Dict, Any, List
from app.agents.base import BaseAgent, AgentTraceStep
from app.core.logging import logger

class QueryRouterAgent(BaseAgent):
    """Parses user intent, checks industry terminology, and plans multi-agent tasks."""

    def __init__(self):
        super().__init__(name="Query Router & Planner", role="Intent Classification & Orchestration Planning")

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        query = context.get("query", "").lower()
        pack = context.get("industry_pack", {})
        terms = pack.get("terminology", {}).get("terms", [])
        
        # Match domain terms
        matched_terms = []
        for t in terms:
            term_name = t.get("term", "").lower()
            synonyms = [s.lower() for s in t.get("synonyms", [])]
            if term_name in query or any(syn in query for syn in synonyms):
                matched_terms.append(t.get("term"))

        # Determine agent requirements
        requires_structured = any(w in query for w in ["downtime", "hours", "rate", "cost", "ppm", "sales", "rank", "units", "compare", "lines", "numbers"])
        requires_documents = any(w in query for w in ["action", "procedure", "sop", "memo", "manual", "investigation", "reduce", "factor", "reason", "why", "corrective"])
        requires_external = any(w in query for w in ["advisory", "vendor", "bulletin", "market", "supplier", "regulatory"])
        
        # If ambiguous, default to full multi-source intelligence
        if not requires_structured and not requires_documents:
            requires_structured = True
            requires_documents = True

        plan = {
            "query": context.get("query"),
            "matched_terms": matched_terms,
            "agents_to_invoke": [],
            "plan_summary": ""
        }

        if requires_structured:
            plan["agents_to_invoke"].append("StructuredDataAgent")
        if requires_documents:
            plan["agents_to_invoke"].append("DocumentAgent")
        if requires_external:
            plan["agents_to_invoke"].append("ExternalAgent")
            
        plan["plan_summary"] = f"Decomposed query into {len(plan['agents_to_invoke'])} agent tasks: {', '.join(plan['agents_to_invoke'])}"
        
        duration = (time.time() - start) * 1000
        trace = AgentTraceStep(
            agent=self.name,
            action=plan["plan_summary"],
            duration_ms=round(duration, 2),
            details={"matched_terms": matched_terms, "planned_agents": plan["agents_to_invoke"]}
        )
        
        return {
            "plan": plan,
            "trace": trace.model_dump()
        }
