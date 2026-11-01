import json
from pathlib import Path
from app.services.chunking import Chunk

class ChunkStore:
    def __init__(self):
        self._store: dict[int, Chunk] = {}

    def add(self, chunk_id: int, chunk: Chunk) -> None:
        self._store[chunk_id] = chunk

    def get(self, chunk_id: int) -> Chunk:
        return self._store[chunk_id]

    def save(self, path: Path) -> None:
        data = {str(k): vars(v) for k, v in self._store.items()}
        path.write_text(json.dumps(data, ensure_ascii=False))

    @classmethod
    def load(cls, path: Path) -> "ChunkStore":
        instance = cls()
        data = json.loads(path.read_text())
        for k, v in data.items():
            instance._store[int(k)] = Chunk(**v)
        return instance
