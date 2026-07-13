FROM python:3.12-slim AS data-builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    RAW_DATA_DIR=/app/dataset \
    PREPARED_FEATURES_PATH=/app/backend/data/prepared_orders.jsonl

WORKDIR /app

COPY backend ./backend
COPY dataset ./dataset

RUN pip install --no-cache-dir -r backend/requirements-ml.txt \
 && mkdir -p /app/backend/data && cd /app/backend \
 && python -m app.prepare_data \
 && python -m app.train_model

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PREPARED_FEATURES_PATH=/app/backend/data/prepared_orders.jsonl \
    MODEL_PATH=/app/backend/data/model.joblib

WORKDIR /app/backend

COPY backend/requirements.txt backend/requirements-ml.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-ml.txt

COPY backend ./
COPY --from=data-builder /app/backend/data/prepared_orders.jsonl ./data/prepared_orders.jsonl
COPY --from=data-builder /app/backend/data/model.joblib ./data/model.joblib

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"

CMD ["sh", "-c", "uvicorn app.api:app --host 0.0.0.0 --port ${PORT:-8000}"]
