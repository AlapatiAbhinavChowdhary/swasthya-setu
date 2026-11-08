import pytest
from pathlib import Path

from swasthya_setu.tools import (
    AlertProvider,
    JsonAlertProvider,
    outbreak_alerts,
    find_hospital,
    vaccination_schedule,
)
from swasthya_setu.generation.agent import run_agent, route_intent


def test_vaccination_schedule_filtering():
    all_items = vaccination_schedule()
    assert "reviewed" in all_items
    assert len(all_items["schedule"]) > 0

    # 9 months
    at_9m = vaccination_schedule(age_months=9)
    assert at_9m["age_months_queried"] == 9
    assert any("MR-1" in v or "Measles" in v for item in at_9m["schedule"] for v in item["vaccines"])

    # Birth
    at_birth = vaccination_schedule(age_months=0)
    assert any("BCG" in v for item in at_birth["schedule"] for v in item["vaccines"])


def test_json_alert_provider_filters(tmp_path):
    alerts_file = tmp_path / "alerts.json"
    alerts_file.write_text(
        """{
        "alerts": [
            {"id": "A1", "disease": "Dengue", "district": "South Delhi", "state": "Delhi", "date": "2026-10-01", "advisory": "Clean water", "source": "State"},
            {"id": "A2", "disease": "Malaria", "district": "Sundargarh", "state": "Odisha", "date": "2026-09-01", "advisory": "Bed nets", "source": "District"}
        ]
    }""",
        encoding="utf-8",
    )
    provider = JsonAlertProvider(file_path=alerts_file)

    # All alerts
    all_alerts = provider.get_alerts()
    assert len(all_alerts) == 2
    assert all(a["label"] == "DEMO" for a in all_alerts)

    # Filter by disease
    dengue_only = provider.get_alerts(disease="dengue")
    assert len(dengue_only) == 1
    assert dengue_only[0]["id"] == "A1"

    # Filter by state
    odisha_only = provider.get_alerts(state="Odisha")
    assert len(odisha_only) == 1
    assert odisha_only[0]["id"] == "A2"


def test_custom_alert_provider():
    class MockProvider:
        def get_alerts(self, district=None, state=None, disease=None):
            return [{"id": "MOCK-1", "label": "DEMO", "disease": "Flu", "district": "Test", "state": "Test", "date": "2026-01-01", "advisory": "Rest", "source": "Mock"}]

    res = outbreak_alerts(provider=MockProvider())
    assert res["is_demo"] is True
    assert res["count"] == 1
    assert res["alerts"][0]["disease"] == "Flu"


def test_outbreak_alerts_disclaimers():
    en_res = outbreak_alerts(language="en")
    assert en_res["is_demo"] is True
    assert "not a live alert" in en_res["disclaimer"]

    hi_res = outbreak_alerts(language="hi")
    assert hi_res["is_demo"] is True
    assert "डेमो डेटा" in hi_res["disclaimer"]


def test_find_hospital_filters_and_disclaimer():
    en_res = find_hospital(language="en")
    assert en_res["is_sample"] is True
    assert "108" in en_res["disclaimer"]
    assert en_res["count"] > 0
    assert all(f["label"] == "SAMPLE" for f in en_res["facilities"])

    # Hindi disclaimer
    hi_res = find_hospital(language="hi")
    assert "108" in hi_res["disclaimer"]

    # Filter by district
    delhi_res = find_hospital(district="Delhi")
    assert delhi_res["count"] > 0
    assert all("delhi" in f["district"].lower() for f in delhi_res["facilities"])


def test_agent_outbreak_alerts_and_find_hospital_intents(monkeypatch):
    # Mock LLM router proposal
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._route_and_rewrite",
        lambda _q: ("outbreak_alerts", "dengue alerts delhi"),
    )
    state = run_agent("Are there any dengue alerts in Delhi?", session_id="test-alerts-1", language="en")
    assert state["response"]["intent"] == "outbreak_alerts"
    assert "DEMO" in state["response"]["answer"]
    assert "not a live alert" in state["response"]["answer"]
    assert "108" in state["response"]["answer"]

    # Test find_hospital
    monkeypatch.setattr(
        "swasthya_setu.generation.agent._route_and_rewrite",
        lambda _q: ("find_hospital", "hospitals delhi"),
    )
    state_hosp = run_agent("Find hospitals in Delhi", session_id="test-hosp-1", language="en")
    assert state_hosp["response"]["intent"] == "find_hospital"
    assert "SAMPLE" in state_hosp["response"]["answer"]
    assert "108" in state_hosp["response"]["answer"]
