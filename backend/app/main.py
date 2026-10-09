from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.core.config import settings
from backend.app.api.router import api_router
from backend.app.models.schemas import HealthResponse
from backend.app.rag.retriever import vector_store

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure vector store is initialized and documents indexed
    try:
        vector_store.initialize()
    except Exception as e:
        print(f"Warning during vector store startup initialization: {e}")
    yield
    # Shutdown logic if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Educational banking guidance grounded in retrieved documents with explicit provenance labels.",
    lifespan=lifespan
)

# CORS Middleware
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    settings.FRONTEND_ORIGIN
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include aggregate router
app.include_router(api_router)

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    try:
        docs = vector_store.get_sources_overview()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    total_chunks = sum(d.get("chunks_count", 0) for d in docs)
    
    return HealthResponse(
        status="healthy",
        version=settings.VERSION,
        llm_configured=settings.has_valid_api_key,
        provider=settings.LLM_PROVIDER,
        model=settings.MODEL_NAME,
        indexed_documents_count=len(docs),
        total_chunks=total_chunks
    )

@app.get("/", tags=["Root"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "tagline": "Understand Banking. Navigate Digital Services. Stay Scam-Aware.",
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
