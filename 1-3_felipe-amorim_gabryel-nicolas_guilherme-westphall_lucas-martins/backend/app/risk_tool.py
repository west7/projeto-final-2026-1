"""Historical delay-risk estimation over prepared Olist order features."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from app.data_prep import OrderFeature, load_prepared_features
from app.schemas import OrderInput, RiskEvidence

DEFAULT_MIN_SEGMENT_SIZE = 30


@dataclass(frozen=True)
class SegmentRule:
    name: str
    fields: tuple[str, ...]


FALLBACK_HIERARCHY = (
    SegmentRule("seller_state + customer_state + product_category_name", ("seller_state", "customer_state", "product_category_name")),
    SegmentRule("seller_state + customer_state", ("seller_state", "customer_state")),
    SegmentRule("customer_state + product_category_name", ("customer_state", "product_category_name")),
    SegmentRule("seller_state + product_category_name", ("seller_state", "product_category_name")),
    SegmentRule("customer_state", ("customer_state",)),
    SegmentRule("product_category_name", ("product_category_name",)),
    SegmentRule("global delivered-order baseline", ()),
)


class HistoricalRiskTool:
    """Estimate risk from comparable historical segments.

    The tool does not train a model. It selects the most specific segment with
    enough historical examples and returns the observed delayed-order rate.
    """

    def __init__(self, features: Iterable[OrderFeature], min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE):
        self.features = list(features)
        self.min_segment_size = min_segment_size
        if min_segment_size < 1:
            raise ValueError("min_segment_size must be positive")

    @classmethod
    def from_path(cls, path: Path, min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE) -> "HistoricalRiskTool":
        return cls(load_prepared_features(path), min_segment_size=min_segment_size)

    def estimate_delay_risk(self, order: OrderInput) -> RiskEvidence:
        if not self.features:
            return RiskEvidence(
                risk_score=0.0,
                risk_level="low",
                confidence="low",
                sample_size=0,
                segment_used="global delivered-order baseline",
                fallback_used=True,
                factors=["historical dataset is empty; returning safe low-confidence baseline"],
            )

        attempted_specific = False
        for depth, rule in enumerate(FALLBACK_HIERARCHY):
            if not _rule_can_match(rule, order):
                continue

            matches = _match_features(self.features, order, rule)
            is_global = not rule.fields
            enough_examples = len(matches) >= self.min_segment_size
            if is_global or enough_examples:
                delayed_count = sum(1 for feature in matches if feature.delayed)
                score = (delayed_count / len(matches)) if matches else 0.0
                fallback_used = attempted_specific or depth > 0
                return RiskEvidence(
                    risk_score=round(score, 4),
                    risk_level=_risk_level(score),
                    confidence=_confidence(len(matches), depth, fallback_used, self.min_segment_size),
                    sample_size=len(matches),
                    segment_used=rule.name,
                    fallback_used=fallback_used,
                    factors=_factors(order, rule, delayed_count, len(matches), score, fallback_used),
                )

            attempted_specific = True

        raise RuntimeError("fallback hierarchy must always end with a global baseline")


def estimate_delay_risk(
    order: OrderInput,
    features: Iterable[OrderFeature],
    min_segment_size: int = DEFAULT_MIN_SEGMENT_SIZE,
) -> RiskEvidence:
    return HistoricalRiskTool(features, min_segment_size=min_segment_size).estimate_delay_risk(order)


def _rule_can_match(rule: SegmentRule, order: OrderInput) -> bool:
    return all(getattr(order, field) is not None for field in rule.fields)


def _match_features(features: list[OrderFeature], order: OrderInput, rule: SegmentRule) -> list[OrderFeature]:
    if not rule.fields:
        return features
    return [
        feature
        for feature in features
        if all(getattr(feature, field) == getattr(order, field) for field in rule.fields)
    ]


def _risk_level(score: float) -> str:
    if score >= 0.20:
        return "high"
    if score >= 0.10:
        return "medium"
    return "low"


def _confidence(sample_size: int, depth: int, fallback_used: bool, min_segment_size: int) -> str:
    if sample_size >= max(min_segment_size * 5, 100) and depth <= 1 and not fallback_used:
        return "high"
    if sample_size >= min_segment_size and depth <= 4:
        return "medium"
    return "low"


def _factors(
    order: OrderInput,
    rule: SegmentRule,
    delayed_count: int,
    sample_size: int,
    score: float,
    fallback_used: bool,
) -> list[str]:
    factors = [
        f"{delayed_count} de {sample_size} pedidos historicos comparaveis atrasaram ({score:.1%})",
        f"recorte usado: {rule.name}",
    ]
    if rule.fields:
        values = ", ".join(f"{field}={getattr(order, field)}" for field in rule.fields)
        factors.append(f"valores do recorte: {values}")
    if fallback_used:
        factors.append("fallback aplicado por amostra insuficiente em recortes mais especificos")
    return factors
