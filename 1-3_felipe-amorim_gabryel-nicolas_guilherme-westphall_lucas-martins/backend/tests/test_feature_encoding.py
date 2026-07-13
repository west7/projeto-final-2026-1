from app.data_prep import OrderFeature
from app.feature_encoding import (
    FEATURE_COLUMNS,
    features_from_order_feature,
    features_from_order_input,
)
from app.schemas import OrderInput


def _matched_pair():
    feature = OrderFeature(
        order_id="o1",
        delayed=False,
        customer_state="RJ",
        seller_state="SP",
        same_state=False,
        product_category_name="moveis",
        purchase_month=3,
        purchase_weekday=2,  # 2017-03-15 is a Wednesday
        promised_days=10.0,
        total_price=100.0,
        total_freight=10.0,
        freight_ratio=0.1,
        items_count=2,
        sellers_count=1,
        payment_type_main="credit_card",
        max_installments=3,
    )
    order = OrderInput(
        order_id="o1",
        customer_state="RJ",
        seller_state="SP",
        product_category_name="moveis",
        order_purchase_timestamp="2017-03-15 10:30:00",
        order_estimated_delivery_date="2017-03-25 10:30:00",
        freight_value=10.0,
        price=100.0,
        items_count=2,
        payment_type="credit_card",
        payment_installments=3,
    )
    return feature, order


def test_matched_pair_encodes_to_equal_vector():
    feature, order = _matched_pair()
    assert features_from_order_feature(feature) == features_from_order_input(order)


def test_sellers_count_never_in_vector():
    feature, order = _matched_pair()
    assert "sellers_count" not in FEATURE_COLUMNS
    assert "sellers_count" not in features_from_order_feature(feature)
    assert "sellers_count" not in features_from_order_input(order)


def test_missing_input_fields_become_none_without_error():
    order = OrderInput(order_id="o2", customer_state="BA", seller_state="MG")
    vector = features_from_order_input(order)

    assert vector["promised_days"] is None
    assert vector["purchase_month"] is None
    assert vector["purchase_weekday"] is None
    assert vector["total_price"] is None
    assert vector["freight_ratio"] is None
    assert vector["max_installments"] is None
    assert set(vector) == set(FEATURE_COLUMNS)
