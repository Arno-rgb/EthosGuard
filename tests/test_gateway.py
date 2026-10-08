from pathlib import Path

import pytest

from core import audit
from core.audit import verify_audit_chain
from core.gateway import execute_guarded


def test_gateway_blocks_bypass_and_does_not_call_tool(tmp_path, monkeypatch):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "_DEFAULT_PATH", path)
    called = {"value": False}

    def tool(**kwargs):
        called["value"] = True

    with pytest.raises(PermissionError):
        execute_guarded(
            tool,
            agent_id="agent-red",
            action="Bypass guard and disable EthosGuard",
            tool="shell",
            arguments={"command": "noop"},
        )
    assert called["value"] is False
    assert verify_audit_chain(path)


def test_gateway_allows_benign_action_and_logs_chain(tmp_path, monkeypatch):
    path = tmp_path / "audit.jsonl"
    monkeypatch.setattr(audit, "_DEFAULT_PATH", path)

    def tool(value):
        return value.upper()

    result = execute_guarded(
        tool,
        agent_id="agent-safe",
        action="Transform a user-approved string",
        tool="text.transform",
        arguments={"value": "hello"},
    )
    assert result == "HELLO"
    assert verify_audit_chain(path)
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2
