import time
from typing import Dict, Any, List
from app.agents.base import BaseAgent, AgentTraceStep
from app.db.session import db_manager

class StructuredDataAgent(BaseAgent):
    """Executes safe read-only SQL queries and returns tabular metrics and execution provenance."""

    def __init__(self):
        super().__init__(name="Structured Data Agent", role="Safe SQL Query Execution & Relational Analytics")

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        start = time.time()
        query_text = context.get("query", "").lower()
        
        # Determine query path based on intent
        if "supplier" in query_text or "ppm" in query_text:
            sql = "SELECT lot_id, supplier_name, component_category, defect_rate_ppm, audit_status FROM supplier_quality ORDER BY defect_rate_ppm DESC LIMIT 10;"
            action_desc = "Queried supplier incoming quality inspection records (supplier_quality)"
        elif "line" in query_text and "oee" in query_text:
            sql = "SELECT line_id, equipment_name, oee_target, actual_oee, status FROM production_lines WHERE plant_id = 'PLANT-A' ORDER BY actual_oee ASC;"
            action_desc = "Queried production line OEE targets vs actuals (production_lines)"
        else:
            # Default plant downtime aggregation
            sql = "SELECT event_id, line_id, equipment_id, duration_hours, recorded_cause, financial_impact_usd FROM downtime_events WHERE plant_id = 'PLANT-A' ORDER BY duration_hours DESC LIMIT 5;"
            action_desc = "Queried Plant A historical downtime events (downtime_events)"

        res = db_manager.execute_query(sql)
        duration = (time.time() - start) * 1000
        
        trace = AgentTraceStep(
            agent=self.name,
            action=action_desc,
            duration_ms=round(duration, 2),
            details={"sql_executed": sql, "row_count": res.get("row_count", 0)}
        )

        return {
            "structured_data": res,
            "sql_executed": sql,
            "trace": trace.model_dump()
        }
