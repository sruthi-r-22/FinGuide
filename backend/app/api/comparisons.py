from fastapi import APIRouter, HTTPException
from typing import List, Dict
from backend.app.models.schemas import ComparisonResponse
from backend.app.services.comparison_service import get_comparison, list_available_comparisons

router = APIRouter(prefix="/comparisons", tags=["Banking Comparisons"])

@router.get("", response_model=List[Dict[str, str]])
async def list_comparisons():
    return list_available_comparisons()

@router.get("/{topic}", response_model=ComparisonResponse)
async def get_comparison_topic(topic: str):
    data = get_comparison(topic)
    if not data:
        raise HTTPException(status_code=404, detail=f"Comparison topic '{topic}' not found.")
    return data
