"""Model-backed risk tool (ML-01, ML-04, ML-05).

The calibrated model supplies the risk *number*; ``HistoricalRiskTool`` still
supplies the traceable *evidence* (factors/segment/sample_size) and is the
fallback. Any problem loading the model degrades to pure historical scoring —
``from_paths`` never raises on a missing dependency or a missing/corrupt file.
"""
from __future__ import annotations

from pathlib import Path

from app.feature_encoding import features_from_order_input
from app.risk_tool import DEFAULT_MIN_SEGMENT_SIZE, HistoricalRiskTool, _risk_level
from app.schemas import OrderInput, RiskEvidence


class ModelRiskTool:
    def __init__(self, historical: HistoricalRiskTool, model):
        self.historical = historical
        self.model = model

    @classmethod
    def from_paths(
        cls,
        prepared_path: Path,
        model_path: Path,
        min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
    ) -> "ModelRiskTool":
        historical = HistoricalRiskTool.from_path(prepared_path, min_segment_size=min_segment_size)
        return cls(historical, _load_model(model_path))

    def estimate_delay_risk(self, order: OrderInput) -> RiskEvidence:
        ev = self.historical.estimate_delay_risk(order)
        if self.model is None:
            return ev
        p = float(self.model.predict_proba([features_from_order_input(order)])[0][1])
        return ev.model_copy(update={
            "risk_score": round(p, 4),
            "risk_level": _risk_level(p),
            "factors": [
                f"score do modelo calibrado: {p:.1%} (probabilidade de atraso prevista)",
                *ev.factors,
            ],
        })


def _load_model(model_path: Path):
    try:
        import joblib

        path = Path(model_path)
        if not path.is_file():
            return None
        return joblib.load(path)
    except Exception:  # missing sklearn/joblib or corrupt artifact → historical fallback
        return None
