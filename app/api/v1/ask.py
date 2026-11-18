import openai
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.dependencies import get_rag_service
from app.schemas.ask import AskRequest, AskResponse
from app.services.rag_service import RAGService

router = APIRouter()


# Plain "def" (not "async def"): the work below blocks, so FastAPI runs it in a thread pool
# and the server stays responsive while one request waits for the language model.
@router.post("/ask", response_model=AskResponse)
def ask(body: AskRequest, rag: RAGService = Depends(get_rag_service)):
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    if not settings.INDEX_PATH.exists():
        raise HTTPException(
            status_code=422,
            detail="No documents indexed yet. Please ingest PDFs first via /api/v1/ingest.",
        )

    try:
        return rag.answer(question, k=settings.TOP_K, min_score=settings.MIN_SCORE)
    except openai.OpenAIError:
        # the real reason is logged by Generator
        raise HTTPException(
            status_code=502,
            detail="The language model service is unavailable. Please try again shortly.",
        )