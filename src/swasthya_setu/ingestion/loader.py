import logging
import re
from collections import Counter
from pathlib import Path

import pymupdf as fitz
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

_PAGE_NUMBER = re.compile(r"^\s*(?:page\s+)?\d+\s*$", re.IGNORECASE)
_TOC_LINE = re.compile(r"^.+(?:\.{2,}\s*|\s+)\d+\s*$")
_GLUED_REPAIRS = {
    "caninclude": "can include",
    "retro-orbitalpain": "retro-orbital pain",
    "malnutritionare": "malnutrition are",
}


def normalize_page_text(text: str) -> str:
    """Normalize PDF line noise without changing meaningful paragraph text."""
    text = text.replace("\u00ad", "").replace("\u00a0", " ")
    for glued, repaired in _GLUED_REPAIRS.items():
        text = re.sub(re.escape(glued), repaired, text, flags=re.IGNORECASE)
    lines = []
    for raw_line in text.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line or _PAGE_NUMBER.fullmatch(line):
            continue
        lines.append(line)
    return "\n".join(lines)


def _is_table_of_contents(text: str) -> bool:
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        return False
    heading = " ".join(lines[:3]).lower()
    toc_lines = sum(bool(_TOC_LINE.match(line)) for line in lines)
    return "table of contents" in heading or (
        len(lines) >= 8 and toc_lines / len(lines) >= 0.45
    )


def _repeated_margin_lines(page_lines: list[list[str]]) -> set[str]:
    threshold = max(2, len(page_lines) // 5)
    margins = []
    for lines in page_lines:
        margins.extend(lines[:2] + lines[-2:])
    counts = Counter(line for line in margins if line)
    return {line for line, count in counts.items() if count >= threshold}


def load_pdf_paths(pdf_paths: list[Path]) -> list[Document]:
    """Load explicitly selected PDFs with PyMuPDF and return cleaned pages."""
    documents: list[Document] = []
    for pdf_path in sorted(pdf_paths):
        with fitz.open(pdf_path) as pdf:
            raw_pages = [normalize_page_text(page.get_text("text")) for page in pdf]
        page_lines = [page.splitlines() for page in raw_pages]
        repeated = _repeated_margin_lines(page_lines)
        pages = []
        for page_number, lines in enumerate(page_lines):
            cleaned_lines = [
                line for line in lines
                if line not in repeated and not _PAGE_NUMBER.fullmatch(line)
            ]
            text = "\n".join(cleaned_lines).strip()
            if _is_table_of_contents(text):
                logger.info("Dropped table-of-contents page %s page=%d", pdf_path.name, page_number + 1)
                continue
            pages.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(pdf_path),
                        "page": page_number,
                        "page_label": str(page_number + 1),
                    },
                )
            )
        logger.info("Loaded %s (%d cleaned pages)", pdf_path.name, len(pages))
        documents.extend(pages)
    return documents


def load_pdfs(directory: Path) -> list[Document]:
    """Load PDFs directly inside a directory."""
    return load_pdf_paths(list(directory.glob("*.pdf")))