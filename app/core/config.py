from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    #model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATA_DIR: Path = BASE_DIR / "data"
    INDEX_PATH: Path = BASE_DIR / "data" / "index" / "faiss.index"
    CHUNKS_PATH: Path = BASE_DIR / "data" / "index" / "chunks.json"
    RAW_DIR: Path = BASE_DIR / "data" / "raw"

    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDING_DIM: int = 384

    NVIDIA_API_KEY: str
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_MODEL: str = "moonshotai/kimi-k2.5"

    TOP_K: int = 5


settings = Settings()
