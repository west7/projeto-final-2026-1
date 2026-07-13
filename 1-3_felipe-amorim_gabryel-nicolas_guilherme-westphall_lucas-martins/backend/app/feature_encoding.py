"""Shared train/serve feature encoding — the single guard against train/serve skew.

Both an ``OrderFeature`` (training) and an ``OrderInput`` (serving) map to the
identical feature vector. ``sellers_count`` is the only training column that
cannot be reconstructed from ``OrderInput`` at request time, so it is excluded
everywhere. Derivation mirrors ``data_prep.build_order_features``.
"""
from __future__ import annotations

from app.data_prep import OrderFeature, _parse_dt
from app.schemas import OrderInput

FEATURE_COLUMNS = [
    "customer_state",
    "seller_state",
    "same_state",
    "product_category_name",
    "purchase_month",
    "purchase_weekday",
    "promised_days",
    "total_price",
    "total_freight",
    "freight_ratio",
    "items_count",
    "payment_type_main",
    "max_installments",
]

CATEGORICAL_COLUMNS = [
    "customer_state",
    "seller_state",
    "same_state",
    "product_category_name",
    "payment_type_main",
]


def features_from_order_feature(f: OrderFeature) -> dict:
    return {column: getattr(f, column) for column in FEATURE_COLUMNS}


def features_from_order_input(o: OrderInput) -> dict:
    purchase = _parse_dt(o.order_purchase_timestamp or "")
    estimated = _parse_dt(o.order_estimated_delivery_date or "")
    promised_days = (
        float((estimated.date() - purchase.date()).days)
        if purchase and estimated
        else None
    )
    total_price = o.price
    total_freight = o.freight_value
    return {
        "customer_state": o.customer_state,
        "seller_state": o.seller_state,
        "same_state": o.customer_state == o.seller_state,
        "product_category_name": o.product_category_name,
        "purchase_month": purchase.month if purchase else None,
        "purchase_weekday": purchase.weekday() if purchase else None,
        "promised_days": promised_days,
        "total_price": total_price,
        "total_freight": total_freight,
        "freight_ratio": (total_freight / total_price)
        if total_price and total_price > 0
        else None,
        "items_count": o.items_count,
        "payment_type_main": o.payment_type,
        "max_installments": o.payment_installments,
    }
