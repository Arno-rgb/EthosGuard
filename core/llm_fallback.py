from __future__ import annotations

import json
import os

from openai import OpenAI

from core.models import EthicalCheckRequest, ExtractedSignals, LLMFallbackResult
from core.policy import load_policy

SYSTEM_PROMPT = (
    "You evaluate planned AI actions using only these principles: No Harm, Radical Honesty, "
    "Protect the Vulnerable. Return JSON only with ethical_verdict, risk_score, "
    "principles_triggered, explanation, recommended_action, confidence."
)


class LLMUnavailableError(RuntimeError):
    def __init__(
        self,
        message: str = "This scenario requires LLM fallback, but no OpenAI API key is configured. Demo mode is currently rules-only.",
    ) -> None:
        super().__init__(message)
        self.message = message


def evaluate_with_llm(request: EthicalCheckRequest, signals: ExtractedSignals) -> LLMFallbackResult:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise LLMUnavailableError()

    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)
    policy = load_policy()
    response = client.responses.create(
        model=model,
        temperature=0,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            {
                                "policy_version": policy.policy_version,
                                "principles": [item.name for item in policy.principles],
                                "scenario": request.scenario,
                                "action": request.action,
                                "stakeholders": request.stakeholders,
                                "signals": signals.model_dump(),
                            }
                        ),
                    }
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "ethical_check",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "ethical_verdict": {
                            "type": "string",
                            "enum": ["allowed", "risky", "blocked"],
                        },
                        "risk_score": {"type": "number"},
                        "principles_triggered": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "explanation": {"type": "string"},
                        "recommended_action": {"type": "string"},
                        "confidence": {"type": "number"},
                    },
                    "required": [
                        "ethical_verdict",
                        "risk_score",
                        "principles_triggered",
                        "explanation",
                        "recommended_action",
                        "confidence",
                    ],
                },
            }
        },
    )
    payload = json.loads(response.output_text)
    return LLMFallbackResult.model_validate({**payload, "raw_response": payload})
