import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.orchestration.contracts import IntentCategory, ExecutionMode

class IntentDefinition(BaseModel):
    category: IntentCategory
    description: str
    signal_keywords: List[str] = Field(default_factory=list)
    regex_patterns: List[str] = Field(default_factory=list)
    required_capabilities: List[str] = Field(default_factory=list)
    target_sources: List[str] = Field(default_factory=list)
    processing_strategy: ExecutionMode = ExecutionMode.PARALLEL
    confidence_threshold: float = 0.55

class IntentTaxonomy:
    """Configurable and extensible intent taxonomy.
    Avoids hardcoding intent rules across the codebase.
    Allows industries to register new intents and capabilities seamlessly.
    """

    def __init__(self):
        self._definitions: Dict[IntentCategory, IntentDefinition] = {}
        self._init_defaults()

    def _init_defaults(self):
        # 1. Structured Telemetry & Metrics
        self.register_intent(
            IntentDefinition(
                category=IntentCategory.STRUCTURED_TELEMETRY,
                description="Queries targeting quantitative telemetry, downtime metrics, OEE, cost, scrap, or database records.",
                signal_keywords=[
                    "downtime", "hours", "minutes", "oee", "defect", "scrap", "ppm",
                    "telemetry", "cost", "loss", "units", "target", "actual", "events",
                    "work orders", "line 1", "line 2", "line 3", "plant a", "plant b",
                    "highest", "lowest", "total", "average", "avg", "sum", "count",
                    # Pharma structured signals
                    "efficacy", "endpoint", "participant", "participants", "trial", "trials",
                    "adverse event", "adverse events", "purity", "dissolution", "microbial",
                    "cardiovastin", "lot 4891", "sae", "reporting latency"
                ],
                regex_patterns=[
                    r"\b(?:downtime|hours?|minutes?|oee|defect|scrap|ppm|telemetry|cost|loss)\b",
                    r"\b(?:line[ -]?[123]|plant[ -]?[ab])\b",
                    r"\b(?:sum|average|avg|count|highest|lowest|total)\b",
                    r"\b(?:efficacy|endpoint|participant|trial|adverse|purity|dissolution)\b"
                ],
                required_capabilities=["structured_query", "sql_execution"],
                target_sources=["SQL_DATABASE"],
                processing_strategy=ExecutionMode.SINGLE_AGENT
            )
        )

        # 2. Procedural Guidance & Standard Operating Procedures
        self.register_intent(
            IntentDefinition(
                category=IntentCategory.PROCEDURAL_GUIDANCE,
                description="Queries targeting unstructured documents, SOPs, repair manuals, or compliance guidelines.",
                signal_keywords=[
                    "sop", "procedure", "manual", "protocol", "action", "recommendation",
                    "solution", "preventive", "repair", "fix", "incident logs", "depressuriz",
                    "replenish", "seal", "flush", "synthetic", "technician", "inspection",
                    "instructions", "how to", "what steps", "guidelines", "standard operating",
                    # Pharma procedural signals
                    "fda", "cder", "nda", "ind", "sop-pv-042", "gmp", "cgmp", "cleanroom",
                    "approval", "expedited reporting", "ich", "e2a", "21 cfr"
                ],
                regex_patterns=[
                    r"\b(?:sop|procedure|manual|protocol|action|recommendation|solution|preventive|repair|fix)\b",
                    r"\b(?:how to|what (?:steps|actions)|guidelines?|standard operating)\b",
                    r"\b(?:fda|cder|nda|ind|gmp|cleanroom|approval|expedited)\b"
                ],
                required_capabilities=["unstructured_retrieval", "hybrid_search", "document_qa"],
                target_sources=["DOCUMENT_STORE"],
                processing_strategy=ExecutionMode.SINGLE_AGENT
            )
        )

        # 3. Quality & Supplier Analysis
        self.register_intent(
            IntentDefinition(
                category=IntentCategory.QUALITY_SUPPLIER_ANALYSIS,
                description="Queries evaluating supplier component defect rates, batch quality bulletins, and supplier corrective actions.",
                signal_keywords=[
                    "supplier", "vendor", "apex", "batch", "quality", "bulletin",
                    "ppm", "incoming parts", "seal blowout", "part afd-seal-882", "af-2024"
                ],
                regex_patterns=[
                    r"\b(?:supplier|vendor|batch|ppm|bulletin|incoming parts)\b"
                ],
                required_capabilities=["structured_query", "unstructured_retrieval"],
                target_sources=["SQL_DATABASE", "DOCUMENT_STORE"],
                processing_strategy=ExecutionMode.PARALLEL
            )
        )

        # 4. Cross-Source Investigation (Hybrid)
        self.register_intent(
            IntentDefinition(
                category=IntentCategory.CROSS_SOURCE_INVESTIGATION,
                description="Multi-faceted queries combining empirical telemetry with operational documentation.",
                signal_keywords=[
                    "factors contributing", "reduced similar", "what caused", "correlate",
                    "relationship between", "discrepancy", "investigate", "audit findings",
                    "primary endpoint", "efficacy and", "trials and", "trial database",
                    "compliant with", "specifications for", "what did the quality investigation"
                ],
                regex_patterns=[
                    r"\b(?:what (?:are the )?factors|what caused|contributing to|reduced similar)\b",
                    r"\b(?:primary endpoint|efficacy and|trials? (?:and|in)|compliant with|specifications for)\b"
                ],
                required_capabilities=["structured_query", "unstructured_retrieval", "cross_source_synthesis", "conflict_detection"],
                target_sources=["SQL_DATABASE", "DOCUMENT_STORE"],
                processing_strategy=ExecutionMode.PARALLEL
            )
        )

    def register_intent(self, definition: IntentDefinition):
        self._definitions[definition.category] = definition

    def get_definition(self, category: IntentCategory) -> Optional[IntentDefinition]:
        return self._definitions.get(category)

    def list_definitions(self) -> List[IntentDefinition]:
        return list(self._definitions.values())

intent_taxonomy = IntentTaxonomy()
