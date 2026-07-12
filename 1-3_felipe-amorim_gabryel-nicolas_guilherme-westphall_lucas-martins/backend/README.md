# Backend - Agente de Previsão de Atraso

## Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Gate (test command)

Backend quick/full gate runs from `backend/`:

```bash
pytest
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

## LLM Configuration

The agent is designed to use an LLM for the primary explanation/action text and
fall back to deterministic text when the provider is unavailable.

Environment variables for the OpenAI-compatible client:

- `LLM_API_KEY` or `OPENAI_API_KEY`
- `LLM_MODEL` (default: `gpt-4o-mini`)
- `LLM_BASE_URL` (default: `https://api.openai.com/v1`)
- `LLM_TIMEOUT_SECONDS` (default: `20`)

## Layout

- `app/` — application package (agent, LLM client, risk tool, API — added in later tasks).
- `app/health.py` — service smoke/health module.
- `app/prepare_data.py` — startup/local command that creates the prepared feature artifact.
- `tests/` — pytest suite. Import path is configured via `pyproject.toml` (`pythonpath = ["."]`).
