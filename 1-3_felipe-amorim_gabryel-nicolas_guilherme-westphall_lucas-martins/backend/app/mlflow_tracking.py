"""Optional MLflow tracking wrapper (MLF-01).

Everything here is a no-op unless ``MLFLOW_TRACKING_URI`` is set *and* ``mlflow``
is importable, so training and evaluation run unchanged without MLflow present.
"""
from __future__ import annotations

import os

from app.evaluate import EvalReport


def enabled() -> bool:
    if not os.getenv("MLFLOW_TRACKING_URI"):
        return False
    try:
        import mlflow  # noqa: F401
    except ImportError:
        return False
    return True


def _metric_key(name: str) -> str:
    return name.replace("+", "_")


def log_eval_run(report: EvalReport, params: dict) -> None:
    if not enabled():
        return
    import mlflow

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    with mlflow.start_run():
        mlflow.log_params(params)
        for name, alarm in report.alarms.items():
            mlflow.log_metric(f"recall_{_metric_key(name)}", alarm.recall)
            mlflow.log_metric(f"precision_{_metric_key(name)}", alarm.precision)
        for band, stats in report.bands.items():
            mlflow.log_metric(f"observed_rate_{band}", stats.observed_rate)
        mlflow.log_metric("fallback_rate", report.fallback_rate)
        mlflow.log_metric("base_rate", report.base_rate)
        mlflow.log_metric("n", report.n)
