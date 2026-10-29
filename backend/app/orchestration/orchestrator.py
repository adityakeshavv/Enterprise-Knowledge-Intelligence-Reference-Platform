import time
import uuid
import asyncio
from typing import AsyncGenerator, Dict, Any, List, Optional

from app.orchestration.state import WorkflowState, QueryIntent
from app.orchestration.router import query_router
from app.agents.sql_agent import sql_agent
from app.agents.document_agent import document_agent
from app.agents.validation_agent import evidence_validation_agent
from app.agents.graph_builder import evidence_graph_builder
from app.agents.synthesis_agent import synthesis_agent
from app.schemas.query import QueryResponse, TraceStep, CitationItem
from app.orchestration.engine import modular_orchestrator, ModularPipelineEngine

class MultiAgentOrchestrator:
    """Coordinates specialized sub-agents into a unified, autonomous DAG execution workflow.
    Delegates to ModularPipelineEngine while providing 100% backward compatibility for all existing APIs and tests.
    """

    def __init__(
        self,
        router=query_router,
        sql_ag=sql_agent,
        doc_ag=document_agent,
        val_ag=evidence_validation_agent,
        synth_ag=synthesis_agent,
        graph_bld=evidence_graph_builder,
        engine: Optional[ModularPipelineEngine] = None
    ):
        self.router = router
        self.sql_agent = sql_ag
        self.document_agent = doc_ag
        self.validation_agent = val_ag
        self.synthesis_agent = synth_ag
        self.graph_builder = graph_bld
        self.engine = engine or modular_orchestrator

    def orchestrate(
        self,
        query_text: str,
        user_role: str = "CXO",
        industry_id: str = "manufacturing",
        department: Optional[str] = None
    ) -> QueryResponse:
        """Synchronous orchestration execution returning full QueryResponse via ModularPipelineEngine."""
        return self.engine.execute(
            query_text=query_text,
            user_role=user_role,
            industry_id=industry_id,
            department=department
        )

    async def stream_orchestration(
        self,
        query_text: str,
        user_role: str = "CXO",
        industry_id: str = "manufacturing",
        department: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronous streaming generator yielding real-time TraceStep events and final response."""
        async for item in self.engine.stream_execute(
            query_text=query_text,
            user_role=user_role,
            industry_id=industry_id,
            department=department
        ):
            yield item

multi_agent_orchestrator = MultiAgentOrchestrator()
