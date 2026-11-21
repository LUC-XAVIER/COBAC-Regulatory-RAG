"""documents and chunks with vector and full-text search

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.core.config import settings

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False, unique=True),
        sa.Column("doc_type", sa.String(50)),
        sa.Column("issuer", sa.String(50)),
        sa.Column("reference", sa.String(100)),
        sa.Column("published_on", sa.Date),
        sa.Column("status", sa.String(20), nullable=False, server_default="unknown"),
        sa.Column("language", sa.String(5), nullable=False, server_default="fr"),
        sa.Column("page_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "chunks",
        sa.Column("id", sa.BigInteger, primary_key=True),
        sa.Column("document_id", sa.Integer, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("heading", sa.Text, nullable=False, server_default=""),
        sa.Column("page", sa.Integer, nullable=False),
        sa.Column("page_end", sa.Integer),
        sa.Column("embedding", Vector(settings.EMBEDDING_DIM)),
        sa.Column("fts", TSVECTOR, sa.Computed("to_tsvector('french', text)", persisted=True)),
    )
    op.create_index("ix_chunks_document_id", "chunks", ["document_id"])
    op.create_index("ix_chunks_fts", "chunks", ["fts"], postgresql_using="gin")
    op.create_index(
        "ix_chunks_embedding",
        "chunks",
        ["embedding"],
        postgresql_using="hnsw",
        postgresql_with={"m": 16, "ef_construction": 64},
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    op.drop_table("chunks")
    op.drop_table("documents")