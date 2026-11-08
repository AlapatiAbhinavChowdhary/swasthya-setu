"""Safe structured tools backed by verified coverage metadata and official schedules."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from swasthya_setu.coverage import ROOT, get_coverage


def list_diseases() -> list[dict]:
    """Return disease coverage without inventing facts for unindexed diseases."""
    return get_coverage()["diseases"]


def disease_status(disease_id: str) -> dict | None:
    """Return one disease's honest indexed/coming-soon status."""
    return next((row for row in list_diseases() if row["id"] == disease_id), None)


def vaccination_schedule(age_months: int | None = None) -> dict[str, Any]:
    """Return the official National Immunization Schedule, optionally filtered by age in months."""
    schedule_file = ROOT / "data" / "structured" / "vaccination_schedule.json"
    if not schedule_file.exists():
        return {
            "source_label": "NHM National Immunization Schedule; check with your ANM, ASHA or health centre",
            "reviewed": False,
            "schedule": [],
            "footnotes": {},
        }

    data = json.loads(schedule_file.read_text(encoding="utf-8"))
    all_items = data.get("schedule", [])
    footnotes = data.get("footnotes", {})
    source_info = data.get("source", {})
    source_label = source_info.get(
        "source_label",
        "NHM National Immunization Schedule, 2018 edition; check with your ANM, ASHA or health centre for the current schedule",
    )

    if age_months is None:
        filtered = all_items
    else:
        filtered = []
        for item in all_items:
            min_m = item.get("age_months_min")
            max_m = item.get("age_months_max")
            if min_m is not None and max_m is not None:
                if min_m <= age_months <= max_m:
                    filtered.append(item)

    return {
        "source_label": source_label,
        "reviewed": data.get("reviewed", False),
        "age_months_queried": age_months,
        "schedule": filtered,
        "footnotes": footnotes,
    }
