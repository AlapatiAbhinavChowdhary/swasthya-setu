import os

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "intfloat/multilingual-e5-small"


class E5Embeddings(Embeddings):
    """E5 models need 'passage: ' on documents and 'query: ' on questions.
    This wrapper adds them so callers never have to."""

    def __init__(self) -> None:
        self._model = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            encode_kwargs={"normalize_embeddings": True},
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.embed_documents([f"passage: {t}" for t in texts])

    def embed_query(self, text: str) -> list[float]:
        return self._model.embed_query(f"query: {text}")


def get_embeddings() -> E5Embeddings:
    return E5Embeddings()