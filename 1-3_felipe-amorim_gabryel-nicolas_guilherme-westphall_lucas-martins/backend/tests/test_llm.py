import json

from app.explanation import ExplanationResult
from app.llm import OpenAICompatibleLLMClient, build_llm_client_from_env
from app.schemas import OrderInput, RiskEvidence


def _order():
    return OrderInput(order_id="o1", customer_state="SP", seller_state="RJ", product_category_name="informatica")


def _evidence():
    return RiskEvidence(
        risk_score=0.25,
        risk_level="high",
        confidence="medium",
        sample_size=40,
        segment_used="seller_state + customer_state",
        fallback_used=False,
        factors=["10 de 40 pedidos historicos comparaveis atrasaram (25.0%)"],
    )


def _fallback():
    return ExplanationResult(
        explanation="fallback explanation",
        recommended_action="fallback action",
        guardrails=[],
    )


def test_build_llm_client_from_env_returns_none_without_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert build_llm_client_from_env() is None


def test_build_llm_client_from_env_uses_config(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "secret")
    monkeypatch.setenv("LLM_MODEL", "model-x")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example/v1")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "7")
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")

    client = build_llm_client_from_env()

    assert client.api_key == "secret"
    assert client.model == "model-x"
    assert client.base_url == "https://llm.example/v1"
    assert client.timeout_seconds == 7
    assert client.reasoning_effort == "low"


def test_build_llm_client_from_env_defaults_reasoning_effort_to_none(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "secret")
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)

    assert build_llm_client_from_env().reasoning_effort == "none"


def test_openai_compatible_client_sends_evidence_and_reads_content(monkeypatch):
    calls = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": " texto final "}}]}).encode("utf-8")

    def fake_urlopen(request, timeout):
        calls["url"] = request.full_url
        calls["timeout"] = timeout
        calls["headers"] = dict(request.header_items())
        calls["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OpenAICompatibleLLMClient(api_key="secret", model="model-x", base_url="https://llm.example/v1")

    result = client(_order(), _evidence(), _fallback())

    assert result.text == "texto final"
    assert result.usage.model == "model-x"
    assert calls["url"] == "https://llm.example/v1/chat/completions"
    assert calls["timeout"] == 20
    assert calls["headers"]["Authorization"] == "Bearer secret"
    assert calls["payload"]["model"] == "model-x"
    assert calls["payload"]["reasoning_effort"] == "none"  # default disables Gemini thinking
    assert "10 de 40" in calls["payload"]["messages"][1]["content"]


def test_openai_compatible_client_omits_reasoning_effort_when_blank(monkeypatch):
    calls = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode("utf-8")

    def fake_urlopen(request, timeout):
        calls["payload"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OpenAICompatibleLLMClient(api_key="secret", model="model-x", reasoning_effort="")

    client(_order(), _evidence(), _fallback())

    assert "reasoning_effort" not in calls["payload"]


def test_openai_compatible_client_captures_token_usage(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            # total > prompt+completion mirrors reasoning models (e.g. gemini-2.5-flash),
            # where thinking tokens land in total but not completion.
            return json.dumps(
                {
                    "choices": [{"message": {"content": "ok"}}],
                    "usage": {"prompt_tokens": 226, "completion_tokens": 99, "total_tokens": 1026},
                }
            ).encode("utf-8")

    monkeypatch.setattr("urllib.request.urlopen", lambda request, timeout: FakeResponse())
    client = OpenAICompatibleLLMClient(api_key="secret", model="model-x")

    usage = client(_order(), _evidence(), _fallback()).usage

    assert usage.model == "model-x"
    assert usage.prompt_tokens == 226
    assert usage.completion_tokens == 99
    assert usage.total_tokens == 1026


def test_openai_compatible_client_tolerates_missing_usage(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode("utf-8")

    monkeypatch.setattr("urllib.request.urlopen", lambda request, timeout: FakeResponse())
    usage = OpenAICompatibleLLMClient(api_key="secret", model="model-x")(_order(), _evidence(), _fallback()).usage

    assert usage.model == "model-x"
    assert usage.prompt_tokens is None
    assert usage.total_tokens is None
