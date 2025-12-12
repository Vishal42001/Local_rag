from pydantic import BaseModel
from typing import List, Optional

class DocumentMetadata(BaseModel):
    filename: str
    page: Optional[int] = None
    chunk_index: int
    doc_id: str

class Chunk(BaseModel):
    id: str
    text: str
    metadata: DocumentMetadata

class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    messages: List[dict] = [] # Chat history [{"role": "user", "content": "..."}]

class RetrievalResult(BaseModel):
    filename: str
    page: Optional[int]
    chunk_index: int
    excerpt: str
    score: float

class QueryResponse(BaseModel):
    answer: str
    citations: List[RetrievalResult]
    model_used: str

class UploadResponse(BaseModel):
    message: str
    doc_id: str
    chunks_created: int
