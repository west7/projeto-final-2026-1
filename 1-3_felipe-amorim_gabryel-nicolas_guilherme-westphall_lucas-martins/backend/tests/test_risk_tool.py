from app.data_prep import OrderFeature
from app.risk_tool import HistoricalRiskTool, estimate_delay_risk
from app.schemas import OrderInput


def _feature(
    order_id,
    delayed,
    customer_state="SP",
    seller_state="SP",
    product_category_name="informatica",
):
    return OrderFeature(
        order_id=order_id,
        delayed=delayed,
        customer_state=customer_state,
        seller_state=seller_state,
        same_state=customer_state == seller_state,
        product_category_name=product_category_name,
        purchase_month=1,
        purchase_weekday=0,
        promised_days=10.0,
        total_price=100.0,
        total_freight=10.0,
        freight_ratio=0.1,
        items_count=1,
        sellers_count=1,
        payment_type_main="credit_card",
        max_installments=3,
    )


def test_specific_segment_uses_observed_delay_rate():
    features = [
        _feature("o1", True),
        _feature("o2", False),
        _feature("o3", True),
        _feature("o4", False),
    ]
    order = OrderInput(
        order_id="new-1",
        customer_state="SP",
        seller_state="SP",
        product_category_name="informatica",
    )

    evidence = estimate_delay_risk(order, features, min_segment_size=2)

    assert evidence.risk_score == 0.5
    assert evidence.risk_level == "high"
    assert evidence.sample_size == 4
    assert evidence.segment_used == "seller_state + customer_state + product_category_name"
    assert evidence.fallback_used is False
    assert any("2 de 4" in factor for factor in evidence.factors)


def test_fallback_moves_to_seller_customer_when_specific_segment_is_sparse():
    features = [
        _feature("o1", True, product_category_name="informatica"),
        _feature("o2", False, product_category_name="moveis"),
        _feature("o3", False, product_category_name="moveis"),
        _feature("o4", False, product_category_name="moveis"),
    ]
    order = OrderInput(
        order_id="new-2",
        customer_state="SP",
        seller_state="SP",
        product_category_name="informatica",
    )

    evidence = HistoricalRiskTool(features, min_segment_size=2).estimate_delay_risk(order)

    assert evidence.risk_score == 0.25
    assert evidence.risk_level == "high"
    assert evidence.sample_size == 4
    assert evidence.segment_used == "seller_state + customer_state"
    assert evidence.fallback_used is True
    assert evidence.confidence == "medium"


def test_global_baseline_is_used_when_no_segment_has_enough_samples():
    features = [
        _feature("o1", False, customer_state="RJ", seller_state="RJ", product_category_name="beleza"),
        _feature("o2", False, customer_state="MG", seller_state="MG", product_category_name="moveis"),
        _feature("o3", True, customer_state="BA", seller_state="PE", product_category_name="livros"),
    ]
    order = OrderInput(
        order_id="new-3",
        customer_state="SP",
        seller_state="SP",
        product_category_name="informatica",
    )

    evidence = estimate_delay_risk(order, features, min_segment_size=2)

    assert evidence.risk_score == 0.3333
    assert evidence.risk_level == "high"
    assert evidence.sample_size == 3
    assert evidence.segment_used == "global delivered-order baseline"
    assert evidence.fallback_used is True
    assert evidence.confidence == "low"


def test_missing_category_skips_category_segments_and_reports_fallback():
    features = [
        _feature("o1", False, customer_state="SP", seller_state="RJ", product_category_name="moveis"),
        _feature("o2", False, customer_state="SP", seller_state="MG", product_category_name="beleza"),
        _feature("o3", True, customer_state="SP", seller_state="BA", product_category_name="livros"),
    ]
    order = OrderInput(order_id="new-4", customer_state="SP", seller_state="SP")

    evidence = estimate_delay_risk(order, features, min_segment_size=2)

    assert evidence.risk_score == 0.3333
    assert evidence.segment_used == "customer_state"
    assert evidence.fallback_used is True


def test_empty_history_returns_safe_low_confidence_baseline():
    order = OrderInput(order_id="new-5", customer_state="SP", seller_state="SP")

    evidence = estimate_delay_risk(order, [], min_segment_size=2)

    assert evidence.risk_score == 0.0
    assert evidence.risk_level == "low"
    assert evidence.confidence == "low"
    assert evidence.sample_size == 0
    assert evidence.fallback_used is True
