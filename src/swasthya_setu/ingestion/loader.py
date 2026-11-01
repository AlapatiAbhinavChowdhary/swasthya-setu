import logging
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def load_pdfs(directory: Path) -> list[Document]:
    """Load every PDF in a directory. Returns one Document per page."""
    documents: list[Document] = []
    for pdf_path in sorted(directory.glob("*.pdf")):
        pages = PyPDFLoader(str(pdf_path)).load()
        logger.info("Loaded %s (%d pages)", pdf_path.name, len(pages))
        documents.extend(pages)
    return documents