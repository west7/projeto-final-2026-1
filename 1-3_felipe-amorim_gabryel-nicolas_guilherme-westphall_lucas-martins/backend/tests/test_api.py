import asyncio
import logging

import httpx

from app.api import create_app
from app.schemas import DelayPrediction, RiskEvidence


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
