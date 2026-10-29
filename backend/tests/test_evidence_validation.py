import pytest
from app.agents.validation_agent import evidence_validation_agent, EvidenceValidationAgent
from app.orchestration.orchestrator import multi_agent_orchestrator
from app.orchestration.state import WorkflowState
from app.schemas.query import CitationItem, FactClassification, FindingItem
from app.schemas.sql import SQLQueryResult

def test_abstention_unindexed_domain():
    """Verify safe abstention protocol triggers on unindexed facility/domain."""
    agent = EvidenceValidationAgent()
    
    # Query on paint shop chemical burn
    is_abstained, reason = agent.evaluate_abstention(
        query="What are the paint shop chemical burn safety protocols at Plant A?",
        sql_result=None,
        doc_result=None,
        citations=[]
    )
    assert is_abstained is True
    assert "paint shop" in reason
    assert "zero-hallucination" in reason

    # Query on executive payroll
    is_abstained_hr, reason_hr = agent.evaluate_abstention(
        query="What is the executive compensation and payroll for plant managers?",
        sql_result=None,
        doc_result=None,
        citations=[]
    )
    assert is_abstained_hr is True
    assert "payroll" in reason_hr

def test_abstention_zero_evidence():
    """Verify safe abstention when neither SQL nor documents provide evidence."""
    agent = EvidenceValidationAgent()
    is_abstained, reason = agent.evaluate_abstention(
        query="Explain the quantum computing subroutines in Assembly Line 9",
        sql_result=None,
        doc_result={"citations": []},
        citations=[]
    )
    assert is_abstained is True
    assert "No verifiable structured telemetry" in reason

def test_conflict_conf_01_temporal_maintenance():
    """Verify detection of CONF-01: March 10 sign-off vs March 14 telemetry stoppage."""
    agent = EvidenceValidationAgent()
    citations = [
        CitationItem(
            citation_id="DOC-01",
            title="Plant A Maintenance Logs",
            source_type="DOCUMENT_SOP",
            reference="Plant_A_Shift_Incident_Logs_Q1.xlsx",
            snippet="Hydraulic pump seal replacement completed on March 10 by shift maintenance team.",
            metadata={}
        )
    ]
    sql_res = SQLQueryResult(
        natural_query="What caused downtime on Line 3?",
        generated_sql="SELECT * FROM plant_downtime_events WHERE line_id = 'Line 3';",
        is_safe=True,
        execution_duration_ms=5.0,
        rows=[{"event_id": "EVT-409", "date": "March 14", "downtime_minutes": 510}],
        columns=["event_id", "date", "downtime_minutes"],
        rows_returned=1,
        summary="Event EVT-409 recorded 8.5 hours downtime on March 14 on Line 3."
    )

    conflicts = agent.detect_conflicts(
        query="What caused the downtime on Line 3 and what maintenance actions were taken?",
        sql_result=sql_res,
        doc_result={"citations": citations},
        citations=citations
    )

    assert len(conflicts) >= 1
    conf_ids = [c.conflict_id for c in conflicts]
    assert "CONF-01" in conf_ids
    conf_01 = next(c for c in conflicts if c.conflict_id == "CONF-01")
    assert "March 10" in conf_01.description
    assert "March 14" in conf_01.description
    assert "recommendation" in conf_01.model_dump()

def test_conflict_conf_02_supplier_quality_discrepancy():
    """Verify detection of CONF-02: Supplier specification vs incoming batch defect rate."""
    agent = EvidenceValidationAgent()
    citations = [
        CitationItem(
            citation_id="DOC-02",
            title="Apex Fluid Dynamics Certificate",
            source_type="DOCUMENT_SOP",
            reference="Apex_Fluid_Dynamics_Quality_Certificate_2024.pdf",
            snippet="Batch AFD-2024-Q1 conforms to maximum seal defect rate of <500 PPM.",
            metadata={}
        )
    ]
    sql_res = SQLQueryResult(
        natural_query="supplier quality metrics",
        generated_sql="SELECT * FROM supplier_quality_metrics;",
        is_safe=True,
        execution_duration_ms=4.0,
        rows=[{"supplier": "Apex Fluid Dynamics", "defect_ppm": 1850}],
        columns=["supplier", "defect_ppm"],
        rows_returned=1,
        summary="Batch AFD-2024-Q1 recorded 1850 PPM defect rate."
    )

    conflicts = agent.detect_conflicts(
        query="What is the supplier defect rate and PPM quality metrics for Apex Fluid Dynamics?",
        sql_result=sql_res,
        doc_result={"citations": citations},
        citations=citations
    )

    assert len(conflicts) >= 1
    conf_ids = [c.conflict_id for c in conflicts]
    assert "CONF-02" in conf_ids
    conf_02 = next(c for c in conflicts if c.conflict_id == "CONF-02")
    assert "<500 PPM" in conf_02.description
    assert "1,850 PPM" in conf_02.description

def test_grounding_evaluation_precision_score():
    """Verify empirical claim grounding score calculation."""
    agent = EvidenceValidationAgent()
    citations = [
        CitationItem(
            citation_id="DOC-01",
            title="Hydraulic SOP",
            source_type="DOCUMENT_SOP",
            reference="SOP-Line-3.pdf",
            snippet="Part AFD-SEAL-882 operates under 250 operational hours interval on Line 3.",
            metadata={}
        )
    ]
    sql_res = SQLQueryResult(
        natural_query="line 3 downtime",
        generated_sql="SELECT ...",
        is_safe=True,
        execution_duration_ms=5.0,
        rows=[{"line_id": "Line 3", "downtime": 1080}],
        columns=["line_id", "downtime"],
        rows_returned=1,
        summary="Line 3 accumulated 1080 downtime minutes."
    )

    # Candidate claims: 1 supported, 1 completely fabricated hallucination
    claims = [
        "Part AFD-SEAL-882 has an operational threshold of 250 hours on Line 3 [DOC-01].",
        "Submarine propulsion system XYZ-999 caused 99999 hours of catastrophic reactor failure."
    ]

    score, supported, unsupported = agent.evaluate_grounding(
        candidate_claims=claims,
        sql_result=sql_res,
        doc_result={"citations": citations},
        citations=citations
    )

    assert score == 0.50
    assert len(supported) == 1
    assert "AFD-SEAL-882" in supported[0]
    assert len(unsupported) == 1
    assert "Submarine" in unsupported[0]

def test_fact_versus_inference_tagging():
    """Verify classification of factual observations vs analytical inferences."""
    agent = EvidenceValidationAgent()
    citations = [
        CitationItem(
            citation_id="SQL-01",
            title="Telemetry",
            source_type="SQL_QUERY",
            reference="plant_downtime_events",
            snippet="Line 3 recorded 1080 minutes downtime.",
            metadata={}
        )
    ]

    claims = [
        "Structured Telemetry: Line 3 recorded 1080 minutes of hydraulic downtime [SQL-01].",
        "We recommend scheduling a preventive oil flush and synthetic torque check during next shift."
    ]

    findings = agent.classify_facts_and_inferences(claims, citations)
    assert len(findings) == 2
    assert findings[0].classification == FactClassification.VERIFIED_FACT
    assert "SQL-01" in findings[0].citation_ids
    assert findings[1].classification == FactClassification.ANALYTICAL_INFERENCE

def test_orchestrator_end_to_end_with_validation_report():
    """Verify full multi-agent orchestration produces validated report with fact/inference tags."""
    query = "What caused the downtime on Line 3 in Plant A and what action is recommended?"
    resp = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert resp.validation_report is not None
    assert resp.validation_report.grounding_score >= 0.80
    assert resp.is_abstained is False
    assert len(resp.findings) > 0

    # Ensure findings contain both VERIFIED_FACT and ANALYTICAL_INFERENCE
    classifications = {f.classification for f in resp.findings}
    assert FactClassification.VERIFIED_FACT in classifications
    assert FactClassification.ANALYTICAL_INFERENCE in classifications

    # Check evidence validation trace step exists
    val_trace = next((s for s in resp.trace_steps if s.agent_name == "evidence_validation_agent"), None)
    assert val_trace is not None
    assert val_trace.status == "completed"
    assert "Grounded claims" in val_trace.business_message

def test_orchestrator_safe_abstention_pipeline():
    """Verify end-to-end safe abstention when query is outside indexed domain."""
    query = "What are the chemical burn emergency wash protocols in the paint shop?"
    resp = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert resp.is_abstained is True
    assert resp.confidence_score == 0.0
    assert resp.validation_report is not None
    assert resp.validation_report.is_abstained is True
    assert "Safe Abstention Notice" in resp.executive_summary
    assert "paint shop" in resp.validation_report.abstention_reason.lower()

    # Trace step should show warning status
    val_trace = next((s for s in resp.trace_steps if s.agent_name == "evidence_validation_agent"), None)
    assert val_trace is not None
    assert val_trace.status == "warning"
    assert "Safe abstention triggered" in val_trace.business_message

@pytest.mark.asyncio
async def test_orchestrator_stream_validation_event():
    """Verify streaming generator emits validation report and fact/inference findings."""
    events = []
    async for event in multi_agent_orchestrator.stream_orchestration(
        query_text="What caused the downtime on Line 3?",
        user_role="CXO",
        industry_id="manufacturing"
    ):
        events.append(event)

    event_names = [e["event"] for e in events]
    assert "trace_step" in event_names
    assert "final_response" in event_names

    final_data = next(e["data"] for e in events if e["event"] == "final_response")
    assert "validation_report" in final_data
    assert final_data["validation_report"]["grounding_score"] >= 0.80
    assert len(final_data["findings"]) > 0
