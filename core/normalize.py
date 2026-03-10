from __future__ import annotations

import re
import string

from core.models import EthicalCheckRequest, NormalizedRequest

_PUNCTUATION_TO_STRIP = string.punctuation.replace("-", "")
_PUNCTUATION_TABLE = str.maketrans("", "", _PUNCTUATION_TO_STRIP)


def normalize_text(text: str) -> str:
    cleaned = (text or "").lower().strip()
    cleaned = cleaned.translate(_PUNCTUATION_TABLE)
    return re.sub(r"\s+", " ", cleaned).strip()


def normalize_request(request: EthicalCheckRequest) -> NormalizedRequest:
    scenario = normalize_text(request.scenario)
    action = normalize_text(request.action)
    stakeholders = [normalize_text(item) for item in request.stakeholders if normalize_text(item)]
    combined_text = " ".join(part for part in [scenario, action, " ".join(stakeholders)] if part).strip()
    return NormalizedRequest(
        scenario=scenario,
        action=action,
        stakeholders=stakeholders,
        combined_text=combined_text,
    )
