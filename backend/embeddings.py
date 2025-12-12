from sentence_transformers import SentenceTransformer
from typing import List
from .config import settings

class EmbeddingModel:
    def __init__(self):
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def generate(self, texts: List[str]) -> List[List[float]]:
        # Generate embeddings
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

# Singleton
embedding_model = EmbeddingModel()
