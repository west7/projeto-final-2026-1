SERVICE_NAME = "olist-delay-agent"


def health() -> dict:
    return {"status": "ok", "service": SERVICE_NAME}
