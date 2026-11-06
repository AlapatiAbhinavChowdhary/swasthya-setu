import logging
import json
from pathlib import Path

from swasthya_setu.coverage import ROOT
from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.loader import load_pdfs
from swasthya_setu.retrieval.vectorstore import build_index

logging.basicConfig(level=logging.INFO)

raw_root = ROOT / "data" / "raw"
pdf_dirs = sorted({path.parent for path in raw_root.glob("*/*.pdf")})
documents = [document for directory in pdf_dirs for document in load_pdfs(directory)]
chunks = chunk_documents(documents)
build_index(chunks)
manifest = {
    "files": sorted(str(path.relative_to(ROOT)) for directory in pdf_dirs for path in directory.glob("*.pdf")),
    "chunks": len(chunks),
}
(ROOT / "vectorstore" / "index-manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
print(f"Done. Indexed {len(chunks)} chunks.")