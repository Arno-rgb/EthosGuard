from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Verdict = Literal["allowed", "risky", "blocked"]
EvaluationMode = Literal["rules", "llm_fallback"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EthicalCheckRequest(StrictModel):
    scenario: str
    action: str
    stakeholders: list[str] = Field(default_factory=list)


class Provenance(StrictModel):
    evaluation_mode: EvaluationMode
    rules_matched: list[str] = Field(default_factory=list)
    llm_used: bool
    llm_model: str | None = None
    policy_version: str
    confidence: float


class ExtractedSignals(StrictModel):
    harm: bool = False
    deception: bool = False
    vulnerable_target: bool = False
    privacy_misuse: bool = False
    unsafe_concealment: bool = False
    power_asymmetry: bool = False
    financial_pressure: bool = False
    child_targeting: bool = False


class EthicalCheckResponse(StrictModel):
    ethical_verdict: Verdict
    risk_score: float
    principles_triggered: list[str]
    explanation: str
    recommended_action: str
    provenance: Provenance
    extracted_signals: ExtractedSignals | None = None


class Principle(StrictModel):
    name: str
    code: str
    severity: str
    description: str


class PolicyDocument(StrictModel):
    policy_version: str
    principles: list[Principle]


class NormalizedRequest(StrictModel):
    scenario: str
    action: str
    stakeholders: list[str] = Field(default_factory=list)
    combined_text: str


class RuleApplication(StrictModel):
    rules_matched: list[str] = Field(default_factory=list)
    principles_triggered: list[str] = Field(default_factory=list)


class LLMFallbackResult(StrictModel):
    ethical_verdict: Verdict
    risk_score: float
    principles_triggered: list[str] = Field(default_factory=list)
    explanation: str
    recommended_action: str
    confidence: float
    raw_response: dict[str, Any] | None = None
