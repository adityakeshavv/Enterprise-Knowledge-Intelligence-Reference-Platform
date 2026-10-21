import os
import re
import time
from typing import Dict, Any, List, Optional
from app.retrieval.sql_sandbox import sql_sandbox, SQLSecurityError
from app.schemas.query import CitationItem
from app.schemas.sql import SQLQueryResult, TableSchemaInfo, TableColumnInfo

class StructuredDataAgent:
    """Specialized AI agent generating, validating, and executing read-only SQL queries with provenance."""

    def __init__(self, sandbox=sql_sandbox):
        self.sandbox = sandbox
        self.has_gemini = bool(os.environ.get("GEMINI_API_KEY"))

    def get_schema_summary(self) -> List[TableSchemaInfo]:
        """Introspect allowlisted database schemas."""
        return [
            TableSchemaInfo(
                table_name="plant_downtime_events",
                description="Tracks production stoppage events by plant, line, duration, and error codes.",
                columns=[
                    TableColumnInfo(name="event_id", type="VARCHAR(50)", primary_key=True),
                    TableColumnInfo(name="plant_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="line_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="start_timestamp", type="DATETIME"),
                    TableColumnInfo(name="end_timestamp", type="DATETIME"),
                    TableColumnInfo(name="downtime_minutes", type="INTEGER"),
                    TableColumnInfo(name="error_code", type="VARCHAR(50)"),
                    TableColumnInfo(name="root_cause_category", type="VARCHAR(100)"),
                ]
            ),
            TableSchemaInfo(
                table_name="maintenance_work_orders",
                description="Tracks technician repair work orders, parts replaced, and financial costs.",
                columns=[
                    TableColumnInfo(name="work_order_id", type="VARCHAR(50)", primary_key=True),
                    TableColumnInfo(name="plant_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="line_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="completion_date", type="DATETIME"),
                    TableColumnInfo(name="component_replaced", type="VARCHAR(100)"),
                    TableColumnInfo(name="cost_usd", type="FLOAT"),
                    TableColumnInfo(name="labor_hours", type="FLOAT"),
                    TableColumnInfo(name="technician_id", type="VARCHAR(50)"),
                ]
            ),
            TableSchemaInfo(
                table_name="supplier_component_quality",
                description="Monitors incoming parts batch defect rates in PPM by supplier.",
                columns=[
                    TableColumnInfo(name="batch_id", type="VARCHAR(50)", primary_key=True),
                    TableColumnInfo(name="supplier_id", type="VARCHAR(100)"),
                    TableColumnInfo(name="part_number", type="VARCHAR(50)"),
                    TableColumnInfo(name="defect_rate_ppm", type="INTEGER"),
                    TableColumnInfo(name="delivery_date", type="DATETIME"),
                ]
            ),
            TableSchemaInfo(
                table_name="production_line_metrics",
                description="Daily production line output, scrap counts, and OEE percentages.",
                columns=[
                    TableColumnInfo(name="id", type="INTEGER", primary_key=True),
                    TableColumnInfo(name="plant_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="line_id", type="VARCHAR(50)"),
                    TableColumnInfo(name="date", type="DATETIME"),
                    TableColumnInfo(name="planned_units", type="INTEGER"),
                    TableColumnInfo(name="actual_units", type="INTEGER"),
                    TableColumnInfo(name="scrap_units", type="INTEGER"),
                    TableColumnInfo(name="oee_percentage", type="FLOAT"),
                ]
            ),
        ]

    def _generate_sql(self, query: str) -> str:
        """Translates natural language intent into a targeted read-only SQL query."""
        q_lower = query.lower()

        # Check for Gemini API support if available
        if self.has_gemini:
            try:
                from google import genai
                client = genai.Client()
                schema_prompt = (
                    "You are a PostgreSQL/SQLite database engineer. Write a single read-only SELECT query.\n"
                    "Allowed tables:\n"
                    "- plant_downtime_events(event_id, plant_id, line_id, downtime_minutes, error_code, root_cause_category)\n"
                    "- maintenance_work_orders(work_order_id, plant_id, line_id, component_replaced, cost_usd, labor_hours)\n"
                    "- supplier_component_quality(batch_id, supplier_id, part_number, defect_rate_ppm)\n"
                    "- production_line_metrics(plant_id, line_id, planned_units, actual_units, scrap_units, oee_percentage)\n"
                    "Return ONLY the SQL query without markdown or explanations."
                )
                res = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[schema_prompt, f"User question: {query}"]
                )
                if res and res.text:
                    sql = res.text.strip().replace("```sql", "").replace("```", "").strip()
                    if sql.upper().startswith("SELECT"):
                        return sql
            except Exception as e:
                print(f"Gemini Text-to-SQL fallback: {e}")

        # Deterministic Semantic Synthesizer Fallback
        if "oee" in q_lower or "efficiency" in q_lower or "scrap" in q_lower:
            return (
                "SELECT line_id, ROUND(AVG(oee_percentage), 1) AS avg_oee, "
                "SUM(actual_units) AS total_units, SUM(scrap_units) AS total_scrap "
                "FROM production_line_metrics "
                "GROUP BY line_id "
                "ORDER BY avg_oee ASC LIMIT 10;"
            )
        elif "supplier" in q_lower or "defect" in q_lower or "ppm" in q_lower or "batch" in q_lower:
            return (
                "SELECT supplier_id, part_number, defect_rate_ppm, batch_id "
                "FROM supplier_component_quality "
                "ORDER BY defect_rate_ppm DESC LIMIT 10;"
            )
        elif "cost" in q_lower or "work order" in q_lower or "repair" in q_lower:
            return (
                "SELECT line_id, component_replaced, SUM(cost_usd) AS total_cost, SUM(labor_hours) AS total_labor "
                "FROM maintenance_work_orders "
                "GROUP BY line_id, component_replaced "
                "ORDER BY total_cost DESC LIMIT 10;"
            )
        elif "line 3" in q_lower or "line_3" in q_lower:
            return (
                "SELECT line_id, error_code, root_cause_category, SUM(downtime_minutes) AS total_downtime "
                "FROM plant_downtime_events "
                "WHERE line_id LIKE '%Line_3%' "
                "GROUP BY line_id, error_code, root_cause_category "
                "ORDER BY total_downtime DESC LIMIT 10;"
            )
        else:
            # Default plant downtime aggregation
            return (
                "SELECT line_id, error_code, root_cause_category, SUM(downtime_minutes) AS total_downtime "
                "FROM plant_downtime_events "
                "GROUP BY line_id, error_code, root_cause_category "
                "ORDER BY total_downtime DESC LIMIT 10;"
            )

    def process(self, query: str) -> SQLQueryResult:
        """Executes natural language query through Text-to-SQL, AST security validation, and sandbox."""
        generated_sql = self._generate_sql(query)

        try:
            columns, rows, duration_ms, sanitized_sql = self.sandbox.execute_safe_query(generated_sql)
            summary = self._summarize_results(rows, columns)

            return SQLQueryResult(
                natural_query=query,
                generated_sql=sanitized_sql,
                execution_duration_ms=round(duration_ms, 2),
                rows_returned=len(rows),
                columns=columns,
                rows=rows,
                summary=summary,
                is_safe=True
            )
        except SQLSecurityError as sec_err:
            return SQLQueryResult(
                natural_query=query,
                generated_sql=generated_sql,
                execution_duration_ms=0.0,
                rows_returned=0,
                columns=[],
                rows=[],
                summary=f"Query rejected by security sandbox: {sec_err}",
                is_safe=False,
                error=str(sec_err)
            )
        except Exception as err:
            return SQLQueryResult(
                natural_query=query,
                generated_sql=generated_sql,
                execution_duration_ms=0.0,
                rows_returned=0,
                columns=[],
                rows=[],
                summary=f"Database execution error: {err}",
                is_safe=True,
                error=str(err)
            )

    def _summarize_results(self, rows: List[Dict[str, Any]], columns: List[str]) -> str:
        if not rows:
            return "Query executed successfully, but 0 matching records were found in the database."

        first_row = rows[0]
        if "total_downtime" in first_row:
            top_line = first_row.get("line_id", "Unknown")
            mins = first_row.get("total_downtime", 0)
            return f"Database shows {top_line} accumulated highest downtime ({mins} minutes, ~{mins/60:.1f} hours)."
        elif "defect_rate_ppm" in first_row:
            supp = first_row.get("supplier_id", "Supplier")
            ppm = first_row.get("defect_rate_ppm", 0)
            return f"Highest defect rate recorded from {supp} at {ppm} PPM."
        elif "total_cost" in first_row:
            comp = first_row.get("component_replaced", "Component")
            cost = first_row.get("total_cost", 0)
            return f"Top maintenance expense was {comp} totaling ${cost:,.2f} USD."
        elif "avg_oee" in first_row:
            line = first_row.get("line_id", "Line")
            oee = first_row.get("avg_oee", 0)
            return f"Lowest line performance recorded on {line} with an average OEE of {oee}%."
        else:
            return f"Retrieved {len(rows)} database records across columns [{', '.join(columns[:4])}]."

    def to_citation_item(self, result: SQLQueryResult) -> CitationItem:
        """Packages SQL query execution into a verifiable CitationItem for the UI Evidence Drawer."""
        return CitationItem(
            citation_id="SQL-01",
            title="Relational Telemetry Query Execution",
            source_type="SQL_QUERY",
            reference="plant_downtime_events / maintenance_work_orders (Database)",
            snippet=result.generated_sql,
            metadata={
                "execution_ms": result.execution_duration_ms,
                "rows_returned": result.rows_returned,
                "columns": result.columns,
                "first_row_preview": result.rows[0] if result.rows else {},
                "database_engine": "SQLite / PostgreSQL Compatible",
                "summary": result.summary
            }
        )

sql_agent = StructuredDataAgent()
