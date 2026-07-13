from app.agent import DelayAgent, classify_order
from app.schemas import OrderInput, RiskEvidence


class FakeRiskTool:
    def __init__(self, evidence):
        self.evidence = evidence
        self.orders = []

    def estimate_delay_risk(self, order):
        self.orders.append(order)
        return self.evidence


def _order():
    return OrderInput(
        order_id="new-1",
        customer_state="SP",
        seller_state="RJ",
        product_category_name="informatica",
    )


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


def test_classify_order_returns_complete_prediction_response():
    def llm_client(order, evidence, fallback):
        return fallback.explanation

    risk_tool = FakeRiskTool(_evidence())
    prediction = DelayAgent(risk_tool, llm_client=llm_client).classify_order(_order())

    assert prediction.order_id == "new-1"
    assert prediction.risk_score == 0.25
    assert prediction.risk_level == "high"
    assert prediction.confidence == "medium"
    assert prediction.recommended_action.startswith("Priorizar acompanhamento logistico")
    assert "amostra historica: 40 pedidos" in prediction.explanation
    assert prediction.evidence.sample_size == 40
    assert prediction.fallback_used is False
    assert prediction.guardrails == []
    assert isinstance(prediction.latency_ms, int)
    assert risk_tool.orders == [_order()]


def test_classify_order_represents_fallback_and_low_confidence_events():
    evidence = _evidence(
        risk_score=0.08,
        risk_level="low",
        confidence="low",
        sample_size=5,
        segment_used="global delivered-order baseline",
        fallback_used=True,
    )
    prediction = classify_order(_order(), FakeRiskTool(evidence), llm_client=lambda order, evidence, fallback: fallback.explanation)

    assert prediction.fallback_used is True
    assert "fallback_used" in prediction.guardrails
    assert "low_confidence" in prediction.guardrails
    assert prediction.recommended_action == "Encaminhar para revisao humana; historico comparavel insuficiente."


def test_output_guardrail_returns_safe_low_confidence_prediction():
    bad_evidence = _evidence(factors=[])

    prediction = DelayAgent(FakeRiskTool(bad_evidence)).classify_order(_order())

    assert prediction.risk_score == 0.0
    assert prediction.risk_level == "low"
    assert prediction.confidence == "low"
    assert prediction.fallback_used is True
    assert prediction.evidence.factors == ["output guardrail blocked incomplete evidence: missing_factors"]
    assert prediction.guardrails == ["output_guardrail:missing_factors", "llm_unconfigured"]
    assert "revisao humana" in prediction.recommended_action


def test_llm_client_is_primary_explanation_path():
    def client(order, evidence, fallback):
        return f"LLM: {order.order_id} {evidence.risk_level}"

    prediction = DelayAgent(FakeRiskTool(_evidence()), llm_client=client).classify_order(_order())

    assert prediction.explanation == "LLM: new-1 high"
    assert prediction.guardrails == []


def test_missing_llm_client_falls_back_to_deterministic_text():
    prediction = DelayAgent(FakeRiskTool(_evidence())).classify_order(_order())

    assert "amostra historica: 40 pedidos" in prediction.explanation
    assert prediction.guardrails == ["llm_unconfigured"]


def test_llm_failure_falls_back_to_deterministic_text():
    def broken_client(order, evidence, fallback):
        raise RuntimeError("offline")

    prediction = DelayAgent(FakeRiskTool(_evidence()), llm_client=broken_client).classify_order(_order())

    assert "amostra historica: 40 pedidos" in prediction.explanation
    assert prediction.guardrails == ["llm_fallback"]


def test_llm_result_usage_is_attached_to_prediction():
    from app.llm import LLMResult
    from app.schemas import LLMUsage

    usage = LLMUsage(model="model-x", prompt_tokens=100, completion_tokens=20, total_tokens=140)

    def client(order, evidence, fallback):
        return LLMResult(text="explicacao do modelo", usage=usage)

    prediction = DelayAgent(FakeRiskTool(_evidence()), llm_client=client).classify_order(_order())

    assert prediction.explanation == "explicacao do modelo"
    assert prediction.llm_usage == usage


def test_deterministic_path_has_no_llm_usage():
    prediction = DelayAgent(FakeRiskTool(_evidence())).classify_order(_order())
    assert prediction.llm_usage is None
