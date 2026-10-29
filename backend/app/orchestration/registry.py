from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field

class AgentManifest(BaseModel):
    agent_id: str
    version: str = "1.0.0"
    label: str
    capabilities: List[str] = Field(default_factory=list)
    description: str = ""
    target_sources: List[str] = Field(default_factory=list)
    required_role: str = "OPERATOR" # Minimum role required (e.g. OPERATOR, RELIABILITY_ENGINEER, QA_SPECIALIST, PLANT_MANAGER, CXO)
    is_active: bool = True
    timeout_seconds: float = 15.0
    retry_limit: int = 2

class AgentRegistry:
    """Central registry of specialized AI agents.
    Allows independent registration, capability declaration, and tool authorization
    without modifying monolithic control logic.
    """

    def __init__(self):
        self._agents: Dict[str, Any] = {}
        self._manifests: Dict[str, AgentManifest] = {}

    def register_agent(
        self,
        manifest: AgentManifest,
        agent_instance: Any
    ):
        """Registers an agent instance and its capability manifest."""
        self._agents[manifest.agent_id] = agent_instance
        self._manifests[manifest.agent_id] = manifest

    def get_agent(self, agent_id: str) -> Optional[Any]:
        return self._agents.get(agent_id)

    def get_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        return self._manifests.get(agent_id)

    def list_manifests(self) -> List[AgentManifest]:
        return list(self._manifests.values())

    def find_agents_for_capability(self, capability: str) -> List[AgentManifest]:
        """Finds all agents that advertise a specific capability."""
        return [
            m for m in self._manifests.values()
            if capability in m.capabilities and m.is_active
        ]

    def find_agents_for_source(self, source_type: str) -> List[AgentManifest]:
        """Finds all agents configured for a specific data source."""
        return [
            m for m in self._manifests.values()
            if source_type in m.target_sources and m.is_active
        ]

    def validate_authorization(self, agent_id: str, user_role: str) -> bool:
        """Validates whether the user's role satisfies the agent's required role clearance."""
        manifest = self.get_manifest(agent_id)
        if not manifest:
            return False

        ROLE_HIERARCHY = {
            "OPERATOR": 1,
            "RELIABILITY_ENGINEER": 2,
            "QA_SPECIALIST": 2,
            "PLANT_MANAGER": 3,
            "CXO": 4,
            "AUDITOR": 4
        }
        user_level = ROLE_HIERARCHY.get(user_role.upper(), 1)
        required_level = ROLE_HIERARCHY.get(manifest.required_role.upper(), 1)
        return user_level >= required_level

# Global agent registry singleton
agent_registry = AgentRegistry()
