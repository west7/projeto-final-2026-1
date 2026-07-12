FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RAW_DATA_DIR=/app/dataset \
    PREPARED_FEATURES_PATH=/app/backend/data/prepared_orders.jsonl

WORKDIR /app/backend

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./
COPY dataset /app/dataset

RUN mkdir -p /app/backend/data

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)"

CMD ["sh", "-c", "python -m app.prepare_data && uvicorn app.api:app --host 0.0.0.0 --port 8000"]
