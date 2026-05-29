from collections.abc import Sequence

from backend.app.core.config import Settings
from backend.app.core.errors import DomainError
from backend.app.schemas.feedback import (
    FeedbackMessage,
    FeedbackMessageMetadata,
    FeedbackMode,
    LLMFeedback,
    LLMProvider,
)


class LLMProviderUnavailableError(DomainError):
    code = "llm_provider_unavailable"
    status_code = 503


class LLMProviderUnsupportedError(DomainError):
    code = "llm_provider_unsupported"
    status_code = 400


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_feedback(
        self,
        messages: Sequence[FeedbackMessage],
        mode: FeedbackMode = FeedbackMode.reconstruction_feedback,
    ) -> LLMFeedback:
        provider = self._provider()
        if provider != LLMProvider.mock:
            raise LLMProviderUnavailableError(
                "Configured LLM provider is disabled in v0 offline mode.",
                {
                    "provider": provider.value,
                    "model": self.settings.llm_model,
                    "mock_required": True,
                },
            )

        message_metadata = self._message_metadata(messages)
        return LLMFeedback(
            provider=provider,
            mode=mode,
            latency_ms=max(self.settings.mock_response_delay_ms, 0),
            is_mock=True,
            model=self.settings.llm_model,
            message_metadata=message_metadata,
            content=f"Mock feedback: offline {mode.value} response for {message_metadata.message_count} message(s).",
        )

    def _provider(self) -> LLMProvider:
        try:
            return LLMProvider(self.settings.llm_provider)
        except ValueError as exc:
            raise LLMProviderUnsupportedError(
                "Configured LLM provider is not supported.",
                {
                    "provider": self.settings.llm_provider,
                    "supported_providers": [provider.value for provider in LLMProvider],
                },
            ) from exc

    @staticmethod
    def _message_metadata(messages: Sequence[FeedbackMessage]) -> FeedbackMessageMetadata:
        lengths = [len(message.content) for message in messages]
        return FeedbackMessageMetadata(
            message_count=len(messages),
            roles=[message.role for message in messages],
            total_characters=sum(lengths),
            max_message_characters=max(lengths, default=0),
        )
