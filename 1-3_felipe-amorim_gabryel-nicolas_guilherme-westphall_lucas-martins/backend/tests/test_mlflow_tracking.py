from app import mlflow_tracking
from app.evaluate import AlarmStats, BandStats, EvalReport


def _report():
    return EvalReport(
        n=100,
        base_rate=0.1,
        bands={"high": BandStats(10, 5), "medium": BandStats(20, 4), "low": BandStats(70, 1)},
        alarms={"high": AlarmStats(tp=5, fp=5, fn=5), "medium+high": AlarmStats(tp=9, fp=20, fn=1)},
        fallback_rate=0.25,
        by_state=[],
        min_segment_size=30,
    )


def test_disabled_when_uri_unset_and_log_is_noop(monkeypatch):
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    assert mlflow_tracking.enabled() is False
    assert mlflow_tracking.log_eval_run(_report(), {"scorer": "model"}) is None


def test_run_recorded_with_tracking_uri(tmp_path, monkeypatch):
    uri = f"sqlite:///{tmp_path / 'mlflow.db'}"
    monkeypatch.setenv("MLFLOW_TRACKING_URI", uri)
    assert mlflow_tracking.enabled() is True

    mlflow_tracking.log_eval_run(_report(), {"scorer": "model", "min_segment_size": 30})

    import mlflow

    mlflow.set_tracking_uri(uri)
    runs = mlflow.search_runs(experiment_ids=["0"])
    assert not runs.empty
    assert runs.iloc[0]["metrics.fallback_rate"] == 0.25
    assert runs.iloc[0]["params.scorer"] == "model"
