import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.orchestration.router import query_router
from app.orchestration.state import QueryIntent, WorkflowState
from app.orchestration.orchestrator import multi_agent_orchestrator
from app.agents.synthesis_agent import synthesis_agent
from app.schemas.sql import SQLQueryResult

client = TestClient(app)

@pytest.fixture
def auth_headers():
    response = client.post(
        "/api/auth/login",
        json={"username": "cxo_exec", "password": "Executive2026!"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- 1. Router & Intent Classification Tests ---

def test_router_classification_structured():
    intent = query_router.classify_intent("What was the total downtime in minutes on Line 3?")
    assert intent == QueryIntent.STRUCTURED_ONLY

def test_router_classification_document():
    intent = query_router.classify_intent("What are the standard operating procedures and guidelines for pump depressurization?")
    assert intent == QueryIntent.DOCUMENT_ONLY

def test_router_classification_cross_source():
    query = "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?"
    intent = query_router.classify_intent(query)
    assert intent == QueryIntent.CROSS_SOURCE_HYBRID

def test_router_execution_plan_subtasks():
    query = "What caused downtime on Line 3 and what SOP steps were recommended?"
    plan = query_router.create_plan(query)
    assert plan.intent == QueryIntent.CROSS_SOURCE_HYBRID
    assert len(plan.subtasks) == 2
    task_agents = {t.agent_name for t in plan.subtasks}
    assert "structured_data_agent" in task_agents
    assert "document_intelligence_agent" in task_agents

# --- 2. State & Synthesis Agent Tests ---

def test_workflow_state_trace_step_tracking():
    state = WorkflowState(query_id="TEST_Q", raw_query="Test Query")
    step = state.add_trace_step(
        agent_name="query_router",
        agent_label="Query Router & Planner",
        status="completed",
        business_message="Test routing step",
        technical_detail="Decomposed into 2 subtasks",
        duration_ms=42.5
    )
    assert step.step_id == 1
    assert step.agent_name == "query_router"
    assert step.duration_ms == 42.5
    assert len(state.trace_steps) == 1

def test_synthesis_agent_cross_source_generation():
    state = WorkflowState(query_id="TEST_SYNTH", raw_query="What caused downtime on Line 3 and what actions to take?")
    state.plan = query_router.create_plan(state.raw_query)
    
    # Mock SQL result
    state.sql_result = SQLQueryResult(
        natural_query=state.raw_query,
        generated_sql="SELECT line_id, SUM(downtime_minutes) FROM plant_downtime_events GROUP BY line_id;",
        execution_duration_ms=18.2,
        rows_returned=1,
        columns=["line_id", "total_downtime"],
        rows=[{"line_id": "Line_3_Assembly", "total_downtime": 1080}],
        summary="Line_3_Assembly accounted for 1,080 minutes of downtime.",
        is_safe=True
    )

    # Mock Doc result
    state.doc_result = {
        "summary": "Found maintenance protocol in SOP-Maint-Line3-Hydraulics-v2.pdf",
        "claims": ["Preventive fluid replacement required every 250 operational hours."],
        "citations": []
    }

    summary, findings, metrics, conflicts = synthesis_agent.synthesize(state)

    assert "Line 3" in summary or "18.0" in summary
    assert len(findings) >= 2
    assert len(metrics) >= 3
    # Conflict detection (temporal discrepancy between shift log and telemetry)
    assert len(conflicts) >= 1
    assert "CONF-01" in conflicts[0].conflict_id

# --- 3. Multi-Agent Orchestrator End-to-End Tests ---

def test_orchestrator_cross_source_query():
    query = "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?"
    response = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert response.query_id.startswith("qry_")
    assert len(response.trace_steps) >= 4

    agent_names = [s.agent_name for s in response.trace_steps]
    assert "query_router" in agent_names
    assert "structured_data_agent" in agent_names
    assert "document_intelligence_agent" in agent_names
    assert "synthesis_agent" in agent_names

    # All trace steps must have completed status and positive latency
    for step in response.trace_steps:
        assert step.status == "completed"
        assert step.duration_ms >= 0

    assert len(response.citations) >= 1
    assert len(response.metrics) >= 2
    assert response.confidence_score >= 0.85
    assert response.total_latency_ms > 0

def test_orchestrator_sql_only_query():
    query = "What is the average OEE percentage for Line 1?"
    response = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert response.query_id.startswith("qry_")
    agent_names = [s.agent_name for s in response.trace_steps]
    assert "structured_data_agent" in agent_names
    # Must have SQL citation
    assert any(c.source_type == "SQL_QUERY" for c in response.citations)

def test_orchestrator_doc_only_query():
    query = "What is the procedure for safety depressurization in standard operating manual?"
    response = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert response.query_id.startswith("qry_")
    agent_names = [s.agent_name for s in response.trace_steps]
    assert "document_intelligence_agent" in agent_names

# --- 4. API Endpoints Integration Tests ---

def test_api_query_post_endpoint(auth_headers):
    payload = {
        "query": "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?",
        "industry_id": "manufacturing"
    }
    response = client.post("/api/query", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["industry_id"] == "manufacturing"
    assert len(data["trace_steps"]) >= 4
    assert len(data["citations"]) >= 1
    assert len(data["metrics"]) >= 2
    assert "executive_summary" in data
    assert data["total_latency_ms"] > 0

def test_api_query_stream_sse_endpoint():
    response = client.get(
        "/api/query/stream",
        params={"query": "What caused downtime at Plant A?", "industry": "manufacturing"}
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    
    # Check that stream contains events
    lines = response.text.split("\n\n")
    data_events = [line for line in lines if line.startswith("data:")]
    assert len(data_events) >= 3
