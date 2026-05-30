import pytest

from backend.app.core.config import Settings
from backend.app.core.errors import DomainError
from backend.app.schemas.feedback import FeedbackMessage, FeedbackMode, LLMProvider
from backend.app.services.llm_client import LLMClient, LLMProviderResponseError


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
        "message": "Configured LLM provider is not implemented yet.",
        "detail": {
            "provider": provider,
            "model": f"{provider}-model",
            "implemented_providers": ["mock", "meituan"],
        },
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
        "supported_providers": ["mock", "openai", "doubao", "deepseek", "qwen", "meituan"],
    }


def test_meituan_provider_requires_api_key_without_secret_leakage():
    client = build_client(
        "meituan",
        llm_model="LongCat-2.0-Preview",
        llm_mock_mode=False,
    )

    with pytest.raises(DomainError) as exc_info:
        client.generate_feedback([FeedbackMessage(role="user", content="hello")])

    payload = exc_info.value.to_payload()

    assert payload == {
        "code": "llm_provider_unavailable",
        "message": "Meituan LongCat API key is not configured.",
        "detail": {
            "provider": "meituan",
            "model": "LongCat-2.0-Preview",
            "required_env": "MEITUAN_API_KEY",
        },
    }


def test_meituan_provider_returns_openai_compatible_content(monkeypatch):
    client = build_client(
        "meituan",
        llm_model="LongCat-2.0-Preview",
        llm_mock_mode=False,
        meituan_api_key="test-meituan-secret",
    )
    captured_messages = []

    def fake_post(messages):
        captured_messages.extend(messages)
        return {"choices": [{"message": {"content": "LongCat response"}}]}

    monkeypatch.setattr(client, "_post_meituan_chat_completion", fake_post)

    feedback = client.generate_feedback([FeedbackMessage(role="user", content="hello")])

    assert feedback.provider == LLMProvider.meituan
    assert feedback.is_mock is False
    assert feedback.model == "LongCat-2.0-Preview"
    assert feedback.content == "LongCat response"
    assert captured_messages == [FeedbackMessage(role="user", content="hello")]
    assert "test-meituan-secret" not in feedback.model_dump_json()


def test_meituan_provider_rejects_malformed_response(monkeypatch):
    client = build_client(
        "meituan",
        llm_model="LongCat-2.0-Preview",
        llm_mock_mode=False,
        meituan_api_key="test-meituan-secret",
    )
    monkeypatch.setattr(client, "_post_meituan_chat_completion", lambda messages: {"choices": []})

    with pytest.raises(LLMProviderResponseError) as exc_info:
        client.generate_feedback([FeedbackMessage(role="user", content="hello")])

    assert exc_info.value.to_payload() == {
        "code": "llm_provider_response_error",
        "message": "Meituan LongCat API response is missing assistant content.",
        "detail": {"provider": "meituan", "model": "LongCat-2.0-Preview"},
    }
