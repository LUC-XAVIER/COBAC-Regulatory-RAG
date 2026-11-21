from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Computed, Date, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(500))
    sha256: Mapped[str] = mapped_column(String(64), unique=True)  # same file cannot be ingested twice
    doc_type: Mapped[str | None] = mapped_column(String(50))      # reglement, decision, circulaire, ...
    issuer: Mapped[str | None] = mapped_column(String(50))        # COBAC, BEAC, CEMAC
    reference: Mapped[str | None] = mapped_column(String(100))    # e.g. "EMF 2018/01"
    published_on: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="unknown", server_default="unknown")
    # status: in_force | amended | abrogated | unknown
    language: Mapped[str] = mapped_column(String(5), default="fr", server_default="fr")
    page_count: Mapped[int] = mapped_column(default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chunks: Mapped[list["Chunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan", passive_deletes=True
    )


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    position: Mapped[int]                                   # order of the chunk inside its document
    text: Mapped[str] = mapped_column(Text)
    heading: Mapped[str] = mapped_column(Text, default="", server_default="")
    page: Mapped[int]
    page_end: Mapped[int | None]
    embedding = mapped_column(Vector(settings.EMBEDDING_DIM))
    # keyword-search column, kept up to date by PostgreSQL itself
    fts = mapped_column(TSVECTOR, Computed("to_tsvector('french', text)", persisted=True))

    document: Mapped[Document] = relationship(back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_fts", "fts", postgresql_using="gin"),
        Index(
            "ix_chunks_embedding",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )