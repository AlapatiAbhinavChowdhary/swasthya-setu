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
    if index_marker.exists():
        last_indexed = datetime.fromtimestamp(
            index_marker.stat().st_mtime, timezone.utc
        ).isoformat()
    source_by_disease: dict[str, set[str]] = {item["id"]: set() for item in diseases}
    for source in sources:
        if source["url"] in indexed:
            for disease_id in source["disease_ids"]:
                source_by_disease.setdefault(disease_id, set()).add(source["url"])
    rows = []
    for disease in diseases:
        count = len(source_by_disease.get(disease["id"], set()))
        rows.append({
            "id": disease["id"],
            "name_en": disease["name_en"],
            "name_hi": disease["name_hi"],
            "documents": count,
            "last_indexed": last_indexed,
            "status": "indexed" if count else "coming_soon",
            "reviewed": disease.get("reviewed", False),
        })
    return {"last_indexed": last_indexed, "diseases": rows}
