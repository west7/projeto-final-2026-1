import csv
from dataclasses import fields

from app.data_prep import (
    OrderFeature,
    build_order_features,
    load_prepared_features,
)

LEAKAGE_FIELDS = {
    "order_delivered_customer_date",
    "order_delivered_carrier_date",
    "order_status",
    "review_score",
    "review_comment_message",
}


def _write(path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _make_dataset(raw_dir):
    _write(
        raw_dir / "olist_customers_dataset.csv",
        ["customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"],
        [
            ["c1", "u1", "01000", "sao paulo", "SP"],
            ["c2", "u2", "30000", "belo horizonte", "MG"],
        ],
    )
    _write(
        raw_dir / "olist_sellers_dataset.csv",
        ["seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"],
        [
            ["s1", "13000", "campinas", "SP"],
            ["s2", "20000", "rio", "RJ"],
        ],
    )
    _write(
        raw_dir / "olist_products_dataset.csv",
        ["product_id", "product_category_name", "product_name_lenght", "product_description_lenght",
         "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"],
        [
            ["p1", "informatica", "", "", "", "", "", "", ""],
            ["p2", "moveis", "", "", "", "", "", "", ""],
        ],
    )
    _write(
        raw_dir / "olist_orders_dataset.csv",
        ["order_id", "customer_id", "order_status", "order_purchase_timestamp", "order_approved_at",
         "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date"],
        [
            # on-time delivered
            ["o1", "c1", "delivered", "2017-01-02 10:00:00", "2017-01-02 11:00:00",
             "2017-01-05 00:00:00", "2017-01-08 12:00:00", "2017-01-10 00:00:00"],
            # late delivered
            ["o2", "c2", "delivered", "2017-02-01 09:00:00", "2017-02-01 10:00:00",
             "2017-02-05 00:00:00", "2017-02-15 08:00:00", "2017-02-10 00:00:00"],
            # not delivered -> dropped
            ["o3", "c1", "shipped", "2017-03-01 09:00:00", "2017-03-01 10:00:00",
             "2017-03-05 00:00:00", "", "2017-03-12 00:00:00"],
        ],
    )
    _write(
        raw_dir / "olist_order_items_dataset.csv",
        ["order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"],
        [
            ["o1", "1", "p1", "s1", "2017-01-04 00:00:00", "100.00", "10.00"],
            ["o2", "1", "p2", "s2", "2017-02-04 00:00:00", "50.00", "5.00"],
            ["o2", "2", "p2", "s2", "2017-02-04 00:00:00", "50.00", "5.00"],
            ["o3", "1", "p1", "s1", "2017-03-04 00:00:00", "20.00", "2.00"],
        ],
    )
    _write(
        raw_dir / "olist_order_payments_dataset.csv",
        ["order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"],
        [
            ["o1", "1", "credit_card", "3", "110.00"],
            ["o2", "1", "credit_card", "5", "30.00"],
            ["o2", "2", "boleto", "1", "80.00"],
        ],
    )


def _prepare(tmp_path):
    raw_dir = tmp_path / "dataset"
    raw_dir.mkdir()
    _make_dataset(raw_dir)
    out = tmp_path / "prepared.jsonl"
    summary = build_order_features(raw_dir, out)
    return summary, out


def test_only_delivered_orders_are_kept(tmp_path):
    summary, out = _prepare(tmp_path)
    features = load_prepared_features(out)
    ids = {f.order_id for f in features}
    assert ids == {"o1", "o2"}  # o3 (shipped) dropped
    assert summary.total_orders == 2


def test_delayed_target_from_delivered_vs_estimated(tmp_path):
    _, out = _prepare(tmp_path)
    by_id = {f.order_id: f for f in load_prepared_features(out)}
    assert by_id["o1"].delayed is False  # delivered before estimated
    assert by_id["o2"].delayed is True   # delivered after estimated


def test_summary_counts_delayed(tmp_path):
    summary, _ = _prepare(tmp_path)
    assert summary.delayed_count == 1


def test_item_and_route_aggregates(tmp_path):
    _, out = _prepare(tmp_path)
    by_id = {f.order_id: f for f in load_prepared_features(out)}
    o1, o2 = by_id["o1"], by_id["o2"]

    assert o1.items_count == 1
    assert o1.total_price == 100.0
    assert o1.total_freight == 10.0
    assert o1.freight_ratio == 0.1
    assert o1.same_state is True  # SP customer, SP seller
    assert o1.customer_state == "SP"
    assert o1.seller_state == "SP"
    assert o1.sellers_count == 1
    assert o1.product_category_name == "informatica"

    assert o2.items_count == 2
    assert o2.total_freight == 10.0
    assert o2.same_state is False  # MG customer, RJ seller


def test_payment_aggregates(tmp_path):
    _, out = _prepare(tmp_path)
    by_id = {f.order_id: f for f in load_prepared_features(out)}
    assert by_id["o1"].payment_type_main == "credit_card"
    assert by_id["o1"].max_installments == 3
    # o2: boleto contributes more value than credit_card -> main; max installments across rows = 5
    assert by_id["o2"].payment_type_main == "boleto"
    assert by_id["o2"].max_installments == 5


def test_timing_features(tmp_path):
    _, out = _prepare(tmp_path)
    o1 = {f.order_id: f for f in load_prepared_features(out)}["o1"]
    assert o1.purchase_month == 1
    assert o1.purchase_weekday == 0  # 2017-01-02 is a Monday
    assert o1.promised_days == 8.0   # 2017-01-02 -> 2017-01-10


def test_leakage_fields_excluded_from_features(tmp_path):
    _, out = _prepare(tmp_path)
    feature_fields = {f.name for f in fields(OrderFeature)}
    assert LEAKAGE_FIELDS.isdisjoint(feature_fields)
