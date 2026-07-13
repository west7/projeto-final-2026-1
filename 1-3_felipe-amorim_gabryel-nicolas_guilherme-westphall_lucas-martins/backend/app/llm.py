"""LLM client for the delay prediction agent.

The agent's primary explanation path should use an LLM. This module keeps the
provider boundary small and testable; network calls are only made when an API
key/configuration is supplied by the API layer.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass

from app.explanation import ExplanationResult
from app.schemas import OrderInput, RiskEvidence

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class LLMClientError(RuntimeError):
    """Raised when the LLM provider cannot return a usable explanation."""


@dataclass(frozen=True)
class OpenAICompatibleLLMClient:
    api_key: str
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: int = 20

    def __call__(self, order: OrderInput, evidence: RiskEvidence, fallback: ExplanationResult) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Voce e um agente operacional de logistica. Responda em portugues do Brasil, "
                        "com explicacao curta, acionavel e fiel as evidencias numericas fornecidas. "
                        "Nao invente dados nem prometa acao automatica. Responda somente em texto puro, "
                        "sem Markdown, titulos, listas ou asteriscos, usando no maximo dois paragrafos curtos."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_prompt(order, evidence, fallback),
                },
            ],
            "temperature": 0.2,
        }
        request = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (OSError, urllib.error.HTTPError, json.JSONDecodeError) as exc:
            raise LLMClientError("llm_request_failed") from exc

        try:
            content = body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, AttributeError) as exc:
            raise LLMClientError("llm_response_missing_content") from exc

        if not content:
            raise LLMClientError("llm_response_empty")
        return content


def build_llm_client_from_env() -> OpenAICompatibleLLMClient | None:
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAICompatibleLLMClient(
        api_key=api_key,
        model=os.getenv("LLM_MODEL", DEFAULT_MODEL),
        base_url=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL),
        timeout_seconds=int(os.getenv("LLM_TIMEOUT_SECONDS", "20")),
    )


def _build_prompt(order: OrderInput, evidence: RiskEvidence, fallback: ExplanationResult) -> str:
    return "\n".join(
        [
            "Explique a previsao de atraso e recomende o proximo passo.",
            f"Pedido: {order.order_id}",
            f"Rota: vendedor {order.seller_state} -> cliente {order.customer_state}",
            f"Categoria: {order.product_category_name or 'nao informada'}",
            f"Risco: {evidence.risk_level} ({evidence.risk_score:.1%})",
            f"Confianca: {evidence.confidence}",
            f"Amostra historica: {evidence.sample_size}",
            f"Recorte usado: {evidence.segment_used}",
            f"Fallback usado: {evidence.fallback_used}",
            "Evidencias:",
            *[f"- {factor}" for factor in evidence.factors],
            f"Acao recomendada pelo fallback deterministico: {fallback.recommended_action}",
        ]
    )
