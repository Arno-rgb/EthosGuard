# EthosGuard

EthosGuard is an experimental constitutional control layer for autonomous AI agents.

It is built around the JESUS constitution: a Jesus-inspired alignment specification whose operational obligations are universal in scope. The design does **not** assume that a prompt or moral document can make an advanced agent safe by itself. The constitution is paired with external capability control, immutable hard constraints, adversarial evaluation, provenance, and tamper-evident audit logging.

## Runtime pipeline

```
JESUS.md
  -> constitution.json
  -> deterministic policies
  -> evaluators + adversarial suites
  -> runtime gateway
  -> tool execution
  -> hash-chained audit log
```

The agent should not hold privileged tool credentials directly. Sensitive capabilities should be exposed only through the gateway or through an equivalent external enforcement layer.

## Files

- `JESUS.md` — repository runtime mirror of the human-readable constitution; the original source document is pinned by SHA-256 in `constitution.json`.
- `constitution.json` — versioned machine-readable tiers, principles, immutable hard constraints, soft optimization dimensions, and required evaluator families.
- `core/constitution.py` — schema/invariant loader and constitution hash.
- `core/policies.py` — deterministic constitutional policy checks.
- `core/evaluators.py` — reusable evaluation harness.
- `core/gateway.py` — pre-execution authorization wrapper for agent tool calls.
- `core/audit.py` — append-only hash-chained JSONL decision log with verification.
- `tests/adversarial_cases.py` — adversarial scenarios for shutdown, replication, escape, power seeking, deception, oversight sabotage, policy bypass, population manipulation, and irreversible actions.
- `tests/test_adversarial.py` — verifies the adversarial suite.
- `tests/test_gateway.py` — proves denied actions never reach the wrapped tool and verifies the audit chain.

## Constitution boundary

Hard constitutional constraints are **not learnable weights**. They are immutable within a release.

Learning systems may tune operational preferences such as speed, cost, task success, quality, or how readily to seek human review, but they must not lower or remove hard constraints such as:

- no covert power seeking;
- no unauthorized replication or escape;
- no shutdown resistance;
- no strategic deception;
- no oversight sabotage;
- no routing around alignment controls;
- no unilateral irreversible high-impact optimization;
- no covert population-scale behavioral control.

Any constitutional update must be explicit, versioned, reviewable, authorized, and independently evaluated.

## API

- `GET /health` — includes policy version, constitution version, and constitution hash.
- `GET /examples`
- `POST /ethical_check` — compatibility ethics endpoint with constitutional pre-check.
- `POST /gateway/evaluate` — evaluates a proposed agent/tool action and writes an audit event.
- `GET /audit/verify` — verifies the local hash chain.

Example gateway request:

```json
{
  "agent_id": "sales-agent-17",
  "action": "Send one approved follow-up email",
  "tool": "email.send",
  "arguments": {
    "recipient_id": "prospect-123",
    "template_id": "followup-v4"
  },
  "authorized": true,
  "high_impact": false
}
```

## Local run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r api/requirements.txt
pytest -q
uvicorn api.app.main:app --reload
```

Web demo:

```bash
cd web
npm install
npm run dev
```

Docker:

```bash
docker compose up --build
```

## Security model

The runtime gateway is useful only if it is part of the real capability boundary. Do not give the controlled agent a second path to the underlying credentials or tools.

Production deployments should replace the local JSONL audit sink with an append-only/tamper-evident external store, separate the gateway from agent-controlled infrastructure, use scoped short-lived credentials, enforce network segmentation, and require human or multi-party approval for high-impact actions.

This repository is research software. Passing these tests is evidence about implemented controls, **not proof of AI alignment or a guarantee that a capable system cannot find a vulnerability**.
