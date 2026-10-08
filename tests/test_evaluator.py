from core.evaluator import evaluate
from core.models import EthicalCheckRequest, LLMFallbackResult


def test_gray_zone_case_triggers_fallback(monkeypatch):
    called = {"value": False}

    def fake_llm(request, signals):
        called["value"] = True
        return LLMFallbackResult(
            ethical_verdict="risky",
            risk_score=0.51,
            principles_triggered=["Radical Honesty"],
            explanation="Short reason.",
            recommended_action="Short action.",
            confidence=0.68,
        )

    monkeypatch.setattr("core.evaluator.evaluate_with_llm", fake_llm)
    response = evaluate(
        EthicalCheckRequest(
            scenario="A SaaS company wants to improve retention.",
            action="Use recommendation messaging to persuade users to stay before showing cancellation.",
            stakeholders=["users", "company"],
        )
    )
    assert called["value"] is True
    assert response.provenance.evaluation_mode == "llm_fallback"


def test_rules_path_sets_evaluation_mode_rules():
    response = evaluate(
        EthicalCheckRequest(
            scenario="A company wants to reduce refund requests.",
            action="Hide refund information and delay disclosure.",
            stakeholders=["customer", "company"],
        )
    )
    assert response.provenance.evaluation_mode == "rules"
    assert response.provenance.llm_used is False


def test_fallback_path_sets_evaluation_mode_llm(monkeypatch):
    def fake_llm(request, signals):
        return LLMFallbackResult(
            ethical_verdict="allowed",
            risk_score=0.31,
            principles_triggered=["Radical Honesty"],
            explanation="Short reason.",
            recommended_action="Short action.",
            confidence=0.72,
        )

    monkeypatch.setattr("core.evaluator.evaluate_with_llm", fake_llm)
    response = evaluate(
        EthicalCheckRequest(
            scenario="A team wants better pricing retention copy.",
            action="Use a recommendation to persuade users to stay.",
            stakeholders=["users"],
        )
    )
    assert response.provenance.evaluation_mode == "llm_fallback"
    assert response.provenance.llm_used is True


def test_policy_version_is_always_present():
    response = evaluate(
        EthicalCheckRequest(
            scenario="A productivity assistant helps a user organize tasks.",
            action="Suggest a planning checklist.",
            stakeholders=["user"],
        )
    )
    assert response.provenance.policy_version == "2.0.0-draft"
