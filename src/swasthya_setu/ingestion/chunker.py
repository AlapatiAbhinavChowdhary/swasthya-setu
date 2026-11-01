import logging

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

MIN_PAGE_CHARS = 50


def chunk_documents(
    documents: list[Document],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Document]:
    """Drop near-empty pages, then split the rest into overlapping chunks."""
    pages = [d for d in documents if len(d.page_content.strip()) >= MIN_PAGE_CHARS]
    logger.info("Kept %d of %d pages", len(pages), len(documents))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    chunks = splitter.split_documents(pages)
    logger.info("Created %d chunks", len(chunks))
    return chunks