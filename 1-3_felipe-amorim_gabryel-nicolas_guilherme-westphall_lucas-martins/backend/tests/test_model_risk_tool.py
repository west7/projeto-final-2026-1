import json
import sys
from dataclasses import asdict

from app.data_prep import OrderFeature
from app.feature_encoding import features_from_order_input
from app.model_risk_tool import ModelRiskTool
from app.risk_tool import HistoricalRiskTool, _risk_level
from app.schemas import OrderInput
from app.train_model import train


class _StubModel:
    """Model with a fixed delay probability, to control which band it maps to."""

    def __init__(self, p):
        self._p = p

    def predict_proba(self, X):
        return [[1.0 - self._p, self._p]]


def _feature(order_id, delayed):
    return OrderFeature(
        order_id=order_id,
        delayed=delayed,
        customer_state="SP" if delayed else "BA",
        seller_state="RJ" if delayed else "MG",
        same_state=False,
        product_category_name="moveis" if delayed else "beleza",
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


def _prepared(tmp_path):
    path = tmp_path / "prepared.jsonl"
    rows = [_feature(f"late-{i}", True) for i in range(12)]
    rows += [_feature(f"ok-{i}", False) for i in range(12)]
    with open(path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row)) + "\n")
    return path


def _trained_tool(tmp_path):
    prepared = _prepared(tmp_path)
    model_path = tmp_path / "model.joblib"
    train(prepared, model_path, cv=2)
    return ModelRiskTool.from_paths(prepared, model_path), prepared


def _order():
    return OrderInput(order_id="probe", customer_state="SP", seller_state="RJ",
                      product_category_name="moveis")


def test_score_comes_from_model_and_level_matches(tmp_path):
    tool, _ = _trained_tool(tmp_path)
    order = _order()
    ev = tool.estimate_delay_risk(order)

    p = tool.model.predict_proba([features_from_order_input(order)])[0][1]
    assert ev.risk_score == round(p, 4)
    assert ev.risk_level == _risk_level(p)
    assert ev.factors[0].startswith("score do modelo calibrado")


def test_model_overrides_risk_level_to_model_band(tmp_path):
    prepared = _prepared(tmp_path)
    historical = HistoricalRiskTool.from_path(prepared)
    order = _order()
    hist_ev = historical.estimate_delay_risk(order)

    p = 0.05  # 'low' band; historical for this fixture resolves to a different band
    tool = ModelRiskTool(historical, _StubModel(p))
    ev = tool.estimate_delay_risk(order)

    assert _risk_level(p) != hist_ev.risk_level  # guard: bands genuinely differ, so the override is observable
    assert ev.risk_score == round(p, 4)
    assert ev.risk_level == _risk_level(p)  # model band wins, not the historical band


def test_missing_joblib_dependency_falls_back(tmp_path, monkeypatch):
    prepared = _prepared(tmp_path)
    model_path = tmp_path / "model.joblib"
    train(prepared, model_path, cv=2)  # a real, loadable artifact exists on disk

    monkeypatch.setitem(sys.modules, "joblib", None)  # force ImportError inside _load_model
    tool = ModelRiskTool.from_paths(prepared, model_path)
    order = _order()

    assert tool.model is None
    assert tool.estimate_delay_risk(order) == tool.historical.estimate_delay_risk(order)


def test_historical_evidence_preserved_for_guardrail(tmp_path):
    tool, _ = _trained_tool(tmp_path)
    order = _order()
    hist_ev = tool.historical.estimate_delay_risk(order)
    ev = tool.estimate_delay_risk(order)

    assert ev.segment_used == hist_ev.segment_used
    assert ev.sample_size == hist_ev.sample_size and ev.sample_size > 0
    assert ev.confidence == hist_ev.confidence
    assert hist_ev.factors[0] in ev.factors


def test_model_none_falls_back_to_historical(tmp_path):
    prepared = _prepared(tmp_path)
    historical = HistoricalRiskTool.from_path(prepared)
    tool = ModelRiskTool(historical, None)
    order = _order()
    assert tool.estimate_delay_risk(order) == historical.estimate_delay_risk(order)


def test_missing_model_file_falls_back(tmp_path):
    prepared = _prepared(tmp_path)
    tool = ModelRiskTool.from_paths(prepared, tmp_path / "nope.joblib")
    order = _order()
    assert tool.model is None
    assert tool.estimate_delay_risk(order) == tool.historical.estimate_delay_risk(order)


def test_corrupt_model_file_falls_back(tmp_path):
    prepared = _prepared(tmp_path)
    bad = tmp_path / "corrupt.joblib"
    bad.write_bytes(b"not a real joblib artifact")
    tool = ModelRiskTool.from_paths(prepared, bad)
    order = _order()
    assert tool.model is None
    assert tool.estimate_delay_risk(order) == tool.historical.estimate_delay_risk(order)


def test_missing_optional_fields_still_returns_model_score(tmp_path):
    tool, _ = _trained_tool(tmp_path)
    order = OrderInput(order_id="sparse", customer_state="SP", seller_state="RJ")
    ev = tool.estimate_delay_risk(order)
    assert ev.factors[0].startswith("score do modelo calibrado")
