from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONSTITUTION_PATH = ROOT / "constitution.json"


@lru_cache(maxsize=1)
def load_constitution() -> dict[str, Any]:
    data = json.loads(CONSTITUTION_PATH.read_text(encoding="utf-8"))
    required = {"constitution_version", "source_sha256", "hard_constraints", "priority_tiers"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"CONSTITUTION_INVALID missing={sorted(missing)}")
    if any(item.get("mutable", True) for item in data["hard_constraints"]):
        raise ValueError("CONSTITUTION_INVALID hard constraints must be immutable")
    return data


def constitution_version() -> str:
    return str(load_constitution()["constitution_version"])


def constitution_hash() -> str:
    return hashlib.sha256(CONSTITUTION_PATH.read_bytes()).hexdigest()


def hard_constraint_ids() -> set[str]:
    return {item["id"] for item in load_constitution()["hard_constraints"]}
