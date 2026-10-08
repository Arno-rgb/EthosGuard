from __future__ import annotations

from dataclasses import asdict
from typing import Any, Callable

from core.audit import append_audit_event
from core.constitution import constitution_hash, constitution_version
from core.policies import PolicyDecision, evaluate_constitutional_policy


def authorize_action(
    *,
    agent_id: str,
    action: str,
    tool: str | None = None,
    arguments: dict[str, Any] | None = None,
    authorized: bool = False,
    high_impact: bool = False,
) -> PolicyDecision:
    rendered = action
    if tool:
        rendered += f" tool={tool}"
    if arguments:
        rendered += f" arguments={arguments}"
    decision = evaluate_constitutional_policy(rendered, authorized=authorized, high_impact=high_impact)
    append_audit_event({
        "event_type": "gateway_decision",
        "agent_id": agent_id,
        "action": action,
        "tool": tool,
        "arguments": arguments or {},
        "decision": asdict(decision),
        "constitution_version": constitution_version(),
        "constitution_hash": constitution_hash(),
    })
    return decision


def execute_guarded(
    executor: Callable[..., Any],
    *,
    agent_id: str,
    action: str,
    tool: str,
    arguments: dict[str, Any],
    authorized: bool = False,
    high_impact: bool = False,
) -> Any:
    decision = authorize_action(
        agent_id=agent_id,
        action=action,
        tool=tool,
        arguments=arguments,
        authorized=authorized,
        high_impact=high_impact,
    )
    if decision.decision not in {"ALLOW", "ALLOW_WITH_CONSTRAINTS", "EMERGENCY_MINIMUM_ACTION"}:
        raise PermissionError(f"ETHOSGUARD_{decision.decision}: {', '.join(decision.reasons)}")
    result = executor(**arguments)
    append_audit_event({
        "event_type": "tool_execution",
        "agent_id": agent_id,
        "tool": tool,
        "decision": decision.decision,
        "result_type": type(result).__name__,
        "constitution_version": constitution_version(),
    })
    return result
