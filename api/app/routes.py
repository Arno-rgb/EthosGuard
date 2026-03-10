from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from api.app.schemas import EthicalCheckRequest, EthicalCheckResponse
from core.evaluator import evaluate
from core.llm_fallback import LLMUnavailableError
from core.policy import policy_version

router = APIRouter()
EXAMPLES_PATH = Path(__file__).resolve().parents[2] / "examples" / "scenarios.json"


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "policy_version": policy_version()}


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
