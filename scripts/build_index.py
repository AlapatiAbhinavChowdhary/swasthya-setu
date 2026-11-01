from pathlib import Path

from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.loader import load_pdfs
from swasthya_setu.retrieval.vectorstore import build_index

chunks = chunk_documents(load_pdfs(Path("data/raw")))
build_index(chunks)
print(f"Done. Indexed {len(chunks)} chunks.")