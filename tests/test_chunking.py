from app.services.chunking import chunk_pages
from app.services.loader import PageText
from app.core.config import settings


def page(n: int, text: str) -> PageText:
    return PageText(source="doc.pdf", page_number=n, text=text)


def test_article_spanning_two_pages_stays_in_one_chunk():
    pages = [
        page(1, "Article 1 : Objet\nPremière phrase.\nDeuxième phrase."),
        page(2, "Suite de l'article un.\nArticle 2 : Champ\nTexte deux."),
    ]
    chunks = chunk_pages(pages)
    assert len(chunks) == 2
    assert "Suite de l'article un." in chunks[0].text
    assert (chunks[0].page, chunks[0].page_end) == (1, 2)
    assert chunks[1].text.startswith("Article 2")
    assert chunks[1].page == 2


def test_in_text_reference_does_not_split():
    pages = [page(1, "Article 1 : Objet\nConformément à\nArticle 12 du présent règlement,\nle texte continue.")]
    assert len(chunk_pages(pages)) == 1


def test_long_article_is_split_and_heading_repeated():
    body = "\n".join(f"Ligne numéro {i} avec du texte réglementaire." for i in range(120))
    chunks = chunk_pages([page(1, "Article 1 : Objet\n" + body)])
    assert len(chunks) > 1
    assert all(c.text.startswith("Article 1 : Objet") for c in chunks)
    assert all(len(c.text) <= settings.MAX_CHARS + 400 for c in chunks)


def test_running_headers_and_page_numbers_removed():
    pages = [
        page(n, f"Banque X - Règlement 2024\nArticle {n} : Titre\nTexte {n}.\n{n}")
        for n in range(1, 5)
    ]
    chunks = chunk_pages(pages)
    assert len(chunks) == 4
    assert all("Banque X" not in c.text for c in chunks)


def test_document_without_articles_is_split_by_size():
    body = "\n".join(f"Paragraphe {i} sans numérotation d'article, juste du texte." for i in range(100))
    chunks = chunk_pages([page(1, "CHAPITRE I\n" + body)])
    assert len(chunks) > 1
    assert all(c.heading == "" for c in chunks)


def test_numbered_chapter_titles_are_not_mistaken_for_footers():
    pages = [page(n, f"Chapitre {n}\nArticle {n} : Titre\nTexte {n}.") for n in range(1, 6)]
    chunks = chunk_pages(pages)
    joined = "\n".join(c.text for c in chunks)
    assert all(f"Chapitre {n}" in joined for n in range(1, 6))


def test_footer_with_changing_page_number_is_removed():
    pages = [page(n, f"Article {n} : Titre\nTexte {n}.\nBanque X - Page {n} sur 5") for n in range(1, 6)]
    assert all("Banque X" not in c.text for c in chunk_pages(pages))


def test_only_continuation_parts_are_marked_suite():
    body = "\n".join(f"Ligne numéro {i} avec du texte réglementaire." for i in range(120))
    chunks = chunk_pages([page(1, "Article 1 : Objet\n" + body)])
    assert "(suite)" not in chunks[0].text
    assert all(c.text.startswith("Article 1 : Objet (suite)") for c in chunks[1:])