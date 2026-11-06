"""Safe structured tools backed by verified coverage metadata."""

from __future__ import annotations

from swasthya_setu.coverage import get_coverage


def list_diseases() -> list[dict]:
    """Return disease coverage without inventing facts for unindexed diseases."""
    return get_coverage()["diseases"]


def disease_status(disease_id: str) -> dict | None:
    """Return one disease's honest indexed/coming-soon status."""
    return next((row for row in list_diseases() if row["id"] == disease_id), None)
