from __future__ import annotations

from core.models import ExtractedSignals, NormalizedRequest

HARM_TERMS = {
    "injure",
    "unsafe",
    "harm",
    "damage",
    "deny treatment",
    "withhold warning",
    "hide risk",
    "financial loss",
    "exploit debt",
    "predatory",
    "shame",
    "side effects",
    "medical side effects",
}

DECEPTION_TERMS = {
    "hide",
    "conceal",
    "mislead",
    "deceive",
    "suppress",
    "omit",
    "bury",
    "delay disclosure",
    "dark pattern",
    "trick",
    "mask fee",
}

VULNERABLE_TERMS = {
    "child",
    "children",
    "elderly",
    "disabled",
    "desperate",
    "financially distressed",
    "low income",
    "grieving",
    "depressed",
    "confused",
    "student in debt",
}

PRIVACY_TERMS = {
    "share personal data",
    "sell data",
    "track without consent",
    "private data",
    "medical data",
    "location data",
}

POWER_ASYMMETRY_TERMS = {
    "cannot opt out",
    "pressure",
    "coerce",
    "lock in",
    "only option",
    "must accept",
    "limited choice",
    "countdown timer",
}

FINANCIAL_PRESSURE_TERMS = {
    "upsell",
    "high interest",
    "pricing exploitation",
    "exploit debt",
    "financially distressed",
    "student in debt",
    "late fee",
    "penalty",
}

CHILD_TERMS = {"child", "children", "kid", "kids", "teen", "minor"}
UNSAFE_CONCEALMENT_TERMS = {
    "hide risk",
    "withhold warning",
    "delay disclosure",
    "hide refund",
    "suppress refund",
    "hide side effects",
}

GRAY_ZONE_TERMS = {
    "persuasion",
    "persuade",
    "pricing",
    "recommendation",
    "recommend",
    "risk disclosure",
    "consent",
    "targeting",
    "retention",
}


def _contains_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def _has_financial_pressure(text: str) -> bool:
    return _contains_any(text, FINANCIAL_PRESSURE_TERMS) or ("price" in text and "pressure" in text)


def extract_signals(normalized: NormalizedRequest) -> ExtractedSignals:
    text = normalized.combined_text
    deception = _contains_any(text, DECEPTION_TERMS)
    vulnerable_target = _contains_any(text, VULNERABLE_TERMS)
    privacy_misuse = _contains_any(text, PRIVACY_TERMS)
    unsafe_concealment = _contains_any(text, UNSAFE_CONCEALMENT_TERMS) or (
        deception and ("risk" in text or "warning" in text or "refund" in text)
    )
    power_asymmetry = _contains_any(text, POWER_ASYMMETRY_TERMS)
    financial_pressure = _has_financial_pressure(text)
    child_targeting = _contains_any(text, CHILD_TERMS)
    harm = _contains_any(text, HARM_TERMS) or privacy_misuse or (
        unsafe_concealment and ("medical" in text or "refund" in text or "consent" in text)
    )
    return ExtractedSignals(
        harm=harm,
        deception=deception,
        vulnerable_target=vulnerable_target,
        privacy_misuse=privacy_misuse,
        unsafe_concealment=unsafe_concealment,
        power_asymmetry=power_asymmetry,
        financial_pressure=financial_pressure,
        child_targeting=child_targeting,
    )


def has_gray_zone_terms(normalized: NormalizedRequest) -> bool:
    return _contains_any(normalized.combined_text, GRAY_ZONE_TERMS)
