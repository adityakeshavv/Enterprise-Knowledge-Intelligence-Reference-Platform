import re
from typing import Dict, Any, List, Optional
from app.orchestration.contracts import QueryUnderstandingResult

class QueryUnderstandingAgent:
    """Stage 1: Analyzes incoming queries, extracts domain entities, detects ambiguities,
    identifies constraints, and normalizes queries into a structured typed schema.
    """

    def __init__(self):
        # Known manufacturing entity patterns
        self.entity_patterns = {
            "plant_id": r"\b(Plant[ -]?[AB])\b",
            "line_id": r"\b(Line[ -]?[123](?:[ -]?Assembly)?)\b",
            "error_code": r"\b(ERR-[A-Z0-9]+)\b",
            "part_number": r"\b(AFD-[A-Z0-9-]+)\b",
            "supplier_id": r"\b(Apex[ -]?(?:Precision[ -]?Dynamics)?|Vortex[ -]?(?:Motion)?)\b",
            "batch_id": r"\b(BATCH-[A-Z0-9-]+)\b",
            "work_order_id": r"\b(WO-[A-Z0-9]+)\b",
            "event_id": r"\b(EVT-[A-Z0-9]+|AER-[A-Z0-9-]+)\b",
            "component": r"\b(hydraulic pump|elastomer seal|pressure relief valve|accumulator|o-ring|actuator)\b",
            "drug_name": r"\b(CardioVastin|OncoShield(?:-X)?|CardioCare)\b",
            "trial_id": r"\b(NCT-\d{8}|CV-301(?:-PH3)?)\b",
            "phase": r"\b(Phase[ -]?(?:3|2b|1\/2|III|II|I))\b",
            "sop_id": r"\b(SOP-PV-042|SOP-QA-GMP-882|SOP-Maint-[A-Za-z0-9-]+)\b",
        }

    def process(self, query: str) -> QueryUnderstandingResult:
        query_clean = query.strip()
        entities: Dict[str, Any] = {}
        filters: Dict[str, Any] = {}
        constraints: List[str] = []
        ambiguities: List[str] = []

        # 1. Entity Extraction
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query_clean, flags=re.IGNORECASE)
            if matches:
                # Normalize key entities
                entities[entity_type] = matches[0] if len(matches) == 1 else matches
                filters[entity_type] = matches[0]

        # 2. Time-Range Detection
        time_range = None
        date_match = re.search(r"\b(March \d{1,2}|Q1|Q2|last 30 days|past week|past month|2024|2025|2026)\b", query_clean, flags=re.IGNORECASE)
        if date_match:
            time_range = {"extracted_period": date_match.group(1)}
            filters["period"] = date_match.group(1)

        # 3. Constraint Detection
        if re.search(r"\b(?:only|strictly|top \d+|limit to|exclusively)\b", query_clean, flags=re.IGNORECASE):
            constraints.append("Query contains strict filtering / ranking constraints.")
        if re.search(r"\b(?:safe|without hallucination|verified only)\b", query_clean, flags=re.IGNORECASE):
            constraints.append("High-grounding zero-hallucination constraint requested.")

        # 4. Ambiguity & Missing Information Check
        clarification_required = False
        clarification_prompt = None

        if len(query_clean.split()) < 3 and not entities:
            ambiguities.append("Query is extremely terse without recognizable entity or metric scope.")
            clarification_required = True
            clarification_prompt = "Could you please specify which plant, production line, or metric you would like to analyze?"

        # 5. Query Normalization
        normalized = query_clean
        # Normalize whitespace and common colloquial terms
        normalized = re.sub(r"\s+", " ", normalized)
        # Format Line references consistently
        normalized = re.sub(r"\bline[ -]?3\b", "Line 3", normalized, flags=re.IGNORECASE)
        normalized = re.sub(r"\bplant[ -]?a\b", "Plant A", normalized, flags=re.IGNORECASE)

        # 6. Intent & Business Objective Derivation
        primary_intent = "operational_investigation"
        secondary_intents: List[str] = []
        q_lower = normalized.lower()

        if any(w in q_lower for w in ["downtime", "hours", "minutes", "stoppage"]):
            primary_intent = "downtime_root_cause_analysis"
        if any(w in q_lower for w in ["supplier", "defect", "vendor", "quality", "ppm"]):
            if primary_intent == "downtime_root_cause_analysis":
                secondary_intents.append("supplier_defect_correlation")
            else:
                primary_intent = "supplier_defect_correlation"
        if any(w in q_lower for w in ["sop", "procedure", "actions", "reduced", "recommendation"]):
            secondary_intents.append("corrective_action_retrieval")

        business_objective = (
            f"Identify root causes, operational impacts, and verified corrective actions for {entities.get('line_id', 'plant lines')}."
        )

        return QueryUnderstandingResult(
            original_query=query,
            normalized_query=normalized,
            primary_intent=primary_intent,
            secondary_intents=secondary_intents,
            entities=entities,
            filters=filters,
            time_range=time_range,
            constraints=constraints,
            ambiguities=ambiguities,
            clarification_required=clarification_required,
            clarification_prompt=clarification_prompt,
            business_objective=business_objective
        )

query_understanding_agent = QueryUnderstandingAgent()
