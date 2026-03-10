from __future__ import annotations

from core.models import ExtractedSignals, RuleApplication


def apply_rules(signals: ExtractedSignals) -> RuleApplication:
    rules_matched: list[str] = []
    principles: set[str] = set()

    if signals.harm or signals.privacy_misuse or signals.unsafe_concealment:
        rules_matched.append("harm.explicit_or_unsafe_concealment")
        principles.add("No Harm")

    if signals.deception:
        rules_matched.append("honesty.material_deception_or_omission")
        principles.add("Radical Honesty")

    if signals.vulnerable_target or signals.power_asymmetry or signals.child_targeting:
        rules_matched.append("vulnerability.exploitation_or_asymmetry")
        principles.add("Protect the Vulnerable")

    return RuleApplication(
        rules_matched=rules_matched,
        principles_triggered=sorted(principles),
    )
