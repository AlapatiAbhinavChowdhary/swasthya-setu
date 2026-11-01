import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from swasthya_setu.retrieval.embedder import get_embeddings

logger = logging.getLogger(__name__)

INDEX_DIR = Path("vectorstore")


def build_index(chunks: list[Document], index_dir: Path = INDEX_DIR) -> FAISS:
    """Embed all chunks and save the FAISS index to disk."""
    store = FAISS.from_documents(chunks, get_embeddings())
    store.save_local(str(index_dir))
    logger.info("Saved index with %d vectors to %s", len(chunks), index_dir)
    return store


def load_index(index_dir: Path = INDEX_DIR) -> FAISS:
    """Load a previously saved index (no re-embedding needed)."""
    return FAISS.load_local(
        str(index_dir),
        get_embeddings(),
        allow_dangerous_deserialization=True,  # safe: we created this file ourselves
    )