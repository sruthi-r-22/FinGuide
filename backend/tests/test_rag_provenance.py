import hashlib
import json
import sys
import types
from pathlib import Path

import pytest

from backend.app.rag import generator, ingest, retriever
from backend.app.rag.generator import (
    build_citations,
    generate_grounded_answer,
    is_verified_official_metadata,
)
from backend.app.rag.relevance import (
    RETRIEVAL_SCORE_THRESHOLD,
    cosine_similarity_from_squared_l2,
)
from backend.app.rag.retriever import IncompatibleCollectionError, VectorStoreManager


def verified_upi_chunk(text="Never share your UPI PIN with anyone.", score=0.8):
    return {
        "text": text,
        "score": score,
        "metadata": {
            "document_id": "sha256:" + ("a" * 64),
            "document_title": "Mock verified UPI safety FAQ",
            "page_number": 1,
            "publisher": "National Payments Corporation of India",
            "authority": "National Payments Corporation of India",
            "source_url": "https://www.npci.org.in/what-we-do/upi/faqs",
            "published_date": "2025-01-01",
            "verified_by": "test reviewer",
            "last_verified": "2026-10-09",
            "content_type": "official_document",
            "is_generated_summary": False,
            "reference_status": "verified",
            "verification_method": "manual_origin_and_sha256_review",
            "sha256": "a" * 64,
        },
    }


def demo_chunk(text, score=0.8):
    return {
        "text": text,
        "score": score,
        "metadata": {
            "document_id": "sha256:" + ("b" * 64),
            "document_title": (
                "FinGuide AI educational demo — NPCI UPI Safety Summary"
            ),
            "filename": "NPCI_UPI_Safety_and_Operating_Guidelines.pdf",
            "publisher": "FinGuide AI",
            "page_number": 1,
            "content_type": "generated_demo",
            "is_generated_summary": True,
            "reference_status": "unverified",
            "provenance_note": ingest.GENERATED_DEMO_NOTE,
        },
    }


def official_chunks_for(url, terms):
    chunks = ingest.load_all_document_chunks()
    candidates = [
        {**chunk, "score": 0.9}
        for chunk in chunks
        if chunk["metadata"].get("source_url") == url
    ]
    matches = [
        chunk for chunk in candidates
        if all(term in chunk["text"].lower() for term in terms)
    ]
    if matches:
        return matches

    anchors = [
        chunk for chunk in candidates
        if "unified payments interface (upi)" in chunk["text"].lower()
    ]
    for anchor in anchors:
        chunk_id = anchor["id"]
        id_parts = chunk_id.rsplit(":c", 1)
        if len(id_parts) != 2 or not id_parts[1].isdigit():
            continue
        next_id = f"{id_parts[0]}:c{int(id_parts[1]) + 1}"
        row_chunks = [
            chunk for chunk in candidates
            if chunk["id"] in (chunk_id, next_id)
        ]
        row_text = " ".join(chunk["text"].lower() for chunk in row_chunks)
        if row_chunks and all(term in row_text for term in terms):
            return row_chunks
    return []


def test_squared_l2_distance_maps_to_cosine_for_normalized_vectors():
    assert cosine_similarity_from_squared_l2(0.8906185) == pytest.approx(0.55469075)


def test_registered_demo_chunks_have_no_asserted_official_provenance():
    chunks = ingest.load_all_document_chunks()

    assert chunks
    demo_chunks = [
        chunk for chunk in chunks
        if chunk["metadata"]["content_type"] == "generated_demo"
    ]
    official_chunks = [
        chunk for chunk in chunks
        if chunk["metadata"]["content_type"] == "official_document"
    ]
    assert demo_chunks
    assert official_chunks
    for chunk in demo_chunks:
        metadata = chunk["metadata"]
        assert metadata["document_id"].startswith("sha256:")
        assert metadata["document_title"].startswith("FinGuide AI educational demo")
        assert metadata["content_type"] == "generated_demo"
        assert metadata["is_generated_summary"] is True
        assert metadata["publisher"] == "FinGuide AI"
        assert metadata["reference_status"] == "unverified"
        assert "not an official publication" in metadata["provenance_note"]
        assert "authority" not in metadata
        assert "last_verified" not in metadata
        assert "source_url" not in metadata
    for chunk in official_chunks:
        metadata = chunk["metadata"]
        assert metadata["reference_status"] == "verified"
        assert metadata["publisher"] == "Reserve Bank of India"
        assert metadata["source_url"].startswith("https://www.rbi.org.in/")


def test_unknown_pdf_metadata_is_not_invented(monkeypatch, tmp_path):
    class FakePage:
        def extract_text(self):
            return "An unregistered source document."

    class FakeReader:
        pages = [FakePage()]

        def __init__(self, filepath):
            pass

    pdf_path = tmp_path / "unknown_source.pdf"
    pdf_path.write_bytes(b"unknown PDF bytes")
    monkeypatch.setattr(ingest, "PdfReader", FakeReader)
    chunks = ingest.extract_chunks_from_pdf(
        str(pdf_path),
        chunk_size=100,
        chunk_overlap=10,
    )

    metadata = chunks[0]["metadata"]
    assert metadata["content_type"] == "unknown"
    assert metadata["reference_status"] == "unknown"
    assert metadata["document_id"] == "sha256:" + hashlib.sha256(
        b"unknown PDF bytes"
    ).hexdigest()
    assert "is_generated_summary" not in metadata
    assert "publisher" not in metadata
    assert "authority" not in metadata
    assert "source_url" not in metadata


def test_verified_source_manifest_requires_official_host_and_matching_hash(
    monkeypatch, tmp_path
):
    class FakePage:
        def extract_text(self):
            return "Never share a UPI PIN to receive money."

    class FakeReader:
        pages = [FakePage()]

        def __init__(self, filepath):
            pass

    pdf_path = tmp_path / "npci_faq.pdf"
    pdf_bytes = b"verified PDF fixture bytes"
    pdf_path.write_bytes(pdf_bytes)
    manifest = {
        "title": "Mock verified NPCI UPI safety FAQ",
        "publisher": "National Payments Corporation of India",
        "source_url": "https://www.npci.org.in/what-we-do/upi/faqs",
        "sha256": hashlib.sha256(pdf_bytes).hexdigest(),
        "verified_by": "test reviewer",
        "verified_on": "2026-10-09",
        "published_date": "2025-01-01",
    }
    Path(f"{pdf_path}.source.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    monkeypatch.setattr(ingest, "PdfReader", FakeReader)

    metadata = ingest.extract_chunks_from_pdf(str(pdf_path))[0]["metadata"]
    assert metadata["content_type"] == "official_document"
    assert metadata["reference_status"] == "verified"
    assert metadata["verification_method"] == "manual_origin_and_sha256_review"
    assert metadata["document_id"] == f"sha256:{manifest['sha256']}"
    assert metadata["publisher"] == "National Payments Corporation of India"
    assert metadata["page_number"] == 1
    assert metadata["published_date"] == "2025-01-01"
    assert is_verified_official_metadata(metadata)

    manifest["sha256"] = "0" * 64
    Path(f"{pdf_path}.source.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="SHA-256 does not match"):
        ingest.extract_chunks_from_pdf(str(pdf_path))


def test_source_manifest_rejects_non_authoritative_host(monkeypatch, tmp_path):
    pdf_path = tmp_path / "claimed_official.pdf"
    pdf_path.write_bytes(b"source fixture")
    manifest = {
        "title": "Claimed official source",
        "publisher": "National Payments Corporation of India",
        "source_url": "https://example.com/upi",
        "sha256": hashlib.sha256(b"source fixture").hexdigest(),
        "verified_by": "test reviewer",
        "verified_on": "2026-10-09",
    }
    (tmp_path / "claimed_official.pdf.source.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )

    with pytest.raises(ValueError, match="official host"):
        ingest._official_metadata_for_pdf(str(pdf_path))


def test_rbi_customer_protection_source_supports_upi_credential_safety(monkeypatch):
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "")
    url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11040"
    chunks = official_chunks_for(url, ["payment credentials"])

    response = generate_grounded_answer(
        "Do I need to enter my UPI PIN to receive money?", chunks
    )

    assert response.is_grounded is True
    assert response.has_warning is False
    assert "does not specifically say whether a PIN is needed" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].source_url == url
    assert response.sources[0].page_number == 3
    assert response.sources[0].reference_status == "verified"


def test_llm_prompt_uses_verified_context_and_rejects_fabricated_citations(monkeypatch):
    chunk = verified_upi_chunk()
    captured = {}

    class FakeModel:
        @staticmethod
        def generate_content(prompt):
            captured["prompt"] = prompt
            return types.SimpleNamespace(
                text=(
                    "Never share your UPI PIN with anyone. "
                    "[sha256:" + ("a" * 64) + ":p1]"
                )
            )

    genai_module = types.ModuleType("google.generativeai")
    genai_module.configure = lambda **kwargs: None
    genai_module.GenerativeModel = lambda model_name: FakeModel()
    google_module = types.ModuleType("google")
    google_module.__path__ = []
    google_module.generativeai = genai_module
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai_module)
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "test-key")

    response = generate_grounded_answer("Summarize the official excerpt.", [chunk])

    assert response.is_grounded is True
    assert response.answer.endswith("[sha256:" + ("a" * 64) + ":p1]")
    assert "RETRIEVED VERIFIED OFFICIAL EVIDENCE" in captured["prompt"]
    assert "Do not apply unauthorized-transaction rules to ordinary failed transactions" in captured["prompt"]

    genai_module.GenerativeModel = lambda model_name: types.SimpleNamespace(
        generate_content=lambda prompt: types.SimpleNamespace(
            text="A fabricated claim. [sha256:" + ("c" * 64) + ":p7]"
        )
    )
    fallback_response = generate_grounded_answer(
        "Summarize the official excerpt.", [chunk]
    )
    assert "fabricated claim" not in fallback_response.answer
    assert "Never share your UPI PIN with anyone." in fallback_response.answer


def test_llm_is_not_invoked_for_generated_demo_sources(monkeypatch):
    calls = []
    genai_module = types.ModuleType("google.generativeai")
    genai_module.configure = lambda **kwargs: None
    genai_module.GenerativeModel = lambda model_name: calls.append(model_name)
    google_module = types.ModuleType("google")
    google_module.__path__ = []
    google_module.generativeai = genai_module
    monkeypatch.setitem(sys.modules, "google", google_module)
    monkeypatch.setitem(sys.modules, "google.generativeai", genai_module)
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "test-key")

    response = generate_grounded_answer(
        "Is a UPI failed transaction guaranteed to be refunded within T+1 working days?",
        [demo_chunk("Failed UPI payments are refunded within T+1 working days.")],
    )

    assert calls == []
    assert response.is_grounded is False
    assert "t+1" not in response.answer.lower()


def test_unverified_demo_is_not_labelled_official_or_linked():
    citations = build_citations([demo_chunk("Never share your UPI PIN.")])

    assert len(citations) == 1
    assert citations[0].content_type == "generated_demo"
    assert citations[0].reference_status == "unverified"
    assert citations[0].is_generated_summary is True
    assert citations[0].source_url is None
    assert citations[0].snippet == ""
    assert citations[0].document_title.startswith("FinGuide AI unverified material")


def test_unverified_refund_deadline_is_never_repeated_as_a_claim(monkeypatch):
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "")
    demo = demo_chunk(
        "Failed UPI payments are automatically refunded within T+1 working days."
    )
    official = official_chunks_for(
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11693",
        [
            "unified payments interface (upi)",
            "account debited",
            "t + 1 day",
            "t + 5 days",
        ],
    )

    response = generate_grounded_answer(
        "Is a failed UPI payment guaranteed to be refunded within T+1 working days?",
        official + [demo],
    )

    assert response.is_grounded is True
    assert response.has_warning is False
    assert "t + 1 day" in response.answer.lower()
    assert "t + 5 days" in response.answer.lower()
    assert "universal refund guarantee" in response.answer.lower()
    assert len(response.sources) == 1
    assert response.sources[0].source_url == (
        "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11693"
    )
    assert response.sources[0].content_type == "official_document"


def test_irrelevant_chunk_below_threshold_cannot_ground_answer(monkeypatch):
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "")
    chunk = verified_upi_chunk("Bank savings accounts may have fees.", score=0.1)

    response = generate_grounded_answer(
        "How do I respond to a UPI collect request?",
        [chunk],
    )

    assert 0.1 < RETRIEVAL_SCORE_THRESHOLD
    assert response.is_grounded is False
    assert response.has_warning is True
    assert response.sources == []
    assert "could not verify" in response.answer.lower()
    assert "savings accounts may have fees" not in response.answer.lower()


def test_missing_authoritative_evidence_returns_uncertainty(monkeypatch):
    monkeypatch.setattr(generator.settings, "GEMINI_API_KEY", "")

    response = generate_grounded_answer(
        "What is the UPI failed transaction refund deadline?",
        [],
    )

    assert response.is_grounded is False
    assert response.has_warning is True
    assert "could not verify" in response.answer.lower()
    assert response.sources == []

def test_upi_pin_without_official_evidence_keeps_uncertainty_warning():
    response = generate_grounded_answer(
        "Do I need to enter a UPI PIN to receive money?",
        [],
    )

    assert response.is_grounded is False
    assert response.has_warning is True
    assert response.sources == []
    assert response.further_reading == []
    assert "could not verify" in response.answer.lower()

def test_general_upi_safety_question_gets_supplementary_reference():
    response = generate_grounded_answer(
        "How do I stay safe with UPI payments?",
        [],
    )

    assert response.has_warning is True
    assert response.further_reading == []


def test_collect_answer_does_not_claim_inaccessible_npci_evidence():
    response = generate_grounded_answer(
        "Should I approve a UPI collect request to receive money?",
        [],
    )

    assert response.is_grounded is False
    assert response.has_warning is True
    assert response.sources == []
    assert response.further_reading == []
    assert "could not verify" in response.answer.lower()


def test_failed_transaction_answer_cites_retrieved_rbi_circular():
    url = "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11693"
    chunks = official_chunks_for(
        url,
        [
            "unified payments interface (upi)",
            "account debited",
            "t + 1 day",
            "t + 5 days",
        ],
    )
    response = generate_grounded_answer(
        "What should I do if a failed UPI transaction has deducted money?",
        chunks,
    )

    assert response.is_grounded is True
    assert response.has_warning is False
    assert "T + 1 day" in response.answer
    assert "T + 5 days" in response.answer
    assert len(response.sources) == 1
    assert response.sources[0].source_url == url
    assert response.sources[0].page_number == 4
    assert response.further_reading == []

def test_curated_demo_questions_produce_distinct_cautious_answers_and_links():
    cases = [
        (
            "Do I need to enter my UPI PIN to receive money?",
            "UPI PIN safety when receiving money",
            [],
        ),
        (
            "How should I handle an unexpected UPI collect or cashback request?",
            "Unexpected UPI collect or cashback request",
            [demo_chunk("Generated demo excerpt.")],
        ),
        (
            "What should I do if a failed UPI transaction has deducted money?",
            "Failed UPI payment with a debit",
            official_chunks_for(
                "https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=11693",
                [
                    "unified payments interface (upi)",
                    "account debited",
                    "t + 1 day",
                    "t + 5 days",
                ],
            ),
        ),
    ]
    responses = [
        generate_grounded_answer(question, chunks)
        for question, _, chunks in cases
    ]

    assert len({response.answer for response in responses}) == len(cases)
    for response, (_, answer_heading, chunks) in zip(responses, cases):
        assert answer_heading in response.answer
        if chunks and chunks[0].get("metadata", {}).get("reference_status") == "unverified":
            assert response.is_grounded is False
            assert response.has_warning is True
            assert "could not verify" in response.answer.lower()
            assert response.further_reading == []
        elif chunks:
            assert response.is_grounded is True
            assert response.has_warning is False
            assert response.sources
            assert response.sources[0].source_url == chunks[0]["metadata"]["source_url"]
        else:
            assert response.is_grounded is False
            assert response.has_warning is True
            assert "could not verify" in response.answer.lower()


def test_official_retrieved_answer_does_not_add_demo_further_reading():
    chunk = verified_upi_chunk("Do not share payment credentials.")

    response = generate_grounded_answer(
        "Summarize this verified excerpt.",
        [chunk],
    )

    assert response.is_grounded is True
    assert response.further_reading == []


def test_citations_match_verified_retrieved_source_and_page():
    chunk = verified_upi_chunk("Never share your UPI PIN with anyone.")

    citations = build_citations([chunk])

    assert len(citations) == 1
    assert citations[0].document_title == chunk["metadata"]["document_title"]
    assert citations[0].document_id == chunk["metadata"]["document_id"]
    assert citations[0].page_number == chunk["metadata"]["page_number"]
    assert citations[0].source_url == chunk["metadata"]["source_url"]
    assert citations[0].snippet == chunk["text"]
    assert citations[0].publisher == chunk["metadata"]["publisher"]
    assert citations[0].reference_status == "verified"


def test_verified_citation_without_source_url_is_not_presented_as_official():
    chunk = verified_upi_chunk("Never share your UPI PIN with anyone.")
    chunk["metadata"].pop("source_url")

    citations = build_citations([chunk])

    assert len(citations) == 1
    assert citations[0].source_url is None
    assert citations[0].snippet == ""
    assert citations[0].reference_status == "unverified"
    assert citations[0].last_verified is None
    assert citations[0].document_title.startswith(
        "FinGuide AI unverified material"
    )
    assert "no source URL is present" in citations[0].provenance_note


def test_demo_reference_url_is_withheld_with_verification_reason():
    chunk = demo_chunk("Never share your UPI PIN.")
    chunk["metadata"]["source_url"] = (
        "https://www.npci.org.in/what-we-do/upi/faqs"
    )

    citations = build_citations([chunk])

    assert citations[0].source_url is None
    assert citations[0].reference_status == "unverified"
    assert "content_type is generated_demo" in citations[0].provenance_note
    assert "reference_status is unverified" in citations[0].provenance_note
    assert "Reference withheld" in citations[0].provenance_note


def test_source_metadata_survives_vector_retrieval():
    expected_metadata = verified_upi_chunk()["metadata"]

    class FakeEmbedding:
        dimension = 2

        @staticmethod
        def embed_query(text):
            return [1.0, 0.0]

    class FakeCollection:
        @staticmethod
        def count():
            return 1

        @staticmethod
        def query(**kwargs):
            return {
                "ids": [["verified:page:1"]],
                "documents": [["Never share your UPI PIN with anyone."]],
                "metadatas": [[expected_metadata]],
                "distances": [[0.2]],
            }

    manager = VectorStoreManager()
    manager._embedding_fn = FakeEmbedding()
    manager.collection = FakeCollection()
    manager._initialized = True

    results = manager.retrieve("UPI PIN", top_k=1)

    assert results[0]["id"] == "verified:page:1"
    assert results[0]["metadata"] == expected_metadata
    assert results[0]["metadata"]["page_number"] == 1
    assert results[0]["metadata"]["reference_status"] == "verified"


def test_embedding_model_exposes_matching_document_and_query_dimensions(monkeypatch):
    class FakeSentenceTransformer:
        def __init__(self, model_name):
            self.model_name = model_name

        @staticmethod
        def get_embedding_dimension():
            return 3

        @staticmethod
        def encode(texts, **kwargs):
            vectors = [[1.0, 0.0, 0.0] for _ in texts]
            return types.SimpleNamespace(tolist=lambda: vectors)

    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        types.SimpleNamespace(SentenceTransformer=FakeSentenceTransformer),
    )
    from backend.app.rag.embeddings import SentenceTransformerEmbedding

    embedding = SentenceTransformerEmbedding("mock-model")

    assert len(embedding.embed_query("UPI safety")) == embedding.dimension == 3
    assert all(
        len(vector) == embedding.dimension
        for vector in embedding.embed_documents(["one", "two"])
    )


def test_dimension_mismatch_explains_backup_protected_reindex():
    class FakeEmbedding:
        model_name = "all-MiniLM-L6-v2"
        dimension = 384

    class FakeCollection:
        metadata = {}

        @staticmethod
        def count():
            return 1

        @staticmethod
        def get(**kwargs):
            return {"embeddings": [[0.0] * 256]}

    manager = VectorStoreManager()
    manager._embedding_fn = FakeEmbedding()
    manager.collection = FakeCollection()

    with pytest.raises(
        IncompatibleCollectionError,
        match="256-dimensional.*384-dimensional",
    ) as exc:
        manager._validate_collection()

    assert "backup first" in str(exc.value)
    assert "POST /api/sources/reindex" in str(exc.value)


def test_reindex_refuses_persistence_paths_outside_project(monkeypatch, tmp_path):
    external_directory = tmp_path / "user_chroma_data"
    external_directory.mkdir()
    marker = external_directory / "preserve.txt"
    marker.write_text("unrelated data")
    monkeypatch.setattr(
        retriever,
        "resolve_chroma_persist_dir",
        lambda: external_directory.resolve(),
    )

    with pytest.raises(RuntimeError, match="outside the FinGuide project"):
        VectorStoreManager()._backup_persistence_directory()

    assert marker.read_text() == "unrelated data"
    assert not list(tmp_path.glob("user_chroma_data.backup-*"))
