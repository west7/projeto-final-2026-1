"""Deterministic explanation and action policy for delay predictions."""
from __future__ import annotations

from dataclasses import dataclass

from app.schemas import ActionIntent, RiskEvidence


class OutputGuardrailError(ValueError):
    """Raised when evidence is not traceable enough to explain safely."""


@dataclass(frozen=True)
class ExplanationResult:
    explanation: str
    action_intent: ActionIntent
    recommended_action: str
    guardrails: list[str]


def explain_risk(evidence: RiskEvidence) -> ExplanationResult:
    """Build a short explanation and action from traceable risk evidence."""
    _validate_evidence(evidence)

    guardrails = []
    if evidence.fallback_used:
        guardrails.append("fallback_used")
    if evidence.confidence == "low":
        guardrails.append("low_confidence")

    explanation = (
        f"Risco {evidence.risk_level} ({evidence.risk_score:.1%}) com confianca "
        f"{evidence.confidence}; recorte usado: {evidence.segment_used}; "
        f"amostra historica: {evidence.sample_size} pedidos. "
        f"Evidencias: {'; '.join(evidence.factors[:3])}."
    )
    if evidence.confidence == "low":
        explanation += " Ha pouco historico comparavel, entao a decisao precisa de revisao humana."

    return ExplanationResult(
        explanation=explanation,
        action_intent=_action_intent(evidence),
        recommended_action=_recommended_action(evidence),
        guardrails=guardrails,
    )


def safe_explanation(reason: str) -> ExplanationResult:
    """Return a safe response when output guardrails block the normal path."""
    return ExplanationResult(
        explanation=(
            "Nao ha evidencia rastreavel suficiente para explicar a previsao com seguranca. "
            "Trate o caso como baixa confianca ate revisao humana."
        ),
        action_intent="human_review",
        recommended_action="Encaminhar para revisao humana antes de qualquer comunicacao automatica.",
        guardrails=[f"output_guardrail:{reason}"],
    )


def _validate_evidence(evidence: RiskEvidence) -> None:
    if not evidence.factors:
        raise OutputGuardrailError("missing_factors")
    if not evidence.segment_used:
        raise OutputGuardrailError("missing_segment")
    if evidence.sample_size <= 0:
        raise OutputGuardrailError("missing_sample")


def _recommended_action(evidence: RiskEvidence) -> str:
    if evidence.confidence == "low":
        return "Encaminhar para revisao humana; historico comparavel insuficiente."
    if evidence.risk_level == "high":
        return "Priorizar acompanhamento logistico e comunicar o cliente de forma proativa."
    if evidence.risk_level == "medium":
        return "Monitorar o pedido diariamente e preparar comunicacao preventiva se houver novo sinal de atraso."
    return "Manter fluxo normal e reavaliar se prazo, rota ou transportadora mudarem."


def _action_intent(evidence: RiskEvidence) -> ActionIntent:
    if evidence.confidence == "low":
        return "human_review"
    if evidence.risk_level == "high":
        return "prioritize"
    if evidence.risk_level == "medium":
        return "monitor"
    return "normal_flow"
