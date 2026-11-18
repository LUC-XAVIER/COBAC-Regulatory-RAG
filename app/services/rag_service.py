from app.services.retriever import Retriever
from app.services.prompt_builder import build_messages
from app.services.generator import Generator
from app.schemas.ask import AskResponse, Citation
import logging

logger = logging.getLogger("uvicorn.error")

class RAGService:
    def __init__(self, retriever: Retriever, generator: Generator):
        self.retriever = retriever
        self.generator = generator

    def answer(self, question: str, k: int = 5, min_score: float = 0.0) -> AskResponse:
        found = self.retriever.retrieve(question, k=k)
        logger.info("retrieval scores: %s", [round(r.score, 3) for r in found])
        retrieved = [r for r in found if r.score >= min_score]

        if not retrieved:
            return AskResponse(
                response="No relevant information found in the indexed documents.",
                citations=[],
            )

        prompt = build_messages(question, retrieved)
        answer_text = self.generator.generate(prompt)

        citations = [
            Citation(source=r.chunk.source, page=r.chunk.page, snippet=r.chunk.text[:200])
            for r in retrieved
        ]
        return AskResponse(response=answer_text, citations=citations)
