"""Quick check that the database is reachable and migrated.  Run: uv run python db_check.py"""
from sqlalchemy import text

from app.db.session import get_engine

with get_engine().connect() as conn:
    print("PostgreSQL :", conn.execute(text("SHOW server_version")).scalar())
    print("pgvector   :", conn.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'")).scalar())
    for table in ("documents", "chunks"):
        n = conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
        print(f"{table:<11}: {n} rows")