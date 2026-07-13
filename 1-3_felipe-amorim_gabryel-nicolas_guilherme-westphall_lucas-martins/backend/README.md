# Backend - Agente de Previsão de Atraso

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-ml.txt
```

## Gate (test command)

Backend quick/full gate runs from `backend/`:

```bash
./.venv/bin/python -m pytest -q
```

## Prepared Data

The API needs a prepared order-level feature file. In Docker, this is generated
automatically before Uvicorn starts.

Manual local generation from the project folder:

```bash
cd backend
python -m app.prepare_data
```

Environment variables:

- `RAW_DATA_DIR` (default: `../dataset` from the project root layout)
- `PREPARED_FEATURES_PATH` (default: `backend/data/prepared_orders.jsonl`)

The generated `.jsonl` is ignored by git.

## Model (ML) — train, evaluate, MLflow

The ML stack lives in a separate `requirements-ml.txt`, so a historical-only
local deployment can omit it. The current production image installs this file,
trains the calibrated model during the build and serves with `MODEL_PATH` set.
Install it locally when training, evaluating or running the complete test suite:

```bash
pip install -r requirements-ml.txt
```

Reproducible retrain — regenerates `data/model.joblib` (gitignored) from the
prepared data with the same features/config every time:

```bash
python -m app.train_model
```

Offline evaluation (leave-one-out for the baseline, out-of-fold for the model),
writing the full report as a committed JSON artifact:

```bash
python -m app.evaluate --scorer historical --json-out data/eval_historical.json
python -m app.evaluate --scorer model      --json-out data/eval_model.json
```

`eval_historical.json` and `eval_model.json` are the committed baseline-vs-model
comparison evidence (overall + per-band calibration + per-state + alarm TP/FP/FN).

MLflow tracking is optional. When `MLFLOW_TRACKING_URI` is unset, train/eval run
normally with all MLflow calls no-oped. To record runs, start the optional
tracking server and point eval at it:

```bash
docker compose --profile mlflow up -d mlflow            # server on :5000
MLFLOW_TRACKING_URI=http://localhost:5000 \
  python -m app.evaluate --scorer model --json-out data/eval_model.json
```

## Deployment modes

The API works in two modes with an identical contract:

- **Model-enabled** — install `requirements-ml.txt` and set `MODEL_PATH` to a
  trained `model.joblib`. Risk scores come from the calibrated model; evidence
  factors still come from the historical tool.
- **Fallback** — no sklearn and/or no `MODEL_PATH` (or an absent/corrupt model
  file). The API imports and serves using the historical segment-average
  scorer. The current Render image installs the ML dependencies, trains the
  artifact during build and sets `MODEL_PATH`.

## LLM Configuration

The agent requests a strict structured response (`explanation`, closed
`action_intent`, `recommended_action`) for the primary explanation/action text.
The LLM wording is accepted only when its intent matches the deterministic
policy; malformed, incompatible or unavailable responses fall back safely for
both visible fields.

Environment variables for the OpenAI-compatible client:

- `LLM_API_KEY` or `OPENAI_API_KEY`
- `LLM_MODEL` (default: `gpt-4o-mini`)
- `LLM_BASE_URL` (default: `https://api.openai.com/v1`)
- `LLM_TIMEOUT_SECONDS` (default: `20`)
- `LLM_REASONING_EFFORT` (default: `none`; blank omits the provider field)

## Layout

- `app/` — application package (agent, LLM client, risk tool, API — added in later tasks).
- `app/health.py` — service smoke/health module.
- `app/prepare_data.py` — startup/local command that creates the prepared feature artifact.
- `tests/` — pytest suite. Import path is configured via `pyproject.toml` (`pythonpath = ["."]`).
