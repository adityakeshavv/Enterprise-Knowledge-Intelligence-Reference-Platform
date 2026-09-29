from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Nebula9 Enterprise Knowledge Intelligence"

def test_list_industries():
    response = client.get("/api/industries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    ids = [item["id"] for item in data]
    assert "manufacturing" in ids
    assert "retail_cpg" in ids

def test_get_industry_details():
    response = client.get("/api/industries/manufacturing")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "manufacturing"
    assert len(data["scenarios"]["scenarios"]) >= 4

def test_auth_login():
    response = client.post("/api/auth/login", json={"username": "executive"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "Executive"

def test_query_endpoint():
    response = client.post("/api/query", json={
        "query": "What are the major factors contributing to production downtime at Plant A, and what actions have previously reduced similar downtime?",
        "industry_id": "manufacturing"
    })
    assert response.status_code == 200
    data = response.json()
    assert "executive_summary" in data
    assert len(data["key_findings"]) >= 3
    assert len(data["citations"]) >= 2
    assert len(data["conflicts"]) == 1
    assert data["grounding_confidence"] >= 0.8
    assert len(data["agent_trace"]) == 6
