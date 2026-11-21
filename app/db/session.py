from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session

from app.core.config import settings


@lru_cache
def get_engine() -> Engine:
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set. Add it to .env (see .env.example).")
    # pool_pre_ping checks a connection is still alive before using it
    return create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency: one database session per request, always closed afterwards."""
    with Session(get_engine()) as session:
        yield session