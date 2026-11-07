"""Honest document coverage derived from the source lockfile and local index."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]


def get_coverage() -> dict[str, Any]:
    diseases = yaml.safe_load(
        (ROOT / "data" / "diseases.yaml").read_text(encoding="utf-8")
    ).get("diseases", [])
    sources = yaml.safe_load(
        (ROOT / "data" / "sources.yaml").read_text(encoding="utf-8")
    ).get("sources", [])
    lock_path = ROOT / "data" / "sources.lock.json"
    last_indexed = None
    index_marker = ROOT / "vectorstore" / "index-manifest.json"
    chunks_by_source: dict[str, int] = {}
    if index_marker.exists():
        marker = json.loads(index_marker.read_text(encoding="utf-8"))
        chunks_by_source = marker.get("chunks_by_source", {})
        last_indexed = datetime.fromtimestamp(
            index_marker.stat().st_mtime, timezone.utc
        ).isoformat()
    source_by_disease: dict[str, set[str]] = {item["id"]: set() for item in diseases}
    for source in sources:
        local_file = source.get("file")
        if local_file and (ROOT / local_file).exists():
            for disease_id in source["disease_ids"]:
                source_by_disease.setdefault(disease_id, set()).add(source["id"])
    rows = []
    for disease in diseases:
        source_ids = source_by_disease.get(disease["id"], set())
        details = []
        chunks = 0
        for source in sources:
            if source["id"] not in source_ids:
                continue
            source_chunks = chunks_by_source.get(source["id"], 0)
            if source_chunks == 0:
                source_chunks = chunks_by_source.get(Path(source.get("file", "")).name, 0)
            if source_chunks == 0:
                continue
            chunks += source_chunks
            details.append({
                "id": source["id"],
                "title": source["title"],
                "publisher": source["publisher"],
                "url": source.get("url", ""),
                "chunks": source_chunks,
                "coverage": source.get("coverage", "general"),
                "label": "disease-specific" if source.get("coverage") == "disease-specific" else "general information only",
            })
        count = len(details)
        rows.append({
            "id": disease["id"],
            "name_en": disease["name_en"],
            "name_hi": disease["name_hi"],
            "documents": len(details),
            "documents_detail": details,
            "chunks": chunks,
            "last_indexed": last_indexed,
            "status": "indexed" if count else "coming_soon",
            "reviewed": disease.get("reviewed", False),
        })
    return {"last_indexed": last_indexed, "diseases": rows}
