import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOCS_DIR: str = os.path.join(BASE_DIR, "docs")
    CHROMA_DB_PATH: str = os.path.join(BASE_DIR, "data", "chroma")
    
    # Models
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    DEFAULT_LLM_MODEL: str = "gemma2:2b"
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    
    # RAG Parameters
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 15

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure dirs exist
os.makedirs(settings.DOCS_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
