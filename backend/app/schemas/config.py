from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IndustrySummary(BaseModel):
    id: str
    name: str
    description: str
    version: str
    scenario_count: int
    is_active: bool

class ScenarioItem(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    question: str
    description: Optional[str] = None
    expected_agents: List[str] = []
    highlight_metrics: List[str] = []

class IndustryDetail(BaseModel):
    id: str
    metadata: Dict[str, Any]
    terminology: Dict[str, Any]
    sources: Dict[str, Any]
    scenarios: List[ScenarioItem]
    prompts: Dict[str, Any]

class ChangeActiveIndustryRequest(BaseModel):
    industry_id: str
