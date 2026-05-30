from enum import Enum

from pydantic import Field

from backend.app.schemas.common import FlexibleSchema


class LLMProvider(str, Enum):
    mock = "mock"
    openai = "openai"
    doubao = "doubao"
    deepseek = "deepseek"
    qwen = "qwen"
    meituan = "meituan"


class FeedbackMode(str, Enum):
    reconstruction_feedback = "reconstruction_feedback"


class FeedbackMessage(FlexibleSchema):
    role: str
    content: str


class FeedbackMessageMetadata(FlexibleSchema):
    message_count: int
    roles: list[str]
    total_characters: int
    max_message_characters: int


class LLMFeedback(FlexibleSchema):
    provider: LLMProvider
    mode: FeedbackMode
    latency_ms: int = Field(ge=0)
    is_mock: bool
    model: str
    message_metadata: FeedbackMessageMetadata
    content: str
