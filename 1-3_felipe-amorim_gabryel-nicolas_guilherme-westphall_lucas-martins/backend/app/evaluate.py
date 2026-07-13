"""Offline evaluation of the historical delay-risk baseline (DELAY-09).

Leave-one-out over the prepared Olist orders: each order is scored by the same
segment/fallback logic the agent uses in production, then compared to its known
`delayed` label. Reports confusion/calibration by risk band, recall/precision
for the alarm bands, fallback rate, and a per-state breakdown.

Scoring reuses ``FALLBACK_HIERARCHY``, ``DEFAULT_MIN_SEGMENT_SIZE`` and
``_risk_level`` from ``risk_tool`` so the evaluation never drifts from the
tool it grades. A precomputed segment index replaces the tool's per-call linear
scan, turning an O(n^2) sweep into O(n) — required to evaluate ~96k orders.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from app import mlflow_tracking
from app.data_prep import OrderFeature, load_prepared_features
from app.risk_tool import DEFAULT_MIN_SEGMENT_SIZE, FALLBACK_HIERARCHY, _risk_level

_DEFAULT_PREPARED_PATH = Path(__file__).resolve().parents[1] / "data" / "prepared_orders.jsonl"
_BAND_ORDER = ("high", "medium", "low")


@dataclass
class Prediction:
    risk_level: str
    fallback_used: bool
    sample_size: int


@dataclass
class BandStats:
    n: int
    delayed: int

    @property
    def observed_rate(self) -> float:
        return self.delayed / self.n if self.n else 0.0


@dataclass
class AlarmStats:
    tp: int
    fp: int
    fn: int

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0.0

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0.0


@dataclass
class StateStats:
    n: int
    delayed: int
    flagged_delayed: int
    fallback: int

    @property
    def recall(self) -> float:
        return self.flagged_delayed / self.delayed if self.delayed else 0.0

    @property
    def fallback_rate(self) -> float:
        return self.fallback / self.n if self.n else 0.0


@dataclass
class EvalReport:
    n: int
    base_rate: float
    bands: dict[str, BandStats]
    alarms: dict[str, AlarmStats]
    fallback_rate: float
    by_state: list[tuple[str, StateStats]]
    min_segment_size: int


def build_segment_index(features: list[OrderFeature]) -> dict[str, dict[tuple, list[int]]]:
    """For each segment rule, map its field-value tuple to [total, delayed]."""
    index: dict[str, dict[tuple, list[int]]] = {rule.name: defaultdict(lambda: [0, 0]) for rule in FALLBACK_HIERARCHY}
    for feature in features:
        for rule in FALLBACK_HIERARCHY:
            if any(getattr(feature, field) is None for field in rule.fields):
                continue
            key = tuple(getattr(feature, field) for field in rule.fields)
            cell = index[rule.name][key]
            cell[0] += 1
            if feature.delayed:
                cell[1] += 1
    return index


def predict(
    order_like,
    index: dict[str, dict[tuple, list[int]]],
    min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
    self_delayed: bool | None = None,
) -> Prediction:
    """Score an order via the same hierarchy as ``HistoricalRiskTool``.

    When ``self_delayed`` is given the order is assumed present in ``index`` and
    is removed from its own segment (leave-one-out) before scoring.
    """
    attempted_specific = False
    for depth, rule in enumerate(FALLBACK_HIERARCHY):
        if any(getattr(order_like, field) is None for field in rule.fields):
            continue
        key = tuple(getattr(order_like, field) for field in rule.fields)
        total, delayed = index[rule.name].get(key, (0, 0))
        if self_delayed is not None:
            total -= 1
            if self_delayed:
                delayed -= 1
        is_global = not rule.fields
        if is_global or total >= min_segment_size:
            score = (delayed / total) if total > 0 else 0.0
            fallback_used = attempted_specific or depth > 0
            return Prediction(_risk_level(score), fallback_used, total)
        attempted_specific = True
    raise RuntimeError("fallback hierarchy must always end with a global baseline")


def compute_report(
    features: list[OrderFeature],
    min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
) -> EvalReport:
    if not features:
        raise ValueError("no prepared features to evaluate")

    index = build_segment_index(features)
    predictions = [
        predict(feature, index, min_segment_size, self_delayed=feature.delayed)
        for feature in features
    ]
    return _report_from_predictions(features, predictions, min_segment_size)


def compute_model_report(
    features: list[OrderFeature],
    min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
    cv: int = 5,
) -> EvalReport:
    """Score every order with an out-of-fold model probability.

    ``cross_val_predict`` refits per fold so no order is scored by a model that
    saw it — the model-equivalent of the baseline's leave-one-out.
    """
    if not features:
        raise ValueError("no prepared features to evaluate")

    import pandas as pd
    from sklearn.model_selection import cross_val_predict

    from app.feature_encoding import FEATURE_COLUMNS, features_from_order_feature
    from app.train_model import build_pipeline

    X = pd.DataFrame([features_from_order_feature(f) for f in features], columns=FEATURE_COLUMNS)
    y = [f.delayed for f in features]
    proba = cross_val_predict(build_pipeline(cv=cv), X, y, cv=cv, method="predict_proba")[:, 1]
    predictions = [Prediction(_risk_level(p), fallback_used=False, sample_size=0) for p in proba]
    return _report_from_predictions(features, predictions, min_segment_size)


def _report_from_predictions(
    features: list[OrderFeature],
    predictions: list[Prediction],
    min_segment_size: int,
) -> EvalReport:
    bands = {band: BandStats(0, 0) for band in _BAND_ORDER}
    # "high" = flag only the top band; "medium+high" = flag anything above low.
    alarms = {"high": AlarmStats(0, 0, 0), "medium+high": AlarmStats(0, 0, 0)}
    alarm_bands = {"high": {"high"}, "medium+high": {"high", "medium"}}
    by_state: dict[str, StateStats] = defaultdict(lambda: StateStats(0, 0, 0, 0))
    fallback_count = 0
    delayed_total = 0

    for feature, prediction in zip(features, predictions):
        band = bands[prediction.risk_level]
        band.n += 1
        if feature.delayed:
            band.delayed += 1
            delayed_total += 1
        if prediction.fallback_used:
            fallback_count += 1

        for name, flagged in alarm_bands.items():
            alarm = alarms[name]
            predicted_positive = prediction.risk_level in flagged
            if feature.delayed and predicted_positive:
                alarm.tp += 1
            elif feature.delayed:
                alarm.fn += 1
            elif predicted_positive:
                alarm.fp += 1

        state = feature.customer_state
        if state:
            stats = by_state[state]
            stats.n += 1
            if prediction.fallback_used:
                stats.fallback += 1
            if feature.delayed:
                stats.delayed += 1
                if prediction.risk_level in alarm_bands["high"]:
                    stats.flagged_delayed += 1

    n = len(features)
    ranked_states = sorted(by_state.items(), key=lambda kv: kv[1].n, reverse=True)
    return EvalReport(
        n=n,
        base_rate=delayed_total / n,
        bands=bands,
        alarms=alarms,
        fallback_rate=fallback_count / n,
        by_state=ranked_states,
        min_segment_size=min_segment_size,
    )


def render_report(report: EvalReport, top_states: int = 15) -> str:
    lines = [
        "Olist delay-risk baseline — offline evaluation (leave-one-out)",
        f"orders: {report.n:,}   base delay rate: {report.base_rate:.1%}   "
        f"min_segment_size: {report.min_segment_size}",
        "",
        "Risk band × outcome (predicted rate should track observed = calibration):",
        f"  {'band':<8}{'orders':>10}{'delayed':>10}{'observed':>12}",
    ]
    for band in _BAND_ORDER:
        stats = report.bands[band]
        share = stats.n / report.n if report.n else 0.0
        lines.append(
            f"  {band:<8}{stats.n:>10,}{stats.delayed:>10,}{stats.observed_rate:>11.1%}"
            f"   ({share:.0%} of orders)"
        )

    lines += ["", "Alarm quality (detecting orders that were actually late):",
              f"  {'alarm':<14}{'recall':>10}{'precision':>12}{'TP':>8}{'FP':>8}{'FN':>8}"]
    for name, alarm in report.alarms.items():
        lines.append(
            f"  {name:<14}{alarm.recall:>9.1%}{alarm.precision:>11.1%}"
            f"{alarm.tp:>8,}{alarm.fp:>8,}{alarm.fn:>8,}"
        )

    lines += ["", f"Fallback rate (segment too small → wider recorte): {report.fallback_rate:.1%}"]

    shown = [item for item in report.by_state if item[1].delayed > 0][:top_states]
    if shown:
        lines += ["", f"Per customer state (top {len(shown)} by volume, high-alarm recall):",
                  f"  {'uf':<5}{'orders':>9}{'delay%':>9}{'recall':>9}{'fallback':>10}"]
        for state, stats in shown:
            lines.append(
                f"  {state:<5}{stats.n:>9,}{stats.delayed / stats.n:>8.1%}"
                f"{stats.recall:>9.1%}{stats.fallback_rate:>10.1%}"
            )
    return "\n".join(lines)


def bands_ordered(report: EvalReport) -> bool:
    """True when observed delay rate is monotone high > medium > low (calibration held)."""
    return (
        report.bands["high"].observed_rate
        > report.bands["medium"].observed_rate
        > report.bands["low"].observed_rate
    )


def report_to_dict(report: EvalReport) -> dict:
    return {
        "n": report.n,
        "base_rate": report.base_rate,
        "fallback_rate": report.fallback_rate,
        "min_segment_size": report.min_segment_size,
        "bands_ordered": bands_ordered(report),
        "bands": {
            band: {"n": s.n, "delayed": s.delayed, "observed_rate": s.observed_rate}
            for band, s in report.bands.items()
        },
        "alarms": {
            name: {"tp": a.tp, "fp": a.fp, "fn": a.fn, "recall": a.recall, "precision": a.precision}
            for name, a in report.alarms.items()
        },
        "by_state": [
            {
                "state": state,
                "n": s.n,
                "delayed": s.delayed,
                "flagged_delayed": s.flagged_delayed,
                "fallback": s.fallback,
                "recall": s.recall,
                "fallback_rate": s.fallback_rate,
            }
            for state, s in report.by_state
        ],
    }


def run_evaluation(
    features: list[OrderFeature],
    scorer: str = "historical",
    min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
    cv: int = 5,
) -> EvalReport:
    if scorer == "model":
        report = compute_model_report(features, min_segment_size=min_segment_size, cv=cv)
    else:
        report = compute_report(features, min_segment_size=min_segment_size)
    mlflow_tracking.log_eval_run(report, {"scorer": scorer, "min_segment_size": min_segment_size})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate the delay-risk baseline over prepared Olist orders.")
    parser.add_argument("--path", type=Path, default=_DEFAULT_PREPARED_PATH,
                        help="prepared_orders.jsonl produced by prepare_data.py")
    parser.add_argument("--scorer", choices=("historical", "model"), default="historical")
    # ponytail: accepted for interface parity; the model scorer refits out-of-fold, so it never loads a saved artifact.
    parser.add_argument("--model-path", type=Path, default=None)
    parser.add_argument("--json-out", type=Path, default=None, help="write the full EvalReport as JSON")
    parser.add_argument("--min-segment-size", type=int, default=DEFAULT_MIN_SEGMENT_SIZE)
    parser.add_argument("--top-states", type=int, default=15)
    args = parser.parse_args()

    if not args.path.is_file():
        raise SystemExit(f"Prepared features not found: {args.path}. Run app/prepare_data.py first.")

    features = load_prepared_features(args.path)
    report = run_evaluation(features, scorer=args.scorer, min_segment_size=args.min_segment_size)
    print(render_report(report, top_states=args.top_states))
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report_to_dict(report), indent=2))
        print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()
