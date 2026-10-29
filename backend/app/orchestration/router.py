import re
from typing import List
from app.orchestration.state import QueryIntent, SubTask, ExecutionPlan
from app.orchestration.contracts import IntentCategory
from app.agents.query_understanding_agent import query_understanding_agent
from app.agents.intent_classification_agent import intent_classification_agent
from app.agents.routing_agent import routing_agent
from app.agents.investigation_planner import investigation_planner

class QueryRouter:
    """Intelligent query intent classifier and DAG execution planner.
    Acts as a facade bridging existing callers with the modular 9-stage pipeline.
    """

    def __init__(
        self,
        understanding_agent=query_understanding_agent,
        classification_agent=intent_classification_agent,
        routing_ag=routing_agent,
        planner=investigation_planner
    ):
        self.understanding_agent = understanding_agent
        self.classification_agent = classification_agent
        self.routing_agent = routing_ag
        self.planner = planner

        # Signal patterns preserved for fast-path / fallback evaluation
        self.sql_signals = [
            r"\b(?:downtime|hours?|minutes?|oee|defect|scrap|ppm|telemetry|cost|loss|units|target|actual|events?|work orders?)\b",
            r"\b(?:line[ -]?[123]|plant[ -]?[ab]|supplier|batch|shift)\b",
            r"\b(?:sum|average|avg|count|highest|lowest|top|most)\b"
        ]
        self.doc_signals = [
            r"\b(?:sop|procedure|manual|protocol|action|recommendation|solution|preventive|repair|fix|incident logs?)\b",
            r"\b(?:depressuriz|replenish|seal|flush|synthetic|technician|inspection|instructions?)\b",
            r"\b(?:how to|what (?:steps|actions)|guidelines?|standard operating)\b"
        ]

    def classify_intent(self, query: str) -> QueryIntent:
        """Classifies incoming query intent into structured, document, or cross-source."""
        understanding = self.understanding_agent.process(query)
        classification = self.classification_agent.classify(understanding)

        if classification.predicted_intent == IntentCategory.STRUCTURED_TELEMETRY:
            return QueryIntent.STRUCTURED_ONLY
        elif classification.predicted_intent == IntentCategory.PROCEDURAL_GUIDANCE:
            return QueryIntent.DOCUMENT_ONLY
        else:
            return QueryIntent.CROSS_SOURCE_HYBRID

    def create_plan(self, query: str) -> ExecutionPlan:
        """Generates an execution plan with subtasks matching the query requirements."""
        understanding = self.understanding_agent.process(query)
        classification = self.classification_agent.classify(understanding)
        routing = self.routing_agent.route(understanding, classification)
        plan = self.planner.plan(understanding, classification, routing)

        intent = self.classify_intent(query)
        subtasks: List[SubTask] = []

        for t in plan.tasks:
            agent_name = "document_intelligence_agent" if "unstructured" in t.assigned_agent else "structured_data_agent"
            agent_label = "Document Intelligence Agent" if "unstructured" in t.assigned_agent else "Structured Data Agent"
            subtasks.append(
                SubTask(
                    task_id=t.task_id,
                    agent_name=agent_name,
                    agent_label=agent_label,
                    sub_query=query,
                    target_source=t.source_type,
                    dependencies=t.dependencies
                )
            )

        reasoning = (
            f"Modular investigation plan ({classification.predicted_intent.value}) prepared "
            f"with {len(subtasks)} subtask(s) across authorized source adapters."
        )

        return ExecutionPlan(
            intent=intent,
            subtasks=subtasks,
            is_parallel=True,
            reasoning=reasoning
        )

query_router = QueryRouter()
