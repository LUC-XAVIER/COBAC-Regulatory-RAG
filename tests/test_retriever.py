import sys
import numpy as np
from unittest.mock import MagicMock
from app.services.chunking import Chunk
from app.store.chunk_store import ChunkStore
from app.services.indexer import VectorIndex

sys.modules.setdefault("sentence_transformers", MagicMock())

from app.services.retriever import Retriever, RetrievedChunk  # noqa: E402


def _build_retriever(chunks: list[Chunk]) -> Retriever:
    dim = 4
    store = ChunkStore()
    index = VectorIndex(dim=dim)

    if chunks:
        vectors = np.random.rand(len(chunks), dim).astype("float32")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        vectors = vectors / norms

        ids = list(range(len(chunks)))
        for i, chunk in enumerate(chunks):
            store.add(i, chunk)
        index.add(vectors, ids)
    else:
        vectors = np.zeros((1, dim), dtype="float32")

    mock_embedding = MagicMock()
    mock_embedding.embed_query.return_value = vectors[:1]

    return Retriever(index=index, chunk_store=store, embedding_model=mock_embedding)


class TestRetriever:
    def test_retrieve_returns_results(self):
        chunks = [
            Chunk(text="Article 1 Capital requirements", source="reg.pdf", page=1),
            Chunk(text="Article 2 Liquidity ratios", source="reg.pdf", page=2),
        ]
        retriever = _build_retriever(chunks)
        results = retriever.retrieve("capital", k=2)

        assert len(results) > 0
        assert all(isinstance(r, RetrievedChunk) for r in results)

    def test_retrieve_returns_correct_chunk_data(self):
        chunks = [
            Chunk(text="Article 5 Sanctions", source="cobac.pdf", page=10),
        ]
        retriever = _build_retriever(chunks)
        results = retriever.retrieve("sanctions", k=1)

        assert len(results) == 1
        assert results[0].chunk.source == "cobac.pdf"
        assert results[0].chunk.page == 10
        assert results[0].score > 0

    def test_retrieve_respects_k(self):
        chunks = [
            Chunk(text=f"Article {i}", source="reg.pdf", page=i)
            for i in range(10)
        ]
        retriever = _build_retriever(chunks)
        results = retriever.retrieve("article", k=3)

        assert len(results) <= 3

    def test_retrieve_empty_index(self):
        retriever = _build_retriever([])
        results = retriever.retrieve("anything", k=5)
        assert results == []
