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

## Layout

- `app/` — application package (agent, risk tool, API — added in later tasks).
- `app/health.py` — service smoke/health module.
- `tests/` — pytest suite. Import path is configured via `pyproject.toml` (`pythonpath = ["."]`).
