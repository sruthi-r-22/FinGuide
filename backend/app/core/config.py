import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file from backend root if present
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

class Settings(BaseModel):
    PROJECT_NAME: str = "FinGuide AI"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Banking Account & Digital Service Explainer Bot"
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-1.5-flash")
    
    # Embedding & Vector DB Settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHROMA_PERSIST_DIR: str = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(PROJECT_DIR / "data" / "chroma_db")
    )
    DOCUMENTS_DIR: str = str(BACKEND_DIR / "data" / "documents")
    DATA_DIR: str = str(BACKEND_DIR / "data")
    
    # CORS
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    
    @property
    def has_valid_api_key(self) -> bool:
        return bool(self.GEMINI_API_KEY and self.GEMINI_API_KEY.strip() and not self.GEMINI_API_KEY.startswith("your_"))

settings = Settings()


def resolve_chroma_persist_dir() -> Path:
    """Resolve relative persistence paths from the project root."""
    configured_path = Path(settings.CHROMA_PERSIST_DIR).expanduser()
    if not configured_path.is_absolute():
        configured_path = PROJECT_DIR / configured_path
    return configured_path.resolve()
