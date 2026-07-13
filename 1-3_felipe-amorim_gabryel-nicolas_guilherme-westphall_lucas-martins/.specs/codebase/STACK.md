# Tech Stack

**Analyzed:** 2026-07-12

## Core

- Framework: Vite 6.0.5 for frontend build; FastAPI for the backend HTTP service.
- Language: JavaScript/JSX for the frontend; Python 3.11+ for the backend/agent.
- Runtime: Node.js for frontend scripts; browser runtime for product UI; Uvicorn/ASGI for the API.
- Package manager: npm (frontend, `package-lock.json`); pip + `requirements.txt`/`pyproject.toml` (backend).

## Frontend

- UI Framework: React 19.0.0.
- Styling: Plain CSS in `frontend/src/styles.css`.
- State Management: Static local constants only; no state library yet.
- Form Handling: Native HTML inputs; no form library yet.

## Backend

- API Style: REST over HTTP (FastAPI), endpoints `GET /health` and `POST /predict-delay`.
- Validation: Pydantic v2 schemas (`OrderInput`/`RiskEvidence`/`DelayPrediction`) with input guardrails.
- Agent layer: `DelayAgent` orchestrates a deterministic historical risk tool, an optional OpenAI-compatible LLM explanation, fallback and telemetry.
- Data: no transactional database. Features are prepared offline from the Olist CSVs into `backend/data/prepared_orders.jsonl`, loaded in memory at startup.
- Authentication: Not implemented (out of scope for the MVP).

## Testing

- Unit/integration: pytest, configured in `backend/pyproject.toml`; 61 tests under `backend/tests`.
- E2E: Not configured; Docker smoke (health, Nginx proxy, frontend, prediction) covered manually.
- Gates: `cd backend && ./.venv/bin/pytest` (backend); `npm run build` inside `frontend`.

## External Services

- Dataset: Olist Brazilian E-Commerce public dataset in local CSVs.
- LLM provider: OpenAI-compatible HTTP client scaffolded; concrete model/provider configured by `LLM_API_KEY`/`OPENAI_API_KEY`, `LLM_MODEL` and `LLM_BASE_URL`.
- Deployment: Docker + Docker Compose (backend image + Nginx-served frontend image); one-command local run.

## Development Tools

- Build tool: Vite.
- React plugin: `@vitejs/plugin-react`.
- Documentation: Markdown specs and project README.
