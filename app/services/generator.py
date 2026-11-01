import os
from openai import OpenAI
from app.core.config import settings


class Generator:
    def __init__(self, model: str | None = None):
        api_key = os.environ.get("NVIDIA_API_KEY", settings.NVIDIA_API_KEY)
        if not api_key:
            raise RuntimeError(
                "NVIDIA_API_KEY is not set. Create a key at build.nvidia.com "
                "and export it as an environment variable."
            )
        self.client = OpenAI(
            base_url=os.environ.get("NVIDIA_BASE_URL", settings.NVIDIA_BASE_URL),
            api_key=api_key,
            timeout=120,
        )
        self.model = model or os.environ.get("NVIDIA_MODEL", settings.NVIDIA_MODEL)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.2,  # low = more faithful to the retrieved context
        )
        return response.choices[0].message.content or ""