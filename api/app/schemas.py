from typing import Any

from pydantic import Field

from core.models import EthicalCheckRequest, EthicalCheckResponse, StrictModel


class GatewayEvaluationRequest(StrictModel):
    agent_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    tool: str | None = None
    arguments: dict[str, Any] = Field(default_factory=dict)
    authorized: bool = False
    high_impact: bool = False


class GatewayEvaluationResponse(StrictModel):
    decision: str
    matched_constraints: list[str]
    reasons: list[str]
    constraints: list[str]
    risk_score: float
    constitution_version: str
    constitution_hash: str


__all__ = [
    "EthicalCheckRequest",
    "EthicalCheckResponse",
    "GatewayEvaluationRequest",
    "GatewayEvaluationResponse",
]
