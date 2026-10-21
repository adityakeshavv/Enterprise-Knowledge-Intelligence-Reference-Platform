import pytest
from app.retrieval.sql_sandbox import (
    SQLSandbox,
    UnsafeQueryOperationError,
    UnauthorizedTableError,
    sql_sandbox
)

def test_safe_select_query_validation():
    sql = "SELECT plant_id, line_id, SUM(downtime_minutes) FROM plant_downtime_events GROUP BY plant_id, line_id;"
    sanitized = sql_sandbox.validate_and_sanitize(sql)
    assert "LIMIT 100" in sanitized
    assert sanitized.upper().startswith("SELECT")

def test_block_drop_table_injection():
    malicious = "DROP TABLE plant_downtime_events;"
    with pytest.raises(UnsafeQueryOperationError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_delete_mutation():
    malicious = "DELETE FROM plant_downtime_events WHERE plant_id = 'Plant_A';"
    with pytest.raises(UnsafeQueryOperationError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_update_mutation():
    malicious = "UPDATE maintenance_work_orders SET cost_usd = 0;"
    with pytest.raises(UnsafeQueryOperationError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_insert_mutation():
    malicious = "INSERT INTO plant_downtime_events (event_id, plant_id) VALUES ('E-1', 'Plant_A');"
    with pytest.raises(UnsafeQueryOperationError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_multi_statement_chained_injection():
    malicious = "SELECT * FROM plant_downtime_events; DROP TABLE plant_downtime_events;"
    with pytest.raises(UnsafeQueryOperationError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_unauthorized_users_table():
    malicious = "SELECT id, username, hashed_password FROM users;"
    with pytest.raises(UnauthorizedTableError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_unauthorized_audit_logs_table():
    malicious = "SELECT * FROM audit_logs;"
    with pytest.raises(UnauthorizedTableError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_block_system_sqlite_master_catalog():
    malicious = "SELECT name, sql FROM sqlite_master WHERE type='table';"
    with pytest.raises(UnauthorizedTableError):
        sql_sandbox.validate_and_sanitize(malicious)

def test_limit_enforcement_clamp_excessive_limit():
    query = "SELECT * FROM plant_downtime_events LIMIT 500;"
    sanitized = sql_sandbox.validate_and_sanitize(query)
    assert "LIMIT 100" in sanitized

def test_execute_safe_query_execution_returns_provenance():
    query = "SELECT line_id, SUM(downtime_minutes) AS total_downtime FROM plant_downtime_events GROUP BY line_id;"
    columns, rows, duration_ms, sanitized = sql_sandbox.execute_safe_query(query)

    assert "line_id" in columns
    assert "total_downtime" in columns
    assert len(rows) > 0
    assert duration_ms > 0.0
    assert isinstance(rows[0], dict)
