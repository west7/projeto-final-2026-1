# Tech Stack

**Analyzed:** 2026-07-13

## Core

- Frontend: React 19 with Vite 6, JavaScript/JSX and npm (`package-lock.json`).
- Backend: Python 3.12, FastAPI, Pydantic v2 and Uvicorn.
- Packaging: Docker multi-stage builds, Docker Compose locally and Render Blueprint in production.

## Frontend

- UI: operational delay-risk dashboard in `frontend/src/App.jsx`.
- Styling: global plain CSS in `frontend/src/styles.css`.
- State: React `useState`, `useMemo` and `useEffect`; no external state library.
- API client: native `fetch` wrapper in `frontend/src/api.js` with cold-start polling.
- Production delivery: Render Static Site; the Docker development image serves the same build through Nginx.

## Backend and Agent

- API: REST endpoints `GET /health` and `POST /predict-delay`.
- Validation: Pydantic schemas and friendly request-validation responses.
- Orchestration: `DelayAgent` combines risk scoring, output guardrails, structured LLM text and deterministic fallback.
- Historical scorer: `HistoricalRiskTool`, using a progressive segment fallback hierarchy.
- Model scorer: scikit-learn `HistGradientBoostingClassifier` wrapped by isotonic `CalibratedClassifierCV` and served through `ModelRiskTool`.
- LLM: Gemini 2.5 Flash through an OpenAI-compatible HTTP contract, strict JSON Schema output and token telemetry.
- Data: Olist CSVs are transformed offline into `prepared_orders.jsonl`; no transactional database.

## ML and Experimentation

- Training/serving: scikit-learn 1.9.0 and Joblib.
- Evaluation: leave-one-out historical baseline and out-of-fold model evaluation.
- Tracking: optional MLflow 3.14+ server and model registry through the Compose `mlflow` profile.
- Evidence: committed evaluation JSON and charts under `backend/data/` and `assets/`.

## Testing

- Backend: pytest, 101 tests covering schemas, data preparation, scoring, model training/evaluation, MLflow, agent, LLM and API.
- Frontend: production build gate with `npm run build`; no component-test framework.
- E2E/CI: no automated browser suite and no CI pipeline; deployment smoke and UI behavior are validated manually.

## External Services

- Data source: Olist Brazilian E-Commerce dataset stored locally.
- LLM provider: Google Gemini OpenAI-compatible endpoint, configured by environment variables.
- Hosting: Render Web Service for the API and Render Static Site for the dashboard.
