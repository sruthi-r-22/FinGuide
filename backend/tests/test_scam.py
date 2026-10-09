import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_scam_samples():
    response = client.get("/api/scam/samples")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4
    assert any("KYC" in s["title"] for s in data)

def test_analyze_scam_message():
    fake_msg = "Your account is blocked! Click http://bit.ly/sbi-verify within 24 hours to update KYC and share OTP."
    response = client.post("/api/scam/analyze", json={"message_text": fake_msg})
    assert response.status_code == 200
    data = response.json()
    assert "potential_warning_signs" in data
    assert len(data["potential_warning_signs"]) >= 2
    assert "why_suspicious" in data
    assert "safe_actions" in data
    assert len(data["official_safety_resources"]) >= 2
    assert "CRITICAL" in data["risk_level"] or "ELEVATED" in data["risk_level"]

def test_reject_sensitive_credentials_in_scam_input():
    credential_msg = "Here is my debit card 4111 2222 3333 4444"
    response = client.post("/api/scam/analyze", json={"message_text": credential_msg})
    assert response.status_code == 400
    assert "sensitive" in response.json()["detail"].lower()
