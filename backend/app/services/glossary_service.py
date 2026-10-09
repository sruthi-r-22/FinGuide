import os
import json
from typing import List, Optional
from backend.app.core.config import settings
from backend.app.models.schemas import GlossaryItem

GLOSSARY_FILE = os.path.join(settings.DATA_DIR, "glossary.json")

def load_glossary_data() -> List[GlossaryItem]:
    if not os.path.exists(GLOSSARY_FILE):
        return []
    with open(GLOSSARY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [GlossaryItem(**item) for item in data]

def get_glossary_items(query: Optional[str] = None, category: Optional[str] = None) -> List[GlossaryItem]:
    items = load_glossary_data()
    if category and category.strip():
        cat_lower = category.lower().strip()
        items = [i for i in items if i.category.lower() == cat_lower]

    if query and query.strip():
        q_lower = query.lower().strip()
        items = [
            i for i in items
            if q_lower in i.term.lower()
            or (i.full_form and q_lower in i.full_form.lower())
            or q_lower in i.definition.lower()
            or q_lower in i.category.lower()
        ]

    return items

def get_glossary_item_by_id(item_id: str) -> Optional[GlossaryItem]:
    items = load_glossary_data()
    for item in items:
        if item.id.lower() == item_id.lower():
            return item
    return None
