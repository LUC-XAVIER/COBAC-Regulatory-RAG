import re
from dataclasses import dataclass
from typing import NamedTuple

from app.services.loader import PageText
from app.core.config import settings


# A real article heading: "Article 7", "Article 7 :", "Article 7 -", "Article 7 (nouveau)",
# "Art. 7.", "ARTICLE PREMIER", "Article 7 bis -". The number must be followed by the end
# of the line or by punctuation, so in-text references such as "Article 12 du présent
# règlement" or "Article 12, alinéa 2" are NOT treated as headings.
ARTICLE_RE = re.compile(
    r"^(?:Article|ARTICLE|Art\.)\s+"
    r"(?:\d+|premier|Premier|PREMIER|1er|[IVXLC]+)"
    r"(?:\s*(?:bis|ter|quater))?"
    r"\s*(?:$|[:.\-–—(])"
)
PAGE_NUMBER_RE = re.compile(r"^(?:page\s*)?\d+(?:\s*(?:/|sur)\s*\d+)?$", re.IGNORECASE)


@dataclass
class Chunk:
    text: str
    source: str
    page: int                    # first page of the chunk
    page_end: int | None = None  # last page, when the chunk spans several pages
    heading: str = ""            # e.g. "Article 7 : Capital minimum"

    @property
    def page_label(self) -> str:
        if self.page_end and self.page_end != self.page:
            return f"{self.page}-{self.page_end}"
        return str(self.page)


class Line(NamedTuple):
    text: str
    page: int
    source: str


def chunk_pages(pages: list[PageText]) -> list[Chunk]:
    """One chunk per article, even when the article runs over several pages.
    Articles longer than MAX_CHARS are split, and each part repeats the heading.
    Text with no article headings (preamble, other document types) is split by size."""

    chunks: list[Chunk] = []
    for heading, unit in _split_into_units(_clean_lines(pages)):
        chunks.extend(_pack(heading, unit))
    return chunks


def _clean_lines(pages: list[PageText]) -> list[Line]:
    """Flatten all pages into lines, dropping page numbers and repeated headers/footers."""

    per_page = [[l.strip() for l in p.text.splitlines() if l.strip()] for p in pages]

    # A short line that appears on many pages is a running header or footer.
    counts: dict[str, int] = {}
    for lines in per_page:
        for norm in {_normalize(l) for l in lines if not ARTICLE_RE.match(l)}:
            counts[norm] = counts.get(norm, 0) + 1
    threshold = max(3, int(0.4 * len(pages)))
    repeated = {n for n, c in counts.items() if c >= threshold}

    out: list[Line] = []
    for page, lines in zip(pages, per_page):
        for line in lines:
            if PAGE_NUMBER_RE.match(line):
                continue
            if not ARTICLE_RE.match(line) and len(line) < 100 and _normalize(line) in repeated:
                continue
            out.append(Line(line, page.page_number, page.source))
    return out


def _normalize(line: str) -> str:
    return re.sub(r"\d+", "#", line.lower())


def _split_into_units(lines: list[Line]) -> list[tuple[str, list[Line]]]:
    """Group lines by article. Lines before the first article get an empty heading."""
    units: list[tuple[str, list[Line]]] = []
    heading, current = "", []
    for line in lines:
        if ARTICLE_RE.match(line.text):
            if current:
                units.append((heading, current))
            heading, current = line.text, [line]
        else:
            current.append(line)
    if current:
        units.append((heading, current))
    return units


def _pack(heading: str, lines: list[Line]) -> list[Chunk]:
    """Turn one unit into chunks of at most about MAX_CHARS, cutting only between lines."""

    chunks: list[Chunk] = []
    current: list[Line] = []
    size = 0
    continued = False

    def flush() -> None:
        body = "\n".join(l.text for l in current)
        text = f"{heading} (suite)\n{body}" if continued and heading else body
        chunks.append(
            Chunk(
                text=text,
                source=current[0].source,
                page=current[0].page,
                page_end=current[-1].page,
                heading=heading,
            )
        )

    for line in lines:
        added = len(line.text) + 1
        if current and size + added > settings.MAX_CHARS:
            flush()
            continued = True
            current = _overlap_tail(current)
            size = sum(len(l.text) + 1 for l in current)
        current.append(line)
        size += added

    if current:
        flush()
    return chunks


def _overlap_tail(lines: list[Line]) -> list[Line]:
    tail: list[Line] = []
    total = 0
    for line in reversed(lines[1:]):  # never carry over the whole chunk
        if total + len(line.text) + 1 > settings.OVERLAP_CHARS:
            break
        tail.insert(0, line)
        total += len(line.text) + 1
    return tail