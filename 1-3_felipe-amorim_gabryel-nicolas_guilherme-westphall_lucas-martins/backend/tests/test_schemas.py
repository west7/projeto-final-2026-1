import pytest
from pydantic import ValidationError

from app.schemas import OrderInput, format_validation_error


def test_valid_input_with_only_required_fields_parses():
    order = OrderInput(order_id="abc", customer_state="SP", seller_state="MG")
    assert order.order_id == "abc"
    assert order.customer_state == "SP"
    assert order.seller_state == "MG"
    assert order.freight_value is None
    assert order.product_category_name is None


def test_valid_input_with_optional_fields_parses():
    order = OrderInput(
        order_id="abc",
        customer_state="SP",
        seller_state="SP",
        product_category_name="informatica",
        freight_value=12.5,
        price=100.0,
        items_count=2,
        payment_type="credit_card",
        payment_installments=3,
    )
    assert order.items_count == 2
    assert order.payment_installments == 3


@pytest.mark.parametrize("missing", ["order_id", "customer_state", "seller_state"])
def test_missing_required_field_is_rejected(missing):
    data = {"order_id": "abc", "customer_state": "SP", "seller_state": "MG"}
    del data[missing]
    with pytest.raises(ValidationError):
        OrderInput(**data)


@pytest.mark.parametrize("bad_uf", ["sp", "S", "SPX", "XX", "12"])
def test_invalid_uf_is_rejected(bad_uf):
    with pytest.raises(ValidationError):
        OrderInput(order_id="abc", customer_state=bad_uf, seller_state="MG")


@pytest.mark.parametrize(
    "field,value",
    [("freight_value", -1.0), ("price", -5.0), ("items_count", -1)],
)
def test_impossible_numeric_values_are_rejected(field, value):
    data = {"order_id": "abc", "customer_state": "SP", "seller_state": "MG", field: value}
    with pytest.raises(ValidationError):
        OrderInput(**data)


def test_friendly_error_names_offending_field_without_stack_trace():
    try:
        OrderInput(customer_state="SP", seller_state="MG")
    except ValidationError as exc:
        errors = format_validation_error(exc)

    assert isinstance(errors, list)
    assert all(set(e.keys()) == {"field", "message"} for e in errors)
    assert any(e["field"] == "order_id" for e in errors)
    for e in errors:
        assert isinstance(e["message"], str)
        assert "Traceback" not in e["message"]


def test_friendly_error_reports_invalid_uf_field():
    try:
        OrderInput(order_id="abc", customer_state="XX", seller_state="MG")
    except ValidationError as exc:
        errors = format_validation_error(exc)

    assert any(e["field"] == "customer_state" for e in errors)
