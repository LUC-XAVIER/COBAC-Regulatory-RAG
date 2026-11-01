from sentence_transformers import SentenceTransformer
import numpy as np
from app.core.config import settings


class EmbeddingModel:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL):
        self.model = SentenceTransformer(model_name)

    def embed_passages(self, texts: list[str]) -> np.ndarray:
        prefixed = [f"passage: {t}" for t in texts]
        return self.model.encode(prefixed, normalize_embeddings=True)

    def embed_query(self, query: str) -> np.ndarray:
        prefixed = [f"query: {query}"]
        return self.model.encode(prefixed, normalize_embeddings=True)
