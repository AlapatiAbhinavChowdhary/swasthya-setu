import os
from pathlib import Path
import pytest

# Ensure offline execution and dummy credentials before test module imports
os.environ.setdefault("GEMINI_API_KEY", "ci-dummy-key")
os.environ.setdefault("GEMINI_MODEL", "ci-dummy-model")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


@pytest.fixture(autouse=True)
def isolate_test_environment(monkeypatch, tmp_path):
    """Keep tests completely isolated from live files, real API, and global state."""
    from swasthya_setu.config import settings

    # Isolate SQLite feedback database to a unique temporary file per test
    temp_db = tmp_path / "test_feedback.db"
    monkeypatch.setattr(settings, "feedback_database", str(temp_db))
