import uuid
from typing import List, Optional
from app.orchestration.contracts import (
    RoutingDecision, IntentCategory, ExecutionMode,
    IntentClassificationResult, QueryUnderstandingResult
)
from app.orchestration.registry import agent_registry

class QueryRoutingAgent:
    """Stage 3: Maps classified intents to authorized agents and tools.
    Validates user RBAC role clearance against requested agents before workflow dispatch.
    """

    def __init__(self, registry=agent_registry):
        self.registry = registry

    def route(
        self,
        understanding: QueryUnderstandingResult,
        classification: IntentClassificationResult,
        user_role: str = "CXO"
    ) -> RoutingDecision:
        workflow_id = f"wf_{uuid.uuid4().hex[:8]}"
        selected_agents: List[str] = []
        skipped_agents: List[str] = []
        authorized_sources: List[str] = []

        # 1. Resolve agents based on target source types and required capabilities
        candidate_agents = set()
        for source in classification.target_source_types:
            manifests = self.registry.find_agents_for_source(source)
            for m in manifests:
                candidate_agents.add(m.agent_id)

        # Fallback if registry not fully populated with dynamic instances yet
        if not candidate_agents:
            if "SQL_DATABASE" in classification.target_source_types:
                candidate_agents.add("structured_document_agent")
            if "DOCUMENT_STORE" in classification.target_source_types:
                candidate_agents.add("unstructured_document_agent")

        # 2. Check RBAC clearance for each candidate agent
        unauthorized_agents = []
        for agent_id in candidate_agents:
            # Check clearance
            if self.registry.get_manifest(agent_id):
                has_auth = self.registry.validate_authorization(agent_id, user_role)
            else:
                has_auth = True # default permit for core agents if role is standard

            if has_auth:
                selected_agents.append(agent_id)
            else:
                unauthorized_agents.append(agent_id)
                skipped_agents.append(agent_id)

        # Track skipped standard agents
        all_possible = ["structured_document_agent", "unstructured_document_agent"]
        for a in all_possible:
            if a not in selected_agents and a not in skipped_agents:
                skipped_agents.append(a)

        # 3. Determine Execution Mode
        if len(selected_agents) > 1:
            exec_mode = classification.processing_strategy
        else:
            exec_mode = ExecutionMode.SINGLE_AGENT

        # 4. Determine Authorized Sources
        if "structured_document_agent" in selected_agents:
            authorized_sources.append("SQL_DATABASE")
        if "unstructured_document_agent" in selected_agents:
            authorized_sources.append("DOCUMENT_STORE")

        # 5. Build Rationale
        if unauthorized_agents:
            is_authorized = False
            auth_error = f"User role '{user_role}' lacks clearance for: {', '.join(unauthorized_agents)}."
            rationale = f"Routing partially blocked: {auth_error}"
        else:
            is_authorized = True
            auth_error = None
            rationale = (
                f"Intent '{classification.predicted_intent.value}' dispatched to {len(selected_agents)} "
                f"agent(s) [{', '.join(selected_agents)}] in {exec_mode.value} mode. "
                f"Skipped: [{', '.join(skipped_agents)}]."
            )

        return RoutingDecision(
            workflow_id=workflow_id,
            selected_agents=selected_agents,
            skipped_agents=skipped_agents,
            execution_mode=exec_mode,
            authorized_sources=authorized_sources,
            rationale=rationale,
            is_authorized=is_authorized,
            authorization_error=auth_error
        )

routing_agent = QueryRoutingAgent()
