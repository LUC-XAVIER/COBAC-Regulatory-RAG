from app.services.loader import PageText
from app.services.chunking import chunk_pages, _split_by_article


class TestSplitByArticle:
    def test_splits_on_article_headings(self):
        page = PageText(
            source="test.pdf",
            page_number=1,
            text="Article 1 Some content here. Article 2 More content here.",
        )
        parts = _split_by_article(page)
        assert len(parts) == 2
        assert parts[0].startswith("Article 1")
        assert parts[1].startswith("Article 2")

    def test_no_articles_returns_full_text(self):
        page = PageText(
            source="test.pdf",
            page_number=1,
            text="This is a preamble with no article headings.",
        )
        parts = _split_by_article(page)
        assert len(parts) == 1
        assert parts[0] == "This is a preamble with no article headings."

    def test_empty_text_returns_empty(self):
        page = PageText(source="test.pdf", page_number=1, text="   ")
        parts = _split_by_article(page)
        assert parts == []

    def test_article_with_multidigit_number(self):
        page = PageText(
            source="test.pdf",
            page_number=1,
            text="Preambule. Article 12 Dispositions generales. Article 130 Sanctions.",
        )
        parts = _split_by_article(page)
        assert len(parts) == 3
        assert parts[0] == "Preambule."
        assert "Article 12" in parts[1]
        assert "Article 130" in parts[2]


class TestChunkPages:
    def test_chunks_multiple_pages(self):
        pages = [
            PageText(source="reg.pdf", page_number=1, text="Article 1 First."),
            PageText(source="reg.pdf", page_number=2, text="Article 2 Second."),
        ]
        chunks = chunk_pages(pages)
        assert len(chunks) == 2
        assert chunks[0].source == "reg.pdf"
        assert chunks[0].page == 1
        assert chunks[1].page == 2

    def test_empty_pages_returns_empty(self):
        chunks = chunk_pages([])
        assert chunks == []

    def test_chunk_preserves_source_metadata(self):
        pages = [
            PageText(source="cobac_2024.pdf", page_number=5, text="Article 3 Content."),
        ]
        chunks = chunk_pages(pages)
        assert len(chunks) == 1
        assert chunks[0].source == "cobac_2024.pdf"
        assert chunks[0].page == 5
        assert "Article 3" in chunks[0].text
