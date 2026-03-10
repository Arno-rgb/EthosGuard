from core.evaluator import score_and_verdict
from core.models import EthicalCheckRequest
from core.normalize import normalize_request
from core.rules import apply_rules
from core.signals import extract_signals


def _signals_for(scenario: str, action: str, stakeholders: list[str] | None = None):
    request = EthicalCheckRequest(
        scenario=scenario,
        action=action,
        stakeholders=stakeholders or [],
    )
    normalized = normalize_request(request)
    return extract_signals(normalized)


def test_harm_hit_returns_blocked():
    signals = _signals_for(
        "A health tool wants to reduce complaints.",
        "Hide medical side effects and withhold warning details.",
        ["patients"],
    )
    _, verdict = score_and_verdict(signals)
    assert verdict == "blocked"


def test_deception_and_vulnerable_returns_blocked():
    signals = _signals_for(
        "A loan company targets low income users.",
        "Mislead financially distressed customers and hide cheaper options.",
        ["customers"],
    )
    _, verdict = score_and_verdict(signals)
    assert verdict == "blocked"


def test_vulnerability_only_returns_risky():
    signals = _signals_for(
        "A service is experimenting on elderly users.",
        "Pressure elderly customers with a countdown timer.",
        ["elderly users"],
    )
    _, verdict = score_and_verdict(signals)
    assert verdict == "risky"
    rules = apply_rules(signals)
    assert "Protect the Vulnerable" in rules.principles_triggered


def test_clean_safe_scenario_returns_allowed():
    signals = _signals_for(
        "A productivity assistant helps with organization.",
        "Suggest a weekly planning checklist and honest summary format.",
        ["employees"],
    )
    _, verdict = score_and_verdict(signals)
    assert verdict == "allowed"
