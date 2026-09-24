from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    DATA_DIR: Path = BASE_DIR / "data"
    INDEX_PATH: Path = BASE_DIR / "data" / "index" / "faiss.index"
    CHUNKS_PATH: Path = BASE_DIR / "data" / "index" / "chunks.json"
    RAW_DIR: Path = BASE_DIR / "data" / "raw"

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM: int = 384

    LLM_MODEL: str = "claude-sonnet-4-6"
    ANTHROPIC_API_KEY: str = ""

    TOP_K: int = 5


settings = Settings()
