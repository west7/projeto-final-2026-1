import json

import pytest

from app.data_prep import PrepSummary
from app import prepare_data


def _feature(order_id="o1"):
    return {
        "order_id": order_id,
        "delayed": False,
        "customer_state": "SP",
        "seller_state": "SP",
        "same_state": True,
        "product_category_name": "informatica",
        "purchase_month": 1,
        "purchase_weekday": 0,
        "promised_days": 8.0,
        "total_price": 100.0,
        "total_freight": 10.0,
        "freight_ratio": 0.1,
        "items_count": 1,
        "sellers_count": 1,
        "payment_type_main": "credit_card",
        "max_installments": 3,
    }


def _configure(monkeypatch, tmp_path):
    raw_dir = tmp_path / "dataset"
    raw_dir.mkdir()
    output = tmp_path / "data" / "prepared_orders.jsonl"
    monkeypatch.setenv("RAW_DATA_DIR", str(raw_dir))
    monkeypatch.setenv("PREPARED_FEATURES_PATH", str(output))
    return raw_dir, output


def test_existing_valid_artifact_is_reused(monkeypatch, tmp_path):
    _, output = _configure(monkeypatch, tmp_path)
    output.parent.mkdir()
    output.write_text(json.dumps(_feature()) + "\n")

    def unexpected_build(*args):
        raise AssertionError("valid artifact should not be rebuilt")

    monkeypatch.setattr(prepare_data, "build_order_features", unexpected_build)

    prepare_data.main()

    assert json.loads(output.read_text())["order_id"] == "o1"


def test_corrupt_artifact_is_replaced_atomically(monkeypatch, tmp_path):
    raw_dir, output = _configure(monkeypatch, tmp_path)
    output.parent.mkdir()
    output.write_text('{"incomplete":')

    def fake_build(received_raw_dir, temporary_path):
        assert received_raw_dir == raw_dir
        assert temporary_path != output
        temporary_path.write_text(json.dumps(_feature("rebuilt")) + "\n")
        return PrepSummary(total_orders=1, delayed_count=0, output=temporary_path)

    monkeypatch.setattr(prepare_data, "build_order_features", fake_build)

    prepare_data.main()

    assert json.loads(output.read_text())["order_id"] == "rebuilt"
    assert not output.with_suffix(".jsonl.tmp").exists()


def test_failed_generation_does_not_publish_partial_artifact(monkeypatch, tmp_path):
    _, output = _configure(monkeypatch, tmp_path)

    def broken_build(raw_dir, temporary_path):
        temporary_path.write_text('{"partial":')
        raise RuntimeError("interrupted")

    monkeypatch.setattr(prepare_data, "build_order_features", broken_build)

    with pytest.raises(RuntimeError, match="interrupted"):
        prepare_data.main()

    assert not output.exists()
    assert not output.with_suffix(".jsonl.tmp").exists()
