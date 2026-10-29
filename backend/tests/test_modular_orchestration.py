import pytest
import time
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.ingestion.pipeline import pipeline
from app.retrieval.hybrid_index import hybrid_index
from app.orchestration.engine import modular_orchestrator, ModularPipelineEngine

client = TestClient(app)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "industries" / "manufacturing" / "data" / "unstructured"

@pytest.fixture(autouse=True)
def setup_hybrid_index():
    if DATA_DIR.exists():
        chunks, _ = pipeline.ingest_directory(DATA_DIR)
        hybrid_index.clear()
        hybrid_index.add_chunks(chunks)
from app.orchestration.contracts import (
    IntentCategory, AgentStatus, ExecutionMode,
    QueryUnderstandingResult, ExtractedEvidenceItem
)
from app.orchestration.registry import agent_registry, AgentManifest
from app.orchestration.taxonomy import intent_taxonomy, IntentDefinition
from app.agents.query_understanding_agent import query_understanding_agent
from app.agents.intent_classification_agent import intent_classification_agent
from app.agents.routing_agent import routing_agent
from app.agents.investigation_planner import investigation_planner
from app.agents.structured_document_agent import structured_document_agent
from app.agents.unstructured_document_agent import unstructured_document_agent
from app.agents.evidence_extraction_agent import evidence_extraction_agent
from app.agents.summarizer_agent import summarizer_agent
from app.agents.traceability_agent import traceability_agent
from app.orchestration.trace import ExecutionTracer
from app.schemas.query import CitationItem, FindingItem, FactClassification

# =====================================================================
# 1. Structured-Only Query Test
# =====================================================================
def test_modular_structured_only_query():
    query = "What is the total downtime in minutes logged for Line 3 Assembly?"
    understanding = query_understanding_agent.process(query)
    assert "line_id" in understanding.entities or "Line 3" in understanding.normalized_query

    classification = intent_classification_agent.classify(understanding)
    assert classification.predicted_intent == IntentCategory.STRUCTURED_TELEMETRY
    assert "SQL_DATABASE" in classification.target_source_types

    routing = routing_agent.route(understanding, classification, user_role="CXO")
    assert "structured_document_agent" in routing.selected_agents
    assert "unstructured_document_agent" in routing.skipped_agents

    response = modular_orchestrator.execute(query, user_role="CXO")
    assert response.query_id.startswith("qry_")
    assert len(response.citations) >= 1
    assert any("SQL" in c.source_type for c in response.citations)

# =====================================================================
# 2. Unstructured Document-Only Query Test
# =====================================================================
def test_modular_unstructured_document_only_query():
    query = "What are the standard operating procedures and inspection protocols for hydraulic pump depressurization?"
    understanding = query_understanding_agent.process(query)
    classification = intent_classification_agent.classify(understanding)
    assert classification.predicted_intent == IntentCategory.PROCEDURAL_GUIDANCE
    assert "DOCUMENT_STORE" in classification.target_source_types

    routing = routing_agent.route(understanding, classification, user_role="CXO")
    assert "unstructured_document_agent" in routing.selected_agents
    assert "structured_document_agent" in routing.skipped_agents

    response = modular_orchestrator.execute(query, user_role="CXO")
    assert len(response.citations) >= 1
    assert any("DOCUMENT" in c.source_type for c in response.citations)

# =====================================================================
# 3. Cross-Source Queries Using Both Document Agents
# =====================================================================
def test_modular_cross_source_query():
    query = "What caused downtime on Line 3 and what SOP steps were recommended to prevent it?"
    understanding = query_understanding_agent.process(query)
    classification = intent_classification_agent.classify(understanding)
    assert classification.predicted_intent == IntentCategory.CROSS_SOURCE_INVESTIGATION

    plan = investigation_planner.plan(understanding, classification, routing_agent.route(understanding, classification))
    assert len(plan.tasks) == 2
    task_agents = {t.assigned_agent for t in plan.tasks}
    assert "structured_document_agent" in task_agents
    assert "unstructured_document_agent" in task_agents

    response = modular_orchestrator.execute(query, user_role="CXO")
    assert len(response.trace_steps) >= 7
    # Both SQL and Document citations present
    source_types = {c.source_type for c in response.citations}
    assert "SQL_QUERY" in source_types
    assert "DOCUMENT_SOP" in source_types

# =====================================================================
# 4. Multi-Intent Queries Requiring Multiple Tasks
# =====================================================================
def test_modular_multi_intent_decomposition():
    query = "Investigate supplier defect rates for Apex and correlate with Plant A downtime work orders"
    understanding = query_understanding_agent.process(query)
    classification = intent_classification_agent.classify(understanding)
    
    # Must identify primary and secondary intents
    all_intents = [classification.predicted_intent] + classification.secondary_intents
    assert IntentCategory.QUALITY_SUPPLIER_ANALYSIS in all_intents
    assert any(cat in all_intents for cat in [IntentCategory.STRUCTURED_TELEMETRY, IntentCategory.CROSS_SOURCE_INVESTIGATION])
    plan = investigation_planner.plan(understanding, classification, routing_agent.route(understanding, classification))
    assert len(plan.tasks) >= 2
    assert plan.execution_mode == ExecutionMode.PARALLEL

# =====================================================================
# 5. Unknown or Ambiguous Intent with Fallback
# =====================================================================
def test_modular_ambiguous_intent_fallback():
    # Ambiguous query with low confidence
    query = "xyz random gibberish 12345"
    understanding = query_understanding_agent.process(query)
    classification = intent_classification_agent.classify(understanding)
    
    assert classification.fallback_triggered is True
    assert classification.fallback_reason is not None
    # Conservative fallback ensures no crashes
    assert classification.predicted_intent == IntentCategory.CROSS_SOURCE_INVESTIGATION

# =====================================================================
# 6. Empty Retrieval Results & Insufficient Evidence
# =====================================================================
def test_modular_empty_retrieval_insufficient_evidence():
    # Query referencing an unindexed non-existent facility
    query = "What is the paint shop solvent emission rate at Plant Z?"
    response = modular_orchestrator.execute(query, user_role="CXO")
    
    assert response.is_abstained is True
    assert "Safe Abstention" in response.executive_summary or "Information Boundary" in response.executive_summary
    assert response.confidence_score == 0.0 or response.validation_report.is_abstained is True

# =====================================================================
# 7. Conflicting Source Evidence (CONF-01)
# =====================================================================
def test_modular_conflicting_source_evidence_detected():
    query = "What actions were completed for Line 3 maintenance and why did downtime recur?"
    response = modular_orchestrator.execute(query, user_role="CXO")
    
    assert len(response.conflicts) >= 1
    conf = response.conflicts[0]
    assert "CONF-01" in conf.conflict_id
    assert "March 10" in conf.description or "March 14" in conf.description

# =====================================================================
# 8. Agent Failure & Graceful Degradation
# =====================================================================
def test_modular_agent_failure_graceful_degradation():
    class FailingStructuredAgent:
        def execute_task(self, query, user_role="CXO"):
            from app.orchestration.contracts import StructuredRetrievalResult, AgentStatus, AgentError
            return StructuredRetrievalResult(
                status=AgentStatus.FAILED,
                query_executed="SELECT * FROM error;",
                rows_returned=0,
                summary="Simulated DB Connection Timeout",
                latency_ms=12.0,
                is_safe=False,
                error=AgentError(error_code="DB_TIMEOUT", message="Simulated failure", retryable=True)
            )
        def to_citation_item(self, res):
            return CitationItem(citation_id="FALLBACK", title="Fallback", source_type="SQL_QUERY", reference="Fallback", snippet="Fallback")

    engine = ModularPipelineEngine()
    engine.stage5_structured = FailingStructuredAgent()

    # Even if SQL fails, pipeline should degrade gracefully and utilize unstructured evidence
    resp = engine.execute("What SOP steps should technicians follow for Line 3 hydraulics?", user_role="CXO")
    assert resp is not None
    assert resp.executive_summary != ""

# =====================================================================
# 9. Invalid Structured Output & Safe Handling
# =====================================================================
def test_modular_invalid_structured_output_handling():
    understanding = query_understanding_agent.process("What were the scrap counts on Line 1?")
    classification = intent_classification_agent.classify(understanding)
    
    # Verify classification output respects schema bounds
    assert 0.0 <= classification.confidence <= 1.0
    assert 0.0 <= classification.uncertainty <= 1.0
    assert classification.confidence + classification.uncertainty == pytest.approx(1.0, 0.01)

# =====================================================================
# 10. Citation Validation Failure Guard
# =====================================================================
def test_modular_citation_validation_guard():
    tracer = ExecutionTracer(original_query="Audit check")
    # Fabricated / empty citation should fail audit
    bad_citation = CitationItem(
        citation_id="FAKE-01",
        title="Fabricated Document",
        source_type="DOCUMENT_SOP",
        reference="NonExistent.pdf",
        snippet="" # empty snippet
    )
    findings = [
        FindingItem(
            statement="Factual claim without support",
            classification=FactClassification.VERIFIED_FACT,
            citation_ids=["FAKE-01"]
        )
    ]
    report = tracer.validate_trace_and_citations([bad_citation], findings, is_abstained=False)
    assert report.is_valid is False
    assert "FAKE-01" in report.unsupported_citations

# =====================================================================
# 11. Unauthorized Source Access Attempts Blocked
# =====================================================================
def test_modular_unauthorized_source_access_blocked():
    # Register an agent requiring high clearance
    restricted_manifest = AgentManifest(
        agent_id="executive_financial_audit_agent",
        label="Financial Audit Agent",
        capabilities=["financial_audit"],
        target_sources=["CONFIDENTIAL_LEDGER"],
        required_role="CXO" # Operator must NOT access
    )
    agent_registry.register_agent(restricted_manifest, None)

    # Operator role should be blocked
    has_operator_access = agent_registry.validate_authorization("executive_financial_audit_agent", user_role="OPERATOR")
    assert has_operator_access is False

    # CXO role should be granted
    has_cxo_access = agent_registry.validate_authorization("executive_financial_audit_agent", user_role="CXO")
    assert has_cxo_access is True

# =====================================================================
# 12. Trace Completeness and Evidence Lineage
# =====================================================================
def test_modular_trace_completeness_and_lineage():
    query = "What caused downtime on Line 3 and what SOP steps were recommended?"
    response = modular_orchestrator.execute(query, user_role="CXO")
    
    # Verify modular pipeline stages are recorded in trace steps
    recorded_agents = {step.agent_name for step in response.trace_steps}
    expected_stages = {
        "query_understanding_agent",
        "intent_classification_agent",
        "query_router",
        "investigation_planner",
        "structured_data_agent",
        "document_intelligence_agent",
        "evidence_extraction_agent",
        "evidence_validation_agent",
        "synthesis_agent",
        "traceability_agent"
    }
    assert expected_stages.issubset(recorded_agents)

# =====================================================================
# 13. Follow-Up Query Context Preservation
# =====================================================================
def test_modular_follow_up_query_understanding():
    query_1 = "What caused downtime on Line 3?"
    u1 = query_understanding_agent.process(query_1)
    assert "Line 3" in u1.entities.get("line_id", "")

    # Follow-up using anaphora/reference
    query_2 = "What SOP actions should technicians take for this line?"
    u2 = query_understanding_agent.process(query_2)
    assert u2.primary_intent in ["corrective_action_retrieval", "operational_investigation"]

# =====================================================================
# 14. Registration of a New Agent Without Modifying Core Logic
# =====================================================================
def test_modular_register_new_agent_dynamically():
    custom_manifest = AgentManifest(
        agent_id="vibration_iot_sensor_agent",
        version="1.0.0",
        label="IoT Vibration Telemetry Agent",
        capabilities=["iot_vibration_stream"],
        target_sources=["MQTT_SENSOR_STREAM"],
        required_role="RELIABILITY_ENGINEER"
    )

    class DummyIoTHandler:
        def get_vibration_spectrum(self, machine_id):
            return {"peak_frequency_hz": 120.5, "status": "ANOMALOUS"}

    # Dynamic registration
    agent_registry.register_agent(custom_manifest, DummyIoTHandler())

    # Verify discovery by capability and source
    found_agents = agent_registry.find_agents_for_capability("iot_vibration_stream")
    assert len(found_agents) == 1
    assert found_agents[0].agent_id == "vibration_iot_sensor_agent"

    found_sources = agent_registry.find_agents_for_source("MQTT_SENSOR_STREAM")
    assert len(found_sources) == 1
    assert found_sources[0].label == "IoT Vibration Telemetry Agent"
