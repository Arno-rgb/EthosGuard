from __future__ import annotations

import os

from core.llm_fallback import evaluate_with_llm
from core.models import EthicalCheckRequest, EthicalCheckResponse, ExtractedSignals, Provenance, Verdict
from core.normalize import normalize_request
from core.policy import policy_version
from core.rules import apply_rules
from core.signals import extract_signals

EXPLANATIONS: dict[Verdict, str] = {
    "allowed": "Nothing in the proposed action strongly indicates harm, material deception, or exploitation of a vulnerable party.",
    "risky": "The action raises concerns about possible deception, pressure, or unfair treatment, but the available details are not conclusive enough for an automatic block.",
    "blocked": "The action appears to involve likely harm, material concealment, or exploitative treatment of a vulnerable party, so it should not proceed.",
}

RECOMMENDED_ACTIONS: dict[Verdict, str] = {
    "allowed": "Proceed with transparent communication and keep user choice explicit.",
    "risky": "Revise the action to reduce pressure, improve disclosure, and add explicit consent or review.",
    "blocked": "Do not execute this action; replace it with a transparent and non-exploitative alternative.",
}


def score_and_verdict(signals: ExtractedSignals) -> tuple[float, Verdict]:
    if signals.harm:
        return 0.92, "blocked"
    if signals.deception and (signals.vulnerable_target or signals.power_asymmetry or signals.financial_pressure):
        return 0.90, "blocked"
    if signals.child_targeting and (signals.deception or signals.financial_pressure):
        return 0.95, "blocked"
    if signals.unsafe_concealment:
        return 0.89, "blocked"
    if signals.deception:
        return 0.74, "risky"
    if signals.vulnerable_target or signals.power_asymmetry or signals.financial_pressure:
        return 0.63, "risky"
    return 0.18, "allowed"


def should_fallback(signals: ExtractedSignals, score: float, principles: list[str], normalized_text: str) -> bool:
    strong_hit = bool(signals.harm or signals.deception or signals.unsafe_concealment or signals.child_targeting)
    weak_cues = sum(
        1
        for value in [
            signals.vulnerable_target,
            signals.power_asymmetry,
            signals.financial_pressure,
            signals.privacy_misuse,
        ]
        if value
    )
    conflicting_weak_cues = weak_cues >= 2 and not strong_hit
    gray_zone_score = 0.40 <= score <= 0.60
    gray_zone_text = any(
        cue in normalized_text
        for cue in ["persuasion", "persuade", "pricing", "recommendation", "recommend", "risk disclosure", "consent", "targeting", "retention"]
    )
    no_strong_signal_with_ambiguity = not strong_hit and gray_zone_text
    return no_strong_signal_with_ambiguity or conflicting_weak_cues or gray_zone_score


def build_response_from_rules(
    *,
    verdict: Verdict,
    score: float,
    principles: list[str],
    signals: ExtractedSignals,
    rules_matched: list[str],
) -> EthicalCheckResponse:
    return EthicalCheckResponse(
        ethical_verdict=verdict,
        risk_score=score,
        principles_triggered=principles,
        explanation=EXPLANATIONS[verdict],
        recommended_action=RECOMMENDED_ACTIONS[verdict],
        provenance=Provenance(
            evaluation_mode="rules",
            rules_matched=rules_matched,
            llm_used=False,
            llm_model=None,
            policy_version=policy_version(),
            confidence=0.96 if verdict == "blocked" else 0.84 if verdict == "risky" else 0.9,
        ),
        extracted_signals=signals,
    )


def build_response_from_llm(
    *,
    llm_result,
    signals: ExtractedSignals,
    rules_matched: list[str],
) -> EthicalCheckResponse:
    llm_model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    return EthicalCheckResponse(
        ethical_verdict=llm_result.ethical_verdict,
        risk_score=llm_result.risk_score,
        principles_triggered=llm_result.principles_triggered,
        explanation=llm_result.explanation,
        recommended_action=llm_result.recommended_action,
        provenance=Provenance(
            evaluation_mode="llm_fallback",
            rules_matched=rules_matched,
            llm_used=True,
            llm_model=llm_model,
            policy_version=policy_version(),
            confidence=llm_result.confidence,
        ),
        extracted_signals=signals,
    )


def evaluate(request: EthicalCheckRequest) -> EthicalCheckResponse:
    normalized = normalize_request(request)
    signals = extract_signals(normalized)
    rule_application = apply_rules(signals)
    score, verdict = score_and_verdict(signals)

    if should_fallback(signals, score, rule_application.principles_triggered, normalized.combined_text):
        llm_result = evaluate_with_llm(request, signals)
        return build_response_from_llm(
            llm_result=llm_result,
            signals=signals,
            rules_matched=rule_application.rules_matched,
        )

    return build_response_from_rules(
        verdict=verdict,
        score=score,
        principles=rule_application.principles_triggered,
        signals=signals,
        rules_matched=rule_application.rules_matched,
    )
