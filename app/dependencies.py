from functools import lru_cache
from app.core.config import settings
from app.services.embedding import EmbeddingModel
from app.services.indexer import VectorIndex
from app.store.chunk_store import ChunkStore
from app.services.retriever import Retriever
from app.services.generator import Generator
from app.services.rag_service import RAGService


@lru_cache
def get_embedding_model() -> EmbeddingModel:
    return EmbeddingModel(model_name=settings.EMBEDDING_MODEL)


def get_vector_index() -> VectorIndex:
    if settings.INDEX_PATH.exists():
        return VectorIndex.load(settings.INDEX_PATH, dim=settings.EMBEDDING_DIM)
    return VectorIndex(dim=settings.EMBEDDING_DIM)


def get_chunk_store() -> ChunkStore:
    if settings.CHUNKS_PATH.exists():
        return ChunkStore.load(settings.CHUNKS_PATH)
    return ChunkStore()


def get_retriever() -> Retriever:
    return Retriever(
        index=get_vector_index(),
        chunk_store=get_chunk_store(),
        embedding_model=get_embedding_model(),
    )


@lru_cache
def get_generator() -> Generator:
    return Generator(model=settings.LLM_MODEL)


def get_rag_service() -> RAGService:
    return RAGService(
        retriever=get_retriever(),
        generator=get_generator(),
    )
