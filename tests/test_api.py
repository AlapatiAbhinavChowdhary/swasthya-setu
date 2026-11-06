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
        assert client.get("/health").json() == {"status": "ok"}
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
