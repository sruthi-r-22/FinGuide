import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_all_glossary_terms():
    response = client.get("/api/glossary")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 15
    terms = [item["term"].lower() for item in data]
    assert "kyc" in terms
    assert "neft" in terms
    assert "upi" in terms

def test_filter_glossary_by_search():
    response = client.get("/api/glossary?search=rtgs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["term"] == "RTGS"
    assert "Real Time Gross Settlement" in data[0]["full_form"]

def test_glossary_detail():
    response = client.get("/api/glossary/ifsc")
    assert response.status_code == 200
    data = response.json()
    assert data["term"] == "IFSC"
    assert "Indian Financial System Code" in data["full_form"]
    assert "safety_note" in data

def test_glossary_not_found():
    response = client.get("/api/glossary/unknown_term_xyz")
    assert response.status_code == 404
