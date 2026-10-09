import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_chat_with_valid_question():
    response = client.post("/api/chat", json={"question": "What is KYC and what documents are required?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert len(data["answer"]) > 50
    assert "sources" in data
    assert "follow_up_questions" in data
    assert len(data["follow_up_questions"]) >= 2
    assert "disclaimer" in data

def test_chat_detects_sensitive_pin_or_card():
    response = client.post("/api/chat", json={"question": "My upi-pin: 1234 is not working, why?"})
    assert response.status_code == 200
    data = response.json()
    assert data["has_warning"] is True
    assert "warning_message" in data
    assert "Sensitive Credential Detected" in data["answer"]
    # Sources should be empty when blocked for security
    assert len(data["sources"]) == 0

def test_chat_empty_question():
    response = client.post("/api/chat", json={"question": ""})
    assert response.status_code == 422 or response.status_code == 400

def test_chat_sources_metadata():
    response = client.get("/api/sources")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert len(data["documents"]) >= 1
    assert data["total_chunks"] > 0
    for document in data["documents"]:
        assert document["document_id"]
        if document["content_type"] == "generated_demo":
            assert document["is_generated_summary"] is True
            assert document["reference_status"] == "unverified"
            assert document["last_verified"] is None
            assert document["source_url"] is None
            assert "official-source verification failed" in document["provenance_note"]
            assert "content_type is generated_demo" in document["provenance_note"]
        elif document["content_type"] == "official_document":
            assert document["publisher"] == "Reserve Bank of India"
            assert document["reference_status"] == "verified"
            assert document["source_url"].startswith("https://www.rbi.org.in/")


def test_chat_does_not_treat_demo_as_verified_upi_collect_guidance():
    response = client.post(
        "/api/chat",
        json={"question": "What is a UPI collect request and how should I handle it?"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is False
    assert data["has_warning"] is True
    assert data["sources"]
    assert all(source["content_type"] == "generated_demo" for source in data["sources"])
    assert all(source["reference_status"] == "unverified" for source in data["sources"])
    assert all(source["source_url"] is None for source in data["sources"])
    assert data["further_reading"] == []
    assert "could not verify" in data["answer"].lower()


def test_chat_upi_pin_answer_cites_retrieved_rbi_evidence_with_caveat():
    response = client.post(
        "/api/chat",
        json={"question": "Do I need to enter my UPI PIN to receive money?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is True
    assert data["has_warning"] is False
    assert len(data["sources"]) == 1
    assert data["sources"][0]["source_url"] == (
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11040"
    )
    assert data["sources"][0]["page_number"] == 3
    assert "does not specifically say whether a PIN is needed to receive money" in (
        data["answer"]
    )


def test_chat_does_not_confirm_demo_failed_transaction_deadline():
    response = client.post(
        "/api/chat",
        json={
            "question": (
                "Is a failed UPI transaction guaranteed to be refunded within "
                "T+1 working days?"
            )
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_grounded"] is True
    assert data["has_warning"] is False
    assert "t + 1 day" in data["answer"].lower()
    assert "t + 5 days" in data["answer"].lower()
    assert "universal refund guarantee" in data["answer"].lower()
    assert data["sources"]
    assert all(
        source["source_url"] == (
            "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11693"
        )
        and source["content_type"] == "official_document"
        and source["reference_status"] == "verified"
        for source in data["sources"]
    )
    assert data["further_reading"] == []
