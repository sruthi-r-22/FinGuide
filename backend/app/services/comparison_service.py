import os
import json
from typing import Dict, Any, Optional, List
from backend.app.core.config import settings
from backend.app.models.schemas import ComparisonResponse

COMPARISONS_FILE = os.path.join(settings.DATA_DIR, "comparisons.json")

def load_all_comparisons() -> Dict[str, Any]:
    if not os.path.exists(COMPARISONS_FILE):
        return {}
    with open(COMPARISONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def get_comparison(topic: str) -> Optional[ComparisonResponse]:
    comps = load_all_comparisons()
    key = topic.lower().strip()
    data = comps.get(key)
    if not data:
        return None
    return ComparisonResponse(**data)

def list_available_comparisons() -> List[Dict[str, str]]:
    comps = load_all_comparisons()
    return [
        {
            "topic": k,
            "title": v.get("title", k),
            "description": v.get("description", "")
        }
        for k, v in comps.items()
    ]
