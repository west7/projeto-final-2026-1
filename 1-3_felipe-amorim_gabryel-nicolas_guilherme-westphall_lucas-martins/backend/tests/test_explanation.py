import pytest

from app.explanation import OutputGuardrailError, explain_risk, safe_explanation
from app.schemas import RiskEvidence


def _evidence(**overrides):
    data = {
        "risk_score": 0.25,
        "risk_level": "high",
        "confidence": "medium",
        "sample_size": 40,
        "segment_used": "seller_state + customer_state",
        "fallback_used": False,
        "factors": [
            "10 de 40 pedidos historicos comparaveis atrasaram (25.0%)",
            "recorte usado: seller_state + customer_state",
        ],
    }
    data.update(overrides)
    return RiskEvidence(**data)


def test_explanation_cites_score_segment_sample_and_factors():
    result = explain_risk(_evidence())

    assert "Risco high (25.0%)" in result.explanation
    assert "seller_state + customer_state" in result.explanation
    assert "amostra historica: 40 pedidos" in result.explanation
    assert "10 de 40" in result.explanation
    assert result.guardrails == []


@pytest.mark.parametrize(
    "risk_level,expected_action",
    [
        ("high", "Priorizar acompanhamento logistico"),
        ("medium", "Monitorar o pedido diariamente"),
        ("low", "Manter fluxo normal"),
    ],
)
def test_action_differs_by_risk_level(risk_level, expected_action):
    result = explain_risk(_evidence(risk_level=risk_level))

    assert result.recommended_action.startswith(expected_action)


def test_low_confidence_recommends_human_review():
    result = explain_risk(_evidence(confidence="low", risk_level="high", sample_size=3))

    assert "revisao humana" in result.explanation
    assert result.recommended_action == "Encaminhar para revisao humana; historico comparavel insuficiente."
    assert "low_confidence" in result.guardrails


def test_fallback_is_reported_as_guardrail_event():
    result = explain_risk(_evidence(fallback_used=True))

    assert result.guardrails == ["fallback_used"]


@pytest.mark.parametrize(
    "overrides",
    [
        {"factors": []},
        {"segment_used": ""},
        {"sample_size": 0},
    ],
)
def test_output_guardrail_rejects_missing_traceable_evidence(overrides):
    with pytest.raises(OutputGuardrailError):
        explain_risk(_evidence(**overrides))


def test_safe_explanation_returns_human_review_action():
    result = safe_explanation("missing_factors")

    assert "evidencia rastreavel suficiente" in result.explanation
    assert "revisao humana" in result.recommended_action
    assert result.guardrails == ["output_guardrail:missing_factors"]
