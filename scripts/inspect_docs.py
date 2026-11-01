from pathlib import Path

from swasthya_setu.ingestion.loader import load_pdfs

docs = load_pdfs(Path("data/raw"))

empty = [d for d in docs if len(d.page_content.strip()) < 50]
print(f"Total pages: {len(docs)}")
print(f"Pages with almost no text: {len(empty)}")
print("Empty page numbers:", [d.metadata["page"] for d in empty])

# Show a page that does have text
sample = next(d for d in docs if len(d.page_content.strip()) > 500)
print("\n--- Sample page metadata ---")
print(sample.metadata)
print("\n--- First 500 characters ---")
print(sample.page_content[:500])