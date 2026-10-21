import re
from typing import List
from app.orchestration.state import QueryIntent, SubTask, ExecutionPlan

class QueryRouter:
    """Intelligent query intent classifier and DAG execution planner."""

    def __init__(self):
        # Patterns indicative of structured relational telemetry / KPIs
        self.sql_signals = [
            r"\b(?:downtime|hours?|minutes?|oee|defect|scrap|ppm|telemetry|cost|loss|units|target|actual|events?|work orders?)\b",
            r"\b(?:line[ -]?[123]|plant[ -]?[ab]|supplier|batch|shift)\b",
            r"\b(?:sum|average|avg|count|highest|lowest|top|most)\b"
        ]
        
        # Patterns indicative of unstructured manuals / SOPs / procedures
        self.doc_signals = [
            r"\b(?:sop|procedure|manual|protocol|action|recommendation|solution|preventive|repair|fix|incident logs?)\b",
            r"\b(?:depressuriz|replenish|seal|flush|synthetic|technician|inspection|instructions?)\b",
            r"\b(?:how to|what (?:steps|actions)|guidelines?|standard operating)\b"
        ]

    def classify_intent(self, query: str) -> QueryIntent:
        query_lower = query.lower()
        
        has_sql = any(re.search(pat, query_lower) for pat in self.sql_signals)
        has_doc = any(re.search(pat, query_lower) for pat in self.doc_signals)

        # Cross-source questions ask for metrics/downtime alongside actions/reductions/procedures
        if has_sql and has_doc:
            return QueryIntent.CROSS_SOURCE_HYBRID
        elif has_sql:
            return QueryIntent.STRUCTURED_ONLY
        elif has_doc:
            return QueryIntent.DOCUMENT_ONLY
        else:
            # Default to cross-source for broad executive inquiries to ensure complete grounding
            return QueryIntent.CROSS_SOURCE_HYBRID

    def create_plan(self, query: str) -> ExecutionPlan:
        intent = self.classify_intent(query)
        subtasks: List[SubTask] = []

        if intent == QueryIntent.STRUCTURED_ONLY:
            subtasks.append(
                SubTask(
                    task_id="task_sql",
                    agent_name="structured_data_agent",
                    agent_label="Structured Data Agent",
                    sub_query=query,
                    target_source="SQL_DATABASE",
                    dependencies=[]
                )
            )
            reasoning = "Query classified as pure structured data retrieval. Routing exclusively to Safe SQL Sandbox."

        elif intent == QueryIntent.DOCUMENT_ONLY:
            subtasks.append(
                SubTask(
                    task_id="task_doc",
                    agent_name="document_intelligence_agent",
                    agent_label="Document Intelligence Agent",
                    sub_query=query,
                    target_source="DOCUMENT_STORE",
                    dependencies=[]
                )
            )
            reasoning = "Query classified as document / procedural retrieval. Routing exclusively to Document Agent."

        else: # CROSS_SOURCE_HYBRID
            subtasks.append(
                SubTask(
                    task_id="task_sql",
                    agent_name="structured_data_agent",
                    agent_label="Structured Data Agent",
                    sub_query=query,
                    target_source="SQL_DATABASE",
                    dependencies=[]
                )
            )
            subtasks.append(
                SubTask(
                    task_id="task_doc",
                    agent_name="document_intelligence_agent",
                    agent_label="Document Intelligence Agent",
                    sub_query=query,
                    target_source="DOCUMENT_STORE",
                    dependencies=[]
                )
            )
            reasoning = (
                "Query requires cross-source synthesis: decomposing into structured telemetry query "
                "and procedural documentation search across parallel intelligence agents."
            )

        return ExecutionPlan(
            intent=intent,
            subtasks=subtasks,
            is_parallel=True,
            reasoning=reasoning
        )

query_router = QueryRouter()
