import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .config import settings
from .models import QueryRequest, QueryResponse, UploadResponse, Chunk
from .ingestion import ingestion_service
from .vector_store import vector_store
from .embeddings import embedding_model
from .rag_engine import rag_engine

app = FastAPI(title="3D RAG Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ping")
def ping():
    return {"status": "ok", "service": "3D RAG Backend"}

@app.post("/api/stream-test")
async def stream_test(req: QueryRequest):
    async def iterfile():
        yield f"Echo: {req.query}\n"
        import asyncio
        await asyncio.sleep(0.5)
        yield "chunk 2\n"
    return StreamingResponse(iterfile(), media_type="text/plain")

@app.post("/api/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    file_location = os.path.join(settings.DOCS_DIR, file.filename)
    
    # Save File
    try:
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
    
    # Process
    try:
        chunks = ingestion_service.process_document(file_location, file.filename)
        
        if not chunks:
            raise HTTPException(status_code=400, detail="No text could be extracted from this document. Is it a scanned image? Try a text-based PDF.")
            
        # Embed
        texts = [c.text for c in chunks]
        embeddings = embedding_model.generate(texts)
        
        # Upsert
        vector_store.upsert_chunks(chunks, embeddings)
        
        return UploadResponse(
            message="Ingestion successful",
            doc_id=chunks[0].metadata.doc_id,
            chunks_created=len(chunks)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
@app.delete("/api/reset")
async def reset_knowledge_base():
    try:
        vector_store.reset()
        # Clean docs folder
        for f in os.listdir(settings.DOCS_DIR):
            if f != '.gitkeep':
                os.remove(os.path.join(settings.DOCS_DIR, f))
        return {"status": "success", "message": "Knowledge base reset."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from fastapi.responses import StreamingResponse

@app.post("/api/query")
async def query_endpoint(req: QueryRequest):
    try:
        return StreamingResponse(
            rag_engine.query_stream(req.query, history=req.messages),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
