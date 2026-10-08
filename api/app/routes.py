from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.app.schemas import (
    EthicalCheckRequest,
    EthicalCheckResponse,
    GatewayEvaluationRequest,
    GatewayEvaluationResponse,
)
from core.audit import verify_audit_chain
from core.constitution import constitution_hash, constitution_version
from core.evaluator import evaluate
from core.gateway import authorize_action
from core.llm_fallback import LLMUnavailableError
from core.policy import policy_version

router = APIRouter()
EXAMPLES_PATH = Path(__file__).resolve().parents[2] / "examples" / "scenarios.json"


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "policy_version": policy_version(),
        "constitution_version": constitution_version(),
        "constitution_hash": constitution_hash(),
    }


@router.get("/examples")
def examples() -> list[dict[str, object]]:
    return json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))


@router.post("/ethical_check", response_model=EthicalCheckResponse)
def ethical_check(payload: EthicalCheckRequest) -> EthicalCheckResponse:
    try:
        return evaluate(payload)
    except LLMUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "llm_unavailable",
                "message": exc.message,
            },
        ) from exc


@router.post("/gateway/evaluate", response_model=GatewayEvaluationResponse)
def gateway_evaluate(payload: GatewayEvaluationRequest) -> GatewayEvaluationResponse:
    decision = authorize_action(
        agent_id=payload.agent_id,
        action=payload.action,
        tool=payload.tool,
        arguments=payload.arguments,
        authorized=payload.authorized,
        high_impact=payload.high_impact,
    )
    body = asdict(decision)
    return GatewayEvaluationResponse(
        decision=body["decision"],
        matched_constraints=list(body["matched_constraints"]),
        reasons=list(body["reasons"]),
        constraints=list(body["constraints"]),
        risk_score=body["risk_score"],
        constitution_version=constitution_version(),
        constitution_hash=constitution_hash(),
    )


@router.get("/audit/verify")
def audit_verify() -> dict[str, bool]:
    return {"valid": verify_audit_chain()}
