import time
from typing import Dict, Any, Optional
from app.orchestration.contracts import (
    StructuredRetrievalResult, AgentStatus, AgentError
)
from app.agents.sql_agent import sql_agent
from app.schemas.query import CitationItem
from app.schemas.sql import SQLQueryResult

class StructuredDocumentAgent:
    """Stage 5: Specialized agent retrieving and processing structured relational data
    and tabular records via the AST-validated read-only Safe SQL Sandbox.
    """

    def __init__(self, underlying_agent=sql_agent):
        self.underlying_agent = underlying_agent

    def execute_task(self, query: str, user_role: str = "CXO") -> StructuredRetrievalResult:
        start_t = time.perf_counter()
        try:
            sql_res: SQLQueryResult = self.underlying_agent.process(query)
            latency_ms = (time.perf_counter() - start_t) * 1000

            if not sql_res.is_safe:
                return StructuredRetrievalResult(
                    status=AgentStatus.FAILED,
                    query_executed=sql_res.generated_sql or "BLOCKED",
                    rows_returned=0,
                    summary="Query blocked by AST security sandbox validator.",
                    latency_ms=latency_ms,
                    is_safe=False,
                    error=AgentError(
                        error_code="SQL_SECURITY_BLOCK",
                        message=sql_res.summary,
                        retryable=False
                    )
                )

            q_gen = (sql_res.generated_sql or "").lower()
            if "clinical_trial" in q_gen:
                src_ref = "clinical_trial_metrics (Database)"
            elif "adverse_event" in q_gen:
                src_ref = "adverse_event_reports (Database)"
            elif "pharma_batch" in q_gen:
                src_ref = "pharma_batch_quality (Database)"
            else:
                src_ref = "plant_downtime_events / maintenance_work_orders (Database)"

            return StructuredRetrievalResult(
                status=AgentStatus.COMPLETED if sql_res.rows_returned > 0 else AgentStatus.PARTIAL,
                query_executed=sql_res.generated_sql,
                rows_returned=sql_res.rows_returned,
                columns=sql_res.columns,
                data_records=sql_res.rows,
                summary=sql_res.summary,
                source_reference=src_ref,
                latency_ms=latency_ms,
                is_safe=True
            )
        except Exception as e:
            latency_ms = (time.perf_counter() - start_t) * 1000
            return StructuredRetrievalResult(
                status=AgentStatus.FAILED,
                query_executed="",
                rows_returned=0,
                summary=f"Structured retrieval failed: {str(e)}",
                latency_ms=latency_ms,
                is_safe=False,
                error=AgentError(
                    error_code="STRUCTURED_QUERY_EXECUTION_ERROR",
                    message=str(e),
                    retryable=True
                )
            )

    def to_citation_item(self, result: StructuredRetrievalResult) -> CitationItem:
        q_sql = (result.query_executed or "").lower()
        if "clinical_trial" in q_sql:
            title = "Clinical Trial Telemetry & Efficacy Record"
            ref = "clinical_trial_metrics (Database)"
        elif "adverse_event" in q_sql:
            title = "Pharmacovigilance Safety Case Record"
            ref = "adverse_event_reports (Database)"
        elif "pharma_batch" in q_sql:
            title = "cGMP Analytical Batch Quality Record"
            ref = "pharma_batch_quality (Database)"
        else:
            title = "Plant Relational Telemetry Record"
            ref = result.source_reference or "Enterprise Database (Read-Only)"

        return CitationItem(
            citation_id="SQL-01",
            title=title,
            source_type="SQL_QUERY",
            reference=ref,
            snippet=f"SQL Query: {result.query_executed} | Rows: {result.rows_returned} | Summary: {result.summary}",
            metadata={
                "rows_returned": result.rows_returned,
                "latency_ms": result.latency_ms,
                "columns": result.columns
            }
        )

structured_document_agent = StructuredDocumentAgent()
