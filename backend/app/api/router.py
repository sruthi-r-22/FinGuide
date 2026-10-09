from fastapi import APIRouter
from backend.app.api.chat import router as chat_router
from backend.app.api.glossary import router as glossary_router
from backend.app.api.checklist import router as checklist_router
from backend.app.api.scam import router as scam_router
from backend.app.api.comparisons import router as comparisons_router
from backend.app.api.sources import router as sources_router

api_router = APIRouter(prefix="/api")

api_router.include_router(chat_router)
api_router.include_router(glossary_router)
api_router.include_router(checklist_router)
api_router.include_router(scam_router)
api_router.include_router(comparisons_router)
api_router.include_router(sources_router)
