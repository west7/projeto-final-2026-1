"""HTTP API for the Olist delay prediction agent."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agent import DelayAgent
from app.health import health
from app.llm import build_llm_client_from_env
from app.model_risk_tool import ModelRiskTool
from app.risk_tool import HistoricalRiskTool
from app.schemas import DelayPrediction, OrderInput, format_validation_error

logger = logging.getLogger(__name__)
_UNSET = object()
_DEFAULT_PREPARED_PATH = Path(__file__).resolve().parents[1] / "data" / "prepared_orders.jsonl"

_TELEMETRY_FIELDS = (
    "event_type", "latency_ms", "guardrails", "llm_model",
    "llm_prompt_tokens", "llm_completion_tokens", "llm_total_tokens",
)


class _JsonLogFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {"level": record.levelname, "logger": record.name, "message": record.getMessage()}
        for field in _TELEMETRY_FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        return json.dumps(payload)


def _configure_logging() -> None:
    # uvicorn never configures the root/app logger, so app INFO telemetry is dropped
    # (root defaults to WARNING). Attach one JSON handler scoped to `app.*`.
    app_logger = logging.getLogger("app")
    app_logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
    if not any(isinstance(h.formatter, _JsonLogFormatter) for h in app_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(_JsonLogFormatter())
        app_logger.addHandler(handler)
        app_logger.propagate = False


_configure_logging()


def create_app(agent=_UNSET, startup_error: str | None = None) -> FastAPI:
    if agent is _UNSET:
        agent, startup_error = _build_default_agent()

    api = FastAPI(title="Olist Delay Agent API")
    api.state.agent = agent
    api.state.startup_error = startup_error
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip().rstrip("/")
    if frontend_origin:
        api.add_middleware(
            CORSMiddleware,
            allow_origins=[frontend_origin],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

    @api.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "request_validation_failed",
            extra={"event_type": "guardrail_validation", "latency_ms": 0},
        )
        return JSONResponse(
            status_code=422,
            content={"error": "validation_error", "details": format_validation_error(exc)},
        )

    @api.get("/health")
    async def get_health() -> dict:
        return health()

    @api.post("/predict-delay", response_model=DelayPrediction)
    async def predict_delay(order: OrderInput, request: Request):
        started = perf_counter()
        configured_agent = request.app.state.agent
        if configured_agent is None:
            logger.error(
                "prediction_unavailable",
                extra={"event_type": "service_unavailable", "latency_ms": _elapsed_ms(started)},
            )
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": "O historico de pedidos nao esta disponivel no momento.",
                },
            )

        try:
            prediction = configured_agent.classify_order(order)
        except Exception:
            logger.exception(
                "prediction_failed",
                extra={"event_type": "prediction_error", "latency_ms": _elapsed_ms(started)},
            )
            return JSONResponse(
                status_code=503,
                content={
                    "error": "service_unavailable",
                    "message": "Nao foi possivel classificar o pedido no momento.",
                },
            )

        event_type = "prediction_fallback" if prediction.fallback_used or prediction.guardrails else "prediction_success"
        extra = {
            "event_type": event_type,
            "latency_ms": _elapsed_ms(started),
            "guardrails": prediction.guardrails,
        }
        message = "delay_prediction"
        if prediction.llm_usage is not None:
            usage = prediction.llm_usage
            extra["llm_model"] = usage.model
            extra["llm_prompt_tokens"] = usage.prompt_tokens
            extra["llm_completion_tokens"] = usage.completion_tokens
            extra["llm_total_tokens"] = usage.total_tokens
            message = (
                f"delay_prediction llm_model={usage.model} llm_prompt_tokens={usage.prompt_tokens} "
                f"llm_completion_tokens={usage.completion_tokens} llm_total_tokens={usage.total_tokens}"
            )
        logger.info(message, extra=extra)
        return prediction

    return api


def _build_default_agent() -> tuple[DelayAgent | None, str | None]:
    prepared_path = Path(os.getenv("PREPARED_FEATURES_PATH", _DEFAULT_PREPARED_PATH))
    if not prepared_path.is_file():
        return None, "prepared_data_not_found"

    model_path = os.getenv("MODEL_PATH")
    try:
        if model_path:
            risk_tool = ModelRiskTool.from_paths(prepared_path, model_path)
        else:
            risk_tool = HistoricalRiskTool.from_path(prepared_path)
        llm_client = build_llm_client_from_env()
    except (OSError, ValueError):
        logger.exception("agent_startup_failed", extra={"event_type": "startup_error", "latency_ms": 0})
        return None, "agent_startup_failed"
    return DelayAgent(risk_tool, llm_client=llm_client), None


def _elapsed_ms(started: float) -> int:
    return max(0, int((perf_counter() - started) * 1000))


app = create_app()
