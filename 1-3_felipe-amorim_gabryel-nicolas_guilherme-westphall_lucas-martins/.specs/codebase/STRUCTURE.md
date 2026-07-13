# Project Structure

**Analyzed:** 2026-07-12

```text
.
├── README.md
├── docker-compose.yml
├── .dockerignore
├── dataset/
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── app/
│   │   ├── api.py            # FastAPI app: /health, /predict-delay
│   │   ├── agent.py          # DelayAgent orchestration
│   │   ├── risk_tool.py      # HistoricalRiskTool (segment fallback hierarchy)
│   │   ├── explanation.py    # deterministic explanation + action policy
│   │   ├── llm.py            # OpenAI-compatible LLM client
│   │   ├── schemas.py        # Pydantic models + input guardrails
│   │   ├── data_prep.py      # build/load prepared order features
│   │   ├── prepare_data.py   # startup artifact builder
│   │   ├── evaluate.py       # offline baseline evaluation (T7)
│   │   └── health.py
│   └── tests/                # pytest suite (61 tests)
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       ├── App.jsx
│       ├── api.js
│       ├── main.jsx
│       └── styles.css
└── .specs/
    ├── project/
    ├── codebase/
    └── features/
```

## Ownership Boundaries

- Course/project brief: repository root `readme.md` and `trilhas.md`, outside this delivery folder.
- Project-specific planning: `README.md` and `.specs`.
- Raw data: `dataset`. Treat as source input; do not edit manually.
- Product UI: `frontend`.

## Generated / Runtime (not in git)

- `backend/data/prepared_orders.jsonl`: derived feature artifact built at startup from `dataset/`; persisted in a Docker volume.
- `backend/.venv`: local virtualenv for the backend test gate.
- `backend/.env`: local LLM configuration (gitignored).

## Expected Additions

- Report file(s) inside this project root (T12).
