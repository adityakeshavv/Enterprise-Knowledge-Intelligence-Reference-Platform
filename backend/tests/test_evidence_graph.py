import pytest
from app.agents.graph_builder import evidence_graph_builder, EvidenceGraphBuilder
from app.orchestration.orchestrator import multi_agent_orchestrator
from app.schemas.query import (
    CitationItem, ConflictItem, FindingItem, FactClassification
)

def test_evidence_graph_builder_normal():
    """Verify standard query graph topology construction."""
    builder = EvidenceGraphBuilder()
    
    citations = [
        CitationItem(
            citation_id="SQL-01",
            title="Downtime Telemetry",
            source_type="SQL_QUERY",
            reference="plant_downtime_events",
            snippet="Line 3 recorded 1080 min downtime."
        ),
        CitationItem(
            citation_id="DOC-01",
            title="Line 3 Maintenance SOP",
            source_type="DOCUMENT_SOP",
            reference="SOP-Maint-Line3.pdf",
            snippet="Hydraulic seal requires inspection."
        )
    ]

    findings = [
        FindingItem(
            statement="Structured Telemetry: Line 3 downtime was 18.0 hours [SQL-01]",
            classification=FactClassification.VERIFIED_FACT,
            citation_ids=["SQL-01"],
            confidence=0.98
        ),
        FindingItem(
            statement="Operating Protocol: Replace seal every 250 hours [DOC-01]",
            classification=FactClassification.VERIFIED_FACT,
            citation_ids=["DOC-01"],
            confidence=0.95
        ),
        FindingItem(
            statement="Recommended Action: Flush hydraulic fluid during shift change",
            classification=FactClassification.ANALYTICAL_INFERENCE,
            citation_ids=[],
            confidence=0.88
        )
    ]

    graph = builder.build_graph(
        query_text="What caused downtime on Line 3 and what action to take?",
        findings=findings,
        citations=citations,
        conflicts=[],
        is_abstained=False
    )

    assert len(graph.nodes) >= 6 # 1 query + 2 sources + 3 findings
    node_types = {n.node_type for n in graph.nodes}
    assert "query" in node_types
    assert "sql_source" in node_types
    assert "doc_source" in node_types
    assert "finding" in node_types

    assert len(graph.edges) >= 4
    relations = {e.relation for e in graph.edges}
    assert "RETRIEVED" in relations
    assert "GROUNDS" in relations

def test_evidence_graph_builder_with_conflict():
    """Verify discrepancy/conflict node and contradiction edge tagging."""
    builder = EvidenceGraphBuilder()
    citations = [
        CitationItem(
            citation_id="DOC-01",
            title="Shift Incident Log",
            source_type="DOCUMENT_SOP",
            reference="Shift_Logs_Q1.xlsx",
            snippet="Seal replacement finished March 10."
        ),
        CitationItem(
            citation_id="SQL-01",
            title="Plant Downtime Events",
            source_type="SQL_QUERY",
            reference="plant_downtime_events",
            snippet="Event EVT-409 recorded stoppage on March 14."
        )
    ]
    conflicts = [
        ConflictItem(
            conflict_id="CONF-01",
            title="Maintenance Completion vs Telemetry Stoppage",
            description="March 10 maintenance completion contradicted by March 14 downtime event.",
            source_a="Shift_Logs_Q1.xlsx",
            source_b="plant_downtime_events",
            recommendation="Inspect physical valve seals."
        )
    ]

    graph = builder.build_graph(
        query_text="Explain Line 3 maintenance discrepancy",
        findings=[],
        citations=citations,
        conflicts=conflicts,
        is_abstained=False
    )

    conf_nodes = [n for n in graph.nodes if n.node_type == "conflict"]
    assert len(conf_nodes) == 1
    assert conf_nodes[0].category == "discrepancy"

    conflict_edges = [e for e in graph.edges if e.is_conflict]
    assert len(conflict_edges) >= 1
    assert conflict_edges[0].relation == "CONTRADICTS"

def test_evidence_graph_builder_abstained():
    """Verify boundary node structure when safe abstention is triggered."""
    builder = EvidenceGraphBuilder()
    graph = builder.build_graph(
        query_text="What are the paint shop chemical burn protocols?",
        findings=[],
        citations=[],
        conflicts=[],
        is_abstained=True
    )

    assert len(graph.nodes) == 2
    assert graph.nodes[0].node_type == "query"
    assert graph.nodes[1].id == "node_abstention_boundary"
    assert len(graph.edges) == 1
    assert graph.edges[0].relation == "BLOCKED_BY"
    assert graph.edges[0].is_conflict is True

def test_orchestrator_end_to_end_evidence_graph():
    """Verify multi-agent orchestrator returns populated evidence graph."""
    query = "What caused the downtime on Line 3 in Plant A?"
    resp = multi_agent_orchestrator.orchestrate(
        query_text=query,
        user_role="CXO",
        industry_id="manufacturing"
    )

    assert resp.evidence_graph is not None
    assert len(resp.evidence_graph.nodes) >= 4
    assert len(resp.evidence_graph.edges) >= 3

    # Check query node
    query_node = next((n for n in resp.evidence_graph.nodes if n.node_type == "query"), None)
    assert query_node is not None

    # Check source node
    src_node = next((n for n in resp.evidence_graph.nodes if "source" in n.node_type), None)
    assert src_node is not None

@pytest.mark.asyncio
async def test_orchestrator_stream_evidence_graph():
    """Verify streaming response delivers complete evidence graph in final response."""
    events = []
    async for event in multi_agent_orchestrator.stream_orchestration(
        query_text="What caused the downtime on Line 3?",
        user_role="CXO",
        industry_id="manufacturing"
    ):
        events.append(event)

    final_data = next(e["data"] for e in events if e["event"] == "final_response")
    assert "evidence_graph" in final_data
    graph_data = final_data["evidence_graph"]
    assert len(graph_data["nodes"]) >= 4
    assert len(graph_data["edges"]) >= 3
