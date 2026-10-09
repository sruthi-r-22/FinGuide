import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_comparisons():
    response = client.get("/api/comparisons")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    topics = [item["topic"] for item in data]
    assert "neft-rtgs-imps" in topics
    assert "upi-vs-netbanking" in topics
    assert "savings-vs-current" in topics
    assert "debit-vs-credit" in topics

def test_get_comparison_detail():
    response = client.get("/api/comparisons/neft-rtgs-imps")
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "neft-rtgs-imps"
    assert len(data["columns"]) >= 3
    assert len(data["rows"]) >= 5
    assert len(data["official_sources"]) >= 2
    assert "neutral_summary" in data

def test_comparison_not_found():
    response = client.get("/api/comparisons/invalid_topic_name")
    assert response.status_code == 404
