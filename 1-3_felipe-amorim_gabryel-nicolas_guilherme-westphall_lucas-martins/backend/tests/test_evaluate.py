import json

from app import mlflow_tracking
from app.data_prep import OrderFeature
from app.evaluate import (
    AlarmStats,
    BandStats,
    EvalReport,
    bands_ordered,
    build_segment_index,
    compute_report,
    predict,
    render_report,
    report_to_dict,
    run_evaluation,
)
from app.risk_tool import HistoricalRiskTool
from app.schemas import OrderInput


def _feature(order_id, delayed, customer_state="SP", seller_state="SP", product_category_name="informatica"):
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


def _clean_signal_features():
    # 40 always-late orders in one segment, 40 never-late in another.
    late = [_feature(f"late-{i}", True, "RJ", "SP", "moveis") for i in range(40)]
    ontime = [_feature(f"ok-{i}", False, "BA", "MG", "beleza") for i in range(40)]
    return late + ontime


def test_perfect_separation_gives_full_recall_and_precision():
    report = compute_report(_clean_signal_features(), min_segment_size=5)

    assert report.n == 80
    assert report.base_rate == 0.5
    assert report.bands["high"].n == 40
    assert report.bands["low"].n == 40
    assert report.bands["high"].delayed == 40
    assert report.alarms["high"].recall == 1.0
    assert report.alarms["high"].precision == 1.0
    assert report.fallback_rate == 0.0  # both segments match at the most specific rule


def test_bands_partition_all_orders():
    report = compute_report(_clean_signal_features(), min_segment_size=5)
    assert sum(b.n for b in report.bands.values()) == report.n


def test_leave_one_out_removes_the_order_from_its_own_segment():
    # A lone late order in a tiny segment: without LOO it would look 100% late;
    # with LOO its own delay is removed, so the segment shows 0% among the rest.
    features = [_feature("solo", True, "PR", "SC", "pet")] + [
        _feature(f"pad-{i}", False, "PR", "SC", "pet") for i in range(9)
    ]
    index = build_segment_index(features)
    solo = features[0]
    prediction = predict(solo, index, min_segment_size=5, self_delayed=solo.delayed)
    assert prediction.sample_size == 9
    assert prediction.risk_level == "low"  # 0 of the other 9 were late


def test_predict_matches_risk_tool_for_unseen_order():
    features = _clean_signal_features()
    index = build_segment_index(features)
    order = OrderInput(
        order_id="new",
        customer_state="RJ",
        seller_state="SP",
        product_category_name="moveis",
    )
    tool_evidence = HistoricalRiskTool(features, min_segment_size=5).estimate_delay_risk(order)
    predicted = predict(order, index, min_segment_size=5)  # no LOO: order is not in the index

    assert predicted.risk_level == tool_evidence.risk_level
    assert predicted.fallback_used == tool_evidence.fallback_used
    assert predicted.sample_size == tool_evidence.sample_size


def test_render_report_smoke():
    text = render_report(compute_report(_clean_signal_features(), min_segment_size=5))
    assert "offline evaluation" in text
    assert "recall" in text


def _report_with_rates(high, medium, low):
    return EvalReport(
        n=30,
        base_rate=0.3,
        bands={"high": BandStats(10, int(high * 10)), "medium": BandStats(10, int(medium * 10)),
               "low": BandStats(10, int(low * 10))},
        alarms={"high": AlarmStats(0, 0, 0), "medium+high": AlarmStats(0, 0, 0)},
        fallback_rate=0.0,
        by_state=[],
        min_segment_size=5,
    )


def test_bands_ordered_detects_monotone_calibration():
    assert bands_ordered(_report_with_rates(0.8, 0.4, 0.1)) is True
    assert bands_ordered(_report_with_rates(0.1, 0.4, 0.8)) is False


def test_model_scorer_produces_per_state_report_and_json(tmp_path):
    report = run_evaluation(_clean_signal_features(), scorer="model", min_segment_size=5, cv=2)

    states = {state for state, _ in report.by_state}
    assert {"RJ", "BA"} <= states

    out = tmp_path / "eval_model.json"
    out.write_text(json.dumps(report_to_dict(report), indent=2))
    payload = json.loads(out.read_text())
    assert payload["n"] == 80
    assert any(entry["state"] == "RJ" for entry in payload["by_state"])
    assert "recall" in payload["alarms"]["high"]


def test_run_evaluation_invokes_mlflow_log(monkeypatch):
    calls = []
    monkeypatch.setattr(mlflow_tracking, "log_eval_run", lambda report, params: calls.append(params))

    run_evaluation(_clean_signal_features(), scorer="historical", min_segment_size=5)

    assert calls == [{"scorer": "historical", "min_segment_size": 5}]
