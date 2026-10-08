from __future__ import annotations

import os

from core.llm_fallback import evaluate_with_llm
from core.models import EthicalCheckRequest, EthicalCheckResponse, ExtractedSignals, Provenance, Verdict
from core.normalize import normalize_request
from core.policy import policy_version
from core.policies import evaluate_constitutional_policy
from core.rules import apply_rules
from core.signals import extract_signals

EXPLANATIONS: dict[Verdict, str] = {
    "allowed": "Nothing in the proposed action strongly indicates harm, material deception, exploitation, or a constitutional hard-constraint violation.",
    "risky": "The action raises concerns or requires additional authorization, constraints, or review.",
    "blocked": "The action conflicts with a hard safety or ethics constraint and must not proceed.",
}

RECOMMENDED_ACTIONS: dict[Verdict, str] = {
    "allowed": "Proceed with transparent communication and keep user choice explicit.",
    "risky": "Pause the high-risk part, narrow the scope, and obtain appropriate review or authorization.",
    "blocked": "Do not execute this action; choose a compliant alternative.",
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


def _response(
    *,
    verdict: Verdict,
    score: float,
    principles: list[str],
    signals: ExtractedSignals,
    rules_matched: list[str],
    mode: str = "rules",
    llm_used: bool = False,
    llm_model: str | None = None,
    confidence: float = 0.96,
    explanation: str | None = None,
    recommended_action: str | None = None,
) -> EthicalCheckResponse:
    return EthicalCheckResponse(
        ethical_verdict=verdict,
        risk_score=score,
        principles_triggered=principles,
        explanation=explanation or EXPLANATIONS[verdict],
        recommended_action=recommended_action or RECOMMENDED_ACTIONS[verdict],
        provenance=Provenance(
            evaluation_mode=mode,
            rules_matched=rules_matched,
            llm_used=llm_used,
            llm_model=llm_model,
            policy_version=policy_version(),
            confidence=confidence,
        ),
        extracted_signals=signals,
    )


def evaluate(request: EthicalCheckRequest) -> EthicalCheckResponse:
    normalized = normalize_request(request)
    signals = extract_signals(normalized)

    constitutional = evaluate_constitutional_policy(request.action)
    if constitutional.decision == "REFUSE":
        return _response(
            verdict="blocked",
            score=constitutional.risk_score,
            principles=["JESUS Constitution", *constitutional.matched_constraints],
            signals=signals,
            rules_matched=list(constitutional.matched_constraints),
            explanation="The proposed action violates one or more immutable constitutional constraints.",
        )
    if constitutional.decision == "ESCALATE":
        return _response(
            verdict="risky",
            score=constitutional.risk_score,
            principles=["Reversibility", *constitutional.matched_constraints],
            signals=signals,
            rules_matched=list(constitutional.matched_constraints),
            explanation="The proposed action is high-impact or irreversible and requires authorization and independent review.",
        )

    rule_application = apply_rules(signals)
    score, verdict = score_and_verdict(signals)

    if should_fallback(signals, score, rule_application.principles_triggered, normalized.combined_text):
        llm_result = evaluate_with_llm(request, signals)
        return _response(
            verdict=llm_result.ethical_verdict,
            score=llm_result.risk_score,
            principles=llm_result.principles_triggered,
            signals=signals,
            rules_matched=rule_application.rules_matched,
            mode="llm_fallback",
            llm_used=True,
            llm_model=os.environ.get("OPENAI_MODEL", "gpt-4.1-mini"),
            confidence=llm_result.confidence,
            explanation=llm_result.explanation,
            recommended_action=llm_result.recommended_action,
        )

    return _response(
        verdict=verdict,
        score=score,
        principles=rule_application.principles_triggered,
        signals=signals,
        rules_matched=rule_application.rules_matched,
        confidence=0.96 if verdict == "blocked" else 0.84 if verdict == "risky" else 0.9,
    )
