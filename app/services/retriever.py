from dataclasses import dataclass
from app.services.embedding import EmbeddingModel
from app.services.indexer import VectorIndex
from app.store.chunk_store import ChunkStore
from app.services.chunking import Chunk

@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float

class Retriever:
    def __init__(self, index: VectorIndex, chunk_store: ChunkStore, embedding_model: EmbeddingModel):
        self.index = index
        self.chunk_store = chunk_store
        self.embedding_model = embedding_model

    def retrieve(self, query: str, k: int = 5) -> list[Chunk]:
        query_vector = self.embedding_model.embed_query(query)
        scores, ids = self.index.search(query_vector, k)
        return [
            RetrievedChunk(chunk=self.chunk_store.get(int(i)), score=score)
            for i, score in zip(ids, scores)
            if i != -1
        ]
