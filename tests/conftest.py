import os
from pathlib import Path
import pytest

# Ensure offline execution and dummy credentials before test module imports
os.environ.setdefault("GEMINI_API_KEY", "ci-dummy-key")
os.environ.setdefault("GEMINI_MODEL", "ci-dummy-model")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


class DummyEmbeddings:
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 384 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [0.1] * 384


@pytest.fixture(autouse=True)
def isolate_test_environment(monkeypatch, tmp_path):
    """Keep tests completely isolated from live files, real API, and global state."""
    from swasthya_setu.config import settings
    import swasthya_setu.retrieval.embedder as embedder_module

    # Mock embeddings to be fast and completely offline
    monkeypatch.setattr(embedder_module, "get_embeddings", lambda: DummyEmbeddings())

    # Isolate SQLite feedback database to a unique temporary file per test
    temp_db = tmp_path / "test_feedback.db"
    monkeypatch.setattr(settings, "feedback_database", str(temp_db))

    # Mock chain store to avoid reading Chroma SQLite on disk during unit tests
    import swasthya_setu.generation.chain as chain_module
    class DummyStore:
        def similarity_search(self, *args, **kwargs):
            return []
    monkeypatch.setattr(chain_module, "_store", lambda: DummyStore())
