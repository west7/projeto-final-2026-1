"""Delay prediction agent service."""
from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from app.explanation import OutputGuardrailError, explain_risk, safe_explanation
from app.schemas import DelayPrediction, OrderInput, RiskEvidence

ExplanationClient = Callable[[OrderInput, RiskEvidence, str], str]


class DelayAgent:
    """Orchestrate risk lookup, explanation policy and telemetry fields."""

    def __init__(self, risk_tool, explanation_client: ExplanationClient | None = None):
        self.risk_tool = risk_tool
        self.explanation_client = explanation_client

    def classify_order(self, order: OrderInput) -> DelayPrediction:
        started = perf_counter()
        guardrails: list[str] = []
        evidence = self.risk_tool.estimate_delay_risk(order)

        try:
            explanation_result = explain_risk(evidence)
        except OutputGuardrailError as exc:
            evidence = _safe_evidence(evidence, str(exc))
            explanation_result = safe_explanation(str(exc))

        guardrails.extend(explanation_result.guardrails)
        explanation = explanation_result.explanation
        if self.explanation_client is not None:
            explanation = self._try_external_explanation(order, evidence, explanation, guardrails)

        latency_ms = max(0, int((perf_counter() - started) * 1000))
        return DelayPrediction(
            order_id=order.order_id,
            risk_score=evidence.risk_score,
            risk_level=evidence.risk_level,
            confidence=evidence.confidence,
            explanation=explanation,
            recommended_action=explanation_result.recommended_action,
            evidence=evidence,
            guardrails=guardrails,
            fallback_used=evidence.fallback_used,
            latency_ms=latency_ms,
        )

    def _try_external_explanation(
        self,
        order: OrderInput,
        evidence: RiskEvidence,
        deterministic_explanation: str,
        guardrails: list[str],
    ) -> str:
        try:
            generated = self.explanation_client(order, evidence, deterministic_explanation)
        except Exception:
            guardrails.append("llm_fallback")
            return deterministic_explanation

        if not generated or not generated.strip():
            guardrails.append("llm_fallback:empty_response")
            return deterministic_explanation
        return generated.strip()


def classify_order(
    order: OrderInput,
    risk_tool,
    explanation_client: ExplanationClient | None = None,
) -> DelayPrediction:
    return DelayAgent(risk_tool, explanation_client=explanation_client).classify_order(order)


def _safe_evidence(evidence: RiskEvidence, reason: str) -> RiskEvidence:
    return RiskEvidence(
        risk_score=0.0,
        risk_level="low",
        confidence="low",
        sample_size=max(evidence.sample_size, 0),
        segment_used=evidence.segment_used or "output guardrail fallback",
        fallback_used=True,
        factors=[f"output guardrail blocked incomplete evidence: {reason}"],
    )
