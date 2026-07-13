# Integrations

**Analyzed:** 2026-07-13

## Current Integrations

| System | Method | Status | Implementation |
| --- | --- | --- | --- |
| Olist dataset | Local CSV files | Active | `dataset/` -> `app.prepare_data` -> prepared JSONL |
| Calibrated model | Local Joblib artifact | Active | Built by `app.train_model`, loaded by `ModelRiskTool` |
| Gemini 2.5 Flash | OpenAI-compatible HTTPS | Optional/primary text path | `backend/app/llm.py` |
| Agent API | REST/JSON | Active | FastAPI `GET /health`, `POST /predict-delay` |
| Dashboard | REST/JSON | Active | `frontend/src/api.js` calls the configured API base |
| MLflow | HTTP tracking and registry | Optional | Compose profile plus `mlflow_tracking.py` |
| Render | Docker Web Service + Static Site | Active | `render.yaml` |

## Prediction Contract

`POST /predict-delay` accepts route, order timing and optional commercial/payment features. It returns:

- score, risk band and confidence;
- traceable historical evidence and fallback state;
- separate explanation and recommended action;
- guardrail events and end-to-end latency;
- LLM model and token counts when the provider path succeeds.

The frontend uses the same contract in local proxy mode and direct production API mode.

## Configuration and Authentication

- LLM: `LLM_API_KEY`/`OPENAI_API_KEY`, model, base URL, timeout and reasoning effort.
- Browser access: `FRONTEND_ORIGIN` configures the single allowed CORS origin in production.
- Model serving: `PREPARED_FEATURES_PATH` and optional `MODEL_PATH`.
- MLflow: `MLFLOW_TRACKING_URI`; calls are disabled when it is absent.
- The product has no end-user authentication or transactional database by explicit MVP scope.

## Failure Behavior

- Missing/corrupt model or missing ML dependency -> historical scorer.
- Missing/unavailable/rate-limited LLM or invalid structured response -> deterministic explanation and action.
- Sleeping Render backend -> frontend health polling and retry state.
- Missing prepared data at API startup -> friendly service-unavailable response.

## Security and Privacy

- Secrets belong in ignored `.env` files or Render secret environment variables.
- Only structured order fields reach the LLM prompt; there is no free-text prompt input.
- Olist identifiers are pseudonymous, and the API does not add customer personal data.
