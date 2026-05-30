from collections.abc import Sequence
import json
import time
from urllib import error, request

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


class LLMProviderResponseError(DomainError):
    code = "llm_provider_response_error"
    status_code = 502


class LLMClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate_feedback(
        self,
        messages: Sequence[FeedbackMessage],
        mode: FeedbackMode = FeedbackMode.reconstruction_feedback,
    ) -> LLMFeedback:
        provider = self._provider()
        if provider == LLMProvider.mock or self.settings.llm_mock_mode:
            return self._generate_mock_feedback(messages, mode)

        if provider == LLMProvider.meituan:
            return self._generate_meituan_feedback(messages, mode)

        if provider != LLMProvider.mock:
            raise LLMProviderUnavailableError(
                "Configured LLM provider is not implemented yet.",
                {
                    "provider": provider.value,
                    "model": self.settings.llm_model,
                    "implemented_providers": [LLMProvider.mock.value, LLMProvider.meituan.value],
                },
            )

        return self._generate_mock_feedback(messages, mode)

    def _generate_mock_feedback(
        self,
        messages: Sequence[FeedbackMessage],
        mode: FeedbackMode,
    ) -> LLMFeedback:
        message_metadata = self._message_metadata(messages)
        return LLMFeedback(
            provider=LLMProvider.mock,
            mode=mode,
            latency_ms=max(self.settings.mock_response_delay_ms, 0),
            is_mock=True,
            model=self.settings.llm_model,
            message_metadata=message_metadata,
            content=f"Mock feedback: offline {mode.value} response for {message_metadata.message_count} message(s).",
        )

    def _generate_meituan_feedback(
        self,
        messages: Sequence[FeedbackMessage],
        mode: FeedbackMode,
    ) -> LLMFeedback:
        if not self.settings.meituan_api_key:
            raise LLMProviderUnavailableError(
                "Meituan LongCat API key is not configured.",
                {
                    "provider": LLMProvider.meituan.value,
                    "model": self.settings.llm_model,
                    "required_env": "MEITUAN_API_KEY",
                },
            )

        started_at = time.perf_counter()
        response_payload = self._post_meituan_chat_completion(messages)
        latency_ms = max(round((time.perf_counter() - started_at) * 1000), 0)
        content = self._extract_openai_compatible_content(response_payload)
        message_metadata = self._message_metadata(messages)

        return LLMFeedback(
            provider=LLMProvider.meituan,
            mode=mode,
            latency_ms=latency_ms,
            is_mock=False,
            model=self.settings.llm_model,
            message_metadata=message_metadata,
            content=content,
        )

    def _post_meituan_chat_completion(self, messages: Sequence[FeedbackMessage]) -> dict:
        endpoint = f"{self.settings.meituan_base_url.rstrip('/')}/v1/chat/completions"
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in messages
            ],
            "max_tokens": self.settings.llm_max_tokens,
            "temperature": self.settings.llm_temperature,
        }
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.settings.meituan_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                http_request,
                timeout=self.settings.llm_request_timeout_seconds,
            ) as response:
                raw_response = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise LLMProviderUnavailableError(
                "Meituan LongCat API returned an error.",
                {
                    "provider": LLMProvider.meituan.value,
                    "model": self.settings.llm_model,
                    "status_code": exc.code,
                },
            ) from exc
        except (error.URLError, TimeoutError) as exc:
            raise LLMProviderUnavailableError(
                "Meituan LongCat API request failed.",
                {
                    "provider": LLMProvider.meituan.value,
                    "model": self.settings.llm_model,
                    "timeout_seconds": self.settings.llm_request_timeout_seconds,
                },
            ) from exc

        try:
            loaded = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise LLMProviderResponseError(
                "Meituan LongCat API returned invalid JSON.",
                {"provider": LLMProvider.meituan.value, "model": self.settings.llm_model},
            ) from exc

        if not isinstance(loaded, dict):
            raise LLMProviderResponseError(
                "Meituan LongCat API returned an unexpected response shape.",
                {"provider": LLMProvider.meituan.value, "model": self.settings.llm_model},
            )
        return loaded

    def _extract_openai_compatible_content(self, payload: dict) -> str:
        try:
            choices = payload["choices"]
            first_choice = choices[0]
            message = first_choice["message"]
            content = message["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderResponseError(
                "Meituan LongCat API response is missing assistant content.",
                {"provider": LLMProvider.meituan.value, "model": self.settings.llm_model},
            ) from exc

        if not isinstance(content, str):
            raise LLMProviderResponseError(
                "Meituan LongCat API assistant content is not text.",
                {"provider": LLMProvider.meituan.value, "model": self.settings.llm_model},
            )
        return content

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
