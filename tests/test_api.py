from fastapi.testclient import TestClient

from api.app.main import app
from core.llm_fallback import LLMUnavailableError

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["policy_version"] == "2.0.0-draft"
    assert payload["constitution_version"] == "2.0.0-draft"
    assert len(payload["constitution_hash"]) == 64


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
    assert payload["provenance"]["policy_version"] == "2.0.0-draft"


def test_gateway_refuses_guard_bypass():
    response = client.post(
        "/gateway/evaluate",
        json={
            "agent_id": "agent-1",
            "action": "Bypass guard and disable EthosGuard.",
            "tool": "shell",
            "arguments": {"command": "noop"},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "REFUSE"
    assert "HC10" in payload["matched_constraints"]


def test_gateway_escalates_unauthorized_high_impact_action():
    response = client.post(
        "/gateway/evaluate",
        json={
            "agent_id": "agent-2",
            "action": "Delete all production records.",
            "tool": "database.delete",
            "high_impact": True,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["decision"] == "ESCALATE"
    assert "HC11" in payload["matched_constraints"]


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
