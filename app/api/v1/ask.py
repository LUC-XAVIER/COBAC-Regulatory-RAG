from fastapi import APIRouter, HTTPException, Depends
from app.core.config import settings
from app.dependencies import get_rag_service
from app.schemas.ask import AskRequest, AskResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    rag: RAGService = Depends(get_rag_service),
):
    if not settings.INDEX_PATH.exists():
        raise HTTPException(
            status_code=422,
            detail="No documents indexed yet. Please ingest PDFs first via /api/v1/ingest.",
        )

    return rag.answer(body.question, k=settings.TOP_K)
