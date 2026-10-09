import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_generate_savings_checklist():
    response = client.post("/api/checklist", json={"task": "savings_account"})
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "savings_account"
    assert len(data["items"]) >= 3
    assert any("Proof of Identity" in item["requirement"] for item in data["items"])
    assert "disclaimer" in data

def test_generate_checklist_with_bank_filter():
    response = client.post("/api/checklist", json={"task": "savings_account", "bank": "sbi"})
    assert response.status_code == 200
    data = response.json()
    assert data["bank"] == "sbi"
    assert "SBI" in data["task_title"]

def test_download_checklist_pdf():
    response = client.post("/api/checklist/pdf", json={"task": "savings_account"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 1000  # valid non-empty PDF
    assert response.content.startswith(b"%PDF")

def test_invalid_checklist_request():
    response = client.post("/api/checklist", json={"task": ""})
    assert response.status_code == 400
