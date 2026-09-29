from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentMessage(BaseModel):
    sender: str
    recipient: str
    content: Dict[str, Any]
    timestamp: Optional[str] = None

class AgentTraceStep(BaseModel):
    agent: str
    action: str
    duration_ms: float
    status: str = "SUCCESS"
    details: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Base abstract contract for all specialized intelligence agents."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    @abstractmethod
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming context/subtask and return findings."""
        pass
