from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.core.security import detect_sensitive_credentials, sanitize_user_input, EDUCATIONAL_DISCLAIMER
from backend.app.rag.retriever import vector_store
from backend.app.rag.generator import generate_grounded_answer

router = APIRouter(prefix="/chat", tags=["Chat & RAG"])

@router.post("", response_model=ChatResponse)
async def ask_finguide(request: ChatRequest):
    cleaned_query = sanitize_user_input(request.question)
    if len(cleaned_query) < 2:
        raise HTTPException(status_code=400, detail="Question cannot be empty or too short.")

    # Sensitive credential detection
    has_sensitive, reasons = detect_sensitive_credentials(cleaned_query)
    if has_sensitive:
        warning_msg = (
            "Security Alert: Your question appears to include sensitive credentials ("
            + "; ".join(reasons)
            + "). For your security, FinGuide AI will never accept, log, or process banking PINs, OTPs, CVVs, full card numbers, or passwords. Please remove any sensitive numbers and rephrase your question."
        )
        return ChatResponse(
            answer=(
                "⚠️ **Security Warning: Sensitive Credential Detected**\n\n"
                "FinGuide AI is an educational guidance system and **strictly forbids entering sensitive financial information**.\n\n"
                "- **Never enter:** ATM PINs, UPI PINs, One-Time Passwords (OTPs), CVVs, passwords, or full 16-digit debit card numbers.\n"
                "- **Safety Rule:** Legitimate banks and government officials will never request these credentials from you under any circumstances.\n\n"
                "Please rephrase your question in general educational terms (e.g., *'What documents are required to open a savings account?'*)."
            ),
            sources=[],
            follow_up_questions=[
                "What documents are needed to open a savings account?",
                "How do I recognize a fake KYC notification?",
                "What is the difference between NEFT and RTGS?"
            ],
            is_grounded=False,
            has_warning=True,
            warning_message=warning_msg,
            disclaimer=EDUCATIONAL_DISCLAIMER
        )

    # Give curated topics enough context to retrieve their specific official passage.
    normalized_query = " ".join(cleaned_query.lower().split())
    retrieval_query = cleaned_query
    curated_retrieval = False
    if "upi" in normalized_query and any(
        term in normalized_query
        for term in ("pin", "receive money", "receiving money", "share my pin")
    ):
        retrieval_query = (
            "RBI unauthorized transaction shared payment credentials "
            "customer negligence report to bank"
        )
        curated_retrieval = True
    elif "upi" in normalized_query and any(
        term in normalized_query
        for term in ("failed", "unsuccessful", "not credited", "payment failed")
    ):
        retrieval_query += (
            " RBI UPI account debited beneficiary not credited transfer "
            "merchant confirmation auto-reversal T + 1 day T + 5 days"
        )
        curated_retrieval = True

    # Vector retrieval
    try:
        retrieved_chunks = vector_store.retrieve(
            retrieval_query,
            top_k=8 if curated_retrieval else 4,
        )
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Document retrieval is unavailable: {e}",
        ) from e

    # Grounded answer generation
    response = generate_grounded_answer(cleaned_query, retrieved_chunks)
    return response
