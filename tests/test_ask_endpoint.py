from unittest.mock import patch, MagicMock
from app.main import app
from app.dependencies import get_rag_service
from app.schemas.ask import AskResponse, Citation


class TestAskEndpoint:
    def test_ask_returns_422_when_no_index(self, client, tmp_path):
        fake_path = tmp_path / "nonexistent.index"
        with patch("app.api.v1.ask.settings") as mock_settings:
            mock_settings.INDEX_PATH = fake_path
            response = client.post("/api/v1/ask", json={"question": "What is COBAC?"})

        assert response.status_code == 422
        assert "No documents indexed" in response.json()["detail"]

    def test_ask_returns_valid_response(self, client, tmp_path):
        fake_index = tmp_path / "faiss.index"
        fake_index.touch()

        mock_rag = MagicMock()
        mock_rag.answer.return_value = AskResponse(
            response="COBAC is the banking commission.",
            citations=[Citation(source="reg.pdf", page=1, snippet="COBAC est...")],
        )

        app.dependency_overrides[get_rag_service] = lambda: mock_rag
        try:
            with patch("app.api.v1.ask.settings") as mock_settings:
                mock_settings.INDEX_PATH = fake_index
                mock_settings.TOP_K = 5
                response = client.post("/api/v1/ask", json={"question": "What is COBAC?"})
        finally:
            app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "COBAC" in data["response"]
        assert len(data["citations"]) == 1
        assert data["citations"][0]["source"] == "reg.pdf"

    def test_ask_rejects_empty_body(self, client):
        response = client.post("/api/v1/ask", json={})
        assert response.status_code == 422
