import hashlib
import json
import logging
from pathlib import Path
import shutil
import yaml

from swasthya_setu.config import settings
from swasthya_setu.coverage import ROOT
from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.html_loader import load_html_paths
from swasthya_setu.ingestion.loader import load_pdf_paths
from swasthya_setu.retrieval.vectorstore import build_index, load_index

logging.basicConfig(level=logging.INFO)

FORBIDDEN_EXACT = ["Newsroom", "Select language", "Emergencies", "Disease Outbreak News", "Member States", "cookie"]

raw_root = ROOT / "data" / "raw"
current_files = sorted(raw_root.rglob("*.pdf"))
current_html = sorted(raw_root.rglob("*.html"))
all_files = current_files + current_html

source_manifest = yaml.safe_load(
    (ROOT / "data" / "sources.yaml").read_text(encoding="utf-8")
).get("sources", [])

source_metadata = {}
source_by_hash = {}
for source in source_manifest:
    file_name = source.get("file")
    if file_name:
        path = ROOT / file_name
        source_metadata[str(path.resolve())] = source
        if path.exists():
            source_by_hash[hashlib.sha256(path.read_bytes()).hexdigest()] = source


def prepare_documents(paths):
    unique_paths = set()
    unique_input_paths = []
    for path in paths:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in unique_paths:
            unique_paths.add(digest)
            unique_input_paths.append(path)
    documents = load_pdf_paths([p for p in unique_input_paths if p.suffix.lower() == ".pdf"])
    documents.extend(load_html_paths([p for p in unique_input_paths if p.suffix.lower() == ".html"]))
    unique_documents = []
    for document in documents:
        path = Path(document.metadata["source"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        source = source_metadata.get(str(path.resolve())) or source_by_hash.get(digest)
        if source:
            document.metadata["source_id"] = source["id"]
            document.metadata["doc_id"] = digest
            document.metadata["disease_ids"] = ",".join(source["disease_ids"])
            document.metadata["title"] = source["title"]
            document.metadata["publisher"] = source["publisher"]
            document.metadata["source_url"] = source.get("url", "")
            document.metadata["coverage"] = source.get("coverage", "general")
            document.metadata["year"] = int(source.get("year", 2024))
            document.metadata["doc_type"] = source.get("doc_type", "fact_sheet")
            document.metadata["outdated"] = bool(source.get("outdated", False))
        unique_documents.append(document)
    return unique_documents


def unique_chunks(chunks):
    seen = set()
    result = []
    filtered_boilerplate = 0
    for chunk in chunks:
        # Check forbidden boilerplate
        if any(f in chunk.page_content for f in FORBIDDEN_EXACT):
            filtered_boilerplate += 1
            continue
        digest = hashlib.sha256(chunk.page_content.strip().encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        result.append(chunk)
    if filtered_boilerplate:
        logging.info("Filtered %d chunks containing boilerplate tokens", filtered_boilerplate)
    return result


def main():
    marker_path = ROOT / "vectorstore" / "index-manifest.json"
    chroma_dir = ROOT / "vectorstore" / "chroma"
    if marker_path.exists():
        marker_path.unlink()
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)

    logging.info("Rebuilding index from scratch with %d input files...", len(all_files))
    documents = prepare_documents(all_files)
    chunks = unique_chunks(chunk_documents(documents))
    build_index(chunks)
    chunks_count = len(chunks)
    chunks_by_source = {}
    for doc in chunks:
        source_id = doc.metadata.get("source_id", Path(doc.metadata["source"]).name)
        chunks_by_source[source_id] = chunks_by_source.get(source_id, 0) + 1

    manifest = {
        "schema_version": 4,
        "files": sorted(str(path.relative_to(ROOT)) for path in all_files),
        "chunks": chunks_count,
        "chunks_by_source": chunks_by_source,
    }
    marker_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logging.info("Index rebuild complete: %d chunks indexed.", chunks_count)


if __name__ == "__main__":
    main()
