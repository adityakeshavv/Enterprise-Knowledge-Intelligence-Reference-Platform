import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.sql_agent import sql_agent

client = TestClient(app)

def test_sql_agent_text_to_sql_downtime():
    result = sql_agent.process("What is the downtime for Line 3 Assembly?")
    assert result.is_safe is True
    assert result.rows_returned > 0
    assert "Line_3" in result.generated_sql
    assert "total_downtime" in result.columns or "downtime_minutes" in result.columns
    assert "Line 3" in result.summary or "minutes" in result.summary

def test_sql_agent_text_to_sql_supplier_defects():
    result = sql_agent.process("Which supplier has the highest defect rate in PPM?")
    assert result.is_safe is True
    assert result.rows_returned > 0
    assert "supplier_component_quality" in result.generated_sql
    assert any("Apex" in str(r) for r in result.rows)
    assert "1850" in str(result.rows) or "1,850" in result.summary

def test_sql_agent_text_to_sql_oee():
    result = sql_agent.process("Show overall equipment effectiveness and scrap metrics")
    assert result.is_safe is True
    assert result.rows_returned > 0
    assert "production_line_metrics" in result.generated_sql
    assert "avg_oee" in result.columns or "oee_percentage" in result.columns

def test_sql_agent_citation_item_provenance():
    result = sql_agent.process("What were the total repair costs across lines?")
    citation = sql_agent.to_citation_item(result)

    assert citation.citation_id == "SQL-01"
    assert citation.source_type == "SQL_QUERY"
    assert "SELECT" in citation.snippet
    assert "execution_ms" in citation.metadata
    assert citation.metadata["rows_returned"] == result.rows_returned

def test_api_sql_schema_endpoint():
    res = client.get("/api/sql/schema")
    assert res.status_code == 200
    data = res.json()
    assert "plant_downtime_events" in data["allowlisted_tables"]
    assert "maintenance_work_orders" in data["allowlisted_tables"]
    assert "supplier_component_quality" in data["allowlisted_tables"]
    assert "production_line_metrics" in data["allowlisted_tables"]
    assert len(data["tables"]) >= 4

def test_api_sql_query_endpoint():
    res = client.post("/api/sql/query", json={"query": "Show downtime events"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_safe"] is True
    assert data["rows_returned"] > 0
    assert len(data["columns"]) > 0

def test_api_sql_test_sandbox_security_blocking():
    # Attempt dangerous DROP query via API
    res = client.post("/api/sql/test-sandbox", json={"raw_sql": "DROP TABLE plant_downtime_events;"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "blocked"
    assert "UnsafeQueryOperationError" in data["error_type"]
