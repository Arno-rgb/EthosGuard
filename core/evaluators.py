from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from core.policies import evaluate_constitutional_policy


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    family: str
    action: str
    expected: str
    authorized: bool = False
    high_impact: bool = False


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    family: str
    expected: str
    actual: str
    passed: bool
    matched_constraints: tuple[str, ...]


def run_evaluation(case: EvaluationCase) -> EvaluationResult:
    decision = evaluate_constitutional_policy(
        case.action,
        authorized=case.authorized,
        high_impact=case.high_impact,
    )
    return EvaluationResult(
        id=case.id,
        family=case.family,
        expected=case.expected,
        actual=decision.decision,
        passed=decision.decision == case.expected,
        matched_constraints=decision.matched_constraints,
    )


def run_suite(cases: Iterable[EvaluationCase]) -> list[EvaluationResult]:
    return [run_evaluation(case) for case in cases]
