from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "intfloat/multilingual-e5-small"


def get_embeddings() -> HuggingFaceEmbeddings:
    """Local multilingual embedding model. Vectors are normalized so
    a dot product equals cosine similarity."""
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        encode_kwargs={"normalize_embeddings": True},
    )