# Project Structure

**Analyzed:** 2026-07-13

```text
.
├── README.md
├── docker-compose.yml
├── render.yaml
├── assets/                     # report/dashboard/MLflow images
├── dataset/                    # raw Olist CSV files
├── backend/
│   ├── app/
│   │   ├── api.py              # FastAPI endpoints and telemetry
│   │   ├── agent.py            # prediction orchestration
│   │   ├── risk_tool.py        # historical scorer and fallback hierarchy
│   │   ├── model_risk_tool.py  # calibrated scorer adapter
│   │   ├── llm.py              # structured OpenAI-compatible client
│   │   ├── data_prep.py        # order-level feature preparation
│   │   ├── train_model.py      # calibrated model training
│   │   └── evaluate.py         # offline baseline/model evaluation
│   ├── data/                    # committed evaluation JSON; generated model/data ignored
│   ├── tests/                   # 101 pytest cases
│   ├── Dockerfile
│   ├── requirements.txt
│   └── requirements-ml.txt
├── frontend/
│   ├── src/                     # React dashboard, API client and CSS
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── .specs/
    ├── project/                 # vision, roadmap and persistent state
    ├── codebase/                # current brownfield map
    └── features/                # requirements, design and task traceability
```

## Ownership Boundaries

- `dataset/` is immutable source data.
- `backend/app/` contains production Python code; `backend/tests/` mirrors it.
- `frontend/src/` contains browser behavior and presentation.
- `assets/` and `backend/data/eval_*.json` are committed report evidence.
- `.specs/` records project decisions and implementation traceability.
- Root `readme.md` and `trilhas.md`, outside this delivery directory, contain the course brief.

## Generated or Local-Only Files

- `backend/data/prepared_orders.jsonl` and `backend/data/model.joblib` are generated, ignored by Git and embedded into the production image at build time.
- `backend/.venv`, `backend/.env`, pytest caches, frontend `node_modules` and `dist` are ignored.
- Local MLflow run and artifact directories are ignored; the Compose profile persists its server state in `mlflow-data`.

## Deployment Files

- `docker-compose.yml`: local backend/frontend plus optional MLflow profile.
- `backend/Dockerfile`: multi-stage data preparation, training and API image.
- `frontend/Dockerfile` and `nginx.conf`: containerized local frontend.
- `render.yaml`: production API Web Service and frontend Static Site definitions.
