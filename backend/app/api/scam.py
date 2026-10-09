from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.app.models.schemas import ScamAnalyzeRequest, ScamAnalyzeResponse
from backend.app.core.security import detect_sensitive_credentials, sanitize_user_input
from backend.app.services.scam_service import analyze_message, get_sample_scenarios

router = APIRouter(prefix="/scam", tags=["Scam Awareness"])

@router.get("/samples", response_model=List[Dict[str, Any]])
async def get_scam_samples():
    return get_sample_scenarios()

@router.post("/analyze", response_model=ScamAnalyzeResponse)
async def analyze_suspicious_message(request: ScamAnalyzeRequest):
    cleaned = sanitize_user_input(request.message_text)
    if len(cleaned) < 5:
        raise HTTPException(status_code=400, detail="Message too short for meaningful safety analysis.")

    # Sensitive credentials check
    has_sensitive, reasons = detect_sensitive_credentials(cleaned)
    if has_sensitive:
        raise HTTPException(
            status_code=400,
            detail=(
                "Security alert: Submitted text contains sensitive personal financial credentials ("
                + "; ".join(reasons)
                + "). Never submit real PINs, passwords, OTPs, or credit card numbers into any tool."
            )
        )

    return analyze_message(message_text=cleaned, scenario_type=request.scenario_type)
