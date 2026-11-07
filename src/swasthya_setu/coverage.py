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
    lock = {item["url"]: item for item in json.loads(lock_path.read_text(encoding="utf-8"))} if lock_path.exists() else {}
    indexed = {
        item["url"]
        for item in lock.values()
        if item.get("status") in {"downloaded", "skipped"}
        and (ROOT / item["file"]).exists()
    }
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
        is_local = source.get("status") == "local_file" and local_file and (ROOT / local_file).exists()
        if source["url"] in indexed or is_local:
            for disease_id in source["disease_ids"]:
                source_by_disease.setdefault(disease_id, set()).add(source["id"])
    rows = []
    for disease in diseases:
        source_ids = source_by_disease.get(disease["id"], set())
        count = len(source_ids)
        chunks = 0
        for source in sources:
            if source["id"] not in source_ids:
                continue
            chunks += chunks_by_source.get(source["id"], 0)
            if source.get("file"):
                chunks += chunks_by_source.get(Path(source["file"]).name, 0)
        rows.append({
            "id": disease["id"],
            "name_en": disease["name_en"],
            "name_hi": disease["name_hi"],
            "documents": count,
            "chunks": chunks,
            "last_indexed": last_indexed,
            "status": "indexed" if count else "coming_soon",
            "reviewed": disease.get("reviewed", False),
        })
    return {"last_indexed": last_indexed, "diseases": rows}
