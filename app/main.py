from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import ask, ingest

app = FastAPI(
    title="COBAC Regulatory RAG",
    description="RAG system for COBAC, CEMAC and BEAC financial regulations",
    version="0.1.0",
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
