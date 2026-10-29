import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_query_flow_manufacturing():
    payload = {
        "query": "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?",
        "industry_id": "manufacturing"
    }
    response = client.post("/api/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["industry_id"] == "manufacturing"
    assert "Plant A" in data["executive_summary"]
    assert len(data["key_findings"]) >= 3
    assert len(data["metrics"]) >= 3
    assert len(data["citations"]) >= 2
    assert len(data["conflicts"]) >= 1  # Verifies conflict trap is active
    assert len(data["trace_steps"]) >= 5
    assert data["confidence_score"] > 0.8

def test_config_active_switching_api():
    # Ensure baseline is manufacturing
    client.post("/api/config/active", json={"industry_id": "manufacturing"})
    
    # 1. Check default active
    res1 = client.get("/api/config/active")
    assert res1.status_code == 200
    assert res1.json()["id"] == "manufacturing"
    
    # 2. Switch to retail_cpg
    switch_res = client.post("/api/config/active", json={"industry_id": "retail_cpg"})
    assert switch_res.status_code == 200
    
    # 3. Verify active updated
    res2 = client.get("/api/config/active")
    assert res2.status_code == 200
    assert res2.json()["id"] == "retail_cpg"
    
    # 4. Switch back to manufacturing
    switch_res2 = client.post("/api/config/active", json={"industry_id": "manufacturing"})
    assert switch_res2.status_code == 200
    assert client.get("/api/config/active").json()["id"] == "manufacturing"

def test_frontend_static_serving():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

