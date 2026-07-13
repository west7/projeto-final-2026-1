"""Prepare order-level features from raw Olist CSVs.

Only delivered orders get a `delayed` target. Leakage columns (actual delivery
dates, final status, reviews) never enter the feature output — see design.md.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

_DT_FORMAT = "%Y-%m-%d %H:%M:%S"
_DT_FORMATS = (_DT_FORMAT, "%Y-%m-%d")  # raw CSVs use full timestamps; the API/form send date-only


@dataclass
class OrderFeature:
    order_id: str
    delayed: bool
    customer_state: str | None
    seller_state: str | None
    same_state: bool
    product_category_name: str | None
    purchase_month: int
    purchase_weekday: int
    promised_days: float
    total_price: float
    total_freight: float
    freight_ratio: float | None
    items_count: int
    sellers_count: int
    payment_type_main: str | None
    max_installments: int | None


@dataclass
class PrepSummary:
    total_orders: int
    delayed_count: int
    output: Path


def _parse_dt(value: str) -> datetime | None:
    value = (value or "").strip()
    if not value:
        return None
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _read_csv(path: Path):
    with open(path, newline="") as fh:
        yield from csv.DictReader(fh)


def _load_lookup(path: Path, key: str, value: str) -> dict[str, str]:
    return {row[key]: row[value] for row in _read_csv(path)}


def _load_items(path: Path):
    items: dict[str, list[dict]] = defaultdict(list)
    for row in _read_csv(path):
        items[row["order_id"]].append(row)
    return items


def _load_payments(path: Path):
    by_order: dict[str, list[dict]] = defaultdict(list)
    for row in _read_csv(path):
        by_order[row["order_id"]].append(row)
    return by_order


def _payment_aggregate(rows: list[dict]) -> tuple[str | None, int | None]:
    if not rows:
        return None, None
    value_by_type: dict[str, float] = defaultdict(float)
    max_installments = 0
    for row in rows:
        value_by_type[row["payment_type"]] += float(row["payment_value"] or 0)
        max_installments = max(max_installments, int(row["payment_installments"] or 0))
    main_type = max(value_by_type, key=value_by_type.get)
    return main_type, max_installments


def build_order_features(raw_dir: Path, output_path: Path) -> PrepSummary:
    raw_dir = Path(raw_dir)
    output_path = Path(output_path)

    customer_state = _load_lookup(raw_dir / "olist_customers_dataset.csv", "customer_id", "customer_state")
    seller_state = _load_lookup(raw_dir / "olist_sellers_dataset.csv", "seller_id", "seller_state")
    product_category = _load_lookup(raw_dir / "olist_products_dataset.csv", "product_id", "product_category_name")
    items = _load_items(raw_dir / "olist_order_items_dataset.csv")
    payments = _load_payments(raw_dir / "olist_order_payments_dataset.csv")

    total = 0
    delayed_count = 0
    with open(output_path, "w") as out:
        for order in _read_csv(raw_dir / "olist_orders_dataset.csv"):
            if order["order_status"] != "delivered":
                continue
            purchase = _parse_dt(order["order_purchase_timestamp"])
            delivered = _parse_dt(order["order_delivered_customer_date"])
            estimated = _parse_dt(order["order_estimated_delivery_date"])
            if purchase is None or delivered is None or estimated is None:
                continue

            order_items = items.get(order["order_id"], [])
            total_price = sum(float(i["price"] or 0) for i in order_items)
            total_freight = sum(float(i["freight_value"] or 0) for i in order_items)
            sellers = {i["seller_id"] for i in order_items}
            main_seller = order_items[0]["seller_id"] if order_items else None
            main_category = product_category.get(order_items[0]["product_id"]) if order_items else None
            cust_state = customer_state.get(order["customer_id"])
            sell_state = seller_state.get(main_seller) if main_seller else None
            pay_type, max_inst = _payment_aggregate(payments.get(order["order_id"], []))

            delayed = delivered > estimated
            feature = OrderFeature(
                order_id=order["order_id"],
                delayed=delayed,
                customer_state=cust_state,
                seller_state=sell_state,
                same_state=cust_state is not None and cust_state == sell_state,
                product_category_name=main_category or None,
                purchase_month=purchase.month,
                purchase_weekday=purchase.weekday(),
                promised_days=float((estimated.date() - purchase.date()).days),
                total_price=total_price,
                total_freight=total_freight,
                freight_ratio=(total_freight / total_price) if total_price > 0 else None,
                items_count=len(order_items),
                sellers_count=len(sellers),
                payment_type_main=pay_type,
                max_installments=max_inst,
            )
            out.write(json.dumps(asdict(feature)) + "\n")
            total += 1
            if delayed:
                delayed_count += 1

    return PrepSummary(total_orders=total, delayed_count=delayed_count, output=output_path)


def load_prepared_features(path: Path) -> list[OrderFeature]:
    with open(Path(path)) as fh:
        return [OrderFeature(**json.loads(line)) for line in fh if line.strip()]
