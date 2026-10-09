from fastapi import APIRouter, Response, HTTPException
from backend.app.models.schemas import ChecklistRequest, ChecklistResponse
from backend.app.services.checklist_service import get_checklist, generate_pdf_bytes

router = APIRouter(prefix="/checklist", tags=["Document Checklist"])

@router.post("", response_model=ChecklistResponse)
async def generate_document_checklist(request: ChecklistRequest):
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Checklist task cannot be empty.")
    return get_checklist(task=request.task, bank=request.bank)

@router.post("/pdf")
async def download_checklist_pdf(request: ChecklistRequest):
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Checklist task cannot be empty.")
    
    checklist_resp = get_checklist(task=request.task, bank=request.bank)
    pdf_bytes = generate_pdf_bytes(checklist_resp)
    
    filename = f"FinGuide_Checklist_{request.task}_{request.bank or 'General'}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
