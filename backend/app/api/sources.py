from fastapi import APIRouter, HTTPException
from backend.app.models.schemas import SourcesResponse, DocumentMetadata
from backend.app.rag.retriever import vector_store

router = APIRouter(prefix="/sources", tags=["Sources & Documents"])

@router.get("", response_model=SourcesResponse)
async def list_sources():
    try:
        raw_docs = vector_store.get_sources_overview()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    documents = [DocumentMetadata(**doc) for doc in raw_docs]
    total_chunks = sum(doc.chunks_count for doc in documents)
    
    return SourcesResponse(
        documents=documents,
        total_chunks=total_chunks,
        index_status="Active & Synchronized" if total_chunks > 0 else "Empty"
    )

@router.post("/reindex")
async def trigger_reindex():
    try:
        result = vector_store.reindex_all()
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        "status": "success",
        "message": (
            f"Re-indexed {result['documents_indexed']} documents with "
            f"{result['total_chunks']} chunks."
        ),
        **result,
    }
