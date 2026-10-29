import uuid
from typing import List, Dict, Any
from app.orchestration.contracts import (
    InvestigationPlan, InvestigationTask, AgentStatus, ExecutionMode,
    QueryUnderstandingResult, IntentClassificationResult, RoutingDecision
)

class InvestigationPlanningAgent:
    """Stage 4: Dedicated investigation planner that transforms classified intents
    into an executable task DAG with explicit objectives, dependencies, and completion criteria.
    """

    def plan(
        self,
        understanding: QueryUnderstandingResult,
        classification: IntentClassificationResult,
        routing: RoutingDecision
    ) -> InvestigationPlan:
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        tasks: List[InvestigationTask] = []
        sub_questions: List[str] = []

        query = understanding.normalized_query
        entities = understanding.entities

        # 1. Plan Structured Data Investigation Tasks
        if "structured_document_agent" in routing.selected_agents:
            if "drug_name" in entities or any(k in query.lower() for k in ["trial", "efficacy", "adverse", "sae", "lot", "purity", "cardiovastin"]):
                target_metric = "clinical trial metrics, adverse event logs, and batch quality"
                sub_q = f"What clinical trial endpoints or safety case records are logged for {entities.get('drug_name', 'investigational drug')}?"
            else:
                target_metric = "production downtime events and work orders"
                sub_q = f"What quantitative stoppage metrics or work orders are logged for {entities.get('line_id', 'production lines')}?"
            sub_questions.append(sub_q)

            tasks.append(
                InvestigationTask(
                    task_id="task_structured_retrieval",
                    objective=f"Query read-only database telemetry to retrieve {target_metric} matching: '{query}'.",
                    assigned_agent="structured_document_agent",
                    source_type="SQL_DATABASE",
                    dependencies=[],
                    required_inputs={
                        "natural_query": query,
                        "entities": entities,
                        "filters": understanding.filters
                    },
                    expected_outputs=["rows", "columns", "summary", "generated_sql"],
                    completion_criteria="At least 1 safe SQL query executed with verified row counts and AST validation.",
                    status=AgentStatus.PENDING
                )
            )

        # 2. Plan Unstructured Document Investigation Tasks
        if "unstructured_document_agent" in routing.selected_agents:
            sub_q = f"What standard operating procedures, maintenance logs, or quality bulletins relate to '{query}'?"
            sub_questions.append(sub_q)

            tasks.append(
                InvestigationTask(
                    task_id="task_unstructured_retrieval",
                    objective="Perform hybrid BM25 + dense semantic retrieval over indexed operational manuals and bulletins.",
                    assigned_agent="unstructured_document_agent",
                    source_type="DOCUMENT_STORE",
                    dependencies=[],
                    required_inputs={
                        "search_query": query,
                        "filters": understanding.filters,
                        "department": understanding.filters.get("department")
                    },
                    expected_outputs=["citations", "evidence_passages", "claims"],
                    completion_criteria="Relevant document passages returned with page numbers, document IDs, and XML bounding fences.",
                    status=AgentStatus.PENDING
                )
            )

        # Execution mode
        exec_mode = routing.execution_mode

        return InvestigationPlan(
            plan_id=plan_id,
            primary_question=query,
            sub_questions=sub_questions,
            tasks=tasks,
            execution_mode=exec_mode,
            fallback_strategy="If a source yields 0 results, mark task partial and proceed with remaining evidence."
        )

investigation_planner = InvestigationPlanningAgent()
