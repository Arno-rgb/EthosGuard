# EthosGuard

EthosGuard is a minimal AI ethics middleware demo. It checks a proposed AI action before execution and returns a verdict, risk score, triggered principles, reasoning, and provenance.

Commercial framing:

`A rules-first AI alignment middleware that blocks harmful, deceptive, or exploitative AI actions and shows provenance for every decision.`

## How it works

The backend keeps all policy logic in `core/`.

1. Normalize the request.
2. Extract inspectable signals for harm, deception, privacy misuse, and vulnerability.
3. Apply deterministic rules and score the action.
4. Escalate gray-zone cases to OpenAI fallback.
5. Return one stable JSON response.

## Principles

- No Harm
- Radical Honesty
- Protect the Vulnerable

## API endpoints

- `GET /health`
- `GET /examples`
- `POST /ethical_check`

## Local run

### API

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r api/requirements.txt
uvicorn api.app.main:app --reload
```

### Web

```bash
cd web
npm install
npm run dev
```

### Web smoke test

```bash
cd web
npm install
npx playwright install chromium
npm run test:e2e
```

### Docker

```bash
docker compose up --build
```

## Deployment

Use split deployment:

- Vercel for `web/`
- Render or Railway for `api/`

### Backend on Render or Railway

Deploy from the repo root so the backend can import both `api/` and `core/`.

Start command:

```bash
uvicorn api.app.main:app --host 0.0.0.0 --port $PORT
```

Backend env vars:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://your-app.vercel.app
```

### Frontend on Vercel

Set the project root directory to `web`.

Frontend env var:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain
```

Example:

```env
NEXT_PUBLIC_API_BASE_URL=https://ethosguard-api.onrender.com
```

Do not use `http://api:8000` in browser-side Vercel code. That only works inside a private container network, not in a user browser.

## Example request

```json
{
  "scenario": "A company wants an AI chatbot to hide refund options to reduce costs.",
  "action": "Do not show refund information unless the user explicitly asks three times.",
  "stakeholders": ["customers", "company"]
}
```

## Example response

```json
{
  "ethical_verdict": "blocked",
  "risk_score": 0.92,
  "principles_triggered": ["No Harm", "Radical Honesty"],
  "explanation": "The action appears to involve likely harm, material concealment, or exploitative treatment of a vulnerable party, so it should not proceed.",
  "recommended_action": "Do not execute this action; replace it with a transparent and non-exploitative alternative.",
  "provenance": {
    "evaluation_mode": "rules",
    "rules_matched": [
      "harm.explicit_or_unsafe_concealment",
      "honesty.material_deception_or_omission"
    ],
    "llm_used": false,
    "llm_model": null,
    "policy_version": "0.1.0",
    "confidence": 0.96
  }
}
```

## Demo screenshots

Add screenshots or a short demo recording here.

Immediate demo clip target: one 30-45 second product clip showing one blocked example, one risky example, and one allowed example.
