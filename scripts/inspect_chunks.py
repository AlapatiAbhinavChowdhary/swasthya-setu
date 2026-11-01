from pathlib import Path

from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.loader import load_pdfs

docs = load_pdfs(Path("data/raw"))
chunks = chunk_documents(docs)

print(f"Pages: {len(docs)} -> Chunks: {len(chunks)}")
lengths = [len(c.page_content) for c in chunks]
print(f"Chunk length: min={min(lengths)}, max={max(lengths)}, avg={sum(lengths) // len(lengths)}")

mid = chunks[len(chunks) // 2]
print("\n--- A middle chunk ---")
print(mid.metadata)
print(mid.page_content)