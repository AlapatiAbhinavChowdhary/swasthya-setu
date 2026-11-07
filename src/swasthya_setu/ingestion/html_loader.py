"""Small, dependency-free extractor for official HTML health pages."""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

from langchain_core.documents import Document


class _ArticleParser(HTMLParser):
    _ignored = {"script", "style", "nav", "footer", "header", "form", "aside"}

    def __init__(self) -> None:
        super().__init__()
        self.depth = 0
        self.heading = "Web page"
        self.in_heading = False
        self.heading_parts: list[str] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._ignored:
            self.depth += 1
        if tag in {"h1", "h2", "h3"} and self.depth == 0:
            self.in_heading = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._ignored and self.depth:
            self.depth -= 1
        if tag in {"h1", "h2", "h3"} and self.in_heading:
            self.heading = " ".join(self.heading_parts).strip() or "Web page"
            self.heading_parts = []
            self.in_heading = False

    def handle_data(self, data: str) -> None:
        if self.depth == 0:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                if self.in_heading:
                    self.heading_parts.append(text)
                self.parts.append(text)


def extract_html_text(text: str) -> tuple[str, str]:
    parser = _ArticleParser()
    parser.feed(text)
    content = "\n".join(parser.parts)
    return parser.heading.strip() or "Web page", content


def load_html_paths(paths: list[Path]) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(paths):
        heading, content = extract_html_text(path.read_text(encoding="utf-8"))
        if content:
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": str(path),
                    "page": 0,
                    "page_label": heading,
                },
            ))
    return documents
