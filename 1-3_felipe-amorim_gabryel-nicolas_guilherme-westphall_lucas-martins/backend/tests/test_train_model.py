import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

import joblib

from app.data_prep import OrderFeature
from app.feature_encoding import features_from_order_feature
from app.train_model import train

_BACKEND_DIR = Path(__file__).resolve().parents[1]


def _feature(order_id, delayed, category):
    return OrderFeature(
        order_id=order_id,
        delayed=delayed,
        customer_state="SP" if delayed else "BA",
        seller_state="RJ" if delayed else "MG",
        same_state=False,
        product_category_name=category,
        purchase_month=3,
        purchase_weekday=2,
        promised_days=10.0,
        total_price=100.0,
        total_freight=10.0,
        freight_ratio=0.1,
        items_count=2,
        sellers_count=1,
        payment_type_main="credit_card",
        max_installments=3,
    )


def _write_fixture(path):
    rows = [_feature(f"late-{i}", True, "moveis") for i in range(12)]
    rows += [_feature(f"ok-{i}", False, "beleza") for i in range(12)]
    with open(path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row)) + "\n")


def test_train_persists_loadable_model_with_calibrated_probabilities(tmp_path):
    prepared = tmp_path / "prepared.jsonl"
    model_path = tmp_path / "model.joblib"
    _write_fixture(prepared)

    summary = train(prepared, model_path, cv=2)

    assert summary.n_orders == 24
    assert model_path.is_file()

    model = joblib.load(model_path)
    order = features_from_order_feature(_feature("probe", True, "moveis"))
    proba = model.predict_proba([order])[0]
    assert len(proba) == 2
    assert all(0.0 <= p <= 1.0 for p in proba)


def test_cli_trained_model_loads_in_a_separate_process(tmp_path):
    # `python -m app.train_model` runs the module as __main__; the pickled pipeline
    # must still resolve its helper in a serving process, or joblib.load fails.
    prepared = tmp_path / "prepared.jsonl"
    model_path = tmp_path / "model.joblib"
    _write_fixture(prepared)

    subprocess.run(
        [sys.executable, "-m", "app.train_model", "--path", str(prepared), "--model-path", str(model_path)],
        cwd=_BACKEND_DIR, check=True, capture_output=True,
    )

    model = joblib.load(model_path)  # loads in this process, not train_model's __main__
    proba = model.predict_proba([features_from_order_feature(_feature("probe", True, "moveis"))])[0]
    assert 0.0 <= proba[1] <= 1.0


def test_mlflow_registration_skipped_when_disabled(tmp_path, monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    prepared = tmp_path / "prepared.jsonl"
    model_path = tmp_path / "model.joblib"
    _write_fixture(prepared)

    summary = train(prepared, model_path, cv=2)

    assert summary.mlflow_logged is False
    assert model_path.is_file()


def test_mlflow_registration_logs_when_enabled(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # keep any mlflow artifact dirs inside tmp
    monkeypatch.setenv("MLFLOW_TRACKING_URI", f"sqlite:///{tmp_path / 'mlflow.db'}")
    prepared = tmp_path / "prepared.jsonl"
    model_path = tmp_path / "model.joblib"
    _write_fixture(prepared)

    summary = train(prepared, model_path, cv=2)

    assert summary.mlflow_logged is True

    import mlflow

    versions = mlflow.MlflowClient().search_model_versions("name='delay-risk'")
    assert len(versions) >= 1  # the model was actually registered, not just logged
