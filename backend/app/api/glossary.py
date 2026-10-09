from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from backend.app.models.schemas import GlossaryItem
from backend.app.services.glossary_service import get_glossary_items, get_glossary_item_by_id

router = APIRouter(prefix="/glossary", tags=["Banking Glossary"])

@router.get("", response_model=List[GlossaryItem])
async def list_glossary(
    search: Optional[str] = Query(None, description="Search term or full form"),
    category: Optional[str] = Query(None, description="Category filter")
):
    return get_glossary_items(query=search, category=category)

@router.get("/{item_id}", response_model=GlossaryItem)
async def get_glossary_detail(item_id: str):
    item = get_glossary_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Glossary term '{item_id}' not found.")
    return item
