from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from core.models import PolicyDocument

POLICY_PATH = Path(__file__).with_name("principles.json")


@lru_cache(maxsize=1)
def load_policy() -> PolicyDocument:
    data = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    return PolicyDocument.model_validate(data)


def policy_version() -> str:
    return load_policy().policy_version
