import pytest
from fastapi.testclient import TestClient

from swasthya_setu.api import app as api_module
from swasthya_setu.config import settings


@pytest.fixture(autouse=True)
def mock_vectorstore_lifespan(monkeypatch):
    """Keep API tests independent from the local embedding model."""
    monkeypatch.setattr(api_module, "_store", lambda: object())
    api_module._requests.clear()
    api_module._cache.clear()


def _state(answer: str, emergency: bool = False) -> dict:
    return {
        "answer": answer,
        "citations": [] if emergency else [1],
        "response": {
            "answer": answer,
            "language": "en",
            "intent": "emergency" if emergency else "disease_info",
            "emergency": emergency,
            "language_consistent": True,
            "sources": [] if emergency else [{
                "source": "dengue.pdf",
                "page": "1",
                "snippet": " 1\nA  very long   source snippet with useful evidence.",
            }],
        },
    }


def test_api_health_and_chat(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setattr(api_module, "run_agent", lambda *_args: _state("Grounded [1]."))
    with TestClient(api_module.app) as client:
        health_data = client.get("/health").json()
        assert health_data["status"] == "ok"
        assert "llm_configured" in health_data
        response = client.post("/chat", json={"message": "What is dengue?"})
        stream = client.post("/chat/stream", json={"message": "What is dengue?"})
    assert response.status_code == 200
    assert response.json()["sources"][0]["number"] == 1
    assert "  " not in response.json()["sources"][0]["snippet"]
    assert stream.status_code == 200
    assert '"number":1' in stream.text


def test_coverage_reports_indexed_and_coming_soon_diseases():
    with TestClient(api_module.app) as client:
        response = client.get("/coverage")
    assert response.status_code == 200
    coverage = {row["id"]: row for row in response.json()["diseases"]}
    assert coverage["child-immunization"]["documents"] >= 0
    assert coverage["diabetes"]["status"] in {"indexed", "coming_soon"}


def test_diseases_alias_returns_coverage():
    with TestClient(api_module.app) as client:
        response = client.get("/diseases")
    assert response.status_code == 200
    assert len(response.json()["diseases"]) >= 20


def test_vaccination_endpoint_with_and_without_age():
    with TestClient(api_module.app) as client:
        # Full schedule
        res_all = client.get("/vaccination")
        assert res_all.status_code == 200
        data_all = res_all.json()
        assert "schedule" in data_all
        assert len(data_all["schedule"]) >= 5
        assert data_all["reviewed"] is False

        # Filtered by 9 months
        res_9m = client.get("/vaccination?age_months=9")
        assert res_9m.status_code == 200
        data_9m = res_9m.json()
        assert len(data_9m["schedule"]) == 1
        assert data_9m["schedule"][0]["age"] == "9-12 Months"
        assert any("MR-1" in v for v in data_9m["schedule"][0]["vaccines"])


def test_api_emergency_response(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setattr(
        api_module, "run_agent", lambda *_args: _state("Emergency", emergency=True)
    )
    with TestClient(api_module.app) as client:
        response = client.post("/chat", json={"message": "My child is vomiting blood"})
    assert response.status_code == 200
    assert response.json()["emergency"] is True


def test_validation_error_is_short_and_does_not_echo_input(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    with TestClient(api_module.app) as client:
        response = client.post("/chat", json={"message": "private text", "language": "xx"})
    assert response.status_code == 422
    assert "private text" not in response.text
    assert response.json()["detail"] == "Please provide a valid message and request."


def test_hindi_validation_message(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    with TestClient(api_module.app) as client:
        response = client.post(
            "/chat",
            json={"message": "x", "language": "xx"},
            headers={"Accept-Language": "hi"},
        )
    assert response.status_code == 422
    assert "कृपया" in response.json()["detail"]


def test_feedback_is_saved(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    with TestClient(api_module.app) as client:
        response = client.post(
            "/feedback",
            json={"session_id": "session", "rating": "up", "comment": "Helpful"},
        )
    assert response.status_code == 200
    assert response.json()["accepted"] is True


def test_rate_limit_runs_before_cache(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setattr(settings, "rate_limit_per_minute", 1)
    api_module._requests.clear()
    api_module._cache.clear()
    calls = []

    def fake_agent(*_args):
        calls.append(True)
        return _state("Cached [1].")

    monkeypatch.setattr(api_module, "run_agent", fake_agent)
    with TestClient(api_module.app) as client:
        first = client.post("/chat", json={"message": "same"})
        second = client.post("/chat", json={"message": "same"})
    assert first.status_code == 200
    assert second.status_code == 429
    assert len(calls) == 1


def test_health_reports_llm_configured_when_valid(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyTestValidKey123")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-flash")
    from swasthya_setu.config import get_settings

    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        health = client.get("/health").json()
        assert health == {"status": "ok", "llm_configured": True}


def test_health_and_endpoints_when_key_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setenv("GEMINI_API_KEY", "")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    from swasthya_setu.config import get_settings

    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        health = client.get("/health").json()
        assert health == {"status": "ok", "llm_configured": False}
        assert client.get("/coverage").status_code == 200
        assert client.get("/sources").status_code == 200


def test_health_and_endpoints_when_dummy_key(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setenv("GEMINI_API_KEY", "ci-dummy-key")
    monkeypatch.setenv("GEMINI_MODEL", "ci-dummy-model")
    from swasthya_setu.config import get_settings

    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        health = client.get("/health").json()
        assert health == {"status": "ok", "llm_configured": False}
        assert client.get("/coverage").status_code == 200
        assert client.get("/sources").status_code == 200


def test_alerts_endpoint_returns_demo_data():
    with TestClient(api_module.app) as client:
        resp = client.get("/alerts")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_demo"] is True
        assert "not a live alert" in data["disclaimer"]
        assert len(data["alerts"]) > 0
        for alert in data["alerts"]:
            assert alert["label"] == "DEMO"

        # Filter by disease
        resp_dengue = client.get("/alerts?disease=dengue")
        assert resp_dengue.status_code == 200
        dengue_data = resp_dengue.json()
        assert all(a["disease"].lower() == "dengue" for a in dengue_data["alerts"])

        # Hindi disclaimer
        resp_hi = client.get("/alerts?language=hi")
        assert resp_hi.status_code == 200
        assert "डेमो डेटा" in resp_hi.json()["disclaimer"]


def test_facilities_endpoint_returns_sample_data():
    with TestClient(api_module.app) as client:
        resp = client.get("/facilities")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_sample"] is True
        assert "108" in data["disclaimer"]
        assert len(data["facilities"]) > 0
        for fac in data["facilities"]:
            assert fac["label"] == "SAMPLE"

        # Filter by district
        resp_pune = client.get("/facilities?district=pune")
        assert resp_pune.status_code == 200
        pune_data = resp_pune.json()
        assert all("pune" in f["district"].lower() for f in pune_data["facilities"])

        # Hindi emergency disclaimer
        resp_hi = client.get("/facilities?language=hi")
        assert resp_hi.status_code == 200
        assert "108" in resp_hi.json()["disclaimer"]
        assert "नमूना" in resp_hi.json()["disclaimer"]


def test_health_when_dummy_placeholder(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    monkeypatch.setenv("GEMINI_API_KEY", "your_api_key_here")
    from swasthya_setu.config import get_settings

    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        health = client.get("/health").json()
        assert health == {"status": "ok", "llm_configured": False}


def test_ask_script_exits_on_missing_or_dummy_key(monkeypatch):
    import runpy
    from swasthya_setu.config import get_settings

    # Missing / empty key
    monkeypatch.setenv("GEMINI_API_KEY", "")
    get_settings.cache_clear()
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path("scripts/ask.py", run_name="__main__")
    assert "GEMINI_API_KEY" in str(exc_info.value)

    # Dummy placeholder key
    monkeypatch.setenv("GEMINI_API_KEY", "ci-dummy-key")
    monkeypatch.setenv("GEMINI_MODEL", "ci-dummy-model")
    get_settings.cache_clear()
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path("scripts/ask.py", run_name="__main__")
    assert "GEMINI_API_KEY" in str(exc_info.value)

    # Valid key with dummy model
    monkeypatch.setenv("GEMINI_API_KEY", "AIzaSyValidKey")
    monkeypatch.setenv("GEMINI_MODEL", "ci-dummy-model")
    get_settings.cache_clear()
    with pytest.raises(SystemExit) as exc_info:
        runpy.run_path("scripts/ask.py", run_name="__main__")
    assert "GEMINI_MODEL" in str(exc_info.value)
