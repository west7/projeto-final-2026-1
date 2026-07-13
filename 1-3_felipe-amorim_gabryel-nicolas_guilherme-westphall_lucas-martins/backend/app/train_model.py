"""Train and persist the calibrated delay-risk classifier (ML-03, MLF-02, ML-07).

Runnable as ``python -m app.train_model``. The pipeline ordinal-encodes the
categorical columns and feeds a ``HistGradientBoostingClassifier`` wrapped in an
isotonic ``CalibratedClassifierCV`` so the output probabilities stay calibrated.
The fitted pipeline is persisted with ``joblib`` and, when MLflow is configured,
registered as a model artifact.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OrdinalEncoder

from app.data_prep import load_prepared_features
from app.feature_encoding import (
    CATEGORICAL_COLUMNS,
    FEATURE_COLUMNS,
    features_from_order_feature,
)

_DEFAULT_PREPARED_PATH = Path(__file__).resolve().parents[1] / "data" / "prepared_orders.jsonl"
_DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[1] / "data" / "model.joblib"


@dataclass
class TrainSummary:
    n_orders: int
    delayed_count: int
    model_path: Path
    mlflow_logged: bool


def _records_to_frame(records) -> pd.DataFrame:
    # Accepts a list of feature dicts (serving) or a DataFrame slice (cross-val); both reindex to FEATURE_COLUMNS.
    return pd.DataFrame(records, columns=FEATURE_COLUMNS)


def build_pipeline(cv: int = 5) -> Pipeline:
    encoder = ColumnTransformer(
        [(
            "cat",
            OrdinalEncoder(
                handle_unknown="use_encoded_value",
                unknown_value=-1,
                encoded_missing_value=-2,
            ),
            CATEGORICAL_COLUMNS,
        )],
        remainder="passthrough",
    )
    categorical_indices = list(range(len(CATEGORICAL_COLUMNS)))
    classifier = CalibratedClassifierCV(
        HistGradientBoostingClassifier(categorical_features=categorical_indices),
        method="isotonic",
        cv=cv,
    )
    return Pipeline([
        ("frame", FunctionTransformer(_records_to_frame)),
        ("encode", encoder),
        ("clf", classifier),
    ])


def _mlflow_enabled() -> bool:
    try:
        from app import mlflow_tracking
    except ImportError:
        return False
    return mlflow_tracking.enabled()


def train(prepared_path: Path, model_path: Path, cv: int = 5) -> TrainSummary:
    features = load_prepared_features(prepared_path)
    X = [features_from_order_feature(f) for f in features]
    y = [f.delayed for f in features]

    pipeline = build_pipeline(cv=cv)
    pipeline.fit(X, y)

    model_path = Path(model_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)

    mlflow_logged = False
    if _mlflow_enabled():
        import mlflow

        with mlflow.start_run(run_name="train_delay_model"):
            mlflow.sklearn.log_model(pipeline, name="model", registered_model_name="delay-risk")
        mlflow_logged = True

    return TrainSummary(
        n_orders=len(features),
        delayed_count=sum(1 for d in y if d),
        model_path=model_path,
        mlflow_logged=mlflow_logged,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the calibrated delay-risk classifier.")
    parser.add_argument("--path", type=Path, default=_DEFAULT_PREPARED_PATH)
    parser.add_argument("--model-path", type=Path, default=_DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"Prepared features not found: {args.path}. Run app/prepare_data.py first.")

    summary = train(args.path, args.model_path)
    print(
        f"trained on {summary.n_orders:,} orders ({summary.delayed_count:,} delayed) "
        f"→ {summary.model_path}   mlflow_logged={summary.mlflow_logged}"
    )


if __name__ == "__main__":
    main()
