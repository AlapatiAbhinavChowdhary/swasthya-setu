"""Safe structured tools backed by verified coverage metadata and official schedules."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Protocol

from swasthya_setu.config import get_settings
from swasthya_setu.coverage import ROOT, get_coverage

logger = logging.getLogger(__name__)


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

    for item in all_items:
        if "supplements" not in item:
            item["supplements"] = []

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


class AlertProvider(Protocol):
    """Protocol for disease outbreak alerts providers."""

    def get_alerts(
        self,
        district: str | None = None,
        state: str | None = None,
        disease: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return list of outbreak alert entries matching optional filters."""
        ...


class JsonAlertProvider:
    """Reads outbreak alerts from a structured JSON file."""

    def __init__(self, file_path: Path | None = None) -> None:
        self.file_path = file_path or (ROOT / "data" / "structured" / "outbreak_alerts.json")

    def get_alerts(
        self,
        district: str | None = None,
        state: str | None = None,
        disease: str | None = None,
    ) -> list[dict[str, Any]]:
        if not self.file_path.exists():
            return []
        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            alerts = data.get("alerts", [])
        except Exception as e:
            logger.warning("Failed to read alerts from %s: %s", self.file_path, e)
            return []

        filtered = []
        for alert in alerts:
            # Ensure every entry is labelled DEMO
            alert["label"] = "DEMO"
            if district and district.lower() not in alert.get("district", "").lower():
                continue
            if state and state.lower() not in alert.get("state", "").lower():
                continue
            if disease and disease.lower() not in alert.get("disease", "").lower():
                continue
            filtered.append(alert)
        return filtered


_DEFAULT_ALERT_PROVIDER = JsonAlertProvider()

ALERT_DISCLAIMERS = {
    "en": "Demo data, not a live alert. For active official disease surveillance in India, consult the Integrated Disease Surveillance Programme (IDSP) at idsp.nic.in.",
    "hi": "केवल डेमो डेटा - यह लाइव अलर्ट नहीं है। भारत में सक्रिय आधिकारिक रोग निगरानी के लिए आईडीएसपी (idsp.nic.in) से परामर्श लें।",
}

FACILITY_DISCLAIMERS = {
    "en": "In a medical emergency, go to the nearest hospital or call 108. (Sample facility data for demonstration purposes only.)",
    "hi": "आपातकाल में नजदीकी अस्पताल जाएँ या 108 पर कॉल करें। (यह केवल प्रदर्शन हेतु नमूना सुविधा डेटा है।)",
}


def outbreak_alerts(
    district: str | None = None,
    state: str | None = None,
    disease: str | None = None,
    language: str = "en",
    provider: AlertProvider | None = None,
) -> dict[str, Any]:
    """Return outbreak alerts matching query parameters with explicit DEMO label."""
    active_provider = provider or _DEFAULT_ALERT_PROVIDER
    alerts = active_provider.get_alerts(district=district, state=state, disease=disease)
    disclaimer = ALERT_DISCLAIMERS.get(language, ALERT_DISCLAIMERS["en"])
    return {
        "disclaimer": disclaimer,
        "is_demo": True,
        "query": {"district": district, "state": state, "disease": disease},
        "count": len(alerts),
        "alerts": alerts,
    }


def find_hospital(
    district: str | None = None,
    state: str | None = None,
    language: str = "en",
) -> dict[str, Any]:
    """Find public healthcare facilities by district/state, labelled SAMPLE."""
    settings = get_settings()
    facilities: list[dict[str, Any]] = []

    # Optional OSM Overpass query if enabled
    if getattr(settings, "enable_overpass", False):
        try:
            import httpx

            area_clause = ""
            if district:
                area_clause = f'["addr:district"~"{district}",i]'
            query = f"""
            [out:json][timeout:5];
            nwr["amenity"="hospital"]{area_clause}(area.searchArea);
            out center 10;
            """
            # Network request with strict 5-second timeout
            resp = httpx.post(
                "https://overpass-api.de/api/interpreter",
                data={"data": query},
                timeout=5.0,
            )
            if resp.status_code == 200:
                elements = resp.json().get("elements", [])
                for el in elements:
                    tags = el.get("tags", {})
                    facilities.append(
                        {
                            "id": f"OSM-{el.get('id')}",
                            "name": tags.get("name", "Hospital"),
                            "type": tags.get("healthcare", "Hospital"),
                            "district": district or tags.get("addr:district", ""),
                            "state": state or tags.get("addr:state", ""),
                            "address": tags.get("addr:full") or tags.get("addr:street", ""),
                            "phone": tags.get("phone", "108 (Helpline)"),
                            "label": "SAMPLE",
                        }
                    )
        except Exception as e:
            logger.info("Overpass query bypassed or failed: %s; falling back to local dataset", e)

    # Local structured facilities CSV
    csv_path = ROOT / "data" / "structured" / "facilities.csv"
    if csv_path.exists():
        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Enforce SAMPLE label
                    row["label"] = "SAMPLE"
                    if district and district.lower() not in row.get("district", "").lower():
                        continue
                    if state and state.lower() not in row.get("state", "").lower():
                        continue
                    facilities.append(dict(row))
        except Exception as e:
            logger.warning("Failed to read facilities CSV: %s", e)

    disclaimer = FACILITY_DISCLAIMERS.get(language, FACILITY_DISCLAIMERS["en"])
    return {
        "disclaimer": disclaimer,
        "is_sample": True,
        "query": {"district": district, "state": state},
        "count": len(facilities),
        "facilities": facilities,
    }
