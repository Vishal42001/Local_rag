import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any
from .config import settings
from .models import Chunk, RetrievalResult, DocumentMetadata

class VectorStore:
    def __init__(self):
        print(f"Initializing Version Store at {settings.CHROMA_DB_PATH}")
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        
        self.collection = self.client.get_or_create_collection(
            name="rag_collection",
            metadata={"hnsw:space": "cosine"}
        )

    def upsert_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        if not chunks:
            return
            
        ids = [c.id for c in chunks]
        texts = [c.text for c in chunks]
        # Flatten metadata for Chroma (it prefers flat dicts)
        metadatas = []
        for c in chunks:
            m = c.metadata.model_dump()
            # Ensure no nested types if any (Pydantic models need to be dicts)
            metadatas.append(m)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def query(self, query_embedding: List[float], top_k: int = 10) -> List[RetrievalResult]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        retrieved = []
        if results['ids']:
            # results is a dict of lists of lists. We grab the first query result.
            ids = results['ids'][0]
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            dists = results['distances'][0] if results['distances'] else [0.0]*len(ids)

            for i in range(len(ids)):
                m = metas[i]
                retrieved.append(RetrievalResult(
                    filename=m.get('filename', 'Unknown'),
                    page=m.get('page'),
                    chunk_index=m.get('chunk_index', 0),
                    excerpt=docs[i],
                    score=dists[i]
                ))
        
        return retrieved
    def reset(self):
        try:
            self.client.delete_collection(name="rag_collection")
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name="rag_collection",
            metadata={"hnsw:space": "cosine"}
        )
vector_store = VectorStore()
