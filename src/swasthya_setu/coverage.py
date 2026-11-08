"""Honest document coverage derived from the source lockfile and local index."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def calculate_depth_tier(chunks: int, unique_docs_count: int, doc_types: list[str], specific_docs_count: int | None = None) -> str:
    """Calculate depth tier with honesty constraints.
    
    Tiers:
      - basic: <30 chunks
      - good: 30-150 chunks
      - deep: >150 chunks
    
    Constraint: Never present a single document or purely a fact sheet as deep coverage.
    Constraint: A disease is deep ONLY when supported by disease-specific documents (specific_docs_count != 0).
    A disease supported only by general handbooks must show "good" or "basic", never "deep".
    """
    if chunks < 30:
        return "basic"
    if chunks <= 150:
        return "good"
    # Over 150 chunks: requires disease-specific documents, multiple documents, and not purely fact sheets
    if specific_docs_count is not None and specific_docs_count == 0:
        return "good"
    if unique_docs_count <= 1 or all(dt == "fact_sheet" for dt in doc_types):
        return "good"
    return "deep"


def get_coverage() -> dict[str, Any]:
    diseases = yaml.safe_load(
        (ROOT / "data" / "diseases.yaml").read_text(encoding="utf-8")
    ).get("diseases", [])
    sources = yaml.safe_load(
        (ROOT / "data" / "sources.yaml").read_text(encoding="utf-8")
    ).get("sources", [])

    last_indexed = None
    index_marker = ROOT / "vectorstore" / "index-manifest.json"
    chunks_by_source: dict[str, int] = {}
    if index_marker.exists():
        marker = json.loads(index_marker.read_text(encoding="utf-8"))
        chunks_by_source = marker.get("chunks_by_source", {})
        last_indexed = datetime.fromtimestamp(
            index_marker.stat().st_mtime, timezone.utc
        ).isoformat()

    rows = []
    for disease in diseases:
        disease_id = disease["id"]
        # Find all sources matching this disease
        matching_sources = []
        for s in sources:
            if disease_id in s.get("disease_ids", []):
                matching_sources.append(s)

        # Deduplicate unique physical documents by content hash
        unique_docs_by_hash: dict[str, dict[str, Any]] = {}
        for source in matching_sources:
            local_file = source.get("file")
            if not local_file:
                continue
            path = ROOT / local_file
            if not path.exists():
                continue
            
            # Content hash
            content_hash = source.get("doc_id")
            if not content_hash:
                content_hash = hashlib.sha256(path.read_bytes()).hexdigest()

            source_chunks = chunks_by_source.get(source.get("id", ""), 0)
            if source_chunks == 0:
                source_chunks = chunks_by_source.get(path.name, 0)

            # Record or merge unique document
            if content_hash not in unique_docs_by_hash:
                unique_docs_by_hash[content_hash] = {
                    "id": source["id"],
                    "doc_id": content_hash,
                    "title": source["title"],
                    "publisher": source["publisher"],
                    "url": source.get("url", ""),
                    "file": local_file,
                    "year": source.get("year"),
                    "doc_type": source.get("doc_type", "fact_sheet"),
                    "chunks": source_chunks,
                    "coverage": source.get("coverage", "general"),
                    "label": "disease-specific" if source.get("coverage") == "disease-specific" else "general information only",
                }
            else:
                # If already present, prefer 'disease-specific' coverage label
                existing = unique_docs_by_hash[content_hash]
                if source.get("coverage") == "disease-specific":
                    existing["coverage"] = "disease-specific"
                    existing["label"] = "disease-specific"
                if source_chunks > existing["chunks"]:
                    existing["chunks"] = source_chunks
                if source.get("year") and (not existing.get("year") or source["year"] > existing["year"]):
                    existing["year"] = source["year"]

        unique_docs = list(unique_docs_by_hash.values())
        total_unique_docs = len(unique_docs)
        specific_docs_count = sum(1 for d in unique_docs if d["coverage"] == "disease-specific")
        # Ensure specific can never exceed total unique documents
        specific_docs_count = min(specific_docs_count, total_unique_docs)
        
        has_general_source = any(d["coverage"] == "general" for d in unique_docs)
        total_chunks = sum(d["chunks"] for d in unique_docs)
        
        years = [d["year"] for d in unique_docs if isinstance(d.get("year"), int)]
        newest_source_year = max(years) if years else None
        
        doc_types = [d.get("doc_type", "fact_sheet") for d in unique_docs]
        depth_tier = calculate_depth_tier(total_chunks, total_unique_docs, doc_types, specific_docs_count)

        rows.append({
            "id": disease["id"],
            "name_en": disease["name_en"],
            "name_hi": disease["name_hi"],
            "documents": total_unique_docs,
            "specific_documents": specific_docs_count,
            "chunks": total_chunks,
            "depth": depth_tier,
            "newest_source_year": newest_source_year,
            "has_general_source": has_general_source,
            "documents_detail": unique_docs,
            "last_indexed": last_indexed,
            "status": "indexed" if total_unique_docs > 0 else "coming_soon",
            "reviewed": disease.get("reviewed", False),
        })

    return {"last_indexed": last_indexed, "diseases": rows}
