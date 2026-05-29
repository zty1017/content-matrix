import pytest

from backend.app.core.config import Settings
from backend.app.core.errors import DomainError
from backend.app.schemas.feedback import FeedbackMessage, FeedbackMode, LLMProvider
from backend.app.services.llm_client import LLMClient


def build_client(provider: str = "mock", **overrides) -> LLMClient:
    settings = Settings(_env_file=None, llm_provider=provider, **overrides)
    return LLMClient(settings)


def test_mock_provider_returns_deterministic_feedback_metadata_and_content():
    client = build_client(mock_response_delay_ms=25)
    messages = [
        FeedbackMessage(role="system", content="Keep the response deterministic."),
        FeedbackMessage(role="user", content="Draft a concise matrix critique."),
    ]

    first = client.generate_feedback(messages, mode=FeedbackMode.reconstruction_feedback)
    second = client.generate_feedback(messages, mode=FeedbackMode.reconstruction_feedback)

    assert first == second
    assert first.provider == LLMProvider.mock
    assert first.mode == FeedbackMode.reconstruction_feedback
    assert first.latency_ms == 25
    assert first.is_mock is True
    assert first.model == "mock-content-matrix-v0"
    assert first.content == "Mock feedback: offline reconstruction_feedback response for 2 message(s)."
    assert first.message_metadata.model_dump(mode="json") == {
        "message_count": 2,
        "roles": ["system", "user"],
        "total_characters": 64,
        "max_message_characters": 32,
    }
    assert "Draft a concise" not in first.model_dump_json()


@pytest.mark.parametrize("provider", ["openai", "doubao", "deepseek", "qwen"])
def test_non_mock_providers_raise_controlled_error_without_secret_leakage(provider: str):
    secret_value = f"{provider}-super-secret-key"
    client = build_client(
        provider,
        llm_model=f"{provider}-model",
        llm_mock_mode=False,
        openai_api_key=secret_value,
        doubao_api_key=secret_value,
        deepseek_api_key=secret_value,
        qwen_api_key=secret_value,
    )

    with pytest.raises(DomainError) as exc_info:
        client.generate_feedback([FeedbackMessage(role="user", content="hello")])

    error = exc_info.value
    payload = error.to_payload()

    assert error.code == "llm_provider_unavailable"
    assert error.status_code == 503
    assert payload == {
        "code": "llm_provider_unavailable",
        "message": "Configured LLM provider is disabled in v0 offline mode.",
        "detail": {"provider": provider, "model": f"{provider}-model", "mock_required": True},
    }
    assert secret_value not in str(error)
    assert secret_value not in repr(payload)


def test_unsupported_provider_raises_controlled_error():
    client = build_client("anthropic")

    with pytest.raises(DomainError) as exc_info:
        client.generate_feedback([FeedbackMessage(role="user", content="hello")])

    payload = exc_info.value.to_payload()

    assert payload["code"] == "llm_provider_unsupported"
    assert payload["detail"] == {
        "provider": "anthropic",
        "supported_providers": ["mock", "openai", "doubao", "deepseek", "qwen"],
    }
