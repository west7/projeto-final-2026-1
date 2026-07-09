# Project Structure

**Analyzed:** 2026-07-09

```text
.
├── README.md
├── projeto_agente_atraso_visao_geral.html
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
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       └── styles.css
└── .specs/
    ├── project/
    ├── codebase/
    └── features/
```

## Ownership Boundaries

- Course/project brief: repository root `readme.md` and `trilhas.md`, outside this delivery folder.
- Project-specific planning: `README.md`, HTML overview and `.specs`.
- Raw data: `dataset`. Treat as source input; do not edit manually.
- Product UI: `frontend`.

## Expected Additions

- `backend/` for API, agent, tools, data prep and tests.
- `backend/data/processed/` or equivalent for generated derived artifacts.
- Docker files at this project root.
- Report files inside this project root.
