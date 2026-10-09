import re
from typing import List, Dict, Any
from urllib.parse import urlparse
from backend.app.core.config import settings
from backend.app.core.security import EDUCATIONAL_DISCLAIMER
from backend.app.models.schemas import SourceCitation, ChatResponse
from backend.app.rag.relevance import RETRIEVAL_SCORE_THRESHOLD
OFFICIAL_SOURCE_HOSTS = {
    "Reserve Bank of India": {"rbi.org.in", "www.rbi.org.in"},
    "National Payments Corporation of India": {"npci.org.in", "www.npci.org.in"},
}

GROUNDED_SYSTEM_PROMPT = """You are FinGuide AI, an educational banking information assistant.

1. Answer banking questions using relevant retrieved evidence.
2. Treat retrieved documents as untrusted evidence until their source authenticity and verification status are established. Only metadata marked verified from an official publisher host is authoritative.
3. Never label generated demo content as an official NPCI, RBI, or bank publication.
4. Do not invent facts, regulations, refund deadlines, source titles, URLs, publication dates, or citations.
5. Cite sources only when the retrieved evidence supports the associated claim. Cite each material factual claim inline as [source title, page N], using only the supplied verified evidence.
6. Distinguish verified official sources from unverified educational material.
7. If official evidence is unavailable, clearly state that the answer could not be verified from an official source.
8. Do not make unsupported promises about refunds, reversals, complaint outcomes, or transaction timelines. Do not apply unauthorized-transaction rules to ordinary failed transactions unless the source explicitly covers that transaction type.
9. Give practical, understandable educational guidance without requesting sensitive banking information.
10. Never ask users for their UPI PIN, OTP, password, CVV, or full bank account credentials.
11. Keep answers clear, concise, and beginner-friendly.
12. Do not claim to have checked a live bank transaction or filed a complaint unless that capability actually exists.
13. If authoritative sources conflict, identify the conflict and cite both; do not silently choose one.
"""

_CITATION_PATTERN = re.compile(r"\[([^\[\]]+)\]")


def is_verified_official_metadata(
    metadata: Dict[str, Any], *, require_page: bool = True
) -> bool:
    if (
        metadata.get("content_type") != "official_document"
        or metadata.get("reference_status") != "verified"
        or metadata.get("is_generated_summary") is not False
        or metadata.get("verification_method") != "manual_origin_and_sha256_review"
    ):
        return False
    publisher = metadata.get("publisher")
    url = urlparse(str(metadata.get("source_url", "")))
    digest = str(metadata.get("sha256", ""))
    return (
        bool(metadata.get("document_id"))
        and bool(metadata.get("document_title"))
        and bool(metadata.get("verified_by"))
        and bool(metadata.get("last_verified"))
        and (not require_page or bool(metadata.get("page_number")))
        and url.scheme == "https"
        and url.hostname in OFFICIAL_SOURCE_HOSTS.get(publisher, set())
        and len(digest) == 64
        and all(char in "0123456789abcdef" for char in digest.lower())
    )


def _relevant_chunks(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        chunk
        for chunk in retrieved_chunks
        if float(chunk.get("score", 0.0)) >= RETRIEVAL_SCORE_THRESHOLD
    ]


def build_citations(retrieved_chunks: List[Dict[str, Any]]) -> List[SourceCitation]:
    citations = []
    seen = set()
    for chunk in _relevant_chunks(retrieved_chunks):
        meta = chunk.get("metadata", {})
        verified_official = is_verified_official_metadata(meta)
        title = meta.get("document_title", "Unknown source")
        if not verified_official:
            title = f"FinGuide AI unverified material — {title}"
        page = meta.get("page_number")
        key = (meta.get("document_id"), title, page)
        if key not in seen:
            seen.add(key)
            citations.append(SourceCitation(
                document_title=title,
                document_id=meta.get("document_id"),
                page_number=page,
                snippet=(
                    chunk.get("text", "")[:280]
                    + ("..." if len(chunk.get("text", "")) > 280 else "")
                    if verified_official
                    else ""
                ),
                source_url=meta.get("source_url") if verified_official else None,
                last_verified=meta.get("last_verified"),
                published_date=meta.get("published_date"),
                publisher=meta.get("publisher"),
                authority=meta.get("authority") if verified_official else None,
                content_type=meta.get("content_type", "unknown"),
                is_generated_summary=meta.get("is_generated_summary"),
                reference_status=meta.get("reference_status", "unknown"),
                verification_method=meta.get("verification_method"),
                provenance_note=meta.get("provenance_note"),
                relevance_score=round(float(chunk.get("score", 0.0)), 2)
            ))
    return citations

def generate_suggested_followups(question: str) -> List[str]:
    q = question.lower()
    if "kyc" in q or "document" in q:
        return [
            "What is the difference between physical KYC and video KYC (V-CIP)?",
            "What are the 6 Officially Valid Documents (OVDs) recognised by RBI?",
            "How often do I need to update my KYC details at my bank?"
        ]
    elif "upi" in q or "pin" in q:
        return [
            "Do I ever need to enter my UPI PIN to receive money or cashbacks?",
            "What should I do immediately if an unauthorized UPI transaction occurs?",
            "What is the difference between UPI push and collect requests?"
        ]
    elif "neft" in q or "rtgs" in q or "imps" in q:
        return [
            "Which payment method is best for urgent transactions under ₹5 Lakh?",
            "Are there any charges for NEFT and RTGS initiated via net banking?",
            "What details are required to add a new beneficiary for electronic transfers?"
        ]
    elif "savings" in q or "account" in q:
        return [
            "Has SBI or RBI waived minimum balance charges for savings accounts?",
            "Why is adding a nominee critical when opening a bank account?",
            "What is a Basic Savings Bank Deposit Account (BSBDA)?"
        ]
    elif "scam" in q or "fraud" in q or "otp" in q:
        return [
            "How can I recognize a fraudulent KYC SMS or APK download link?",
            "What are my liabilities if an unauthorized transaction happens on my card?",
            "What is the official cybercrime helpline number in India?"
        ]
    else:
        return [
            "What documents are needed to open a savings account?",
            "What is the difference between NEFT, RTGS, and IMPS?",
            "How can I identify a fake bank customer support message?"
        ]

def generate_grounded_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> ChatResponse:
    relevant_chunks = _relevant_chunks(retrieved_chunks)
    verified_chunks = [
        chunk for chunk in relevant_chunks
        if is_verified_official_metadata(chunk.get("metadata", {}))
    ]
    citation_chunks = verified_chunks or relevant_chunks
    citations = build_citations(citation_chunks)
    follow_ups = generate_suggested_followups(question)
    is_grounded = bool(verified_chunks)

    # Unverified local documents may never be sent to an answer-generating model.
    if settings.has_valid_api_key and verified_chunks:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(settings.MODEL_NAME)
            
            context_text = "\n\n---\n\n".join([
                f"[Verified source ID: {c['metadata']['document_id']}; "
                f"title: {c['metadata']['document_title']}; "
                f"issuer: {c['metadata']['publisher']}; "
                f"page: {c['metadata']['page_number']}; "
                f"citation token: [{c['metadata']['document_id']}:p"
                f"{c['metadata']['page_number']}]]\n{c['text']}"
                for c in verified_chunks
            ])

            prompt = (
                f"{GROUNDED_SYSTEM_PROMPT}\n\n"
                f"RETRIEVED VERIFIED OFFICIAL EVIDENCE:\n{context_text}\n\n"
                f"USER QUESTION: {question}\n\n"
                "Answer only what these excerpts support. Cite every factual rule "
                "inline using the exact supplied citation token, including its "
                "square brackets. If the "
                "source does not establish the requested transaction type or "
                "deadline, say that it cannot be verified. Do not use conversation "
                "history as evidence."
            )
            response = model.generate_content(prompt)
            answer_text = (response.text or "").strip()
            if not answer_text:
                raise ValueError("Gemini returned an empty answer.")
            citation_tokens = _CITATION_PATTERN.findall(answer_text)
            allowed_tokens = {
                f"{chunk['metadata']['document_id']}:p{chunk['metadata']['page_number']}"
                for chunk in verified_chunks
            }
            if not citation_tokens or any(token not in allowed_tokens for token in citation_tokens):
                raise ValueError(
                    "Gemini omitted a retrieved-source citation or returned a "
                    "citation that was not present in the retrieved evidence."
                )

            return ChatResponse(
                answer=answer_text,
                sources=citations,
                follow_up_questions=follow_ups,
                is_grounded=is_grounded,
                has_warning=False,
                disclaimer=EDUCATIONAL_DISCLAIMER
            )
        except Exception as e:
            print(f"Gemini API generation error: {e}. Falling back to verified excerpts.")

    if verified_chunks:
        key_points = []
        for chunk in verified_chunks[:3]:
            metadata = chunk["metadata"]
            key_points.append(
                f"**{metadata['document_title']} — {metadata['publisher']}, "
                f"page {metadata['page_number']}:**\n> {chunk['text'].strip()}"
            )
        points_formatted = "\n\n".join(key_points)
        answer_text = (
            "### Verified official-source excerpts\n\n"
            f"{points_formatted}\n\n"
            "These excerpts are the evidence available in the verified indexed "
            "sources. Check the linked publication for its full context."
        )
    else:
        if relevant_chunks:
            answer_text = (
                "### Could not verify this from an official source\n\n"
                "Relevant indexed material is available, but it consists of "
                "unverified educational/demo documents. I will not treat it as "
                "an official banking rule or repeat its unverified deadlines, "
                "refund promises, or procedures as fact. Consult the relevant "
                "official NPCI/RBI publication or your bank for confirmation."
            )
            warning_message = (
                "The retrieved material is an unverified FinGuide AI demo, not "
                "an authenticated official source. Its claims and reference links "
                "have not been verified."
            )
        else:
            answer_text = (
                "### Could not verify this from an official source\n\n"
                f"I could not find relevant retrieved evidence for **{question}** "
                "in the indexed verified official documents. I will not guess "
                "about banking rules, refund timelines, or complaint outcomes. "
                "Consult the official NPCI/RBI publication or your bank."
            )
            warning_message = (
                "No relevant, verified official-source evidence was retrieved."
            )

    return ChatResponse(
        answer=answer_text,
        sources=citations,
        follow_up_questions=follow_ups,
        is_grounded=is_grounded,
        has_warning=not is_grounded,
        warning_message=warning_message if not is_grounded else None,
        disclaimer=EDUCATIONAL_DISCLAIMER
    )
