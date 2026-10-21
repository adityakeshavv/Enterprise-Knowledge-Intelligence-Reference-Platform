import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.ingestion.pipeline import pipeline
from app.retrieval.hybrid_index import hybrid_index
from app.retrieval.retriever import document_retriever
from app.agents.document_agent import document_agent

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "config" / "industries" / "manufacturing" / "data" / "unstructured"

@pytest.fixture(autouse=True)
def setup_hybrid_index():
    chunks, _ = pipeline.ingest_directory(DATA_DIR)
    hybrid_index.clear()
    hybrid_index.add_chunks(chunks)

def test_bm25_exact_part_number_retrieval():
    # Exact part number search should rank high
    results = document_retriever.retrieve("AFD-SEAL-882", top_k=3)
    assert len(results) > 0

    top_chunk = results[0]["chunk"]
    assert "AFD-SEAL-882" in top_chunk.text
    assert results[0]["score"] > 0.4

def test_semantic_query_retrieval():
    # Semantic question regarding fluid flush interval
    results = document_retriever.retrieve("What is the required fluid flush interval to prevent pump cavitation?", top_k=2)
    assert len(results) > 0

    full_text = " ".join(r["chunk"].text for r in results)
    assert "250 operational hours" in full_text or "fluid" in full_text.lower()

def test_clearance_filtering():
    # Operator role (Internal clearance) vs CXO (Restricted)
    results_cxo = document_retriever.retrieve("Apex seal advisory", user_role="CXO")
    assert len(results_cxo) > 0

    # Ensure search returns valid citations
    top_citation = results_cxo[0]["citation"]
    assert top_citation.citation_id.startswith("Doc-")
    assert top_citation.reference != ""

def test_document_agent_end_to_end():
    res = document_agent.process(
        query="Explain hydraulic seal failure root causes and corrective SOP flush protocols",
        user_role="CXO"
    )
    assert res["status"] == "completed"
    assert len(res["citations"]) >= 2
    assert len(res["evidence_fences"]) >= 2
    assert any("<retrieved_evidence" in f for f in res["evidence_fences"])

def test_api_documents_list_and_search():
    client = TestClient(app)
    
    # Test list endpoint
    list_res = client.get("/api/documents/list")
    assert list_res.status_code == 200
    data = list_res.json()
    assert data["total_chunks"] >= 5
    assert data["total_documents"] >= 3

    # Test search endpoint
    search_res = client.post("/api/documents/search", json={
        "query": "AFD-SEAL-882 replacement date",
        "top_k": 3
    })
    assert search_res.status_code == 200
    search_data = search_res.json()
    assert search_data["status"] == "completed"
    assert len(search_data["citations"]) > 0
