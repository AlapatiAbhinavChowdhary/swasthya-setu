import logging
import json
import hashlib
from pathlib import Path
import yaml

from swasthya_setu.coverage import ROOT
from swasthya_setu.config import settings
from swasthya_setu.ingestion.chunker import chunk_documents
from swasthya_setu.ingestion.loader import load_pdf_paths
from swasthya_setu.ingestion.html_loader import load_html_paths
from swasthya_setu.retrieval.vectorstore import build_index, load_index

logging.basicConfig(level=logging.INFO)

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
        unique_documents.append(document)
    return unique_documents


def unique_chunks(chunks):
    seen = set()
    result = []
    for chunk in chunks:
        digest = hashlib.sha256(chunk.page_content.strip().encode("utf-8")).hexdigest()
        if digest in seen:
            continue
        seen.add(digest)
        result.append(chunk)
    return result


marker_path = ROOT / "vectorstore" / "index-manifest.json"
previous = json.loads(marker_path.read_text(encoding="utf-8")) if marker_path.exists() else {}
previous_files = {ROOT / path for path in previous.get("files", [])}
can_increment = (
    previous.get("schema_version") == 4
    and
    settings.vectorstore_backend == "chroma"
    and (ROOT / "vectorstore" / "chroma").exists()
    and previous_files.issubset(set(all_files))
)
if can_increment:
    new_files = [path for path in all_files if path not in previous_files]
    new_documents = prepare_documents(new_files)
    new_chunks = unique_chunks(chunk_documents(new_documents))
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
    chunks_by_source = dict(previous.get("chunks_by_source", {}))
    for doc in new_chunks:
        source_id = doc.metadata.get("source_id", Path(doc.metadata["source"]).name)
        chunks_by_source[source_id] = chunks_by_source.get(source_id, 0) + 1
else:
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
(marker_path.write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
))
print(f"Done. Indexed {chunks_count} chunks.")