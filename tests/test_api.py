import pytest
from pathlib import Path
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


def test_safe_streaming_event_order_and_content_equality(monkeypatch, tmp_path):
    import json

    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    multi_sentence_answer = (
        "Dengue fever causes high fever and severe headache [1]. "
        "Joint pain is also commonly reported [1].\n\n"
        "This is health awareness information, not medical advice. "
        "In an emergency, go to the nearest hospital or call 108."
    )
    monkeypatch.setattr(api_module, "run_agent", lambda *_args: _state(multi_sentence_answer))

    with TestClient(api_module.app) as client:
        chat_resp = client.post("/chat", json={"message": "What are dengue symptoms?"}).json()
        stream_resp = client.post("/chat/stream", json={"message": "What are dengue symptoms?"})

    assert stream_resp.status_code == 200
    blocks = [b for b in stream_resp.text.strip().split("\n\n") if b.strip()]

    events = []
    for block in blocks:
        parts = block.strip().split("\n")
        event_type = parts[0].replace("event: ", "").strip()
        data_str = parts[1].replace("data: ", "").strip()
        events.append((event_type, json.loads(data_str)))

    # Verify event order: multiple 'message' events, followed by 'metadata', followed by 'done'
    assert len(events) >= 3
    event_types = [e[0] for e in events]
    assert event_types[-2] == "metadata"
    assert event_types[-1] == "done"
    assert all(t == "message" for t in event_types[:-2])
    assert len([t for t in event_types if t == "message"]) > 1

    # Verify concatenated chunks EQUAL the /chat answer exactly
    reconstructed_text = "".join(e[1]["chunk"] for e in events[:-2])
    assert reconstructed_text == chat_resp["answer"]

    # Verify metadata fields match /chat
    metadata = events[-2][1]
    assert metadata["sources"] == chat_resp["sources"]
    assert metadata["intent"] == chat_resp["intent"]
    assert metadata["emergency"] == chat_resp["emergency"]
    assert metadata["language"] == chat_resp["language"]
    assert metadata["language_consistent"] == chat_resp["language_consistent"]
    assert len(metadata["request_id"]) > 0


def test_safe_streaming_emergency_response(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    emergency_text = "This may be an emergency. Go to the nearest hospital immediately or call 108."
    monkeypatch.setattr(api_module, "run_agent", lambda *_args: _state(emergency_text, emergency=True))

    with TestClient(api_module.app) as client:
        stream_resp = client.post("/chat/stream", json={"message": "vomiting blood"})

    assert stream_resp.status_code == 200
    assert "call 108" in stream_resp.text
    assert '"emergency":true' in stream_resp.text


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


def test_languages_endpoint():
    with TestClient(api_module.app) as client:
        resp = client.get("/languages")
        assert resp.status_code == 200
        data = resp.json()
        assert "languages" in data
        codes = [lang["code"] for lang in data["languages"]]
        assert "en" in codes
        assert "hi" in codes
        assert "or" in codes
        assert "pa" in codes


def test_admin_feedback_protected_by_token(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "feedback_database", str(tmp_path / "api.db"))
    from swasthya_setu.config import get_settings

    # 1. Unset admin_token -> route disabled (404)
    monkeypatch.setenv("ADMIN_TOKEN", "")
    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        resp = client.get("/admin/feedback")
        assert resp.status_code == 404

    # 2. Set admin_token -> unauthorized on missing / wrong token
    test_secret = "super-secret-admin-token-12345"
    monkeypatch.setenv("ADMIN_TOKEN", test_secret)
    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        # Missing token
        assert client.get("/admin/feedback").status_code == 401
        # Wrong token
        assert client.get("/admin/feedback", headers={"Authorization": "Bearer wrong"}).status_code == 401
        assert client.get("/admin/feedback", headers={"X-Admin-Token": "wrong"}).status_code == 401

        # Submit feedback first
        client.post("/feedback", json={"session_id": "test-admin-sess", "rating": "up", "comment": "Great app!"})

        # Correct Bearer token
        resp_bearer = client.get("/admin/feedback", headers={"Authorization": f"Bearer {test_secret}"})
        assert resp_bearer.status_code == 200
        assert resp_bearer.json()["count"] >= 1
        assert resp_bearer.json()["feedback"][0]["comment"] == "Great app!"

        # Correct X-Admin-Token header
        resp_header = client.get("/admin/feedback", headers={"X-Admin-Token": test_secret})
        assert resp_header.status_code == 200
        assert resp_header.json()["count"] >= 1


def test_frontend_serving_flag(monkeypatch):
    from swasthya_setu.config import get_settings

    # Disabled by default
    monkeypatch.setenv("ENABLE_FRONTEND", "false")
    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        resp = client.get("/nonexistent-frontend-route")
        assert resp.status_code == 404

    # Enabled
    monkeypatch.setenv("ENABLE_FRONTEND", "true")
    get_settings.cache_clear()
    with TestClient(api_module.app) as client:
        resp = client.get("/")
        # Should return built index.html if dist exists
        dist_index = Path("web/dist/index.html")
        if dist_index.exists():
            assert resp.status_code == 200
            assert "html" in resp.headers.get("content-type", "").lower()


def test_cors_headers():
    with TestClient(api_module.app) as client:
        resp = client.options("/health", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"})
        assert resp.status_code == 200
        assert resp.headers.get("access-control-allow-origin") == "*"


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
