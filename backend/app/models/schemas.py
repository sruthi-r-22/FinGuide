from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# Chat & RAG Schemas
class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000, description="The banking query to ask FinGuide AI")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Recent conversation turns")

class SourceCitation(BaseModel):
    document_title: str
    document_id: Optional[str] = None
    page_number: Optional[int] = None
    snippet: str
    source_url: Optional[str] = None
    last_verified: Optional[str] = None
    published_date: Optional[str] = None
    publisher: Optional[str] = None
    authority: Optional[str] = None
    content_type: str = "unknown"
    is_generated_summary: Optional[bool] = None
    reference_status: str = "unknown"
    verification_method: Optional[str] = None
    provenance_note: Optional[str] = None
    relevance_score: Optional[float] = None

class OfficialSourceRef(BaseModel):
    title: str
    url: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceCitation]
    further_reading: List[OfficialSourceRef] = Field(default_factory=list)
    follow_up_questions: List[str]
    is_grounded: bool
    has_warning: bool = False
    warning_message: Optional[str] = None
    disclaimer: str

# Glossary Schemas
class GlossaryItem(BaseModel):
    id: str
    term: str
    full_form: Optional[str] = None
    category: str
    definition: str
    example: str
    safety_note: Optional[str] = None
    source_title: str
    source_url: str

# Document Checklist Schemas
class ChecklistRequest(BaseModel):
    task: str = Field(..., description="Banking task, e.g. 'savings_account', 'current_account', 'kyc_update'")
    bank: Optional[str] = Field(None, description="Optional bank filter, e.g. 'sbi', 'general'")

class ChecklistItem(BaseModel):
    requirement: str
    category: str
    why_needed: str
    is_bank_dependent: bool
    source_document: str
    source_url: Optional[str] = None
    verified_status: str

class ChecklistResponse(BaseModel):
    task: str
    task_title: str
    bank: Optional[str] = None
    items: List[ChecklistItem]
    disclaimer: str

# Scam Awareness Schemas
class ScamAnalyzeRequest(BaseModel):
    message_text: str = Field(..., min_length=5, max_length=3000, description="Message or call transcript to analyze")
    scenario_type: Optional[str] = Field(None, description="Optional scenario hint")

class OfficialSafetyResource(BaseModel):
    name: str
    contact_or_url: str
    description: str

class ScamAnalyzeResponse(BaseModel):
    risk_level: str
    potential_warning_signs: List[str]
    why_suspicious: str
    safe_actions: List[str]
    official_safety_resources: List[OfficialSafetyResource]
    disclaimer: str

# Comparison Explainer Schemas
class ComparisonRow(BaseModel):
    feature: str
    values: List[str]

class ComparisonResponse(BaseModel):
    topic: str
    title: str
    description: str
    columns: List[str]
    rows: List[ComparisonRow]
    official_sources: List[OfficialSourceRef]
    neutral_summary: str

# Sources & Documents
class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    title: str
    publisher: Optional[str] = None
    authority: Optional[str] = None
    pages_count: int
    chunks_count: int
    last_verified: Optional[str] = None
    source_url: Optional[str] = None
    published_date: Optional[str] = None
    content_type: str = "unknown"
    is_generated_summary: Optional[bool] = None
    reference_status: str = "unknown"
    verification_method: Optional[str] = None
    verified_by: Optional[str] = None
    provenance_note: Optional[str] = None

class SourcesResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_chunks: int
    index_status: str

# Health Check
class HealthResponse(BaseModel):
    status: str
    version: str
    llm_configured: bool
    provider: str
    model: str
    indexed_documents_count: int
    total_chunks: int
