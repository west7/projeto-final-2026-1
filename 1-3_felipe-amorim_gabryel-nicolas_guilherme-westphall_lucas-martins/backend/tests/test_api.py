import asyncio
import json
import logging
from dataclasses import asdict

import httpx

from app.api import create_app
from app.data_prep import OrderFeature
from app.schemas import DelayPrediction, LLMUsage, RiskEvidence
from app.train_model import train


class FakeAgent:
    def classify_order(self, order):
        evidence = RiskEvidence(
            risk_score=0.25,
            risk_level="high",
            confidence="medium",
            sample_size=40,
            segment_used="seller_state + customer_state",
            fallback_used=False,
            factors=["10 de 40 pedidos historicos comparaveis atrasaram (25.0%)"],
        )
        return DelayPrediction(
            order_id=order.order_id,
            risk_score=evidence.risk_score,
            risk_level=evidence.risk_level,
            confidence=evidence.confidence,
            explanation="Risco alto com base no historico da rota.",
            recommended_action="Priorizar acompanhamento logistico.",
            evidence=evidence,
            guardrails=[],
            fallback_used=False,
            latency_ms=3,
        )


def _payload():
    return {
        "order_id": "new-1",
        "customer_state": "SP",
        "seller_state": "RJ",
        "product_category_name": "informatica",
    }


def _request(app, method, path, **kwargs):
    async def send():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, **kwargs)

    return asyncio.run(send())


def test_health_returns_service_status():
    response = _request(create_app(agent=FakeAgent()), "GET", "/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "olist-delay-agent"}


def test_cors_allows_only_configured_frontend_origin(monkeypatch):
    monkeypatch.setenv("FRONTEND_ORIGIN", "https://olist-delay-dashboard.onrender.com")
    app = create_app(agent=FakeAgent())

    allowed = _request(
        app,
        "OPTIONS",
        "/predict-delay",
        headers={
            "Origin": "https://olist-delay-dashboard.onrender.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    denied = _request(
        app,
        "OPTIONS",
        "/predict-delay",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "https://olist-delay-dashboard.onrender.com"
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers


def test_predict_delay_returns_agent_prediction():
    response = _request(create_app(agent=FakeAgent()), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    body = response.json()
    assert body["order_id"] == "new-1"
    assert body["risk_level"] == "high"
    assert body["evidence"]["sample_size"] == 40


def test_validation_errors_are_friendly_and_hide_technical_details():
    response = _request(
        create_app(agent=FakeAgent()),
        "POST",
        "/predict-delay",
        json={"order_id": "bad", "customer_state": "XX"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert response.json()["details"] == [
        {
            "field": "body.customer_state",
            "message": "Value error, must be a valid Brazilian UF (two uppercase letters)",
        },
        {"field": "body.seller_state", "message": "Field required"},
    ]
    assert "traceback" not in response.text.lower()


def test_prediction_log_includes_latency_and_event_type(caplog):
    with caplog.at_level(logging.INFO, logger="app.api"):
        response = _request(create_app(agent=FakeAgent()), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    record = next(record for record in caplog.records if record.getMessage() == "delay_prediction")
    assert record.event_type == "prediction_success"
    assert record.latency_ms >= 0


def test_app_logger_emits_info_json_with_telemetry_fields():
    from app.api import _JsonLogFormatter, _configure_logging

    _configure_logging()
    app_logger = logging.getLogger("app")
    assert app_logger.getEffectiveLevel() == logging.INFO

    record = logging.LogRecord("app.api", logging.INFO, __file__, 0, "delay_prediction", None, None)
    record.event_type = "prediction_fallback"
    record.latency_ms = 12
    payload = json.loads(_JsonLogFormatter().format(record))
    assert payload["message"] == "delay_prediction"
    assert payload["event_type"] == "prediction_fallback"
    assert payload["latency_ms"] == 12


def test_prediction_log_renders_llm_usage_in_message(caplog):
    class AgentWithUsage(FakeAgent):
        def classify_order(self, order):
            prediction = super().classify_order(order)
            prediction.llm_usage = LLMUsage(
                model="gemini-2.5-flash",
                prompt_tokens=226,
                completion_tokens=99,
                total_tokens=1026,
            )
            return prediction

    with caplog.at_level(logging.INFO, logger="app.api"):
        response = _request(create_app(agent=AgentWithUsage()), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    record = next(record for record in caplog.records if record.getMessage().startswith("delay_prediction"))
    assert record.getMessage() == (
        "delay_prediction llm_model=gemini-2.5-flash llm_prompt_tokens=226 "
        "llm_completion_tokens=99 llm_total_tokens=1026"
    )


def test_prediction_log_includes_guardrail_reason(caplog):
    class RateLimitedAgent(FakeAgent):
        def classify_order(self, order):
            prediction = super().classify_order(order)
            prediction.guardrails = ["llm_fallback:rate_limited"]
            return prediction

    with caplog.at_level(logging.INFO, logger="app.api"):
        response = _request(create_app(agent=RateLimitedAgent()), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    record = next(record for record in caplog.records if record.getMessage() == "delay_prediction")
    assert record.event_type == "prediction_fallback"
    assert record.guardrails == ["llm_fallback:rate_limited"]


def test_unavailable_agent_returns_friendly_service_error():
    response = _request(
        create_app(agent=None, startup_error="prepared_data_not_found"),
        "POST",
        "/predict-delay",
        json=_payload(),
    )

    assert response.status_code == 503
    assert response.json() == {
        "error": "service_unavailable",
        "message": "O historico de pedidos nao esta disponivel no momento.",
    }
    assert "prepared_data_not_found" not in response.text


def _order_feature(order_id, delayed):
    return OrderFeature(
        order_id=order_id,
        delayed=delayed,
        customer_state="SP" if delayed else "BA",
        seller_state="RJ" if delayed else "MG",
        same_state=False,
        product_category_name="informatica" if delayed else "beleza",
        purchase_month=3,
        purchase_weekday=2,
        promised_days=10.0,
        total_price=100.0,
        total_freight=10.0,
        freight_ratio=0.1,
        items_count=2,
        sellers_count=1,
        payment_type_main="credit_card",
        max_installments=3,
    )


def _prepared_fixture(tmp_path):
    path = tmp_path / "prepared.jsonl"
    rows = [_order_feature(f"late-{i}", True) for i in range(12)]
    rows += [_order_feature(f"ok-{i}", False) for i in range(12)]
    with open(path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row)) + "\n")
    return path


def _offline_env(monkeypatch, prepared):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("PREPARED_FEATURES_PATH", str(prepared))


def test_model_path_set_returns_model_sourced_score(tmp_path, monkeypatch):
    prepared = _prepared_fixture(tmp_path)
    model_path = tmp_path / "model.joblib"
    train(prepared, model_path, cv=2)
    _offline_env(monkeypatch, prepared)
    monkeypatch.setenv("MODEL_PATH", str(model_path))

    response = _request(create_app(), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    factors = response.json()["evidence"]["factors"]
    assert factors
    assert factors[0].startswith("score do modelo calibrado")


def test_model_path_unset_uses_historical_path(tmp_path, monkeypatch):
    prepared = _prepared_fixture(tmp_path)
    _offline_env(monkeypatch, prepared)
    monkeypatch.delenv("MODEL_PATH", raising=False)

    response = _request(create_app(), "POST", "/predict-delay", json=_payload())

    assert response.status_code == 200
    factors = response.json()["evidence"]["factors"]
    assert factors
    assert not factors[0].startswith("score do modelo calibrado")
