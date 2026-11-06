import logging
import json
import hashlib
from pathlib import Path

from swasthya_setu.coverage import ROOT
from swasthya_setu.config import settings
from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.loader import load_pdfs
from swasthya_setu.retrieval.vectorstore import build_index, load_index

logging.basicConfig(level=logging.INFO)

raw_root = ROOT / "data" / "raw"
current_files = sorted(raw_root.glob("*/*.pdf"))
marker_path = ROOT / "vectorstore" / "index-manifest.json"
previous = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else {}
previous_files = {ROOT / path for path in previous.get("files", [])}
can_increment = (
    settings.vectorstore_backend == "chroma"
    and (ROOT / "vectorstore" / "chroma").exists()
    and previous_files.issubset(set(current_files))
)
if can_increment:
    new_files = [path for path in current_files if path not in previous_files]
    new_documents = [
        document
        for directory in sorted({path.parent for path in new_files})
        for document in load_pdfs(directory)
    ]
    new_chunks = chunk_documents(new_documents)
    if new_chunks:
        store = load_index()
        ids = [
            hashlib.sha256(
                f"{doc.metadata.get('source')}:{doc.metadata.get('page')}:{doc.page_content}".encode()
            ).hexdigest()
            for doc in new_chunks
        ]
        store.add_documents(new_chunks, ids=ids)
    chunks_count = previous.get("chunks", 0) + len(new_chunks)
else:
    pdf_dirs = sorted({path.parent for path in current_files})
    documents = [document for directory in pdf_dirs for document in load_pdfs(directory)]
    chunks = chunk_documents(documents)
    build_index(chunks)
    chunks_count = len(chunks)
manifest = {
    "files": sorted(str(path.relative_to(ROOT)) for path in current_files),
    "chunks": chunks_count,
}
(marker_path.write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
))
print(f"Done. Indexed {chunks_count} chunks.")