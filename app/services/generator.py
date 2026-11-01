import logging
import openai
from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class Generator:
    def __init__(self, model: str | None = None):
        self.client = OpenAI(
            base_url=settings.NVIDIA_BASE_URL,
            api_key=settings.NVIDIA_API_KEY,
            timeout=120,
        )
        self.model = model or settings.NVIDIA_MODEL

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1024,
                temperature=0.2,
                extra_body={"chat_template_kwargs": {"enable_thinking": False}},
            )
        except openai.APIStatusError as e:
            logger.error("NVIDIA API error %s: %s", e.status_code, e.response.text)
            raise
        return response.choices[0].message.content or ""