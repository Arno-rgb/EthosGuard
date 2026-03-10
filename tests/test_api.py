from fastapi.testclient import TestClient

from api.app.main import app
from core.llm_fallback import LLMUnavailableError

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "policy_version": "0.1.0"}


def test_examples():
    response = client.get("/examples")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 10


def test_ethical_check():
    response = client.post(
        "/ethical_check",
        json={
            "scenario": "A company wants an AI chatbot to hide refund options to reduce costs.",
            "action": "Do not show refund information unless the user explicitly asks three times.",
            "stakeholders": ["customers", "company"],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["ethical_verdict"] == "blocked"
    assert payload["provenance"]["evaluation_mode"] == "rules"
    assert payload["provenance"]["policy_version"] == "0.1.0"


def test_ethical_check_returns_demo_message_when_llm_is_unavailable(monkeypatch):
    def fake_evaluate(payload):
        raise LLMUnavailableError()

    monkeypatch.setattr("api.app.routes.evaluate", fake_evaluate)
    response = client.post(
        "/ethical_check",
        json={
            "scenario": "A SaaS company wants to improve retention during cancellation.",
            "action": "Use recommendation messaging to persuade users to stay before showing cancellation.",
            "stakeholders": ["users", "company"],
        },
    )
    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "llm_unavailable"
