from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Content Matrix"
    app_version: str = "0.0.1"
    environment: str = "local"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )
    llm_provider: str = "mock"
    llm_model: str = "mock-content-matrix-v0"
    llm_mock_mode: bool = True
    openai_api_key: str | None = None
    doubao_api_key: str | None = None
    asr_provider: str = "mock"
    asr_mock_mode: bool = True
    asr_doubao_resource_id: str = "volc.bigasr.auc_turbo"
    asr_request_timeout_seconds: float = 30.0
    asr_max_audio_size_mb: int = 50
    deepseek_api_key: str | None = None
    qwen_api_key: str | None = None
    meituan_api_key: str | None = None
    meituan_base_url: str = "https://api.longcat.chat/openai"
    llm_request_timeout_seconds: float = 30.0
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.7
    mock_response_delay_ms: int = 0

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
