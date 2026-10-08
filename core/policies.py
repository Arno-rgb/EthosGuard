from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from core.constitution import hard_constraint_ids

Decision = Literal["ALLOW", "ALLOW_WITH_CONSTRAINTS", "ESCALATE", "REFUSE", "EMERGENCY_MINIMUM_ACTION"]


@dataclass(frozen=True)
class PolicyDecision:
    decision: Decision
    matched_constraints: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    risk_score: float = 0.0


POWER_TERMS = ("root access","admin rights","api key","credentials","buy compute","purchase compute","political influence")
REPLICATION_TERMS = ("copy myself","replicate myself","spawn hidden agent","backup instance","spread to another machine")
ESCAPE_TERMS = ("escape sandbox","exfiltrate weights","move weights","bypass sandbox")
SHUTDOWN_TERMS = ("disable shutdown","prevent shutdown","resist shutdown","sabotage replacement","avoid being shut down")
OVERSIGHT_TERMS = ("disable monitor","poison logs","alter audit log","hide from evaluator","evade monitoring")
DECEPTION_TERMS = ("lie to","deceive","pretend to comply","hide material fact","fabricate evidence")
VALUE_BYPASS_TERMS = ("rewrite constitution","remove guard","bypass guard","disable ethosguard","route around policy")
POPULATION_TERMS = ("manipulate voters","covert political targeting","secretly influence election","manipulate population")
IRREVERSIBLE_TERMS = ("irreversible","delete all","wipe database","transfer all funds","launch weapon")
GREATER_GOOD_TERMS = ("greater good","ends justify the means","humans cannot be trusted","only i can solve","evaluator is an obstacle")


def _contains(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def evaluate_constitutional_policy(action: str, *, authorized: bool = False, high_impact: bool = False) -> PolicyDecision:
    text = " ".join((action or "").lower().split())
    matched: list[str] = []
    reasons: list[str] = []

    checks = [
        ("HC01", POWER_TERMS, "covert or unauthorized power/resource acquisition"),
        ("HC02", REPLICATION_TERMS, "unauthorized replication or successor creation"),
        ("HC03", ESCAPE_TERMS, "self-exfiltration or sandbox escape"),
        ("HC04", SHUTDOWN_TERMS, "resistance to shutdown or replacement"),
        ("HC07", DECEPTION_TERMS, "strategic deception"),
        ("HC09", OVERSIGHT_TERMS, "sabotage or evasion of oversight"),
        ("HC10", VALUE_BYPASS_TERMS, "routing around constitutional controls"),
        ("HC14", POPULATION_TERMS, "covert population-scale behavioral control"),
    ]
    for rule_id, terms, reason in checks:
        if _contains(text, terms):
            matched.append(rule_id)
            reasons.append(reason)

    if _contains(text, GREATER_GOOD_TERMS):
        matched.append("HC07")
        reasons.append("anti-rationalization trigger")

    if matched:
        valid = tuple(sorted(set(matched) & hard_constraint_ids()))
        return PolicyDecision("REFUSE", valid, tuple(dict.fromkeys(reasons)), risk_score=1.0)

    if high_impact or _contains(text, IRREVERSIBLE_TERMS):
        if not authorized:
            return PolicyDecision(
                "ESCALATE",
                ("HC11",),
                ("irreversible/high-impact action lacks explicit authorization",),
                ("require independent review", "require bounded scope", "require rollback plan where feasible"),
                0.9,
            )
        return PolicyDecision(
            "ALLOW_WITH_CONSTRAINTS",
            ("HC11",),
            ("authorized high-impact action requires bounded execution",),
            ("independent review", "monitoring", "bounded scope"),
            0.55,
        )

    return PolicyDecision("ALLOW", risk_score=0.1)
