import logging
import shutil
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_chroma import Chroma

from swasthya_setu.config import settings
from swasthya_setu.retrieval.embedder import get_embeddings

logger = logging.getLogger(__name__)

INDEX_DIR = Path("vectorstore")


def build_index(chunks: list[Document], index_dir: Path = INDEX_DIR):
    """Build the configured persistent index from verified chunks."""
    if settings.vectorstore_backend == "faiss":
        store = FAISS.from_documents(chunks, get_embeddings())
        store.save_local(str(index_dir))
        logger.info("Saved FAISS index with %d vectors to %s", len(chunks), index_dir)
        return store
    chroma_dir = index_dir / "chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
    store = Chroma.from_documents(
        chunks,
        get_embeddings(),
        collection_name="swasthya_setu",
        persist_directory=str(chroma_dir),
    )
    logger.info("Saved Chroma index with %d vectors to %s", len(chunks), chroma_dir)
    logger.info("Saved index with %d vectors to %s", len(chunks), index_dir)
    return store


def load_index(index_dir: Path = INDEX_DIR):
    """Load the configured persistent index, falling back to legacy FAISS."""
    chroma_dir = index_dir / "chroma"
    if settings.vectorstore_backend != "faiss" and chroma_dir.exists():
        return Chroma(
            collection_name="swasthya_setu",
            persist_directory=str(chroma_dir),
            embedding_function=get_embeddings(),
        )
    return FAISS.load_local(
        str(index_dir),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )