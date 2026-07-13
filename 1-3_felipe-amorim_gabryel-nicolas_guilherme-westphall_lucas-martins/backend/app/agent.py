"""Delay prediction agent service."""
from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from app.explanation import ExplanationResult, OutputGuardrailError, explain_risk, safe_explanation
from app.llm import LLMClientError, LLMResult
from app.schemas import DelayPrediction, LLMUsage, OrderInput, RiskEvidence

LLMClient = Callable[[OrderInput, RiskEvidence, ExplanationResult], "str | LLMResult"]


class DelayAgent:
    """Orchestrate risk lookup, LLM explanation, fallback and telemetry."""

    def __init__(self, risk_tool, llm_client: LLMClient | None = None):
        self.risk_tool = risk_tool
        self.llm_client = llm_client

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
        explanation, recommended_action, llm_usage = self._generate_llm_response(
            order, evidence, explanation_result, guardrails
        )

        latency_ms = max(0, int((perf_counter() - started) * 1000))
        return DelayPrediction(
            order_id=order.order_id,
            risk_score=evidence.risk_score,
            risk_level=evidence.risk_level,
            confidence=evidence.confidence,
            explanation=explanation,
            recommended_action=recommended_action,
            evidence=evidence,
            guardrails=guardrails,
            fallback_used=evidence.fallback_used,
            latency_ms=latency_ms,
            llm_usage=llm_usage,
        )

    def _generate_llm_response(
        self,
        order: OrderInput,
        evidence: RiskEvidence,
        fallback: ExplanationResult,
        guardrails: list[str],
    ) -> tuple[str, str, LLMUsage | None]:
        if self.llm_client is None:
            guardrails.append("llm_unconfigured")
            return fallback.explanation, fallback.recommended_action, None

        try:
            generated = self.llm_client(order, evidence, fallback)
        except LLMClientError as exc:
            event = "llm_fallback:rate_limited" if str(exc) == "llm_rate_limited" else "llm_fallback"
            guardrails.append(event)
            return fallback.explanation, fallback.recommended_action, None
        except Exception:
            guardrails.append("llm_fallback")
            return fallback.explanation, fallback.recommended_action, None

        if isinstance(generated, LLMResult):
            response = generated.response
            if response.action_intent != fallback.action_intent:
                guardrails.append("llm_fallback:action_mismatch")
                return fallback.explanation, fallback.recommended_action, None
            return response.explanation, response.recommended_action, generated.usage

        # Raw-text clients remain supported for deterministic/test integrations,
        # but cannot override the safe action policy.
        if not generated or not generated.strip():
            guardrails.append("llm_fallback:empty_response")
            return fallback.explanation, fallback.recommended_action, None
        return generated.strip(), fallback.recommended_action, None


def classify_order(
    order: OrderInput,
    risk_tool,
    llm_client: LLMClient | None = None,
) -> DelayPrediction:
    return DelayAgent(risk_tool, llm_client=llm_client).classify_order(order)


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
