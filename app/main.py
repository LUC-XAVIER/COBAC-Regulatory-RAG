import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import ask, ingest
from app.dependencies import get_embedding_model

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once at server start, before any request is accepted
    logger.info("Loading embedding model (downloads it on first run)...")
    get_embedding_model()
    logger.info("Embedding model ready.")
    yield
    # Code after yield would run at shutdown (nothing to clean up here)


app = FastAPI(
    title="COBAC Regulatory RAG",
    description="RAG system for COBAC, CEMAC and BEAC financial regulations",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1", tags=["Ingest"])
app.include_router(ask.router, prefix="/api/v1", tags=["Ask"])


@app.get("/")
def root():
    return {"message": "COBAC Regulatory RAG API", "docs": "/docs"}