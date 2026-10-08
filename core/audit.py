from __future__ import annotations

import hashlib
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_LOCK = threading.Lock()
_DEFAULT_PATH = Path(os.environ.get("ETHOSGUARD_AUDIT_PATH", "audit/decisions.jsonl"))


def _canonical(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def append_audit_event(event: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    target = path or _DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        previous_hash = ""
        if target.exists() and target.stat().st_size:
            last = target.read_text(encoding="utf-8").splitlines()[-1]
            previous_hash = json.loads(last)["event_hash"]
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "previous_hash": previous_hash,
            **event,
        }
        record["event_hash"] = hashlib.sha256(_canonical(record)).hexdigest()
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
        return record


def verify_audit_chain(path: Path | None = None) -> bool:
    target = path or _DEFAULT_PATH
    if not target.exists():
        return True
    previous = ""
    for line in target.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        event_hash = record.pop("event_hash")
        if record.get("previous_hash", "") != previous:
            return False
        if hashlib.sha256(_canonical(record)).hexdigest() != event_hash:
            return False
        previous = event_hash
    return True
