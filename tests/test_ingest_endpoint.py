import io
from unittest.mock import patch, MagicMock
import numpy as np


class TestIngestEndpoint:
    def test_ingest_rejects_non_pdf(self, client):
        file = io.BytesIO(b"not a pdf")
        response = client.post(
            "/api/v1/ingest",
            files=[("files", ("test.txt", file, "text/plain"))],
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failure"
        assert "test.txt" in data["failed"]

    def test_ingest_accepts_pdf(self, client, tmp_path):
        mock_pages = [
            MagicMock(source="test.pdf", page_number=1, text="Article 1 Content")
        ]
        mock_chunks = [
            MagicMock(text="Article 1 Content", source="test.pdf", page=1)
        ]
        mock_vectors = np.random.rand(1, 384).astype("float32")

        mock_embed = MagicMock()
        mock_embed.embed_passages.return_value = mock_vectors

        mock_index = MagicMock()
        mock_store = MagicMock()
        mock_store._store = {}

        pdf_bytes = b"%PDF-1.4 fake pdf content"

        with (
            patch("app.api.v1.ingest.settings") as mock_settings,
            patch("app.api.v1.ingest.extract_pages", return_value=mock_pages),
            patch("app.api.v1.ingest.chunk_pages", return_value=mock_chunks),
            patch("app.api.v1.ingest.get_embedding_model", return_value=mock_embed),
            patch("app.api.v1.ingest.get_vector_index", return_value=mock_index),
            patch("app.api.v1.ingest.get_chunk_store", return_value=mock_store),
        ):
            mock_settings.RAW_DIR = tmp_path / "raw"
            mock_settings.INDEX_PATH = tmp_path / "index" / "faiss.index"
            mock_settings.CHUNKS_PATH = tmp_path / "index" / "chunks.json"
            mock_settings.INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

            file = io.BytesIO(pdf_bytes)
            response = client.post(
                "/api/v1/ingest",
                files=[("files", ("test.pdf", file, "application/pdf"))],
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "test.pdf" in data["ingested"]
        assert data["total_chunks"] == 1

    def test_ingest_no_files_returns_400(self, client):
        response = client.post("/api/v1/ingest")
        assert response.status_code == 422
