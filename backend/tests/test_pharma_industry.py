import pytest
from app.core.config_loader import config_loader
from app.retrieval.sql_sandbox import sql_sandbox, UnauthorizedTableError
from app.orchestration.engine import modular_orchestrator
from app.schemas.query import QueryResponse

def test_pharma_industry_discovery():
    industries = config_loader.list_available_industries()
    pharma_ind = next((i for i in industries if i["id"] == "pharma"), None)
    assert pharma_ind is not None
    assert pharma_ind["name"] == "Pharmaceutical & Life Sciences"
    assert pharma_ind["scenario_count"] == 3

def test_pharma_sql_sandbox_allowlist():
    # Valid pharma queries
    q1 = "SELECT trial_id, drug_name, efficacy_rate FROM clinical_trial_metrics WHERE primary_endpoint_met = 1;"
    sanitized1 = sql_sandbox.validate_and_sanitize(q1)
    assert "clinical_trial_metrics" in sanitized1.lower()

    q2 = "SELECT report_id, reaction, days_to_report FROM adverse_event_reports WHERE is_serious = 1;"
    sanitized2 = sql_sandbox.validate_and_sanitize(q2)
    assert "adverse_event_reports" in sanitized2.lower()

    q3 = "SELECT batch_id, purity_percentage, release_status FROM pharma_batch_quality;"
    sanitized3 = sql_sandbox.validate_and_sanitize(q3)
    assert "pharma_batch_quality" in sanitized3.lower()

    # Unauthorized table should be blocked
    with pytest.raises(UnauthorizedTableError):
        sql_sandbox.validate_and_sanitize("SELECT * FROM payroll_records;")

def test_pharma_query_execution_cross_source():
    current_ind = config_loader.active_industry_id
    try:
        config_loader.set_active_industry("pharma")
        query = "What was the primary endpoint efficacy of CardioVastin in Phase 3 trials, and what adverse event rates were reported?"
        
        response: QueryResponse = modular_orchestrator.execute(
            query_text=query,
            user_role="CXO",
            industry_id="pharma"
        )

        assert response is not None
        assert response.confidence_score > 0.70
        assert "CardioVastin" in response.executive_summary
        assert "48.4%" in response.executive_summary or any("48.4%" in str(f) for f in response.key_findings)
        assert len(response.citations) >= 2

        # Check for both structured and unstructured citations
        has_sql_cit = any(c.source_type == "SQL_QUERY" for c in response.citations)
        has_doc_cit = any(c.source_type == "DOCUMENT_SOP" for c in response.citations)
        assert has_sql_cit
        assert has_doc_cit

        # Verify metrics
        metric_labels = [m.label for m in response.metrics]
        assert any("Endpoint" in l for l in metric_labels)
        assert any("Cohort" in l or "Size" in l for l in metric_labels)
    finally:
        config_loader.set_active_industry(current_ind)
